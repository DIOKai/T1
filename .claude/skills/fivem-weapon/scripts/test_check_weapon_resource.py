"""Tests for check_weapon_resource.py (standard library only).

    py -3 -I .claude/skills/fivem-weapon/scripts/test_check_weapon_resource.py
"""
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_weapon_resource as chk  # noqa: E402

MANIFEST = """fx_version 'cerulean'
game 'gta5'
files { 'meta/*.meta' }
data_file 'WEAPONCOMPONENTSINFO_FILE' 'meta/weaponcomponents.meta'
data_file 'WEAPON_METADATA_FILE'      'meta/weaponarchetypes.meta'
data_file 'WEAPON_ANIMATIONS_FILE'    'meta/weaponanimations.meta'
data_file 'PED_PERSONALITY_FILE'      'meta/pedpersonality.meta'
data_file 'WEAPONINFO_FILE'           'meta/weapons.meta'
client_script 'client/names.lua'
"""


def weapons_meta(name='WEAPON_TYPE38', model='w_sr_type38', slot='SLOT_TYPE38', nav_slot=None, label='WT_TYPE38',
                 extra_components=''):
    nav_slot = nav_slot or slot
    return f"""<?xml version="1.0" encoding="UTF - 8"?>
<CWeaponInfoBlob>
  <SlotNavigateOrder><Item><WeaponSlots><Item><OrderNumber value="481"/><Entry>{nav_slot}</Entry></Item></WeaponSlots></Item></SlotNavigateOrder>
  <Infos><Item><Infos>
    <Item type="CWeaponInfo">
      <Name>{name}</Name><Model>{model}</Model><Audio>AUDIO_ITEM_MUSKET</Audio><Slot>{slot}</Slot>
      <DamageType>BULLET</DamageType><HumanNameHash>{label}</HumanNameHash>
      <AttachPoints>
        <Item><AttachBone>WAPClip</AttachBone><Components>
          <Item><Name>COMPONENT_TYPE38_CLIP_01</Name><Default value="true"/></Item></Components></Item>
        <Item><AttachBone>WAPScop</AttachBone><Components>
          <Item><Name>COMPONENT_AT_SCOPE_MEDIUM</Name><Default value="false"/></Item>{extra_components}</Components></Item>
      </AttachPoints>
      <WeaponFlags>CarriedInHand Gun CanFreeAim TwoHanded AnimReload UsableOnFoot LongWeapon</WeaponFlags>
    </Item>
  </Infos></Item></Infos>
  <Name>Type 38</Name>
</CWeaponInfoBlob>"""


def components_meta(bone='AAPClip', model='w_sr_type38_mag1'):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CWeaponComponentInfoBlob><Infos>
  <Item type="CWeaponComponentClipInfo"><Name>COMPONENT_TYPE38_CLIP_01</Name><Model>{model}</Model>
    <AttachBone>{bone}</AttachBone><WeaponAttachBone>WAPClip</WeaponAttachBone><ClipSize value="5"/>
    <ReloadData ref="RELOAD_DEFAULT"/></Item>
</Infos><InfoBlobName/></CWeaponComponentInfoBlob>"""


def archetypes_meta(models=('w_sr_type38', 'w_sr_type38_mag1')):
    items = ''.join(f'<Item><modelName>{m}</modelName><txdName>{m}</txdName><ptfxAssetName>NULL</ptfxAssetName>'
                    f'<lodDist value="500"/></Item>' for m in models)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<CWeaponModelInfo__InitDataList><InitDatas>{items}</InitDatas></CWeaponModelInfo__InitDataList>'


ANIMS = """<?xml version="1.0" encoding="UTF-8"?>
<CWeaponAnimationsSets><WeaponAnimationsSets><Item key="Default"><WeaponAnimations>
  <Item key="WEAPON_TYPE38"><WeaponClipSetHash>weapons@rifle@hi@musket</WeaponClipSetHash></Item>
