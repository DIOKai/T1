#!/usr/bin/env python3
"""Check FiveM freemode clothing resources (add-on or replacement packs). Read-only.

Usage:
    py -3 -I check_clothing_resource.py <resource or folder of resources> [more] [--json]

Standard library only. Never writes, renames or decrypts anything.
Exit code 1 when errors are found, 0 otherwise (warnings do not fail).

Sources for the rules (see references/addon-pack-naming-and-manifest.md):
grzyClothTool BuildResourceHelper.cs (file names, meta fields, fxmanifest),
the Cfx forum add-on how-to (lowercase, prop textures without _uni),
docs.fivem.net data-files list, docs.gta.clothing game-limits / files-naming /
skin-tone pages (26 textures, 128 legacy guidance, 255 usable / 256 reports 0,
16/48 MiB tiers), CodeWalker RpfFile.GetSizeFromFlags (RSC7 size).

What it checks
- fxmanifest.lua: present; game 'gta5'; every ShopPedApparel .meta has
  data_file 'SHOP_PED_APPAREL_META_FILE' and is listed in files {};
  data_file targets exist; first_person_alternates*.meta uses
  PED_FIRST_PERSON_ALTERNATE_DATA and ped(alternative|alternate)variations*.meta
  uses ALTERNATE_VARIATIONS_FILE; alternate _N models exist but neither is declared.
- .meta (ShopPedApparel XML): fullDlcName == pedName_dlcName, eCharacter matches
  the gender (SCR_CHAR_MULTIPLAYER / _F), stream/<fullDlcName>.ymt exists,
  creatureMetaData points at a streamed YMT (info only: grzyClothTool always
  writes the line, the YMT exists only with heels / hat hair scale), a
  creaturemetadata YMT nobody references, duplicate fullDlcName.
- stream/ names (recursive, lowercase):
    components  <ped>_<dlc>^<comp>_<NNN>_<u|r>[_<alt>].ydd|.yld
                <ped>_<dlc>^<comp>_diff_<NNN>_<a-z>_<uni|whi|bla|lat|chi|pak|ara>.ytd
    props       <ped>_p_<dlc>^p_<anchor>_<NNN>[_<alt>].ydd|.yld
                <ped>_p_<dlc>^p_<anchor>_diff_<NNN>_<a-z>.ytd   (no _uni)
    YMT         <ped>_<dlc>.ymt, mp_creaturemetadata_[m_|f_]<dlc>.ymt
  Without _<dlc> (mp_f_freemode_01^...) or with a prefix no local YMT owns,
  the files replace vanilla/DLC slots: reported as a replacement pack, and
  add-on-only checks (orphan textures, numbering, counts) are skipped.
  Uppercase / spaces, unparseable clothing-like names, files without the ^
  prefix, .xml left in stream, raw .dds/.png in stream.
- pairing per drawable: drawable without texture (warning, embedded-only is
  legal), texture without drawable (error in add-on packs), texture letters
  contiguous from a, more than 26 letters, _u with skin textures or _r with
  uni (error), both _u and _r for one number, _r outside head/uppr/lowr/feet,
  prop texture with _uni/_whi, .yld or _N alternate without its base model.
- numbering per (gender, type): starts at 000 and has no gaps; more than 128
  (warning, legacy guidance / grzyClothTool default) and 256 or more (error,
  DCT: 256 reports zero).
- RSC7 header of .ydd/.ytd/.yld/.ymt/.ydr/.yft: memory from the page flags
  (same formula as fivem-mlo-housing/check_mlo_resource.py rsc_page_size,
  CodeWalker GetSizeFromFlags), warning above 16 MiB and above 48 MiB (DCT
  and Cfx forum tiers are warnings, not hard caps). FXAP = Cfx escrow:
  reported, never decrypted. Other magic: not a compiled resource.
- across everything scanned: two resources declaring the same collection
  (fullDlcName / YMT name), the same stream file name in two resources,
  identical .ydd content in two resources (sha1).
- summary per collection: drawables per type, texture count, an estimate of
  shop-meta entries (one per drawable x texture; the global list is 65,520
  and is shared with the base game and every other pack).

Not checked (cannot be verified with the standard library / not verified)
- YTD/YDD contents: resources are compressed; texture size, BC1/BC3/BC7,
  mipmaps, embedded normal/spec, weights, vertex colours, LODs, shaders.
  Check them in CodeWalker / Sollumz.
- YMT contents (binary PSO): texture counts, propMask/texId, flags,
  expressionMods inside the YMT are not compared with the files.
- The per-build free YMT slot budget (only counts are printed), whether
  RSC8 (Enhanced/Gen9) uses the same size formula (assumed, unverified),
  Element Club entitlement (a server-key perk; the script cannot see it).
"""
import argparse
import fnmatch
import hashlib
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

