import {execFileSync, spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createServer} from 'node:http';
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import worker,{STRIPE_PRODUCTS} from '../worker/index.mjs';
const cli=process.env.STRIPE_CLI || 'stripe.exe';
const mode=JSON.parse(execFileSync(cli,['switch','acct_1TKBtaATQfsHIwbt','-p','zippertools-sandbox','--format','json'],{encoding:'utf8',stdio:['ignore','pipe','pipe']}));
if(mode.mode!=='test')throw Error('Sandbox mode required');
mkdirSync('test_runs/release-evidence',{recursive:true});
const realFetch=globalThis.fetch;
function api(method,path,body){
 const args=[method,path,'-p','zippertools-sandbox'];
 for(const [k,v] of new URLSearchParams(body))args.push('-d',`${k}=${v}`);
 const p=JSON.parse(execFileSync(cli,args,{encoding:'utf8',stdio:['ignore','pipe','pipe']}));
 if(p.error)throw Error(JSON.stringify(p.error));
 return p;
}
if(api('get','/v1/account').id!=='acct_1TKBtaATQfsHIwbt')throw Error('Wrong account');
globalThis.fetch=async(url,init={})=>{
 if(String(url).startsWith('https://api.stripe.com/')){
  const p=api((init.method||'get').toLowerCase(),new URL(url).pathname,init.body);
  if(p.object==='checkout.session'&&p.livemode!==false)throw Error('Not test mode');
  return Response.json(p);
 }
 return realFetch(url,init);
};
const env={STRIPE_SECRET_KEY:'test-only-cli-adapter',ASSETS:{fetch:async(req)=>new Response(readFileSync('site/'+(new URL(req.url).pathname.slice(1)||'index')+'.html'))},PAID_ARTIFACTS:{get:async(key)=>{
 const url='https://api.cloudflare.com/client/v4/accounts/a37a93ea2a09b63b434bb40319e3aa1f/storage/kv/namespaces/2793e25033794739a412fd2a4324c744/values/'+encodeURIComponent(key);
 const r=await realFetch(url,{headers:{Authorization:`Bearer ${process.env.CLOUDFLARE_API_TOKEN}`}});
 if(!r.ok)throw Error('KV read failed '+r.status);
 return r.text();
}}};
let webhookCount=0;
const server=createServer(async(req,res)=>{
 try{
 const chunks=[];for await(const c of req)chunks.push(c);
 const r=await worker.fetch(new Request('http://localhost:8789'+req.url,{method:req.method,headers:req.headers,...(chunks.length?{body:Buffer.concat(chunks)}:{})}),env);
 if(req.url==='/stripe/webhook'&&r.status===200)webhookCount++;
 res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));
 }catch(e){res.writeHead(500);res.end(e.message);}
});
await new Promise(resolve=>server.listen(8789,'127.0.0.1',resolve));
const listener=spawn(cli,['listen','-p','zippertools-sandbox','--events','checkout.session.completed','--forward-to','http://127.0.0.1:8789/stripe/webhook'],{stdio:['ignore','pipe','pipe'],windowsHide:true});
try{
 await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('Listener timeout')),30000);function read(c){const m=String(c).match(/whsec_[A-Za-z0-9]+/);if(m){env.STRIPE_WEBHOOK_SECRET=m[0];clearTimeout(timeout);resolve();}}listener.stdout.on('data',read);listener.stderr.on('data',read);});
 const results=[];
 for(const p of Object.values(STRIPE_PRODUCTS)){
  const r=await worker.fetch(new Request('http://localhost:8789/go/'+p.slug+'/release-sandbox'),env);
  if(r.status!==303)throw Error('Checkout create failed '+await r.text());
  const url=r.headers.get('location');const id=url.match(/cs_test_[A-Za-z0-9]+/)[0];
  const unpaid=await worker.fetch(new Request('http://localhost:8789/stripe/delivery?session_id='+id),env);
  if(unpaid.status!==402)throw Error('Unpaid delivery not denied');
  api('get','/v1/payment_pages/'+id);
  const pm=api('post','/v1/payment_methods',new URLSearchParams({'type':'card','card[token]':'tok_visa','billing_details[name]':'Release Test','billing_details[email]':'release@example.com','billing_details[address][line1]':'510 Townsend St','billing_details[address][city]':'San Francisco','billing_details[address][state]':'CA','billing_details[address][postal_code]':'94103','billing_details[address][country]':'US'}));
  api('post','/v1/payment_pages/'+id+'/confirm',new URLSearchParams({payment_method:pm.id,expected_amount:String(p.unitAmount)}));
  const session=api('get','/v1/checkout/sessions/'+id);
  if(session.payment_status!=='paid'||session.livemode!==false||session.amount_total!==p.unitAmount)throw Error('Payment mismatch');
  const delivered=await worker.fetch(new Request('http://localhost:8789/stripe/delivery?session_id='+id),env);
  if(delivered.status!==200)throw Error('Delivery failed '+await delivered.text());
  const bytes=Buffer.from(await delivered.arrayBuffer());
  const recovered=await worker.fetch(new Request('http://localhost:8789/stripe/delivery?session_id='+id),env);
  if(recovered.status!==200 || !Buffer.from(await recovered.arrayBuffer()).equals(bytes))throw Error('Recovery mismatch');
  const success=await worker.fetch(new Request('http://localhost:8789/success?session_id='+id),env);
  if(success.status!==200 || !(await success.text()).includes('session_id'))throw Error('Success page failed');
  writeFileSync('test_runs/release-evidence/'+p.artifactKey,bytes);
  results.push({product:p.slug,session:id,livemode:session.livemode,amount:session.amount_total,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex'),delivery:delivered.status,recovery:200,success:200});
 }
 const deadline=Date.now()+45000;
 while(webhookCount<4 && Date.now()<deadline)await new Promise(resolve=>setTimeout(resolve,500));
 if(webhookCount<4)throw Error('Expected four signed webhooks, got '+webhookCount);
 writeFileSync('test_runs/release-evidence/sandbox-results.json',JSON.stringify({results,webhookCount},null,2));
 console.log(JSON.stringify({results,webhookCount}));
}finally{listener.kill();server.close();}
