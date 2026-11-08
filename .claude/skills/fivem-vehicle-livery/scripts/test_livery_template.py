"""Tests for livery_template.py (standard library only).

    py -3 -I .claude/skills/fivem-vehicle-livery/scripts/test_livery_template.py
"""
import os
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import livery_template as lt  # noqa: E402

PAINT3 = f'hash_{lt.joaat("vehicle_paint3"):08X}'   # CodeWalker writes unresolved names like this
MESH = 'vehicle_mesh'


def geometry(shader, quads):
    data, idx = [], []
    for lines, ind in quads:
        base = len(data)
        data += lines
        idx += [base + i for i in ind]
    rows = '\n'.join('        ' + x for x in data)
    return f"""     <Item>
      <ShaderIndex value="{shader}" />
      <BoneIDs>0, 1, 2</BoneIDs>
      <VertexBuffer>
       <Flags value="0" />
       <Layout type="GTAV1"><Position /><BlendWeights /><BlendIndices /><Normal /><TexCoord0 /><TexCoord1 /></Layout>
       <Data>
{rows}
       </Data>
      </VertexBuffer>
      <IndexBuffer><Data>{' '.join(map(str, idx))}</Data></IndexBuffer>
     </Item>"""


def fragment(high, medium=None, livery_tex='testcar_sign_1'):
    med = ''
    if medium is not None:
        med = f'<DrawableModelsMedium><Item><Geometries>{medium}</Geometries></Item></DrawableModelsMedium>'
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Fragment>
 <Name>testcar</Name>
 <Drawable>
  <Name>skel</Name>
  <ShaderGroup>
   <Shaders>
    <Item><Name>{PAINT3}</Name><Parameters>
      <Item name="DiffuseSampler" type="Texture"><Name>vehicle_generic_smallspecmap</Name></Item>
      <Item name="DiffuseSampler2" type="Texture"><Name>{livery_tex}</Name></Item>
      <Item name="matDiffuseColor" type="Vector" x="2" y="1" z="1" w="0" />
    </Parameters></Item>
    <Item><Name>{MESH}</Name><Parameters>
      <Item name="DiffuseSampler" type="Texture"><Name>testcar_interior</Name></Item>
    </Parameters></Item>
   </Shaders>
  </ShaderGroup>
  <Skeleton><Bones>
   <Item><Name>chassis</Name></Item><Item><Name>door_dside_f</Name></Item><Item><Name>door_pside_f</Name></Item>
  </Bones></Skeleton>
  <DrawableModelsHigh><Item><Geometries>
{high}
  </Geometries></Item></DrawableModelsHigh>
  {med}
 </Drawable>
 <Physics><LOD1><Children><Item><Drawable><DrawableModelsHigh><Item><Geometries>
  <Item><ShaderIndex value="0" /></Item></Geometries></Item></DrawableModelsHigh></Drawable></Item></Children></LOD1></Physics>
