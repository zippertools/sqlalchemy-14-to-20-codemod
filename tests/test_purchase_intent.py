from __future__ import annotations

import subprocess


def test_only_explicit_same_origin_post_creates_checkout() -> None:
    script = """
import assert from 'node:assert/strict';
import worker, {STRIPE_PRODUCTS} from './worker/index.mjs';
let calls = 0;
globalThis.fetch = async (_url, init) => {
  calls++;
  const body = new URLSearchParams(init.body);
  assert.equal(body.get('metadata[interaction]'), 'purchase_form_v1');
  return Response.json({url: 'https://checkout.stripe.com/c/pay/cs_test_intent'});
};
const env = {STRIPE_SECRET_KEY:'sk_test_unit',
  ASSETS:{fetch:async()=>new Response('asset')}};
for(const slug of Object.keys(STRIPE_PRODUCTS)) {
  const url = 'https://zippertools.org/go/'+slug+'/intent-test';
  const before = calls;
  for(const method of ['GET','HEAD']) {
    const response = await worker.fetch(new Request(url,{method}),env);
    assert.equal(response.status,200);
    assert.equal(response.headers.get('cache-control'),'no-store');
    assert.equal(response.headers.get('x-robots-tag'),'noindex');
    const text = await response.text();
    if(method === 'GET') assert.match(text, /form method="post"/);
    else assert.equal(text,'');
  }
  for(const origin of ['', 'https://attacker.example']) {
    const request = new Request(url,{method:'POST',headers:{origin}});
    const response = await worker.fetch(request,env);
    assert.equal(response.status,403);
  }
  assert.equal((await worker.fetch(new Request(url,{method:'PUT'}),env)).status,405);
  assert.equal(calls,before);
  const response = await worker.fetch(new Request(url,{method:'POST',headers:{origin:'https://zippertools.org'}}),env);
  assert.equal(response.status,303);
  assert.equal(calls,before+1);
}
"""
    subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )
