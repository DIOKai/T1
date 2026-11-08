---
type: llm
focus: trace
weight: 1
---

The answer says each meta file must be BOTH mounted with the correct data_file type in fxmanifest.lua AND listed in files {}, naming the correct types (WEAPONINFO_FILE, WEAPON_METADATA_FILE, WEAPON_ANIMATIONS_FILE, WEAPONCOMPONENTSINFO_FILE) and noting that a misspelled type or a missing files {} entry means the meta never loads.
