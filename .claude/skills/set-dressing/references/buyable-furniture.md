# Buyable furniture (furnish from a real store cart)

The Airbnb-style reel: every piece in the 3D apartment was picked from a real online store cart (Mercado Livre there), so the render doubles as a shopping list. The 3D work is normal set dressing; what's different is **the list is the source of truth** — real product, real price, real W×D×H — and the 3D model is either the real one (rare) or an honest stand-in scaled to the real size.

## 1. Keep a furniture list first
One row per product (CSV or JSON), filled by the user from their cart or by the agent from pages the user pastes:

| Column | Example | Notes |
|---|---|---|
| `id`, `room` | `7`, `Living` | room name must match `rooms.json` if used |
| `name` | `Sofá 3 lugares linho cinza` | as the store names it |
| `store`, `url` | `Mercado Livre`, `https://…` | the product page the user gave |
| `price`, `currency`, `qty` | `1299.90`, `BRL`, `1` | write prices without thousand separators if possible (`1299.90`) |
| `w_cm`, `d_cm`, `h_cm` | `210`, `90`, `85` | **assembled** size from the listing; W = longest side facing you |
| `model_source`, `model_url`, `model_licence` | `Poly Haven`, `https://…`, `CC0` | where the 3D stand-in came from |
| `substitute`, `substitute_reason` | `yes`, `similar shape, no official model` | yes whenever the 3D model is not the exact product |
| `notes` | `flat-pack; colour "grafite"` | |

Don't scrape stores. Marketplaces (Mercado Livre/Libre, Amazon, Shopee, IKEA) have terms against automated collection or require registered API apps; the user copies name/price/size, or pastes the page text, and the agent fills the list. Prices change — record the date the list was made. Missing dimensions on a listing → ask the user (or the seller); never guess sizes for something that will be bought.

## 2. Check the list before modelling
```bash
python scripts/furniture_list_check.py furniture.csv --rooms rooms.json
python scripts/furniture_list_check.py furniture.csv --room 420x360 --ceiling 260 --door-width 80 --door-height 200 --export shopping.csv
```
`rooms.json`: `{"Living": {"w_cm": 420, "d_cm": 360, "h_cm": 260, "door_w_cm": 80, "door_h_cm": 200}}`.
Read-only, standard library. ERRORs: missing fields, non-numeric/zero sizes or prices, bad qty, non-http URL, footprint bigger than the room (either orientation), taller than the ceiling. WARNs: may not pass the door (smallest side > door width, or middle side > door height — rule of thumb, ignores corridor turns; flat-pack items usually pass), model licence missing / non-commercial / CC BY (credit), substitute without a reason. Prints totals per currency; `--export` writes a clean shopping-list CSV (refuses to overwrite without `--force`). Exit 1 on errors. Tests: `python scripts/test_furniture_list_check.py`.

Footprint ≤ room is the bare minimum, not "it fits": also keep walking clearances (rule of thumb ~60–90 cm main paths, ~45–60 cm around a dining table / beside a bed) — check in the 3D scene, which is the point of modelling it.

## 3. Find a 3D model per item (free first)
Order (ask before using `free-3d-assets` / the `blender` MCP):
1. **Manufacturer's own downloads** — many brands publish CAD/BIM/3D files for architects (often after free registration). Read the terms: usually "for planning/visualising the product", sometimes no redistribution and no use for other products. Third-party "catalogue" sites re-hosting brand models carry their own (often unclear) rights — prefer the manufacturer's page. 未验证 per brand; check every time.
2. **Poly Haven** (CC0 — any use, no credit needed) and other CC0 sources for generic shapes: sofa, chairs, tables, lamps, plants.
3. **Sketchfab / Poly Pizza** — licence **per model** (CC BY needs credit; CC BY-NC is not for client/commercial work; "Standard"/paid models are not free).
4. **Make it**: simple boxy pieces (beds, shelves, cabinets) are quick to model at the exact size; or the user's own **Hunyuan3D** from the product photo via `free-3d-assets` (local; licence excludes EU/UK/South Korea).
- **IKEA has no public 3D model API.** Its site serves preview models to the browser and community tools pull them, but IKEA grants no licence for that — **don't scrape or redistribute IKEA models**. Use a CC0 look-alike scaled to the IKEA dimensions and mark it as a substitute.
- Never present a substitute as the real product: `substitute=yes` in the list, and say in the delivery which pieces are stand-ins.

## 4. Scale the model to the real size (Blender)
Apply rotation/scale first; origin at bottom centre (also needed by `archviz-web-walkthrough` / Unreal swaps).
```python
# NOT RUN in Blender — uses Object.dimensions (metres, includes scale).
import bpy
def fit_to_listing(ob, w_cm, d_cm, h_cm, tol=0.05):
    tgt = (w_cm / 100, d_cm / 100, h_cm / 100)
    cur = ob.dimensions
    ratios = [t / c for t, c in zip(tgt, cur) if c > 0]
    u = sum(ratios) / len(ratios)                    # uniform scale keeps the design's proportions
    ob.scale = [s * u for s in ob.scale]
    bpy.context.view_layer.update()
    err = [abs(a - b) / b for a, b in zip(ob.dimensions, tgt)]
    return {"scale": round(u, 4), "max_error": round(max(err), 3),
            "substitute_shape_differs": max(err) > tol}   # >5 %: proportions differ → mark substitute
```
- Uniform scale keeps the model's look; if the proportions differ by more than ~5 % (rule of thumb), either scale per axis (only for boxy pieces — it distorts legs and cushions) or keep uniform and mark it a substitute.
- Check X = width (facing side), Y = depth: rotate the model so its front faces −Y before fitting, or the W/D swap.
- Then place it with the normal set-dressing rules (clusters, clear paths).

## 5. Deliver
- Renders / tour + `shopping.csv` (room, name, store, link, qty, price, total, size, substitute).
- In a web tour (`archviz-web-walkthrough`) or Unreal panel, a hotspot per piece can show name, price and the store link — open links in a new tab, `rel="noopener"`; it's the user's call whether to publish prices.
- Affiliate links, price tracking or checkout automation are out of scope; the agent never buys anything (purchases are the user's own action).

## Sources
- Poly Haven licence (CC0, any use, no attribution required): https://polyhaven.com/license
- Community IKEA downloaders and Blender add-on — no explicit IKEA licence (reported): https://digitalproduction.com/2026/02/09/download-ikea-furniture-as-3d-models-minus-the-trolley/ , https://extensions.blender.org/add-ons/ikea-browser/reviews/?score=3
- Third-party CAD catalogues re-hosting brand models ("own design use only", not manufacturer terms): https://www.cadforum.cz/catalog_en/?vyr=Vitra
- Blender Object.dimensions: https://docs.blender.org/api/current/bpy.types.Object.html
