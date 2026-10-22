// Ordering DEMO: no payment, no network calls except loading menu.json.
"use strict";
const $ = (id) => document.getElementById(id);
const state = { menu: null, index: 0, cart: [], draft: null };

function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "text") n.textContent = v; // design text is untrusted: never innerHTML
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (k === "style") n.style.cssText = v;
    else n.setAttribute(k, v);
  }
  kids.forEach((c) => n.append(c));
  return n;
}
const money = (v) => `${state.menu.shop.currency} ${v.toFixed(2)}`;

async function init() {
  try {
    const res = await fetch("menu.json");
    if (!res.ok) throw new Error(res.status);
    state.menu = await res.json();
  } catch (e) {
    document.querySelector("main").replaceChildren(el("p", { text:
      "Could not load menu.json. Serve this folder (e.g. `python -m http.server`) instead of opening the file directly." }));
    return;
  }
  const { shop, drinks } = state.menu;
  document.title = `${shop.name} — order demo`;
  $("shop").textContent = shop.name;
  $("tagline").textContent = shop.tagline || "";
  renderCarousel(drinks);
  bindStatic();
  updateCart();
}

function renderCarousel(drinks) {
  const track = $("carousel");
  track.replaceChildren(...drinks.map((d, i) => el("article", {
      class: "card", "aria-roledescription": "slide", "aria-label": `${i + 1} of ${drinks.length}: ${d.name}`,
    },
    el("div", { class: "cup", style: `--c:${/^#[0-9a-f]{3,8}$/i.test(d.color) ? d.color : "#b5835a"}` }),
    el("h2", { text: d.name }),
    el("p", { text: d.desc || "" }),
    el("div", { class: "row" },
      el("strong", { text: money(d.price) }),
      el("button", { class: "primary", onclick: () => openCustom(d), text: "Customise" })))));
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => { if (en.isIntersecting) setCurrent([...track.children].indexOf(en.target)); });
  }, { root: track, threshold: 0.6 });
  [...track.children].forEach((c) => io.observe(c));
  setCurrent(0);
}

function setCurrent(i) {
  const cards = $("carousel").children;
  state.index = Math.max(0, Math.min(i, cards.length - 1));
  [...cards].forEach((c, n) => c.classList.toggle("current", n === state.index));
  $("pos").textContent = `${state.index + 1} / ${cards.length}`;
}

function go(delta) {
  const cards = $("carousel").children;
  const i = Math.max(0, Math.min(state.index + delta, cards.length - 1));
  const smooth = !matchMedia("(prefers-reduced-motion: reduce)").matches;
  cards[i].scrollIntoView({ behavior: smooth ? "smooth" : "auto", inline: "center", block: "nearest" });
  setCurrent(i);
}

function radios(container, name, items, checkedId, onchange) {
  $(container).replaceChildren(...items.map((it) => el("label", {},
    el("input", Object.assign({ type: "radio", name, value: it.id, onchange: () => onchange(it.id) },
      it.id === checkedId ? { checked: "" } : {})),
    el("span", { text: it.price ? `${it.label} +${it.price.toFixed(2)}` : it.label }))));
}

function openCustom(drink) {
  const o = state.menu.options;
  const d = state.draft = { drink, size: o.sizes[0].id, sweet: o.defaultSweetness ?? o.sweetness[0],
    milk: drink.milk ? o.milks[0].id : null, tops: {}, qty: 1 };
  $("cTitle").textContent = drink.name;
  radios("sizes", "size", o.sizes, d.size, (v) => { d.size = v; refresh(); });
  radios("sweet", "sweet", o.sweetness.map((s) => ({ id: String(s), label: `${s}%` })), String(d.sweet),
    (v) => { d.sweet = Number(v); refresh(); });
  $("milkSet").hidden = !drink.milk;
  if (drink.milk) radios("milks", "milk", o.milks, d.milk, (v) => { d.milk = v; refresh(); });
  $("tops").replaceChildren(...o.toppings.map((t) => {
    const out = el("output", { "aria-live": "polite", text: "0" });
    const step = (delta) => {
      d.tops[t.id] = Math.max(0, Math.min((d.tops[t.id] || 0) + delta, t.max ?? 3));
      out.textContent = d.tops[t.id]; refresh();
    };
    return el("div", { class: "row" },
      el("span", { text: `${t.label} +${t.price.toFixed(2)}` }),
      el("div", { class: "stepper" },
        el("button", { type: "button", "aria-label": `Less ${t.label}`, onclick: () => step(-1), text: "−" }),
        out,
        el("button", { type: "button", "aria-label": `More ${t.label}`, onclick: () => step(1), text: "+" })));
  }));
  $("qty").textContent = "1";
  refresh();
  $("custom").showModal();
}

