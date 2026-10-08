# Third-Party Notices

Skills in `.claude/skills/` were copied from the repositories below. Local changes:

- `video-downloader`: frontmatter `name` changed from `youtube-downloader` to match its directory; example commands use the repo-relative script path; `download_video.py` tolerates missing or fractional `duration` metadata, saves to the user's `Downloads` folder by default instead of `/mnt/user-data/outputs`, and no longer runs `pip install` itself (it finds yt-dlp on PATH or as a Python module, otherwise prints the install command).
- `blender-animation-rigging`: the setup line pointed at `docs/blender-mcp-setup.md` (the Blender Lab MCP server, not bundled); it now points at the T1 README's Blender MCP section (mcp-for-blender).
- `cowork-vs-chat-demo`, `safe-first-task`, `what-can-cowork-do`: removed a link to `references/role-profiles.md`, which does not exist upstream.
- `fivem-react-nui`: removed the "fxmind agent vision (NUI dump)" section, which depends on fxmind MCP tools that are not installed here.
- `.claude/skills/references/` (asset-pipeline, naming-conventions, polycount-budgets, validation-checklist, reference-image-match, reference-analysis-template, visual-match-checklist): shared Blender references copied unchanged from arjun988/blender-skills, because several of its skills link to `../references/`.
- `fivem-pro/CHEATSHEET.md`: copied from leminhhuy113/fivem-pro; the NUI line that said to use `drop-shadow` instead of `box-shadow` was reversed to match `fivem-react-nui` (CEF filters cost FPS).
- `fivem-security-audit` `checks/performance.md`: the N+1 "GOOD" example joined ids into one string for `IN (?)`, which binds a single value; it now passes the id table.
- `client-context-system`, `meeting-machine`, `weekly-business-pulse`, `parallel-power`, `first-scheduled-task`, `what-can-cowork-do`: removed "related skill" pointers to `email-triage`, `weekly-planning-session` and `dispatch-starter`, which are not included in T1.

## EAIconsulting/cowork-skills-library

- Source: https://github.com/EAIconsulting/cowork-skills-library (commit `e8fa1b197ade5fd70d9cbb23bdda2d86c7608e23`)
- License: MIT
- Skills: client-context-system, content-engine, context-manager, cowork-health-check, cowork-setup-wizard, cowork-vs-chat-demo, delegation-coach, first-scheduled-task, meeting-machine, memory-system, parallel-power, research-synthesizer, safe-first-task, safety-and-audit, skill-creator-guide, skill-customizer, teach-your-voice, weekly-business-pulse, what-can-cowork-do, workflow-builder

## ComposioHQ/awesome-claude-skills

- Source: https://github.com/ComposioHQ/awesome-claude-skills (commit `be2a406907dbc61b73e6827ded415c96139d13a2`)
- License: Apache License 2.0 — https://www.apache.org/licenses/LICENSE-2.0
- Skills: changelog-generator, competitive-ads-extractor, content-research-writer, domain-name-brainstormer, file-organizer, image-enhancer, invoice-organizer, lead-research-assistant, meeting-insights-analyzer, raffle-winner-picker, tailored-resume-generator, video-downloader

## leminhhuy113/fivem-pro

- Source: https://github.com/leminhhuy113/fivem-pro (commit `ae642cb753d1cebff701152c5533d1b8c680c02c`)
- License: MIT
- Skills: fivem-pro (SKILL.md, references/, examples/template-resource/)

## matiaspalmac/fivem-audit-skill

- Source: https://github.com/matiaspalmac/fivem-audit-skill (commit `193249ee40c7a7a404e578420cc5e58f3929883d`)
- License: MIT
- Skills: fivem-security-audit (SKILL.md, checks/)

## arjun988/blender-skills

- Source: https://github.com/arjun988/blender-skills (commit `8f778d2405a214b508d4c7d80742be8e43acdd52`)
- License: MIT
- Skills: animation, archviz, asset-optimization, collision-proxy, environment-artist, export-pipeline, hard-surface, lod-pipeline, prop-artist, retopology, rigging, set-dressing, texture-workflow, uv-workflow, vehicle-artist

## germanfndez/fiveai-skills

- Source: https://github.com/germanfndez/fiveai-skills (commit `c9d13e0cf5b327790fceb7aaeaba02e1276e14f4`)
- License: MIT
- Skills: oxlib, oxmysql, ox-inventory, ox-target

