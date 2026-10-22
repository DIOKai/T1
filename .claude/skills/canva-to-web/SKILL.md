---
name: canva-to-web
description: Turn a Canva design (café or bubble-tea menu, restaurant menu, flyer, price list) into an interactive mobile ordering DEMO website — swipe through drinks, customise sweetness, milk and size, add toppings, cart, animated order-complete — by reading the design through the Canva connector, extracting the menu into JSON, and building a small accessible static site from the bundled template. Demo only, no real payments or orders. Covers Canva licence limits (Pro images ≤480,000 px on the web, fonts can't be extracted, no logos from Canva content) and free hosting. Use whenever the user wants to "make my Canva menu a website", "Canva 转网页", "把菜单做成点餐网站", "饮料店点单页面", "咖啡店菜单网站", "做一个可以滑动选饮料的网页", "手机点餐 demo", "Canva 设计变成可以互动的网站" — even if they don't say Canva but have a menu design to convert.
---

# Canva design → mobile ordering demo

Reels show a Canva menu "turning into an app" in one prompt. What actually happens: the menu's **content** (names, prices, options) becomes data, and a real web page is built around it. Canva doesn't export working HTML through the connector, and copying the poster as one big image makes a site that can't be tapped, read by screen readers, or updated. So this skill extracts the content into `menu.json`, keeps the look (colours, mood, photos the licence allows), and builds the interaction in code.

**It's a demo.** No payment, no real order, no personal data collected. Free hosts like GitHub Pages forbid commerce/payments anyway. If the user wants real ordering, say it needs a proper ordering/POS service and is out of scope.

## Workflow

### 1. Connect Canva (user does the login)
The Canva connector is a remote MCP server with OAuth.
- **Claude Code:** the `canva` plugin is installed but must be authorized by the user with `/mcp` → canva → Authenticate. Without the plugin: `claude mcp add --transport http canva https://mcp.canva.com/mcp` (from a third-party guide).
- **Codex:** add the same URL as a remote MCP server in `~/.codex/config.toml` (`[mcp_servers.canva]` with `url = "https://mcp.canva.com/mcp"`) and log in with `codex mcp login canva` — 未验证; check `codex mcp --help` on the user's version.
The agent can't do the OAuth step; ask the user to. If they don't want to connect, they can export the design themselves (PNG/PDF) and type or paste the menu text — the rest of the workflow is the same.

Ask before using the connector (T1 rule). Read `references/canva-connector-and-licensing.md`.

### 2. Read the design
- `search-designs` / the link the user gives → design id.
- `read-design` → all text (names, prices, descriptions, option lists) plus page thumbnails. This is the menu source.
- `export-design` → PNG/JPG (40–25000 px wide) for a visual reference and, if the licence allows, image crops. Formats: pdf, png, jpg, gif, pptx, mp4, csv — **no SVG or HTML** from the connector.
- `get-design-dataset`, autofill, brand templates and resize need **Canva Pro or higher**. `get-design-dataset` is about autofill fields, not reading the menu — don't use it for that.
Rate limit: export 20/min; all tools 300/min/user.

### 3. Write `menu.json`
Copy `assets/order-demo-template/menu.json` and fill it from the design: shop name, currency, drinks (id, name, description, price, a colour from the design, whether milk applies), sizes, sweetness levels, milk options, toppings with prices and max count. Show the user the extracted list (names + prices) before building — OCR-like reading of decorative fonts gets prices wrong, and this is the cheapest moment to fix it. Mark anything you guessed.

### 4. Build from the template
`assets/order-demo-template/` is a working static site (index.html + app.js + menu.json, ~300 lines, no build step, no dependencies):
- drink carousel: native touch swipe (CSS scroll-snap) **plus** prev/next buttons and arrow keys — swipe is never the only way;
- customise sheet (`<dialog>`): size, sweetness radio group, milk, toppings with −/+ steppers, quantity, live price;
- cart sheet with remove, total, and a "Place order (demo)" button;
- order-complete animation (circle + drawn check, < 1.5 s) with the text announced in a `role="status"` region;
- `prefers-reduced-motion: reduce` swaps scale/slide for fades; targets ≥ 44 px (WCAG 2.5.8 minimum is 24×24 CSS px);
- menu text is inserted with `textContent` (no HTML injection from design text).
Preview with `python -m http.server` in that folder (fetching `menu.json` doesn't work from `file://`). Restyle it with the design's colours and a free web font; keep the structure. For a bigger app, port the same data and components to a tiny Vite app — only if the user wants it.

Polish with existing skills — ask first: `impeccable` (critique/polish), `animate` (motion), `mobile-ios-design` (iOS-feeling sheets and controls), `design:ux-copy` (button text, empty cart, confirmation wording). Read `references/ordering-ui-and-hosting.md` for the interaction rules.

### 5. Check before showing
- `node --check app.js`, `menu.json` parses, page opens without console errors.
- Phone width (375 px): no horizontal scroll, every control reachable and ≥ 44 px.
- Keyboard only: Tab through, arrows move the carousel, Esc closes sheets, focus returns.
- Turn on reduced motion (OS setting or devtools emulation): no sliding/scaling, only fades.
- Prices and names match the design exactly.

### 6. Host (free) — ask before publishing
Publishing is the user's call. Options and limits in `references/ordering-ui-and-hosting.md`: GitHub Pages (≤ 1 GB site, ~100 GB/month soft, no commerce/payments), Cloudflare Pages (25 MiB per file, 20,000 files), Netlify free credits, or a private Claude Artifact link for a quick share. Before any public URL, run through the licence checklist below.

## Licence checklist (Canva Content License — not legal advice)
- Pro images on a website: each unedited file ≤ **480,000 px** (e.g. 600×800). Free content: no pixel limit. Mixed design → strictest category wins.
- **Fonts can't be extracted or converted** → set the web text in a free web font that looks close (Google Fonts, OFL).
- Canva content **can't be used as a logo/trademark** → the café's logo must be the user's own.
- Don't offer Canva images as standalone downloads (no gallery of raw files); keep them part of the design.
Tell the user to read the licence themselves for anything commercial.

## Limits (say them, don't hide them)
- The connector gives text, thumbnails and raster/PDF exports — not layout code. The site is a rebuild in the design's style, not a pixel copy.
- Canva Code 2.0 (2026-07, free users) can generate sites inside Canva; whether it exports HTML is **未验证**. The Connect API has `html_bundle`/`html_standalone` exports, but the MCP connector doesn't expose them.
- Text reading from stylised menus can be wrong; the user confirms prices.
- The template was checked with `node --check`, a JSON parse and an HTML structure check, not in a real phone browser — say so, and preview it before sharing.
