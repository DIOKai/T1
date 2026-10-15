# Authorization and Asset Escrow

Primary references:

- Cfx.re Asset Escrow: https://docs.fivem.net/docs/server-manual/asset-escrow/
- Cfx.re resource manifest and `escrow_ignore`: https://docs.fivem.net/docs/scripting-reference/resource-manifest/

Verified points from Cfx.re:

- Asset Escrow is designed to prevent direct access to or modification of protected files.
- Supported protected types include Lua, YFT, YDD, and YDR.
- Legitimate users run protected assets through their account/server entitlement; an unauthorized server receives an entitlement error.
- Creators may deliberately exclude editable files through `escrow_ignore`.
- Creator-owned asset transfer is not generally provided as a way to bypass distribution controls.

Practical decision rule:

- **Readable and licensed for modification:** back up, inspect, convert, edit, and validate.
- **Readable but license unclear:** inventory only; obtain permission before editing or redistributing.
- **Protected by escrow/encryption/DRM:** do not attempt access. Ask the vendor for source or an authorized unlocked build.
- **Broken download or entitlement:** use the official portal/vendor support path; do not patch around it.