</WeaponAnimations></Item></WeaponAnimationsSets></CWeaponAnimationsSets>"""

PERSONA = """<?xml version="1.0" encoding="UTF-8"?>
<CPedModelInfo__PersonalityDataList><MovementModeUnholsterData><Item><Name>UNHOLSTER_UNARMED</Name>
<UnholsterClips><Item><Weapons><Item>WEAPON_TYPE38</Item></Weapons><Clip>unarmed_holster_2h</Clip></Item></UnholsterClips>
</Item></MovementModeUnholsterData></CPedModelInfo__PersonalityDataList>"""

NAMES = "AddTextEntry('WT_TYPE38', 'Type 38 Rifle')\n"

GUN_BONES = ['Gun_Root', 'Gun_GripR', 'Gun_Main_Bone', 'Gun_Cock1', 'Gun_Muzzle', 'WAPScop', 'WAPClip',
             'Gun_Trigger', 'Gun_GripL']


def ydr_xml(bones, bounds=True, tris=500):
    b = ''.join(f'<Item><Name>{n}</Name><Tag value="{i}"/></Item>' for i, n in enumerate(bones))
    idx = ' '.join(['0'] * (tris * 3))
    bd = '<Bounds type="Composite"><Children><Item type="Box"/></Children></Bounds>' if bounds else ''
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<Drawable><Name>x</Name><Skeleton><Bones>{b}</Bones></Skeleton>'
            f'<DrawableModelsHigh><Item><Geometries><Item><IndexBuffer><Data>{idx}</Data></IndexBuffer></Item>'
            f'</Geometries></Item></DrawableModelsHigh>{bd}</Drawable>')


OX = """return {
	Weapons = {
		['WEAPON_TYPE38'] = { label = 'Type 38', weight = 3900, durability = 0.05, ammoname = 'ammo-rifle' },
	},
	Components = {
		['at_scope_medium'] = { label = 'Medium Scope', type = 'sight', client = { component = { `COMPONENT_AT_SCOPE_MEDIUM` } } },
	},
	Ammo = {
		['ammo-rifle'] = { label = '6.5mm', weight = 10 },
	},
}
"""


def rsc(version=165, virt_flags=0, phys_flags=0):
    return b'RSC7' + struct.pack('<III', version, virt_flags, phys_flags) + b'\0' * 16


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as fh:
        fh.write(data.encode('utf-8') if isinstance(data, str) else data)


def build(root, **over):
    """A good add-on rifle; keyword arguments replace or (with None) delete single files."""
    files = {
        'fxmanifest.lua': MANIFEST,
        'meta/weapons.meta': weapons_meta(),
        'meta/weaponcomponents.meta': components_meta(),
        'meta/weaponarchetypes.meta': archetypes_meta(),
        'meta/weaponanimations.meta': ANIMS,
        'meta/pedpersonality.meta': PERSONA,
        'client/names.lua': NAMES,
        'stream/w_sr_type38.ydr': rsc(),
        'stream/w_sr_type38_hi.ydr': rsc(),
        'stream/w_sr_type38.ytd': rsc(13),
        'stream/w_sr_type38_mag1.ydr': rsc(),
        'stream/w_sr_type38_mag1.ytd': rsc(13),
    }
    for k, v in over.items():
        k = k.replace('__', '/').replace('_DOT_', '.')
        if v is None:
            files.pop(k, None)
        else:
            files[k] = v
    res = os.path.join(root, 'w_type38')
    for k, v in files.items():
        write(res, k, v)
    return res


def build_xml(root, base=None, hi=None, mag=None):
    d = os.path.join(root, 'export')
    write(d, 'w_sr_type38.ydr.xml', base if base is not None else ydr_xml(GUN_BONES, True, 2500))
    write(d, 'w_sr_type38_hi.ydr.xml', hi if hi is not None else ydr_xml(GUN_BONES, False, 8000))
    write(d, 'w_sr_type38_mag1.ydr.xml', mag if mag is not None else ydr_xml(['AAPClip'], True, 120))
    return d


def build_ox(root, text=OX, image=True):
    d = os.path.join(root, 'ox_inventory')
    write(d, 'data/weapons.lua', text)
    if image:
        write(d, 'web/images/WEAPON_TYPE38.png', b'\x89PNG')
    return d


def codes(findings, level=None):
    return {f['code'] for f in findings if level is None or f['level'] == level}


class GoodResource(unittest.TestCase):
    def test_good_addon_has_no_errors_or_warnings(self):
        with tempfile.TemporaryDirectory() as d:
            res = build(d)
            found = chk.check([res], ox=build_ox(d), xml_dirs=[build_xml(d)])
        self.assertEqual([f for f in found if f['level'] in ('error', 'warn')], [])

    def test_folder_of_resources_is_walked(self):
        with tempfile.TemporaryDirectory() as d:
            build(d)
            found = chk.check([d])
        self.assertNotIn('NO_MANIFEST', codes(found))
        self.assertEqual(codes(found, 'error'), set())

    def test_meta_only_retune_of_vanilla(self):
        with tempfile.TemporaryDirectory() as d:
            res = os.path.join(d, 'retune')
            write(res, 'fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\nfiles { 'weapons.meta' }\n"
                                         "data_file 'WEAPONINFO_FILE' 'weapons.meta'\n")
            write(res, 'weapons.meta', weapons_meta(name='WEAPON_CARBINERIFLE', model='W_AR_CARBINERIFLE',
                                                    slot='SLOT_CARBINERIFLE', label='WT_RIFLE_CBN'))
            found = chk.check([res])
        self.assertIn('VANILLA_RETUNE', codes(found, 'info'))
        self.assertEqual(codes(found, 'error'), set())

    def test_replacement_pack(self):
        with tempfile.TemporaryDirectory() as d:
            res = os.path.join(d, 'pistol_skin')
            write(res, 'fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\n")
            for f in ('w_pi_pistol.ydr', 'w_pi_pistol_hi.ydr', 'w_pi_pistol_mag1.ydr'):
                write(res, 'stream/' + f, rsc())
            write(res, 'stream/w_pi_pistol.ytd', rsc(13))
            prop = os.path.join(d, 'prop_pack')
            write(prop, 'fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\n")
            write(prop, 'stream/prop_table.ydr', rsc())
            found = chk.check([d])
        packs = [f['file'] for f in found if f['code'] == 'REPLACEMENT_PACK']
        self.assertEqual(packs, ['pistol_skin'])
        self.assertEqual(codes(found, 'error'), set())

    def test_xml_comment_banners_parse(self):
        with tempfile.TemporaryDirectory() as d:
            res = build(d, meta__weaponarchetypes_DOT_meta=archetypes_meta().replace(
                '<InitDatas>', '<InitDatas><!------------------------>'))
            found = chk.check([res])
        self.assertNotIn('META_PARSE', codes(found))

    def test_page_size_formula(self):
        self.assertEqual(chk.rsc_page_size(0), 0)
        self.assertEqual(chk.rsc_page_size((1 << 4) | 8), 32 * chk.MIB)


class Problems(unittest.TestCase):
    def run_case(self, ox=False, xml=None, **over):
        with tempfile.TemporaryDirectory() as d:
            res = build(d, **over)
            oxd = build_ox(d, **ox) if isinstance(ox, dict) else (build_ox(d) if ox else None)
            xd = [build_xml(d, **xml)] if xml is not None else []
            return chk.check([res], ox=oxd, xml_dirs=xd)

    def assertCode(self, found, code, level):
        self.assertIn(code, codes(found, level), msg=str(found))

    def test_typo_data_file_type(self):
        found = self.run_case(fxmanifest_DOT_lua=MANIFEST.replace('WEAPON_ANIMATIONS_FILE', 'WEAPON_ANIMATION_FILE'))
        self.assertCode(found, 'DATA_FILE_UNKNOWN', 'error')
        self.assertIn('WEAPON_ANIMATIONS_FILE', [f for f in found if f['code'] == 'DATA_FILE_UNKNOWN'][0]['message'])

    def test_meta_not_in_files(self):
        found = self.run_case(fxmanifest_DOT_lua=MANIFEST.replace("'meta/*.meta'", "'meta/weapons.meta'"))
        self.assertCode(found, 'NOT_IN_FILES', 'error')

    def test_data_file_without_file(self):
        found = self.run_case(meta__pedpersonality_DOT_meta=None)
        self.assertCode(found, 'DATA_FILE_NO_MATCH', 'error')

    def test_weaponinfo_not_last(self):
        m = MANIFEST.replace("data_file 'WEAPONINFO_FILE'           'meta/weapons.meta'\n", '')
        m = m.replace("data_file 'WEAPONCOMPONENTSINFO_FILE'", "data_file 'WEAPONINFO_FILE' 'meta/weapons.meta'\ndata_file 'WEAPONCOMPONENTSINFO_FILE'")
        self.assertCode(self.run_case(fxmanifest_DOT_lua=m), 'WEAPONINFO_NOT_LAST', 'warn')

    def test_meta_parse_error_and_type_mismatch(self):
        self.assertCode(self.run_case(meta__weaponanimations_DOT_meta='<CWeaponAnimationsSets><oops>'), 'META_PARSE', 'error')
        self.assertCode(self.run_case(meta__weaponanimations_DOT_meta=PERSONA), 'META_TYPE_MISMATCH', 'error')

    def test_unmounted_meta(self):
        found = self.run_case(meta__loadouts_DOT_meta='<?xml version="1.0"?><CPedModelInfo__PersonalityDataList/>',
                              fxmanifest_DOT_lua=MANIFEST.replace("'meta/*.meta'", "'meta/*.meta'"))
        self.assertCode(found, 'META_NOT_MOUNTED', 'warn')

    def test_hi_only_is_invisible(self):
        found = self.run_case(stream__w_sr_type38_DOT_ydr=None)
        self.assertCode(found, 'HI_WITHOUT_BASE', 'error')
        self.assertCode(found, 'MODEL_NOT_STREAMED', 'error')

    def test_model_without_archetype(self):
        self.assertCode(self.run_case(meta__weaponarchetypes_DOT_meta=archetypes_meta(('w_sr_type38_mag1',))),
                        'MODEL_NO_ARCHETYPE', 'error')

    def test_mag_without_archetype(self):
        self.assertCode(self.run_case(meta__weaponarchetypes_DOT_meta=archetypes_meta(('w_sr_type38',))),
                        'COMPONENT_NO_ARCHETYPE', 'error')

    def test_txd_missing(self):
        self.assertCode(self.run_case(stream__w_sr_type38_DOT_ytd=None), 'TXD_MISSING', 'warn')

    def test_stream_problems(self):
        found = self.run_case(stream__w_sr_type38_DOT_ydr_DOT_xml='<Drawable/>',
                              stream__w_sr_type38_mag1_DOT_ydr='<Drawable/>',
                              stream__w_sr_type38_DOT_ytd=rsc(13, 0, (1 << 4) | 8),
                              stream__sub__w_sr_type38_hi_DOT_ydr=rsc(),
                              w_sr_type38_hi_DOT_ytd=rsc(13))
        self.assertCode(found, 'XML_IN_STREAM', 'error')
        self.assertCode(found, 'NOT_RSC7', 'error')
        self.assertCode(found, 'ASSET_OVER_16MIB', 'warn')
        self.assertCode(found, 'DUPLICATE_ASSET', 'error')
        self.assertCode(found, 'NOT_IN_STREAM', 'warn')

    def test_rsc_version(self):
        self.assertCode(self.run_case(stream__w_sr_type38_DOT_ydr=rsc(159)), 'RSC_VERSION', 'warn')

    def test_names_and_slots(self):
        self.assertCode(self.run_case(client__names_DOT_lua='print(1)\n'), 'NO_TEXT_ENTRY', 'warn')
        self.assertCode(self.run_case(meta__weapons_DOT_meta=weapons_meta(nav_slot='SLOT_OTHER')),
                        'SLOT_NOT_IN_NAV', 'warn')

    def test_missing_animation_entry(self):
        found = self.run_case(meta__weaponanimations_DOT_meta=ANIMS.replace('WEAPON_TYPE38', 'WEAPON_OTHER'))
        self.assertCode(found, 'NO_ANIMATION', 'warn')

    def test_component_problems(self):
        self.assertCode(self.run_case(meta__weaponcomponents_DOT_meta=components_meta(bone='WAPClip')),
                        'COMPONENT_BONE', 'warn')
        found = self.run_case(meta__weapons_DOT_meta=weapons_meta(
            extra_components='<Item><Name>COMPONENT_TYPE38_SCOPE_TYPO</Name><Default value="false"/></Item>'))
        self.assertCode(found, 'COMPONENT_UNDEFINED', 'warn')

    def test_ox_problems(self):
        self.assertCode(self.run_case(ox={'text': OX.replace('WEAPON_TYPE38', 'WEAPON_TYPE_38')}), 'OX_MISSING', 'error')
        self.assertCode(self.run_case(ox={'text': OX.replace("['ammo-rifle'] =", "['ammo-65'] =")}),
                        'OX_AMMO_MISSING', 'error')
        self.assertCode(self.run_case(ox={'image': False}), 'OX_IMAGE_MISSING', 'warn')
        self.assertCode(self.run_case(ox={'text': OX.replace('`COMPONENT_AT_SCOPE_MEDIUM`', '`COMPONENT_AT_SCOPE_LARGE`')}),
                        'OX_COMPONENT_MISSING', 'warn')

    def test_ox_model_field_counts(self):
        found = self.run_case(ox={'text': OX.replace("['WEAPON_TYPE38'] = {", "['type38'] = { model = 'WEAPON_TYPE38',")})
        self.assertNotIn('OX_MISSING', codes(found))

    def test_xml_skeleton_problems(self):
        no_muzzle = [b for b in GUN_BONES if b not in ('Gun_Muzzle', 'WAPScop')]
        found = self.run_case(xml={'base': ydr_xml(no_muzzle, bounds=False, tris=9000)})
        self.assertCode(found, 'XML_BONES_MISSING', 'error')
        self.assertCode(found, 'XML_ATTACH_BONE_MISSING', 'error')
        self.assertCode(found, 'XML_NO_BOUNDS', 'warn')
        self.assertCode(found, 'XML_TRIS_HIGH', 'warn')
        self.assertCode(self.run_case(xml={'base': ydr_xml([])}), 'XML_NO_SKELETON', 'error')
        self.assertCode(self.run_case(xml={'mag': ydr_xml(['Gun_Root', 'AAPClip'])}), 'XML_COMPONENT_ROOT', 'warn')
        self.assertCode(self.run_case(xml={'hi': ydr_xml(GUN_BONES, bounds=True)}), 'XML_HI_BOUNDS', 'info')

    def test_escrowed_files_are_skipped(self):
        found = self.run_case(stream__w_sr_type38_hi_DOT_ydr=b'FXAP\x01\x00\x00\x00' + b'\0' * 24)
        self.assertCode(found, 'ESCROWED', 'info')
        self.assertNotIn('NOT_RSC7', codes(found))

    def test_brackets_in_server_folder_names(self):
        with tempfile.TemporaryDirectory() as d:
            res = build(os.path.join(d, '[weapons]'))
            found = chk.check([res])
        self.assertEqual(codes(found, 'error'), set())

    def test_no_manifest(self):
        self.assertCode(self.run_case(fxmanifest_DOT_lua=None), 'NO_MANIFEST', 'error')


if __name__ == '__main__':
    unittest.main()