MIB = 1024 * 1024
COMPONENTS = ('head', 'berd', 'hair', 'uppr', 'lowr', 'hand', 'feet', 'teef', 'accs', 'task', 'decl', 'jbib')
PROPS = ('head', 'eyes', 'ears', 'mouth', 'lhand', 'rhand', 'lwrist', 'rwrist', 'hip', 'lfoot', 'rfoot')
SKIN_SUFFIX = ('whi', 'bla', 'lat', 'chi', 'pak', 'ara')   # DCT skin-tone page preview labels
SKIN_TYPES = ('head', 'uppr', 'lowr', 'feet')               # DCT: skin data on body/legs/shoes (+ heads)
ECHAR = {'mp_m_freemode_01': 'SCR_CHAR_MULTIPLAYER', 'mp_f_freemode_01': 'SCR_CHAR_MULTIPLAYER_F'}
GENDER = {'mp_m_freemode_01': '男', 'mp_f_freemode_01': '女'}
RSC_EXT = ('.ydd', '.ytd', '.yld', '.ymt', '.ydr', '.yft')
WARN_COUNT, MAX_COUNT = 128, 256

_C = '|'.join(COMPONENTS)
_P = '|'.join(PROPS)
_PED = r'(mp_[mf]_freemode_01)'
RE_CREATURE = re.compile(r'^(mp_creaturemetadata_[a-z0-9_]+)\.ymt$')
RE_YMT = re.compile(rf'^{_PED}(?:_([a-z0-9_]+))?\.ymt$')
RE_PROP_MODEL = re.compile(rf'^{_PED}_p(?:_([a-z0-9_]+))?\^p_({_P})_(\d{{3}})(?:_(\d+))?\.(ydd|yld)$')
RE_PROP_TEX = re.compile(rf'^{_PED}_p(?:_([a-z0-9_]+))?\^p_({_P})_diff_(\d{{3}})_([a-z0-9]+)(?:_([a-z]+))?\.ytd$')
RE_COMP_MODEL = re.compile(rf'^{_PED}(?:_([a-z0-9_]+))?\^({_C})_(\d{{3}})_([ur])(?:_(\d+))?\.(ydd|yld)$')
RE_COMP_TEX = re.compile(rf'^{_PED}(?:_([a-z0-9_]+))?\^({_C})_diff_(\d{{3}})_([a-z0-9]+)_([a-z]+)\.ytd$')
# common English words in hand-made file names -> the GTA slot they belong in (hint only)
WORD_HINTS = [('jacket', '上衣/外套 = 组件 11 jbib'), ('shirt', '上衣 = jbib（内衣 accs/undershirt = 8）'), ('hoodie', 'jbib'), ('coat', 'jbib'),
              ('top', 'jbib'), ('vest', 'jbib 或防弹衣 task(9)'), ('pant', '裤子 = 组件 4 lowr'), ('jean', 'lowr'), ('short', 'lowr'),
              ('skirt', 'lowr'), ('shoe', '鞋 = 组件 6 feet'), ('boot', 'feet'), ('sneaker', 'feet'), ('glove', '手 = 组件 3 uppr'),
              ('mask', '面具 = 组件 1 berd'), ('bag', '背包 = 组件 5 hand'), ('hat', '帽子 = 道具 p_head（prop 0）'), ('cap', '帽子 = 道具 p_head'),
              ('helmet', '道具 p_head'), ('glass', '眼镜 = 道具 p_eyes（prop 1）'), ('watch', '手表 = 道具 p_lwrist（prop 6）'),
              ('earring', '耳环 = 道具 p_ears（prop 2）'), ('chain', '项链 = 组件 7 teef')]
RE_LOOKS_CLOTHING = re.compile(rf'^(?:p_)?(?:{_C}|{_P})_(?:diff_)?\d+')


def rsc_page_size(flags):
    # FXServer ConvertRSC7Size / CodeWalker RpfFile.GetSizeFromFlags (copied from check_mlo_resource.py)
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


