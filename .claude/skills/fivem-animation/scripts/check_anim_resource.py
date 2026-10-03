#!/usr/bin/env python3
"""Check custom GTA V / FiveM animation files and the resource they ship in.

Usage:
    python check_anim_resource.py <path> [more paths] [--json]

<path> can be a FiveM resource (e.g. rpemotes-reborn), a folder of Sollumz
exports, or single .ycd / .ycd.xml files. Standard library only, read-only.
Exit code 1 when errors are found.

Checks
- .ycd.xml (Sollumz export): empty or duplicate Clip Hash (the game finds
  clips by Hash, CodeWalker Clip.cs), clip -> animation links, clip Rate != 1
  (Sollumz: rate = animation length / clip Duration, ycdexport.py), animation
  frame rate != 30 fps ((FrameCount-1)/Duration).
- .ycd.xml left inside stream/ (FiveM streams by file extension; XML is not
  loaded as an animation, LoadStreamingFile.cpp).
- .ycd binaries: RSC7 header (CodeWalker ResourceBuilder.cs), lowercase name
  without spaces (dictionary name = file name).
- stream_enhanced/ present but a .ycd only in stream/ (the Enhanced client
  loads stream_enhanced instead of stream, fivem-docs legacy-vs-enhanced).
- rpemotes AnimationListCustom.lua: dictionaries with no local .ycd (fine only
  if vanilla), clips missing from a matching local .ycd.xml, and custom .ycd
  files no emote uses.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ENTRY_RE = re.compile(r'\[\s*["\']([^"\']+)["\']\s*\]\s*=\s*\{\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']')


def walk(paths):
    files = []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            files.append(p)
            continue
        for root, dirs, fs in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files += [os.path.join(root, f) for f in fs]
    return files


def rel(path, bases):
    for b in bases:
        b = os.path.abspath(b)
        if path.startswith(b + os.sep):
            return os.path.relpath(path, b).replace(os.sep, '/')
    return os.path.basename(path)


def val(el, tag):
    child = el.find(tag)
    if child is None:
        return None
    v = child.get('value')
    return v if v is not None else (child.text or '').strip()


def check(paths):
    findings = []

    def add(level, code, where, msg):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg})

    files = walk(paths)
    ycd_stems, xml_clips = {}, {}

    for f in files:
        name = os.path.basename(f)
        low = name.lower()
        r = rel(f, paths)
        parts = r.lower().split('/')
        if low.endswith('.ycd.xml'):
            stem = name[:-8]
            if 'stream' in parts or 'stream_enhanced' in parts:
                add('error', 'XML_IN_STREAM', r, '.ycd.xml 放在 stream 里不会被当成动画加载。用 CodeWalker 的 RPF Explorer "Import XML" 编译成 .ycd 再放进去')
            try:
                root = ET.parse(f).getroot()
            except ET.ParseError as e:
                add('error', 'XML_INVALID', r, f'不是合法的 XML：{e}')
                continue
            anim_hashes = set()
            anims = root.find('Animations')
            for a in (anims if anims is not None else []):
                h = (a.findtext('Hash') or '').strip()
                anim_hashes.add(h.lower())
                fc, dur = val(a, 'FrameCount'), val(a, 'Duration')
                try:
                    fc, dur = int(float(fc)), float(dur)
                    if dur > 0 and fc > 1:
                        fps = (fc - 1) / dur
                        if abs(fps - 30) > 0.5:
                            add('warn', 'ANIM_FPS', r, f"动画 '{h}' 是 {fps:.1f} fps（{fc} 帧 / {dur:.3f} 秒），GTA 动画是 30 fps。在 Blender 把场景帧率设成 30 再导出")
                except (TypeError, ValueError):
                    pass
            clips = root.find('Clips')
            seen = {}
            clip_names = set()
            for c in (clips if clips is not None else []):
                h = (c.findtext('Hash') or '').strip()
                nm = (c.findtext('Name') or '').strip()
                if not h:
                    add('error', 'CLIP_HASH_EMPTY', r, f"clip（Name='{nm}'）的 Hash 是空的。游戏用 Hash 找 clip，要填成 TaskPlayAnim 里用的 clip 名字")
                else:
                    if h.lower() in seen:
                        add('error', 'CLIP_HASH_DUPLICATE', r, f"clip Hash '{h}' 重复，后面那个会找不到")
                    seen[h.lower()] = True
                    clip_names.add(h.lower())
                links = [c] if c.find('AnimationHash') is not None else list(c.find('Animations') or [])
                for link in links:
                    ah = (link.findtext('AnimationHash') or '').strip()
                    if ah and anim_hashes and ah.lower() not in anim_hashes:
                        add('error', 'CLIP_ANIM_MISSING', r, f"clip '{h or nm}' 连到的动画 '{ah}' 不在这个字典里")
                    rate = val(link, 'Rate')
                    try:
                        rate = float(rate)
                        if rate > 0 and abs(rate - 1.0) > 0.02:
                            add('warn', 'CLIP_RATE', r, f"clip '{h or nm}' 的 Rate 是 {rate:.3f}（不是 1），播放速度会变。Sollumz 里 clip 的 Duration 要等于（结束帧-开始帧）/ 30")
                    except (TypeError, ValueError):
                        pass
            xml_clips[stem.lower()] = clip_names
            if stem != stem.lower() or ' ' in stem:
                add('warn', 'NAME_CASE', r, f"字典名 '{stem}' 有大写或空格，建议全小写、不要空格（字典名 = 文件名）")
        elif low.endswith('.ycd'):
            stem = name[:-4]
            ycd_stems.setdefault(stem.lower(), []).append(r)
            with open(f, 'rb') as fh:
                if fh.read(4) != b'RSC7' and 'stream_enhanced' not in parts:
                    add('warn', 'NOT_RSC7', r, '开头不是 RSC7，不像编译好的 .ycd（可能是改了扩展名的 XML、损坏或放错的 Gen9 文件）')
            if stem != stem.lower() or ' ' in stem:
                add('warn', 'NAME_CASE', r, f"字典名 '{stem}' 有大写或空格，建议全小写、不要空格")

    # stream_enhanced coverage, per resource
    resources = {os.path.dirname(f) for f in files if os.path.basename(f) == 'fxmanifest.lua'}
    for res in resources:
        se = os.path.join(res, 'stream_enhanced')
        if os.path.isdir(se):
            enh = {os.path.basename(f).lower() for f in files if f.startswith(se + os.sep) and f.lower().endswith('.ycd')}
            st = [f for f in files if f.startswith(os.path.join(res, 'stream') + os.sep) and f.lower().endswith('.ycd')]
            for f in st:
                if os.path.basename(f).lower() not in enh:
                    add('warn', 'MISSING_IN_STREAM_ENHANCED', rel(f, paths), '这个资源有 stream_enhanced/，Enhanced 版只会读那里，这个 .ycd 也要复制一份过去')

    for stem, where in ycd_stems.items():
        if len(where) > 1:
            add('error', 'DICT_DUPLICATE', where[0], f"字典 '{stem}.ycd' 出现 {len(where)} 次（{', '.join(where)}），会互相覆盖")

    # rpemotes custom list
    for f in files:
        if os.path.basename(f) == 'AnimationListCustom.lua':
            text = open(f, encoding='utf-8', errors='replace').read()
            text = re.sub(r'--\[\[.*?\]\]', '', text, flags=re.S)
            text = re.sub(r'--[^\n]*', '', text)
            entries = ENTRY_RE.findall(text)
            used = {d.lower() for _, d, _ in entries}
            for stem, where in ycd_stems.items():
                if stem not in used and any('custom emotes' in w.lower() for w in where):
                    add('info', 'YCD_NOT_REGISTERED', where[0], f"'{stem}.ycd' 放进了 [Custom Emotes]，但 AnimationListCustom.lua 里没有表情用它，菜单里不会出现")
            for emote, d, clip in entries:
                dl = d.lower()
                if dl not in ycd_stems:
                    add('info', 'DICT_NOT_LOCAL', rel(f, paths), f"表情 '{emote}' 用的字典 '{d}' 没有在这里找到 .ycd：原版动画就没问题，自定义的话要放进 stream/[Custom Emotes]/")
                elif dl in xml_clips and xml_clips[dl] and clip.lower() not in xml_clips[dl]:
                    add('error', 'CLIP_NOT_IN_DICT', rel(f, paths), f"表情 '{emote}' 的 clip '{clip}' 不在 {d}.ycd.xml 的 clip Hash 里（有：{', '.join(sorted(xml_clips[dl]))}）")
    return findings


def main():
    ap = argparse.ArgumentParser(description='Check GTA V / FiveM animation files')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    findings = check(args.paths)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                print(f"{icons[level]} {x['code']}: [{x['file']}] {x['message']}")
        if not findings:
            print('✓ 没发现问题')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
