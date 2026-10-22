# Unreal Engine licensing for archviz (not legal advice)

Epic's license, FAQ and EULA pages returned 403 when this was researched (2026-10-22). Everything below comes from Epic's blog as quoted by press and third parties. **Before any commercial use, the user must read the current terms themselves**: https://www.unrealengine.com/license and https://www.unrealengine.com/en-US/eula/unreal

## Current model (announced 2024, still reported in 2026)
| Who | Cost |
|---|---|
| Students, educators, hobbyists | free |
| Companies with **< US$1M annual gross revenue** | free |
| Non-game companies **> US$1M** annual revenue (linear content: film, TV, **architectural visualization**, immersive experiences not sold to individuals) | Unreal Subscription **US$1,850 per seat per year** (third-party check Sept 2026: unchanged) |
| Games | 5% royalty on lifetime gross above US$1M per product; Epic Games Store revenue excluded |

- From 2026-05-27 the Unreal Subscription reportedly no longer includes Twinmotion and RealityScan (search summary of an Epic blog update — unverified on the primary page).

## Typical archviz cases
- **Stills and videos** delivered to a client: linear content → free under the revenue threshold, seat-based above it. No royalty.
- **Walkthrough app made for one client (work-for-hire)**: under the old EULA, non-recoverable consulting/development fees (Epic's example: an architect's walkthrough) were royalty-exempt; Epic staff said a commissioned piece for one client is royalty-free, but if the client later charges for it (subscription, store sale) royalties apply. That is UE4-era forum guidance — check the current EULA.
- **An app licensed to third parties that depends on Unreal code at runtime** may fall outside the seat model — exact wording unverified.
- Pixel Streaming hosted publicly = your own server/cloud cost on top (not an Epic fee, but not free).

## What to tell the user
"Free for you if your company makes under US$1M a year. Renders, videos and a walkthrough for one client are fine. If you plan to sell the app to the public, or your company is above US$1M, read Epic's current EULA first — I couldn't open those pages to confirm."

## Disk and hardware (practical cost)
- No official disk figure. Reported: UE 5.8.1 39 GB download / ~70 GB installed; Launcher up to 115 GB; source build 160–400 GB. Reserve **≥ 150 GB** on NVMe (engine + project + DDC + builds; experience value).
- Recommended editor PC: Windows 11, 4-core 2.5 GHz, 32 GB RAM, 8 GB+ VRAM, DX12 GPU. HW ray-traced Lumen: RTX 2000 / RX 6000 / Arc A or newer.

## Sources
- Epic pricing blog (403 when fetched): https://www.unrealengine.com/blog/we-are-updating-unreal-engine-twinmotion-and-realitycapture-pricing-in-late-april
- CGPress summary: https://cgpress.org/archives/unreal-engine-updates-pricing-for-non-game-industries.html
- Third-party price check (2026-09-07): https://www.renderahouse.com/blog/twinmotion-pricing
- Work-for-hire forum answer (UE4 era): https://answers.unrealengine.com/questions/184591/view.html
- EULA (403 when fetched): https://www.unrealengine.com/en-US/eula/unreal
- Disk space reports: https://forums.unrealengine.com/t/storage-required-to-install-unreal-engine-5-8-1/2740177 , https://forums.unrealengine.com/t/required-disk-space-to-install-ue5-from-source/2742506
- Hardware specs: https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine
