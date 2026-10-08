# Licences, and getting music and sound effects

pixabay.com is blocked from the environment this skill was written in. The licence points below come from search-engine copies of Pixabay's "Content License Summary" (pixabay.com/service/license/) and third-party guides, read 2026-10-08. Read the full licence on the site before a public or paid release. Not legal advice.

## Pixabay Content License, in short

Allowed (the summary says so; only the full licence is binding):
- Free use, commercial included. No credit to the author required (but `CREDITS-pixabay.md` keeps track of where files came from).
- Modify and adapt into new works.
- It covers all Pixabay "Content": images, video, **music and sound effects**.

Not allowed:
- **Selling or distributing content on a standalone basis**: files passed on in substantially the same form as on Pixabay, with no creative effort added. Wallpaper packs, stock collections, an "image pack" resource on a store.
- Commercial use of content showing **recognisable trademarks or logos** for goods and services, or printing on merchandise for sale.
- Immoral or illegal use, especially of content showing recognisable people.
- Misleading or deceptive use (e.g. a real person's photo as a fake NPC "testimonial").
- Using content as part of a trademark, trade name or business name (don't make your server logo from a Pixabay image).
- Some content carries extra rights (trademarks, designs, privacy, property). The page may say so.

What this means on a FiveM server:

| Situation | OK? |
|---|---|
| Phone wallpapers, menu backgrounds, shop pictures inside your own server | yes |
| A loading screen video or music on your server | yes |
| Prop textures made from photos | yes (you've added creative work) |
| Selling or releasing a resource that bundles a few Pixabay files as part of a UI | generally yes, it's part of a larger work; keep CREDITS |
| Releasing a "wallpaper pack" or "loading screen music pack" that's mostly unedited Pixabay files | **no** (standalone distribution) |
| Server logo or brand made from a Pixabay image | **no** |
| Photo of a real brand's product as a shop item | avoid; use generic products |

## Music and sound effects (no API)

Pixabay has music and sound effects on the site, but the API serves images and videos only. Download by hand:
1. pixabay.com/music or pixabay.com/sound-effects → search → listen → Download (log in).
2. Record it: `pixabay.py credit --out <folder> --file <name> --page <page URL> --user <author> --kind music` (adds a row to `CREDITS-pixabay.md`; editing the `.md` by hand gets overwritten on the next download).
3. Convert for FiveM: **OGG** (Vorbis) for NUI `<audio>` in CEF, mono for short UI sounds, ~96–128 kbps for music. Keep UI sounds short (< 1 s) and quiet.

**YouTube/Twitch Content ID**: some Pixabay music is registered with Content ID by its authors, so a streamer playing on your server can get an automatic claim even though use is allowed. Third-party guides say Pixabay offers a downloadable licence certificate per track to dispute claims (UNVERIFIED on Pixabay's own FAQ). For loading-screen music that streamers will hear, prefer tracks without a Content ID note, or let players mute it.

## Freesound (sound effects, free account)

freesound.org has a huge library of sound effects. Licence is **per sound**:

| Licence | OK on a server? |
|---|---|
| CC0 | yes |
| CC BY | yes, credit the author (CREDITS file) |
| CC BY-NC | avoid if the server takes donations, VIP or a Tebex shop |

Downloading needs a free account. Freesound also has an API (free key), but this skill doesn't wrap it. Download by hand.

## Other free sources (no account needed)
- **Kenney** (kenney.nl): CC0 UI sound packs, game assets.
- **Sonniss GDC bundles**: big free SFX packs released yearly for game developers; read each bundle's licence (royalty-free, no resale).

Don't recommend paid sites (Epidemic Sound, Artlist, Envato) or paid AI music/image generators. Project rule: free only.
