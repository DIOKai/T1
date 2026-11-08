#!/usr/bin/env python3
"""Read compiled GTA V (Legacy, RSC7) .ytd / .ydr / .ytyp files with the standard library only.

Read-only helper shared by check_prop_resource.py and fivem-asset-acceptance/asset_gate.py.
Layouts follow CodeWalker (Texture.cs, Drawable.cs, Meta.cs, MetaNames) and were checked
2026-11-08 against CodeWalker.Core output on vanilla Legacy files (prop_table_06, sofa,
birch tree, prop_pots.ytd) and on the user's own wood_table ytyp.

RSC7 file = 16-byte header (magic, version, virtual flags, physical flags) + raw deflate
body. The body inflates to virtual pages followed by physical pages; pointers 0x5xxxxxxx
point into the virtual block, 0x6xxxxxxx into the physical block. Every structure read
here (texture headers, models, geometry counts, bounds, meta blocks) lives in the virtual
block, so only that part is inflated - a 64 MiB texture dictionary costs a few KB.

Not covered: .yft internals (fragment layout not probed), bound composite flags, lights.
Enhanced (gen9) files and Cfx escrow (FXAP) files are reported by read_header only.
"""
import struct
import zlib

FOURCC = {
    0x31545844: 'DXT1', 0x33545844: 'DXT3', 0x35545844: 'DXT5',
    0x31495441: 'ATI1/BC4', 0x32495441: 'ATI2/BC5', 0x20374342: 'BC7',
}
D3DFMT = {20: 'R8G8B8', 21: 'A8R8G8B8', 22: 'X8R8G8B8', 23: 'R5G6B5', 25: 'A1R5G5B5', 26: 'A4R4G4B4',
          28: 'A8', 32: 'A8B8G8R8', 50: 'L8', 51: 'A8L8'}
BOUND_TYPES = {0: 'Sphere', 1: 'Capsule', 3: 'Box', 4: 'Geometry', 8: 'GeometryBVH', 10: 'Composite',
               12: 'Disc', 13: 'Cylinder'}
ASSET_TYPES = {0: 'UNINITIALIZED', 1: 'FRAGMENT', 2: 'DRAWABLE', 3: 'DRAWABLEDICTIONARY', 4: 'ASSETLESS'}
# CodeWalker MetaName values (structure name hashes inside RSC meta files); checked on wood_table.ytyp
# (CMapTypes + CBaseArchetypeDef) and kiiya_puerta_lobby_int.ytyp (adds CMloArchetypeDef).
META_CMAPTYPES = 3649811809
META_CBASEARCHETYPEDEF = 2195127427
META_CMLOARCHETYPEDEF = 273704021
ARCHETYPE_SIZE = {META_CBASEARCHETYPEDEF: 0x90, META_CMLOARCHETYPEDEF: 0xF0}


class ProbeError(Exception):
    pass


def page_size(flags):
    """FXServer ConvertRSC7Size / CodeWalker RpfFile.GetSizeFromFlags."""
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


def read_header(path):
    """{'kind': 'rsc'|'fxap'|'other', ...}. 'rsc' adds magic, version, virt, phys (bytes)."""
    with open(path, 'rb') as fh:
        head = fh.read(16)
    if len(head) >= 16 and head[:4] in (b'RSC7', b'RSC8'):
        magic, ver, v, p = struct.unpack('<4sIII', head)
        return {'kind': 'rsc', 'magic': magic.decode(), 'version': ver, 'virt_flags': v, 'phys_flags': p,
                'virt': page_size(v), 'phys': page_size(p)}
    if head[:4] == b'FXAP':
        return {'kind': 'fxap'}
    return {'kind': 'other'}


def joaat(s):
    h = 0
    for c in s.lower().encode('utf-8'):
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= h >> 6
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= h >> 11
    return (h + (h << 15)) & 0xFFFFFFFF