function unitPrice(d) {
  const o = state.menu.options;
  const size = o.sizes.find((s) => s.id === d.size)?.price || 0;
  const milk = o.milks.find((m) => m.id === d.milk)?.price || 0;
  const tops = o.toppings.reduce((sum, t) => sum + (d.tops[t.id] || 0) * t.price, 0);
  return d.drink.price + size + milk + tops;
}

function refresh() {
  const d = state.draft;
  $("addBtn").textContent = `Add · ${money(unitPrice(d) * d.qty)}`;
}

function describe(d) {
  const o = state.menu.options;
  const parts = [o.sizes.find((s) => s.id === d.size).label, `${d.sweet}% sweet`];
  if (d.milk) parts.push(o.milks.find((m) => m.id === d.milk).label);
  o.toppings.forEach((t) => { if (d.tops[t.id]) parts.push(`${t.label} ×${d.tops[t.id]}`); });
  return parts.join(", ");
}

function updateCart(bump) {
  const count = state.cart.reduce((n, it) => n + it.qty, 0);
  const total = state.cart.reduce((n, it) => n + unitPrice(it) * it.qty, 0);
  const badge = $("badge");
  badge.textContent = count;
  $("cartBtn").setAttribute("aria-label", `Cart, ${count} item${count === 1 ? "" : "s"}`);
  if (bump) { badge.classList.remove("bump"); void badge.offsetWidth; badge.classList.add("bump"); }
  $("cartList").replaceChildren(...state.cart.map((it, i) => el("li", {},
    el("div", { class: "row" },
      el("strong", { text: `${it.qty} × ${it.drink.name}` }),
      el("button", { "aria-label": `Remove ${it.drink.name}`, text: "Remove",
        onclick: () => { state.cart.splice(i, 1); updateCart(); $("cartClose").focus(); } })),
    el("div", { class: "muted", text: `${describe(it)} · ${money(unitPrice(it) * it.qty)}` }))));
  $("empty").hidden = state.cart.length > 0;
  $("total").textContent = `Total ${money(total)}`;
  $("placeBtn").disabled = state.cart.length === 0;
}

function bindStatic() {
  $("prev").addEventListener("click", () => go(-1));
  $("next").addEventListener("click", () => go(1));
  $("carousel").addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { e.preventDefault(); go(1); }
    if (e.key === "ArrowLeft") { e.preventDefault(); go(-1); }
  });
  const setQty = (delta) => {
    const d = state.draft; d.qty = Math.max(1, Math.min(d.qty + delta, 20));
    $("qty").textContent = d.qty; refresh();
  };
  $("qMinus").addEventListener("click", () => setQty(-1));
  $("qPlus").addEventListener("click", () => setQty(1));
  $("addBtn").addEventListener("click", () => {
    const d = state.draft;
    state.cart.push({ ...d, tops: { ...d.tops } });
    $("custom").close();
    updateCart(true);
  });
  $("cartBtn").addEventListener("click", () => $("cart").showModal());
  $("cartClose").addEventListener("click", () => $("cart").close());
  $("placeBtn").addEventListener("click", () => {
    const no = "A" + String(Math.floor(Math.random() * 900) + 100);
    const total = $("total").textContent;
    state.cart = [];
    updateCart();
    $("cart").close();
    $("doneMsg").textContent = "";
    $("done").showModal();
    // set after opening so screen readers announce it; demo: nothing is charged or sent
    setTimeout(() => { $("doneMsg").textContent = `Order ${no} received. ${total}. Demo only — nothing was charged.`; }, 50);
  });
  $("doneClose").addEventListener("click", () => $("done").close());
}

init();
