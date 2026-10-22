# Canva connector and licensing

## The connector (Canva MCP)
Official remote MCP server: generate/edit designs, search and read designs, pages and folders, assets and brand management, export (PDF, PNG, JPG, PPTX, MP4 …), comments. Canva Developer Terms, usage policy and prohibited-use rules apply.

### Tools that matter here
| Tool | Plan | Use |
|---|---|---|
| `search-designs` | all | find the menu design |
| `read-design` | all | text, page count, metadata, **page thumbnails**, speaker notes; with an editing transaction, structured element data |
| `get-export-formats` | all | what this design can export to |
| `export-design` | all (quality depends on plan) | `type`: `pdf|png|jpg|gif|pptx|mp4|csv` — **no SVG, no HTML**. PNG/JPG width/height 40–25000 px, `as_single_image`, `transparent_background`, `export_quality: regular|pro`; returns a download URL. 20 requests/min |
| `get-assets`, `remove-background`, `separate-image-layers` | all | image work inside Canva |
| `get-design-dataset`, `autofill-design`, brand templates, `list-brand-kits` | **Pro+** | autofill fields — **not** for reading menu content |
| `resize-design` | Pro+ (Free: limited trial) | |
Server-wide limit: 300 calls/min/user. Free accounts can use the core tools (the official tools page marks most as "All"); admin/permission details 未验证 (that page returned 404).

Free-plan export limits (Connect API docs): no lossy PNG, no transparent background, no `export_quality: pro`; exports fail if the design contains unpurchased premium elements; fixed-size designs can't be upscaled more than 1.125×.

### Connect API vs connector
The Connect API itself can export `html_bundle` / `html_standalone`, and says SVG export is "currently unavailable". The MCP connector's `export-design` does **not** offer HTML (checked against the local schema 2026-10-22). Don't promise HTML export.

### Canva Code 2.0
Released 2026-07 and open to free users: builds front-end sites/interactive pieces from prompts and imports HTML as editable designs. **Whether it exports HTML code is 未验证** (only older second-hand blog posts say so).

## Licence rules for putting the design on a website
From the Canva Content License Agreement:
- **Pro Content on the web:** each unedited file at most **480,000 px** (e.g. 600×800). No limit when published through Canva's own website feature or a Canva-hosted embed. Free Content: no pixel limit. (§5A)
- **No standalone extraction:** don't make Content available so others can download/export/obtain the original file (§9.8, 9.10, 9.12). Integrate images into the page design; no downloadable image gallery. (Whether a given use counts as "standalone" is a legal judgement, 未验证.)
- **Fonts:** only inside Canva or as part of an exported design; **no converting or extracting font files** (§9A) → use a free web font.
- **No trademarks/logos** made from Content (§9.2) → the shop logo must be the user's own artwork.
- **Mixed content:** the most restrictive category applies (§1.3–1.4).
This is not legal advice; ask the user to read the licence for commercial use.

## Sources
- Canva MCP: https://www.canva.dev/docs/mcp/
- Tools and plan limits: https://www.canva.dev/docs/mcp/tools/
- Claude Code install command (third party): https://glama.ai/mcp/servers/yfloby6xwt
- Connect API exports: https://www.canva.dev/docs/connect/api-reference/exports/create-design-export-job/
- Canva Code 2.0: https://www.khaleejtimes.com/business/tech/canva-code-20-explained-how-the-new-ai-tool-builds-websites-and-apps , https://www.edtechinnovationhub.com/news/canva-opens-code-20-to-free-users-with-editable-ai-built-websites-and-apps
- Content License Agreement: https://www.canva.com/policies/content-license-agreement/ ; summary: https://www.canva.com/help/licenses-copyright-commercial-use/