class Resource:
    """Inflated virtual block of an RSC7 file with pointer helpers."""

    def __init__(self, data, virt_size):
        self.d = data
        self.vs = virt_size

    @classmethod
    def from_bytes(cls, raw):
        if len(raw) < 16 or raw[:4] != b'RSC7':
            raise ProbeError('not RSC7')
        _, _, v, _ = struct.unpack('<4sIII', raw[:16])
        vs = page_size(v)
        try:
            data = zlib.decompressobj(-15).decompress(raw[16:], vs or 1)
        except zlib.error as e:
            raise ProbeError(f'inflate failed: {e}')
        return cls(data, vs)

    @classmethod
    def load(cls, path):
        """Inflate only the virtual block, reading the file in chunks (big texture dictionaries stay cheap)."""
        with open(path, 'rb') as fh:
            head = fh.read(16)
            if len(head) < 16 or head[:4] != b'RSC7':
                raise ProbeError('not RSC7')
            vs = page_size(struct.unpack('<4sIII', head)[2])
            dec, out = zlib.decompressobj(-15), bytearray()
            try:
                while len(out) < vs:
                    chunk = dec.unconsumed_tail or fh.read(1 << 16)
                    if not chunk:
                        break
                    out += dec.decompress(chunk, vs - len(out))
                    if dec.eof:
                        break
            except zlib.error as e:
                raise ProbeError(f'inflate failed: {e}')
        return cls(bytes(out), vs)

    def at(self, ptr):
        if ptr >> 28 == 5:
            off = ptr & 0x0FFFFFFF
        elif ptr >> 28 == 6:
            off = self.vs + (ptr & 0x0FFFFFFF)
        else:
            raise ProbeError(f'bad pointer {ptr:#x}')
        if off >= len(self.d):
            raise ProbeError(f'pointer {ptr:#x} outside the inflated virtual block')
        return off

    def u8(self, o):
        return self.d[o]

    def u16(self, o):
        return struct.unpack_from('<H', self.d, o)[0]

    def u32(self, o):
        return struct.unpack_from('<I', self.d, o)[0]

    def u64(self, o):
        return struct.unpack_from('<Q', self.d, o)[0]

    def f32(self, o):
        return struct.unpack_from('<f', self.d, o)[0]

    def cstr(self, o, limit=256):
        end = self.d.find(b'\0', o, o + limit)
        return self.d[o:end if end >= 0 else o + limit].decode('latin-1')

    def ptr_list(self, o):
        """ResourcePointerList64 at o: u64 pointer to an array of u64 pointers, u16 count."""
        p, n = struct.unpack_from('<QH', self.d, o)
        if not p or not n:
            return []
        base = self.at(p)
        return [self.u64(base + 8 * i) for i in range(n)]


def format_name(code):
    return FOURCC.get(code) or D3DFMT.get(code) or f'{code:#x}'


def is_compressed(code):
    return code in FOURCC


def textures_at(res, dict_off):
    """Textures of a TextureDictionary struct at dict_off (pointer list at +0x30)."""
    out = []
    for tp in res.ptr_list(dict_off + 0x30):
        t = res.at(tp)
        name_ptr = res.u64(t + 0x28)
        name = res.cstr(res.at(name_ptr)) if name_ptr else ''
        w, h, depth, stride, fmt = struct.unpack_from('<HHHHI', res.d, t + 0x50)
        out.append({'name': name, 'width': w, 'height': h, 'format': format_name(fmt), 'format_code': fmt,
                    'compressed': is_compressed(fmt), 'mips': res.u8(t + 0x5D)})
    return out


def read_ytd(path):
    return textures_at(Resource.load(path), 0)