## proelias7/fivem-skill

- Source: https://github.com/proelias7/fivem-skill (commit `5b4504a7ceacee0e0d83a0d0d40be92deac4a8f0`)
- License: MIT (stated in the upstream README; the repository has no LICENSE file)
- Skills: fivem-react-nui

## MuscleOtter/quantity-surveyor

- Source: https://github.com/MuscleOtter/quantity-surveyor (commit `a3f788c38e7cc32f75f3f229ea04fa31b14098ca`)
- License: MIT (LICENSE included in the skill folder)
- Skills: quantity-surveyor

## LVTD-LLC/skills

- Source: https://github.com/LVTD-LLC/skills (commit `a3ad087f5d1f14c09166de9f70b88c48e63209a7`)
- License: MIT (LICENSE copied into each skill folder)
- Skills: game-balance-economy, game-interface-feedback

## ra100/blender-claude-plugin

- Source: https://github.com/ra100/blender-claude-plugin (commit `78e9151fdc9e01ce37f1d16a9b677c3047411885`)
- License: MIT (LICENSE copied into the skill folder)
- Skills: blender-animation-rigging

## LobzyJay/motion-design-with-claude

- Source: https://github.com/LobzyJay/motion-design-with-claude (commit `a4d48c55ccb54a3b8bc4e100e34f6dcaca3bbfea`)
- License: MIT (LICENSE copied into the skill folder)
- Skills: motion-design

## fivem-graphics-pack (written for this repository)

No third-party code is included. `assets/timecycle_vars.txt` is a list of the timecycle variable names (identifiers only, no values) as they appear in GTA V's `w_extrasunny.xml`; GTA V is © Rockstar Games. `scripts/make_lut.py` writes the LUT layout that ReShade's `LUT.fx` (crosire/reshade-shaders) reads; no ReShade code or images are copied.

## fivem-mlo-housing (written for this repository)

No third-party code is included. The workflow summarises the Sollumz wiki (GPL-3 project), the FiveM documentation, and the public READMEs and configs of qbx_properties, qb-interior, qb-houses, ps-housing, bob74_ipl, object_gizmo and ht_mlotool; flag names and values were read from the Sollumz source (`ytyp/properties/flags.py`) and XML element names from Sollumz szio (MIT).

## pbakaus/impeccable

- Source: https://github.com/pbakaus/impeccable (commit `778c8a7b71ccd5bfe3ca6ac68c15d9d872d0f87d`, plugin version 4.5.0)
- License: Apache 2.0 (LICENSE and NOTICE.md copied into the skill folder)
- Included: `plugin/skills/impeccable` → `.claude/skills/impeccable`, and `plugin/agents/*.md` → `.claude/agents/`
- Local modification: the plugin's hooks (`plugin/hooks/hooks.json`, which run the impeccable engine on SessionStart, after every Edit/Write and on Stop) were deliberately not included.

## Leonxlnx/taste-skill

- Source: https://github.com/Leonxlnx/taste-skill (reviewed at commit `b482f7a970abb98c4108d4a9f761e458c64cefc8`)
- License: MIT
- Not vendored: enabled as the `taste-skill@taste-skill` plugin from its own marketplace in `.claude/settings.json`.

## remotion-dev/skills

- Source: https://github.com/remotion-dev/skills (reviewed at commit `32b241b97f4e0e4ab61fe9a41b05e6e64503f8c5`)
- No licence file in the repository, so nothing is vendored. `scripts/install_local.py --remotion` installs it on the user's own machine with Remotion's documented command (`npx skills add remotion-dev/skills`). Remotion itself is free for individuals and companies of up to 3 people; larger companies need a Remotion licence.

## gamedev-skills/awesome-gamedev-agent-skills

- Source: https://github.com/gamedev-skills/awesome-gamedev-agent-skills (commit `d4b0e35550c55ae70bdfcab4ef5a0e94610438a9`)
- License: Apache 2.0 (LICENSE and NOTICE copied into each skill folder)
- Skills: game-ui-ux, game-feel (unmodified)

## nextlevelbuilder/ui-ux-pro-max-skill

