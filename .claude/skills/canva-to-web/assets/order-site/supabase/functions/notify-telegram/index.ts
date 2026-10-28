// Sends a Telegram message to the shop when a new order is inserted. Free: Telegram bots cost nothing.
// Wiring (see references/backend-setup.md):
//   supabase secrets set TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... WEBHOOK_SECRET=<long random string> MESSAGE_LANG=zh
//   supabase functions deploy notify-telegram --no-verify-jwt
//   Dashboard > Database > Webhooks: table public.orders, event INSERT, HTTP POST to the function URL,
//   header  x-webhook-secret: <the same WEBHOOK_SECRET>
// The message leaves out the phone number on purpose: Telegram is a third party, send it only what the
// kitchen needs (PDPA: share the minimum).

type Line = { qty: number; name: Record<string, string>; options: { label: Record<string, string>; qty: number }[] };

// message language for the staff chat: en (default), zh or ms; item names follow it when the menu has them
const LANG = (Deno.env.get("MESSAGE_LANG") ?? "en") as "en" | "zh" | "ms";
const TEXT = {
  en: { new: "New order", table: "Table", takeaway: "Takeaway, pick up", name: "Name", note: "Note", total: "Total",
        counter: "counter", duitnow_qr: "DuitNow QR", online: "online", unpaid: "unpaid", paid: "paid", refunded: "refunded" },
  zh: { new: "新订单", table: "桌号", takeaway: "外带，取餐时间", name: "名字", note: "备注", total: "合计",
        counter: "柜台付款", duitnow_qr: "DuitNow QR", online: "网上付款", unpaid: "未付款", paid: "已付款", refunded: "已退款" },
  ms: { new: "Pesanan baharu", table: "Meja", takeaway: "Bungkus, ambil pada", name: "Nama", note: "Nota", total: "Jumlah",
        counter: "kaunter", duitnow_qr: "DuitNow QR", online: "dalam talian", unpaid: "belum bayar", paid: "sudah bayar", refunded: "dipulangkan" },
}[LANG] ?? null;
const T = TEXT ?? {
  new: "New order", table: "Table", takeaway: "Takeaway, pick up", name: "Name", note: "Note", total: "Total",
  counter: "counter", duitnow_qr: "DuitNow QR", online: "online", unpaid: "unpaid", paid: "paid", refunded: "refunded",
};
const label = (o: Record<string, string> | null | undefined) => (o && (o[LANG] ?? o.en ?? Object.values(o)[0])) || "";
const rm = (sen: number) => "RM " + (sen / 100).toFixed(2);

function sameSecret(a: string, b: string): boolean {
  // compare in constant time so the secret cannot be guessed from response timing
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

Deno.serve(async (req) => {
  const secret = Deno.env.get("WEBHOOK_SECRET") ?? "";
  if (req.method !== "POST" || !secret || !sameSecret(req.headers.get("x-webhook-secret") ?? "", secret)) {
    return new Response("forbidden", { status: 403 });
  }
  const body = await req.json().catch(() => null);
  const o = body?.record;
  if (body?.type !== "INSERT" || body?.table !== "orders" || !o) return new Response("ignored");

  const tz = Deno.env.get("SHOP_TIMEZONE") ?? "Asia/Kuala_Lumpur";
  const time = (iso: string) => new Intl.DateTimeFormat("en-GB", { timeZone: tz, hour: "2-digit", minute: "2-digit" }).format(new Date(iso));
  const where = o.mode === "dine_in" ? `${T.table} ${o.table_no}` : `${T.takeaway} ${time(o.pickup_at)}`;
  const lines = (o.lines as Line[]).map((l) => {
    const opts = l.options.map((x) => label(x.label) + (x.qty > 1 ? ` x${x.qty}` : "")).join(", ");
    return `${l.qty} x ${label(l.name)}${opts ? ` (${opts})` : ""}`;
  });
  const key = (k: string) => (T as Record<string, string>)[k] ?? k;
  const text = [
    `${T.new} ${o.order_no} - ${where}`,
    `${T.name}: ${String(o.customer_name).slice(0, 60)}`,
    ...lines,
    o.notes ? `${T.note}: ${o.notes}` : "",
    `${T.total} ${rm(o.total_sen)} - ${key(o.payment_method)} - ${key(o.payment_status)}`,
  ].filter(Boolean).join("\n");

  // plain text (no parse_mode), so customer-typed names and notes cannot inject formatting or links
  const res = await fetch(`https://api.telegram.org/bot${Deno.env.get("TELEGRAM_BOT_TOKEN")}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: Deno.env.get("TELEGRAM_CHAT_ID"), text, disable_web_page_preview: true }),
  });
  if (!res.ok) {
    console.error("telegram", res.status, await res.text());
    return new Response("telegram error", { status: 502 });
  }
  return new Response("sent");
});