def read_ydr(path):
    """LOD triangle counts, drawable LOD distances, bounding sphere, embedded bound type and textures."""
    res = Resource.load(path)
    lods = {}
    for i, nm in enumerate(('high', 'med', 'low', 'vlow')):
        mp = res.u64(0x50 + 8 * i)
        tris = geos = 0
        if mp:
            for model_ptr in res.ptr_list(res.at(mp)):
                for geo_ptr in res.ptr_list(res.at(model_ptr) + 0x08):
                    tris += res.u32(res.at(geo_ptr) + 0x58) // 3   # DrawableGeometry.IndicesCount
                    geos += 1
        lods[nm] = {'tris': tris, 'geometries': geos}
    dist = struct.unpack_from('<4f', res.d, 0x70)
    centre = struct.unpack_from('<3f', res.d, 0x20)
    radius = res.f32(0x2C)
    bound_ptr = res.u64(0xC8)
    bound = BOUND_TYPES.get(res.u8(res.at(bound_ptr) + 0x10), 'Other') if bound_ptr else None
    textures = []
    sg = res.u64(0x10)
    if sg:
        txd = res.u64(res.at(sg) + 0x08)
        if txd:
            textures = textures_at(res, res.at(txd))
    return {'lods': lods, 'lod_dist': dict(zip(('high', 'med', 'low', 'vlow'), dist)),
            'bs_centre': centre, 'bs_radius': radius, 'bound': bound, 'textures': textures}


def read_ytyp(path):
    """Archetype records of a compiled .ytyp via the meta data blocks.

    Returns {'mlo': bool, 'archetypes': [ {name_hash, asset_name_hash, lod_dist, flags,
    special_attribute, bs_radius, hd_texture_dist, txd_hash, clip_hash, drawable_dict_hash,
    physics_dict_hash, asset_type, mlo} ]}. Names are hashes (joaat); match them against file
    stems with joaat().
    """
    res = Resource.load(path)
    if res.u32(0x10) != 0x50524430:   # 'PDR0' meta marker
        raise ProbeError('not a meta resource')
    blocks_ptr = res.u64(0x30)
    n_blocks = struct.unpack_from('<h', res.d, 0x4C)[0]
    archetypes, mlo = [], False
    if blocks_ptr and n_blocks > 0:
        base = res.at(blocks_ptr)
        for i in range(n_blocks):
            sh, length, dp = struct.unpack_from('<IiQ', res.d, base + 0x10 * i)
            if sh == META_CMLOARCHETYPEDEF:
                mlo = True
            size = ARCHETYPE_SIZE.get(sh)
            if not size or not dp or length <= 0:
                continue
            o0 = res.at(dp)
            for k in range(length // size):
                o = o0 + k * size
                lod, flags, attr = struct.unpack_from('<fII', res.d, o + 0x08)
                bsr, hdd = struct.unpack_from('<ff', res.d, o + 0x50)
                name, txd, clip, ddict, phys, atype, asset = struct.unpack_from('<7I', res.d, o + 0x58)
                archetypes.append({'name_hash': name, 'asset_name_hash': asset, 'lod_dist': lod, 'flags': flags,
                                   'special_attribute': attr, 'bs_radius': bsr, 'hd_texture_dist': hdd,
                                   'txd_hash': txd, 'clip_hash': clip, 'drawable_dict_hash': ddict,
                                   'physics_dict_hash': phys, 'asset_type': ASSET_TYPES.get(atype, str(atype)),
                                   'mlo': sh == META_CMLOARCHETYPEDEF})
    return {'mlo': mlo, 'archetypes': archetypes}


def ytyp_has_mlo(path):
    try:
        return read_ytyp(path)['mlo']
    except (ProbeError, OSError, struct.error, IndexError):
        return False


if __name__ == '__main__':
    import json
    import os
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    for p in sys.argv[1:]:
        ext = os.path.splitext(p)[1].lower()
        reader = {'.ytd': read_ytd, '.ydr': read_ydr, '.ytyp': read_ytyp}.get(ext)
        out = {'file': p, 'header': read_header(p)}
        if reader and out['header']['kind'] == 'rsc':
            try:
                out['data'] = reader(p)
            except (ProbeError, struct.error, IndexError) as e:
                out['error'] = str(e)
        print(json.dumps(out, ensure_ascii=False, indent=1))