def read_header(path):
    """('rsc', magic, virt, phys) | ('fxap',) | ('other',)."""
    with open(path, 'rb') as fh:
        head = fh.read(16)
    if len(head) >= 16 and head[:4] in (b'RSC7', b'RSC8'):
        magic, _, virt, phys = struct.unpack('<4sIII', head)
        return ('rsc', magic.decode(), rsc_page_size(virt), rsc_page_size(phys))
    if head[:4] == b'FXAP':
        return ('fxap',)
    return ('other',)


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def parse_manifest(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        text = strip_lua_comments(fh.read())
    data_files = re.findall(r"data_file\s*\(?\s*['\"]([A-Za-z0-9_]+)['\"]\s*\)?\s*\(?\s*['\"]([^'\"]+)['\"]", text)
    files = []
    for m in re.finditer(r'\bfiles\s*\(?\s*\{(.*?)\}', text, re.S):
        files += re.findall(r"['\"]([^'\"]+)['\"]", m.group(1))
    files += re.findall(r"\bfile\s*\(?\s*['\"]([^'\"]+)['\"]", text)
    has_game = re.search(r'\bgames?\b', text) is not None
    gta5 = re.search(r"\bgames?\b[^\n]*['\"]gta5['\"]", text) is not None
    return {'data_files': data_files, 'files': [f.replace('\\', '/').lower() for f in files],
            'has_game': has_game, 'gta5': gta5}


def xml_text(root, tag):
    el = root.find(tag)
    if el is None:
        return ''
    return (el.get('value') or el.text or '').strip()


def find_resources(paths):
    """Resource roots: folders with fxmanifest.lua/__resource.lua, or with a stream/ folder but no manifest."""
    out = {}
    for p in paths:
        p = os.path.abspath(p)
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            low = [f.lower() for f in files]
            if 'fxmanifest.lua' in low or '__resource.lua' in low or any(d.lower() == 'stream' for d in dirs):
                # label = path from the scanned folder's parent, so two packs with the same folder name differ
                out[root] = os.path.relpath(root, os.path.dirname(p)).replace(os.sep, '/')
                dirs[:] = []
    return sorted(out.items())


def list_files(res):
    out = []
    for root, dirs, files in os.walk(res):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            full = os.path.join(root, f)
            out.append((os.path.relpath(full, res).replace(os.sep, '/'), full))
    return out


def name_hint(low):
    if '^' not in low:
        return '缺少 <ped>_<包名>^ 前缀'
    tail = low.split('^', 1)[1]
    if re.search(r'_\d{1,2}(?:_|\.)', tail) and not re.search(r'_\d{3}', tail):
        return '编号要 3 位数字（000、001…）'
    if tail.endswith('.ydd') and not tail.startswith('p_') and not re.search(r'_[ur](?:_\d+)?\.ydd$', tail):
        return '组件模型要以 _u（不含皮肤）或 _r（含皮肤）结尾'
    if tail.endswith('.ytd') and '_diff_' not in tail:
        return "贴图名要有 _diff_，例如 jbib_diff_000_a_uni.ytd"
    return '对照 references/addon-pack-naming-and-manifest.md 的命名格式'


def new_slot():
    return {'skin': set(), 'alts': set(), 'ydd': False, 'yld': False, 'tex': {}, 'yld_alts': set()}


def check(paths):
    findings = []

    def add(level, code, where, msg):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg})

    resources = find_resources(paths)
    collections_summary = []
    owners = {}          # collection key (lower) -> [resource label]
    stream_names = {}    # basename lower -> [resource label]
    ydd_by_size = {}     # size -> [(label, full)]
    ymt_per_gender = {'mp_m_freemode_01': 0, 'mp_f_freemode_01': 0}

    for res, label in resources:
        files = list_files(res)
        rels = {r.lower(): (r, full) for r, full in files}
        stream = [(r, full) for r, full in files if r.lower().split('/')[0].startswith('stream')]
        metas = [(r, full) for r, full in files if r.lower().endswith('.meta') and not r.lower().split('/')[0].startswith('stream')]
        man_path = next((full for r, full in files if r.lower() in ('fxmanifest.lua', '__resource.lua')), None)

        if ' ' in os.path.basename(res):
            add('warn', 'RESOURCE_NAME_SPACE', label, '资源文件夹名里有空格，ensure 时容易出错，改成小写加底线')

        # ---------- classify stream files ----------
        colls = {}           # (ped, coll) -> {'comp': {type: {num: slot}}, 'prop': {...}}
        ymts, creatures = {}, {}
        clothing_files = 0
        escrow = 0
        rsc8 = 0
        spaced = []
        for r, full in stream:
            base = os.path.basename(r)
            low = base.lower()
            ext = os.path.splitext(low)[1]
            where = f'{label}/{r}'
            if ext in RSC_EXT or ext == '.yld':
                stream_names.setdefault(low, []).append(label)
            if low.endswith('.xml'):
                add('error', 'XML_IN_STREAM', where, '这是 XML，放在 stream 里不会被加载。先在 CodeWalker RPF Explorer（Edit mode）把它拖进去转成 .ydd/.ytd')
                continue
            if ext in ('.dds', '.png', '.jpg', '.jpeg', '.tga'):
                add('warn', 'RAW_IMAGE_IN_STREAM', where, '图片要先做成 .ytd（CodeWalker 新建 YTD 或 grzyClothTool 转换），单独的图片游戏不会读')
                continue
            if ext not in RSC_EXT:
                continue
            if ' ' in base:
                if 'freemode' in low or '^' in low or low.startswith('mp_creaturemetadata'):
                    add('error', 'NAME_SPACE', where, '文件名有空格，游戏认不出来。全部小写、不要空格')
                else:
                    spaced.append(base)
                continue
            if base != low and ('freemode' in low or '^' in low or low.startswith('mp_creaturemetadata')):
                add('warn', 'NAME_UPPERCASE', where, 'CFX 教程要求名字全部小写，DCT 也说大写名字出过问题。改成小写（YMT、meta、文件要一起改）')

            hdr = read_header(full)
            if hdr[0] == 'fxap':
                escrow += 1
            elif hdr[0] == 'other':
                add('warn', 'NOT_RSC7', where, '开头不是 RSC7，不像编译好的 GTA 文件（可能是改了扩展名的 XML 或文件坏了）')
            else:
                if hdr[1] == 'RSC8':
                    rsc8 += 1
                size, what = max((hdr[2], '虚拟'), (hdr[3], '物理（显存）'))
                if size > 48 * MIB:
                    add('warn', 'ASSET_OVER_48MIB', where, f'{what}内存 {size / MIB:.1f} MiB，超过 48 MiB（DCT/Cfx 的高风险档）。很可能加载不出来或让人闪退：贴图降到 1024（皮肤部分 512）再重做 YTD')
                elif size > 16 * MIB:
                    add('warn', 'ASSET_OVER_16MIB', where, f'{what}内存 {size / MIB:.1f} MiB，超过 16 MiB 警告线（按 RSC 头算）。大多是 2K/4K 贴图，降到 1024')
            if ext == '.ydd':
                try:
                    ydd_by_size.setdefault(os.path.getsize(full), []).append((label, full))
                except OSError:
                    pass

            m = RE_CREATURE.match(low)
            if m:
                creatures[m.group(1)] = where
                clothing_files += 1
                continue
            m = RE_YMT.match(low)
            if m:
                clothing_files += 1
                ped, coll = m.group(1), m.group(2)
                if coll is None:
                    add('warn', 'REPLACES_BASE_YMT', where, f'这是原版 {ped}.ymt 的替换：整个原版集合会被这个文件取代，原有衣服可能消失或编号移位。确认这是作者要求的装法，不是 add-on 包')
                else:
                    ymts[(ped, coll)] = where
                    ymt_per_gender[ped] += 1
                continue
            kind = None
            m = RE_PROP_MODEL.match(low)
            if m:
                kind, ped, coll, typ, num, alt, mext = 'prop', m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5), m.group(6)
                skin = None
            else:
                m = RE_PROP_TEX.match(low)
                if m:
                    ped, coll, typ, num, letter, suffix = m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5), m.group(6)
                    slot = colls.setdefault((ped, coll), {'comp': {}, 'prop': {}})['prop'].setdefault(typ, {}).setdefault(num, new_slot())
                    clothing_files += 1
                    if suffix:
                        add('error', 'PROP_TEXTURE_SUFFIX', where, f'道具贴图不带 _{suffix}，应为 …^p_{typ}_diff_{num:03d}_{letter}.ytd（CFX 教程；_uni/_whi 只用在组件）')
                    if len(letter) != 1 or not letter.isalpha():
                        add('error', 'TEXTURE_LETTER', where, f"贴图编号 '{letter}' 不对：每件只能用一个字母 a–z，最多 26 款")
                    else:
                        slot['tex'].setdefault(letter, set()).add('')
                    continue
                m = RE_COMP_MODEL.match(low)
                if m:
                    kind, ped, coll, typ, num, skin, alt, mext = 'comp', m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5), m.group(6), m.group(7)
                else:
                    m = RE_COMP_TEX.match(low)
                    if m:
                        ped, coll, typ, num, letter, suffix = m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5), m.group(6)
                        clothing_files += 1
                        if suffix not in ('uni',) + SKIN_SUFFIX:
                            add('error', 'TEXTURE_SUFFIX', where, f"贴图结尾 '_{suffix}' 不认得：不含皮肤用 _uni，含皮肤用 _whi（脸可另有 bla/lat/chi/pak/ara）")
                            continue
                        if len(letter) != 1 or not letter.isalpha():
                            add('error', 'TEXTURE_LETTER', where, f"贴图编号 '{letter}' 不对：每件只能用一个字母 a–z，最多 26 款")
                            continue
                        slot = colls.setdefault((ped, coll), {'comp': {}, 'prop': {}})['comp'].setdefault(typ, {}).setdefault(num, new_slot())
                        slot['tex'].setdefault(letter, set()).add(suffix)
                        continue
            if kind is None:
                if 'freemode' in low or '^' in low:
                    add('warn', 'BAD_NAME', where, f'看起来是衣服文件，但名字格式不对，游戏不会认：{name_hint(low)}')
                elif RE_LOOKS_CLOTHING.match(low):
                    add('warn', 'NO_PREFIX', where, f'像是衣服文件但没有 mp_?_freemode_01_<包名>^ 前缀，add-on 包里不会被读到（{name_hint(low)}）')
                elif low.endswith(('.ydd', '.yld')) or ('_diff_' in low and low.endswith('.ytd')):
                    guess = next((v for k, v in WORD_HINTS if k in low), None)
                    add('warn', 'NOT_CLOTHING_NAMED', where, "stream 里的 .ydd/.yld（或 _diff_ 贴图）没有衣服命名，游戏不会当成衣服读到" +
                        (f"。看名字像是 {guess}" if guess else '') + "。组件要叫 mp_m_freemode_01_<包名>^<jbib/lowr/feet…>_000_u.ydd，道具要叫 mp_m_freemode_01_p_<包名>^p_head_000.ydd（见 addon-pack-naming-and-manifest.md）")
                continue
            clothing_files += 1
            if kind == 'comp' and coll and coll.startswith('p_'):
                add('warn', 'PROP_PREFIX_ON_COMPONENT', where, f'前缀里的 _p_ 是道具专用（帽子、眼镜…），组件 {typ} 不要用 _p_')
            slot = colls.setdefault((ped, coll), {'comp': {}, 'prop': {}})[kind].setdefault(typ, {}).setdefault(num, new_slot())
            if mext == 'yld':
                if alt:
                    slot['yld_alts'].add(int(alt))
                else:
                    slot['yld'] = True
                continue
            if alt:
                slot['alts'].add(int(alt))
            else:
                slot['ydd'] = True
                if skin:
                    slot['skin'].add(skin)

        if spaced:
            add('warn', 'SPACED_NAMES', f'{label}/stream', f"{len(spaced)} 个文件名有空格（例如 {sorted(spaced)[0]}）。游戏不会用这种名字去找文件，等于白白下载；像是复本（copy / Kopya / 副本）就移出 stream")
        if escrow:
            add('info', 'ESCROWED', label, f'{escrow} 个文件是 Cfx escrow 加密（FXAP），只能检查名字，内容和大小看不到。不要尝试解密；要在拥有授权的账号的伺服器上用')
        if rsc8:
            add('info', 'RSC8_FILES', label, f'{rsc8} 个文件是 RSC8（应是 Enhanced/Gen9 格式，未验证）。Legacy 和 Enhanced 的包不能混用，确认伺服器跑的是哪一版')

        # ---------- manifest ----------
        man = None
        if man_path is None:
            if clothing_files:
                add('error', 'NO_MANIFEST', label, '有 stream 衣服文件但没有 fxmanifest.lua。至少要 fx_version、game \'gta5\'、files { meta } 和 data_file \'SHOP_PED_APPAREL_META_FILE\'')
        else:
            man = parse_manifest(man_path)
            if os.path.basename(man_path).lower() == '__resource.lua':
                add('info', 'OLD_RESOURCE_LUA', label, '用的是旧的 __resource.lua，建议改成 fxmanifest.lua')
            if not man['has_game']:
                add('warn', 'NO_GAME', label, "fxmanifest 没写 game 'gta5'")
            elif not man['gta5']:
                add('warn', 'GAME_NOT_GTA5', label, "fxmanifest 的 game 不是 'gta5'")

        declared = {}   # path lower -> type
        if man:
            for t, p in man['data_files']:
                pl = p.replace('\\', '/').lower()
                declared[pl] = t
                if ':/' in pl:
                    continue
                if not any(x == pl or fnmatch.fnmatch(x, pl) for x in rels):
                    add('error', 'DATA_FILE_MISSING', label, f"data_file '{t}' '{p}' 指向的文件不存在")
                    continue
                if pl.endswith('.meta') and not any(x == pl or fnmatch.fnmatch(pl, x) for x in man['files']):
                    add('error', 'META_NOT_IN_FILES', label, f"'{p}' 有 data_file 但没列在 files {{ }} 里，客户端收不到这个 meta")
                bn = os.path.basename(pl)
                if 'first_person_alternate' in bn and t != 'PED_FIRST_PERSON_ALTERNATE_DATA':
                    add('warn', 'DATA_FILE_TYPE', label, f"'{p}' 应该用 data_file 'PED_FIRST_PERSON_ALTERNATE_DATA'（现在是 {t}）")
                if re.search(r'alternat\w*variation', bn) and t != 'ALTERNATE_VARIATIONS_FILE':
                    add('warn', 'DATA_FILE_TYPE', label, f"'{p}' 应该用 data_file 'ALTERNATE_VARIATIONS_FILE'（现在是 {t}）")

        # ---------- metas ----------
        meta_by_full = {}
        referenced_creatures = set()
        for r, full in metas:
            where = f'{label}/{r}'
            try:
                root = ET.parse(full).getroot()
            except ET.ParseError as e:
                add('error', 'META_XML_INVALID', where, f'不是合法的 XML：{e}')
                continue
            if root.tag != 'ShopPedApparel':
                continue
            ped, dlc, full_name = xml_text(root, 'pedName'), xml_text(root, 'dlcName'), xml_text(root, 'fullDlcName')
            echar, creature = xml_text(root, 'eCharacter'), xml_text(root, 'creatureMetaData')
            rl = r.lower()
            if man is not None:
                t = declared.get(rl)
                if t is None:
                    add('error', 'META_NOT_DECLARED', where, f"fxmanifest 没有 data_file 'SHOP_PED_APPAREL_META_FILE' '{r}'，这个包的衣服不会出现")
                elif t != 'SHOP_PED_APPAREL_META_FILE':
                    add('error', 'META_WRONG_TYPE', where, f"ShopPedApparel meta 要用 data_file 'SHOP_PED_APPAREL_META_FILE'（现在是 {t}）")
            if ped not in ECHAR:
                add('info', 'CUSTOM_PED', where, f"pedName '{ped}' 不是 freemode 角色，这个脚本只认得 mp_m/mp_f_freemode_01 的规则")
                continue
            if dlc != dlc.lower() or full_name != full_name.lower():
                add('warn', 'META_UPPERCASE', where, 'dlcName / fullDlcName 有大写。全部小写，和 YMT、文件前缀完全一样')
            if full_name.lower() != f'{ped}_{dlc}'.lower():
                add('error', 'META_FULLNAME', where, f"fullDlcName '{full_name}' 应该是 pedName_dlcName = '{ped}_{dlc}'")
            if echar != ECHAR[ped]:
                add('error', 'META_ECHARACTER', where, f"{GENDER[ped]}角 {ped} 的 eCharacter 要写 {ECHAR[ped]}（现在是 '{echar}'）")
            key = full_name.lower()
            if key in meta_by_full:
                add('error', 'META_DUPLICATE', where, f"另一个 meta（{meta_by_full[key]}）也声明了 {full_name}")
            meta_by_full[key] = where
            if not any(f'{a}_{b}'.lower() == key for a, b in ymts):
                add('error', 'META_NO_YMT', where, f"stream 里找不到 {full_name}.ymt。YMT 名、meta 的 fullDlcName、文件前缀要完全一致")
            if creature:
                referenced_creatures.add(creature.lower())
                if creature.lower() not in creatures:
                    add('info', 'CREATURE_YMT_ABSENT', where, f"meta 写了 creatureMetaData '{creature}'，但 stream 里没有这个 YMT。只有高跟鞋或帽子压头发才需要它；grzyClothTool 每次都会写这一行，没用到这两个功能可以不管")
            owners.setdefault(key, []).append(label)
        for cname, where in creatures.items():
            if cname not in referenced_creatures:
                add('warn', 'CREATURE_UNREFERENCED', where, '这个 creaturemetadata YMT 没有被任何 meta 的 <creatureMetaData> 引用，高跟鞋 / 帽子压头发不会生效（名字要和 meta 里写的完全一样，不带 .ymt）')

        addon_pack = bool(ymts or meta_by_full)
        for (ped, coll), where in ymts.items():
            key = f'{ped}_{coll}'
            if key not in meta_by_full and man is not None:
                add('error', 'YMT_NO_META', where, f"有 {key}.ymt 但没有 fullDlcName 为 {key} 的 ShopPedApparel meta，游戏不会加载这个集合")
            if key not in meta_by_full:
                owners.setdefault(key, []).append(label)
            if (ped, coll) not in colls:
                add('warn', 'YMT_EMPTY', where, '这个 YMT 在 stream 里没有任何对应前缀的模型或贴图')

        # ---------- per collection ----------
        any_alt = False
        replacement_reported = False
        for (ped, coll), data in sorted(colls.items(), key=lambda kv: (kv[0][0], kv[0][1] or '')):
            is_addon = coll is not None and (ped, coll) in ymts
            prefix_name = f'{ped}_{coll}' if coll else ped
            if coll is not None and not is_addon:
                if addon_pack:
                    add('error', 'ORPHAN_PREFIX', f'{label}/stream', f"前缀 {prefix_name}^ 的文件没有对应的 {prefix_name}.ymt（改了 YMT 名但没改文件？大小写或性别不同？）")
                    continue
            if not is_addon and not replacement_reported:
                replacement_reported = True
                add('info', 'REPLACEMENT_PACK', label, f'前缀 {prefix_name}^ 没有自己的 YMT，这是「替换」装法：覆盖原版或某个 DLC 的同名衣服，会占掉那个集合、原本的款式会被换掉。add-on 专用的检查（编号连续、孤立贴图、数量）跳过')
            summary = {'resource': label, 'collection': prefix_name, 'addon': is_addon, 'types': {}, 'textures': 0, 'shop_entries': 0}
            for kind in ('comp', 'prop'):
                for typ, slots in sorted(data[kind].items()):
                    tname = typ if kind == 'comp' else f'p_{typ}'
                    nums = sorted(n for n, s in slots.items() if s['ydd'])
                    for num, s in sorted(slots.items()):
                        f_id = f'{label}/stream {prefix_name}^{tname}_{num:03d}'
                        letters = sorted(s['tex'])
                        summary['textures'] += len(letters)
                        if s['ydd']:
                            summary['shop_entries'] += max(1, len(letters))
                        if s['alts']:
                            any_alt = True
                        if (s['alts'] or s['yld'] or s['yld_alts']) and not s['ydd'] and is_addon:
                            add('warn', 'COMPANION_NO_BASE', f_id, '有 .yld（布料物理）或 _1/_2… 替代模型，但没有本体 .ydd（替代模型、物理文件要和本体同名）')
                        if is_addon and letters and not s['ydd']:
                            add('error', 'TEXTURE_NO_DRAWABLE', f_id, f"有贴图 {''.join(letters)} 但没有这个编号的 .ydd 模型")
                        if s['ydd'] and not letters and is_addon:
                            add('warn', 'NO_TEXTURE', f_id, '没有任何 _diff_ 贴图 YTD。只用嵌入贴图是允许的，但大多数衣服至少要一张 a')
                        if letters:
                            expect = [chr(ord('a') + i) for i in range(len(letters))]
                            if letters != expect:
                                add('warn', 'TEXTURE_GAP', f_id, f"贴图字母 {''.join(letters)} 没有从 a 连续排下来，菜单里会出现空款或少款")
                        if kind == 'comp':
                            if len(s['skin']) > 1:
                                add('error', 'BOTH_U_AND_R', f_id, '同一个编号同时有 _u 和 _r 模型，只能留一个')
                            suffixes = set().union(*s['tex'].values()) if s['tex'] else set()
                            if 'u' in s['skin'] and suffixes & set(SKIN_SUFFIX):
                                add('error', 'SKIN_MISMATCH', f_id, f"模型是 _u（不含皮肤）但贴图是 _{'/_'.join(sorted(suffixes & set(SKIN_SUFFIX)))}：_u 配 _uni，_r 配 _whi，否则会显示成皮肤或贴错图")
                            if 'r' in s['skin'] and 'uni' in suffixes:
                                add('error', 'SKIN_MISMATCH', f_id, '模型是 _r（含皮肤）但贴图是 _uni：_r 配 _whi，_u 配 _uni')
                            if 'r' in s['skin'] and typ not in SKIN_TYPES:
                                add('warn', 'SKIN_ON_TYPE', f_id, f'{typ} 用了 _r（含皮肤）。DCT：皮肤数据只用在身体/腿/鞋（uppr/lowr/feet）。确认真的需要')
                    if is_addon and nums:
                        count = nums[-1] + 1
                        missing = sorted(set(range(count)) - set(nums))
                        if missing:
                            add('warn', 'NUMBER_GAP', f'{label}/stream {prefix_name}^{tname}', f"{GENDER[ped]} {tname} 缺编号 {', '.join(f'{x:03d}' for x in missing[:8])}{'…' if len(missing) > 8 else ''}：要从 000 连续编号，空号在菜单里是空白款")
                        if count >= MAX_COUNT:
                            add('error', 'COUNT_256', f'{label}/stream {prefix_name}^{tname}', f'{GENDER[ped]} {tname} 有 {count} 个位置，一个集合每种最多 255 个可用（DCT：到 256 会报 0 个）。拆成两个包（grzyClothTool 会自动拆）')
                        elif count > WARN_COUNT:
                            add('warn', 'COUNT_OVER_128', f'{label}/stream {prefix_name}^{tname}', f'{GENDER[ped]} {tname} 有 {count} 个位置，超过 128（旧版本的上限，同步要客户端和伺服器都是新版；DCT game-limits / grzyClothTool 预设）。旧环境可能缺件')
                    summary['types'][tname] = len(nums)
            collections_summary.append(summary)

        if any_alt and man is not None and not any(t in ('PED_FIRST_PERSON_ALTERNATE_DATA', 'ALTERNATE_VARIATIONS_FILE') for t in declared.values()):
            add('warn', 'ALT_NOT_DECLARED', label, "有 _1/_2… 替代模型，但 fxmanifest 没有 PED_FIRST_PERSON_ALTERNATE_DATA（第一人称 _1）或 ALTERNATE_VARIATIONS_FILE（替代头发等）的 data_file，替代模型不会被用到")
        if not clothing_files and man_path is not None:
            add('info', 'NO_CLOTHING_FILES', label, '没找到 freemode 衣服命名的文件（可能是妆容/纹身贴图包或别的资源），跳过')

    # ---------- across resources ----------
    for key, labels in owners.items():
        uniq = sorted(set(labels))
        if len(uniq) > 1:
            add('error', 'COLLECTION_CLASH', ', '.join(uniq), f"集合 {key} 出现在 {len(uniq)} 个资源里，同名的 YMT 只会有一个生效，其他包的衣服会消失。每个包用不同的包名（dlcName）")
    pairs = {}
    for name, labels in stream_names.items():
        uniq = sorted(set(labels))
        if len(uniq) > 1:
            pairs.setdefault(tuple(uniq), []).append(name)
    for res_pair, names in pairs.items():
        add('warn', 'DUPLICATE_STREAM_FILE', ', '.join(res_pair), f"{len(names)} 个同名 stream 文件（例如 {sorted(names)[0]}）。两个都 ensure 的话只有一个生效（后 ensure 的覆盖），是备份或复本就别同时开")
    dup_pairs = {}
    for size, items in ydd_by_size.items():
        if len({lab for lab, _ in items}) < 2:
            continue
        hashes = {}
        for lab, full in items:
            try:
                with open(full, 'rb') as fh:
                    hashes.setdefault(hashlib.sha1(fh.read()).hexdigest(), []).append((lab, full))
            except OSError:
                continue
        for same in hashes.values():
            labs = tuple(sorted({lab for lab, _ in same}))
            if len(labs) > 1:
                dup_pairs.setdefault(labs, []).append(os.path.basename(same[0][1]))
    for labs, names in dup_pairs.items():
        add('warn', 'DUPLICATE_CONTENT', ', '.join(labs), f"{len(names)} 个 .ydd 内容完全一样（例如 {names[0]}），同一件衣服装了两次，白占名额")
    total = sum(ymt_per_gender.values())
    if total:
        add('info', 'YMT_COUNT', ', '.join(os.path.basename(p) for p in paths),
            f"扫描范围里有 add-on YMT：男 {ymt_per_gender['mp_m_freemode_01']} 个、女 {ymt_per_gender['mp_f_freemode_01']} 个。每个游戏版本能多加的 YMT 很少（DCT 表：b3717–b3889 约 3–5 个，超过会闪退），尽量每个性别合成一个包")
    return findings, collections_summary


def main():
    ap = argparse.ArgumentParser(description='Check FiveM freemode clothing resources (read-only)')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    findings, summary = check(args.paths)
    if args.json:
        print(json.dumps({'findings': findings, 'collections': summary}, ensure_ascii=False, indent=2))
    else:
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                print(f"{icons[level]} {x['code']}: [{x['file']}] {x['message']}")
        if not findings:
            print('✓ 没发现问题')
        if summary:
            print('\n集合统计：')
            for s in summary:
                kinds = '、'.join(f'{k} {v} 件' for k, v in s['types'].items()) or '只有贴图'
                print(f"  [{s['resource']}] {s['collection']}（{'add-on' if s['addon'] else '替换'}）：{kinds}；贴图 {s['textures']} 张；商店条目约 {s['shop_entries']} 条（全局上限 65,520，原版和其他包共用）")
            print('\n提醒：add-on 衣服排在原版后面，顺序跟 ensure 顺序走；正式伺服器串流自制衣服要 Cfx Element Club Argentum 以上的权益（付费，脚本看不到），本机测试服人数设小可以先测。')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
