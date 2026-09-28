// Read-only Stripe aggregation. No session URLs, emails or customer data emitted.
const days = Number(process.argv[2] || 14);
if (!Number.isInteger(days) || days < 1 || days > 366) throw Error("Days must be 1..366");
if (!process.env.STRIPE_SECRET_KEY) throw Error("Missing STRIPE_SECRET_KEY");
const until = Math.floor(Date.now() / 1000);
const since = until - days * 86400;
const groups = {};
let cursor = "", more = true, count = 0;
while (more) {
  const url = new URL("https://api.stripe.com/v1/checkout/sessions");
  url.searchParams.set("limit", "100");
  url.searchParams.set("created[gte]", since);
  url.searchParams.set("created[lt]", until);
  if (cursor) url.searchParams.set("starting_after", cursor);
  const response = await fetch(url, { headers: { Authorization: `Bearer ${process.env.STRIPE_SECRET_KEY}` } });
  const data = await response.json();
  if (!response.ok) throw Error(`Stripe read failed (${response.status}): ${data.error?.code || "unknown"}`);
  for (const session of data.data) {
    if (session.livemode !== true) throw Error("Live business snapshot requires live-mode records");
    const metadata = session.metadata || {};
    const source = metadata.source || "unknown";
    const internal = /(?:^|[-_])(test|audit|sandbox|release)(?:$|[-_])/i.test(source);
    const channel = internal ? "internal_or_test_label" : metadata.interaction === "purchase_form_v1" ? "explicit_form_unverified_human" : "legacy_unverified";
    const key = [new Date(session.created * 1000).toISOString().slice(0, 10), metadata.product_slug || "unknown", channel, session.currency].join("|");
    groups[key] ||= { sessions: 0, paid: 0, grossPaidCents: 0 };
    groups[key].sessions++;
    if (session.payment_status === "paid") {
      groups[key].paid++;
      groups[key].grossPaidCents += session.amount_total || 0;
    }
    count++;
  }
  more = data.has_more;
  cursor = data.data.at(-1)?.id;
  if (more && !cursor) throw Error("Invalid pagination response");
}
console.log(JSON.stringify({ since: new Date(since * 1000).toISOString(), until: new Date(until * 1000).toISOString(), complete: true, count, grouping: "UTC day|product|interaction class|currency", groups, limitations: ["Form submission does not prove a unique human buyer.", "Legacy sessions include bots and audits.", "Gross paid amounts exclude refund, fee and fulfillment reconciliation.", "No local scan executions or source code are collected."] }, null, 2));
