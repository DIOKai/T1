---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

我自己用 Blender + Sollumz 做了一个木桌道具 wood_table_v2。资源里 stream 有 wood_table_v2.ydr（只有 High，1048 面）、wood_table_v2.ytd（两张 2048×2048 的贴图，导出时选了 A8R8G8B8 没压缩）、wood_table_v2.ytyp；fxmanifest 写了 this_is_a_map 'yes' 和 data_file 'DLC_ITYP_REQUEST' 'stream/wood_table_v2.ytyp'。ytyp 里 lodDist 是 200、hdTextureDist 100、flags 0。进服用 CreateObject 生成，有时候看不到、稍微走远就消失，人还可以穿过去。我想让它像街上的椅子一样可以被推动。帮我看哪里有问题、要怎么改，给我步骤。
