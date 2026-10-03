# Third-Party Notices

Skills in `.claude/skills/` were copied from the repositories below. Local changes:

- `video-downloader`: frontmatter `name` changed from `youtube-downloader` to match its directory; example commands use the repo-relative script path; `download_video.py` tolerates missing or fractional `duration` metadata.
- `cowork-vs-chat-demo`, `safe-first-task`, `what-can-cowork-do`: removed a link to `references/role-profiles.md`, which does not exist upstream.
- `fivem-react-nui`: removed the "fxmind agent vision (NUI dump)" section, which depends on fxmind MCP tools that are not installed here.

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