- Source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (commit `477bcb28c9812b385cb51a4605ddf30d7b2266e2`)
- License: MIT (LICENSE copied into the skill folder)
- Skills: ui-ux-pro-max only (the repo's banner/brand/design/logo skills use paid image APIs and were not included)
- Local modifications: script paths changed from `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/` to `${CLAUDE_SKILL_DIR}/`; `scripts/tests` removed.

## fivem-menu-design (written for this repository)

No third-party code is included. Facts come from the FiveM documentation and source (nui-resources, nui-core), ox_lib (LGPL-3.0) and qb-menu (GPL-3.0) source, read for reference only.

## fivem-phone (written for this repository)

No third-party code is included. Facts come from reading, for reference only: project-error/npwd (GPL-3.0) and project-error/npwd-app-template, the lb-phone-app-template (MIT), qbcore-framework/qb-phone (GPL-3.0), Z3MO/z-phone (AGPL-3.0), and Android's foldable / window size class documentation. Short API names, control IDs and animation names are cited as facts; no code was copied.

`fivem-phone/assets/phone-template/` bundles two third-party assets (notices in its `LICENSES.md`):
- Inter font v4.1 (`web/fonts/InterVariable.woff2`), © The Inter Project Authors, SIL Open Font License 1.1 (full text in `web/fonts/Inter-OFL.txt`). Source: https://github.com/rsms/inter
- Lucide icons, lucide-static 0.453.0 (SVG path data in `web/icons.js`), ISC License. Source: https://github.com/lucide-icons/lucide

Design numbers in `references/phone-design.md` were checked against Apple HIG data files and Material 3 token files in androidx (Apache-2.0), cited as facts. Device specs in `references/real-foldables.md` come from public press and carrier coverage.

## emilkowalski/skill

- Source: https://github.com/emilkowalski/skill (commit `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`)
- License: MIT (LICENSE copied into each skill folder)
- Skills: emil-design-eng, break-ui, review-animations, find-animation-opportunities, improve-animations, animate, prototype, animation-vocabulary, apple-design (unmodified). Not included: write-swift, animate-expo, mobile-native, ask-sonner, pick-ui-library.

## jakubkrehel/make-interfaces-feel-better

- Source: https://github.com/jakubkrehel/make-interfaces-feel-better (commit `35545ea1512ad59fa463e6b1f95ca9c052981fe6`)
- License: MIT (LICENSE copied into the skill folder)
- Skills: make-interfaces-feel-better (unmodified)

## Owl-Listener/designer-skills

- Source: https://github.com/Owl-Listener/designer-skills (reviewed at commit `9a6930cf84a822eb458624bd11c61aac5bbdf224`)
- License: MIT
- Not vendored: the `visual-critique`, `ui-design` and `interaction-design` plugins are enabled from the repo's own marketplace (`designer-skills`) in `.claude/settings.json`.

## mastepanoski/claude-skills

- Source: https://github.com/mastepanoski/claude-skills (commit `fbdde8adb5645dd3ab8531200a651c9112472b2b`)
- License: MIT (LICENSE copied into the skill folder)
- Skills: ui-design-review (unmodified)

## vercel-labs/agent-skills

- Source: https://github.com/vercel-labs/agent-skills (commit `063bee94c3f4df8453406c830b0a7df0f2860278`)
- License: MIT (stated in the repository README; there is no separate LICENSE file)
- Skills: web-design-guidelines (unmodified; it fetches its rules from vercel-labs/web-interface-guidelines at run time)

## wshobson/agents

- Source: https://github.com/wshobson/agents (commit `46891e7e60da0e52baf1050b7b6391b64e84c6d9`)
- License: MIT (LICENSE copied into the skill folder)
- Skills: interaction-design, mobile-ios-design, mobile-android-design from `plugins/ui-design/skills/` (unmodified)

## julianoczkowski/designer-skills

- Source: https://github.com/julianoczkowski/designer-skills (commit `c259656c76d9758d7ead46b0d2f125cbe84f8665`)
- License: Apache 2.0 (LICENSE copied into each skill folder)
- Skills: design-brief, design-tokens, design-review, and frontend-design renamed to `designer-frontend-design`
- Local modification: `frontend-design` was renamed to `designer-frontend-design` (it clashed with Anthropic's frontend-design skill), and the references to it in design-brief, design-tokens and design-review were updated.