</Fragment>"""


# driver side (x=-0.9, faces -X). Seen from outside the front is on the left: upright text, not mirrored.
def driver(u0=0.1, v0=0.1, bone=1):
    pts = [(-0.9, -1, 0), (-0.9, 1, 1), (-0.9, 1, 0), (-0.9, -1, 1)]
    # triangles (A,C,B) and (A,D,C) both face -X; write them as two explicit triangles
    uv = lambda p: (u0 + 0.3 * (1 - p[1]) / 2, v0 + 0.3 * (1 - p[2]))
    a, c, b, d = pts
    lines = [f'{p[0]} {p[1]} {p[2]}   255 0 0 0   {bone} 0 0 0   -1 0 0   0 0   {uv(p)[0]} {uv(p)[1]}' for p in (a, c, b, d)]
    return lines, [0, 1, 2, 0, 3, 1]


def passenger(u0=0.6, v0=0.6, mirrored=False, bone=2):
    """Faces +X. Not mirrored = rotated 180 deg like vanilla polgauntlet (front left, top down)."""
    a, b, c, d = (0.9, -1, 0), (0.9, 1, 0), (0.9, 1, 1), (0.9, -1, 1)
    if mirrored:
        uv = lambda p: (u0 + 0.3 * (1 - p[1]) / 2, v0 + 0.3 * (1 - p[2]))      # front left, top up = mirror image
    else:
        uv = lambda p: (u0 + 0.3 * (1 - p[1]) / 2, v0 + 0.3 * p[2])            # front left, top down = 180 deg
    lines = [f'{p[0]} {p[1]} {p[2]}   255 0 0 0   {bone} 0 0 0   1 0 0   0 0   {uv(p)[0]} {uv(p)[1]}' for p in (a, b, c, d)]
    return lines, [0, 1, 2, 0, 2, 3]


def roof():
    a, b, c, d = (-0.5, -0.5, 1.2), (0.5, -0.5, 1.2), (0.5, 0.5, 1.2), (-0.5, 0.5, 1.2)
    uv = lambda p: (0.1 + 0.3 * (p[0] + 0.5), 0.9 - 0.3 * (p[1] + 0.5))
    lines = [f'{p[0]} {p[1]} {p[2]}   255 0 0 0   0 0 0 0   0 0 1   0 0   {uv(p)[0]} {uv(p)[1]}' for p in (a, b, c, d)]
    return lines, [0, 1, 2, 0, 2, 3]


def write(d, name, text):
    p = os.path.join(d, name)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return p


class Template(unittest.TestCase):
    def build(self, d, high, medium=None):
        return write(d, 'testcar.yft.xml', fragment(high, medium))

    def test_sides_rotation_mirror_density(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.build(d, geometry(0, [driver(), passenger(), roof()]) + geometry(1, [roof()]))
            model = lt.read_model(p)
            self.assertEqual(len(model['lods']['high']), 2)                 # physics child drawable ignored
            res = lt.analyse(model)
            self.assertEqual([m['texture'] for m in res['materials']], ['testcar_sign_1'])
            sides = {i['side']: i for i in res['islands']}
            self.assertEqual(set(sides), {'L', 'R', 'C'})
            self.assertEqual(lt.rotation_hint(sides['L']['up']), 0)
            self.assertFalse(sides['L']['mirrored'])
            self.assertEqual(sides['L']['bone'], 'door_dside_f')
            self.assertEqual(lt.rotation_hint(sides['R']['up']), 180)
            self.assertFalse(sides['R']['mirrored'])
            self.assertTrue(sides['C']['horizontal'])
            self.assertEqual(lt.rotation_hint(sides['C']['front']), 0)      # roof: car front = image up
            self.assertLess(sides['L']['front'][0], -0.9)                   # driver side: front points left
            dens = lt.density(res['tris'])
            self.assertAlmostEqual(dens['world_m2'], 2 + 2 + 1, places=3)
            # driver quad: 2 m x 1 m on 0.3 x 0.3 of the texture -> 2048 * sqrt(0.09/2) / 100
            dl = lt.density([t for t in res['tris'] if t['island'] == sides['L']['id']])
            self.assertAlmostEqual(dl[2048], 2048 * (0.09 / 2) ** 0.5 / 100, places=3)

    def test_mirrored_shared_island_and_lod(self):
        with tempfile.TemporaryDirectory() as d:
            high = geometry(0, [driver(0.1, 0.1), passenger(0.1, 0.1, mirrored=True)])
            p = self.build(d, high, medium=geometry(1, [roof()]))
            model = lt.read_model(p)
            res = lt.analyse(model)
            right = [i for i in res['islands'] if i['side'] == 'R'][0]
            self.assertTrue(right['mirrored'])
            res['overlaps'] = lt.overlaps(res['islands'])
            self.assertEqual(len(res['overlaps']), 1)
            ids, sides, differs = res['overlaps'][0]
            self.assertEqual(sides, 'LR')
            self.assertTrue(differs)
            res['lod'] = 'high'
            lods = {k: sum(1 for g in v if g['livery']) for k, v in model['lods'].items() if v}
            text = '\n'.join(lt.report(p, model, res, lods, 2048))
            self.assertIn('镜像', text)
            self.assertIn('med LOD', text)

    def test_cli_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.build(d, geometry(0, [driver(), passenger(), roof()]))
            out = os.path.join(d, 'out', 'tpl')
            r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'livery_template.py'), p, '-o', out,
                                '--size', '256', '--checker'], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for suffix in ('_template.png', '_template.svg', '_checker.png'):
                self.assertTrue(os.path.exists(out + suffix), suffix)
            with open(out + '_template.png', 'rb') as fh:
                head = fh.read(24)
            self.assertEqual(head[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II', head[16:24]), (256, 256))
            with open(out + '_template.svg', encoding='utf-8') as fh:
                svg = fh.read()
            self.assertIn('id="side_L"', svg)
            self.assertIn('door_dside_f', svg)
            self.assertIn('字要转 180°', r.stdout)

    def test_no_livery_material(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.build(d, geometry(1, [roof()]))
            r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'livery_template.py'), p, '--format', 'png'],
                               capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(r.returncode, 1)
            self.assertIn('没找到有涂装层的材质', r.stdout)
            self.assertFalse(os.path.exists(os.path.join(d, 'testcar_template.png')))

    def test_shader_hash_names(self):
        self.assertEqual(lt.shader_name(PAINT3), 'vehicle_paint3')
        self.assertEqual(lt.shader_name('vehicle_paint4'), 'vehicle_paint4')
        self.assertEqual(lt.joaat('vehicle_paint3'), 0xE029BF8E)          # seen in vanilla polgauntlet XML


if __name__ == '__main__':
    unittest.main()
