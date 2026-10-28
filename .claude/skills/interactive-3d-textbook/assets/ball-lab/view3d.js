// 3D view: an open book on a desk; the diagram rises off the page as ink line-art 3D.
// Draws the same primitives as view2d.js. Recipe from SKILL.md / references/ink-rendering.md:
// WebGLRenderer, NoToneMapping, half-float composer, depth+normal Sobel ink, bloom threshold 1.0
// composited as a tint over the paper, glow driven by the energy share, render on demand.
import * as THREE from 'three';
import { EffectComposer, RenderPass, NormalPass, EffectPass, BloomEffect, Effect, EffectAttribute } from 'postprocessing';
import { STORE_COLOR } from './view2d.js';

const PAPER = new THREE.Color('#fbf8f1');   // near-white page; stays ≤ 1.0 so it never blooms

const inkFrag = /* glsl */ `
uniform sampler2D tNormal;
uniform sampler2D tBloom;
uniform float thickness;
float vz(vec2 uv) { return -getViewZ(readDepth(uv)); }
vec3 nrm(vec2 uv) { return texture2D(tNormal, uv).xyz * 2.0 - 1.0; }
void mainImage(const in vec4 inputColor, const in vec2 uv, const in float depth, out vec4 outputColor) {
  vec2 t = texelSize * thickness;
  float d[9]; vec3 n[9]; int i = 0;
  for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
    vec2 o = uv + vec2(float(x), float(y)) * t; d[i] = vz(o); n[i] = nrm(o); i++;
  }
  // Sobel on linear depth (relative, so distance doesn't change line weight) and on normals
  float c = max(d[4], 1e-3);
  float gx = (d[2] + 2.0*d[5] + d[8]) - (d[0] + 2.0*d[3] + d[6]);
  float gy = (d[6] + 2.0*d[7] + d[8]) - (d[0] + 2.0*d[1] + d[2]);
  vec3 nx = (n[2] + 2.0*n[5] + n[8]) - (n[0] + 2.0*n[3] + n[6]);
  vec3 ny = (n[6] + 2.0*n[7] + n[8]) - (n[0] + 2.0*n[1] + n[2]);
  float edge = smoothstep(0.55, 1.1, length(vec2(gx, gy)) / c * 18.0 + length(nx) + length(ny));
  vec3 base = inputColor.rgb;
  float energy = clamp(max(max(base.r, base.g), base.b) - 1.0, 0.0, 1.0);   // HDR pixels = glowing store: no ink over them
  vec3 col = mix(min(base, vec3(1.0)), vec3(0.07), edge * (1.0 - energy));
  vec3 b = texture2D(tBloom, uv).rgb;
  float bl = max(max(b.r, b.g), b.b);
  col = mix(col, b / max(bl, 1e-4), clamp(bl, 0.0, 1.0) * 0.8);             // glow as a tint, visible on white paper
  outputColor = vec4(col, inputColor.a);
}`;

class InkEffect extends Effect {
  constructor(normalTexture, bloomTexture) {
    super('InkEffect', inkFrag, {
      attributes: EffectAttribute.DEPTH,
      uniforms: new Map([['tNormal', new THREE.Uniform(normalTexture)], ['tBloom', new THREE.Uniform(bloomTexture)], ['thickness', new THREE.Uniform(1)]])
    });
  }
}

export async function createView3D(host) {
  const canvas = document.createElement('canvas');
  canvas.className = 'diagram-3d';
  canvas.setAttribute('aria-hidden', 'true');                // the host carries the live text alternative
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, stencil: false, depth: false, powerPreference: 'low-power' });
  if (!renderer.getContext()) throw new Error('webgl');
  host.replaceChildren(canvas);
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const touch = matchMedia('(pointer: coarse)').matches;
  let pixelRatio = Math.min(devicePixelRatio, touch ? 1.5 : 2);
  renderer.setPixelRatio(pixelRatio);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#d9cbb3');               // desk mat
  const camera = new THREE.PerspectiveCamera(32, 16 / 9, 0.1, 50);
  const views = [[0, 2.4, 6.4], [-3.8, 2.2, 5.4], [3.8, 2.2, 5.4]];
  let viewIndex = 0;
  const aim = new THREE.Vector3(0, 0.95, 0);
  const placeCamera = () => { camera.position.set(...views[viewIndex]); camera.lookAt(aim); };
  placeCamera();

  // No lights: every surface is unlit, so paper renders exactly its colour (lit Lambert paper read ~#E0DFDA, grey)
  // and the depth+normal ink lines carry the form, as in a line-art textbook.

  // ---------------------------------------------------------------- the book (softly lit, never moves)
  const pageMat = new THREE.MeshBasicMaterial({ color: PAPER });
  const coverMat = new THREE.MeshBasicMaterial({ color: '#3d5a4a' });
  const book = new THREE.Group();
  for (const side of [-1, 1]) {
    const cover = new THREE.Mesh(new THREE.BoxGeometry(3.3, 0.04, 2.5), coverMat);
    cover.position.set(side * 1.66, 0.02, 0); book.add(cover);
    const pages = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.12, 2.4), pageMat);
    pages.position.set(side * 1.61, 0.1, 0); book.add(pages);
  }
  scene.add(book);

  // ---------------------------------------------------------------- the diagram (all inked, rises off the page)
  const diagram = new THREE.Group();
  diagram.position.set(0, 0.2, 0.2);
  scene.add(diagram);
  const ink = new THREE.MeshBasicMaterial({ color: PAPER });
  const dark = new THREE.MeshBasicMaterial({ color: '#1a1a1a' });
  const floor = new THREE.Mesh(new THREE.BoxGeometry(1, 0.06, 0.8), ink);   // the pop-up card the experiment stands on
  diagram.add(floor);
  const pools = { ball: [], marker: [], rod: [], arrow: [], trail: [], heat: null };
  // glow material: paper-white when the store is empty, the store colour pushed above 1.0 (HDR) when it holds energy
  const glowMat = (store) => Object.assign(new THREE.MeshBasicMaterial({ color: PAPER }), { userData: { store } });
  pools.heat = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.01, 40), glowMat('lost'));
  diagram.add(pools.heat);
  const get = (kind, make) => (i) => { while (pools[kind].length <= i) { const o = make(); pools[kind].push(o); diagram.add(o); } return pools[kind][i]; };
  const ball = get('ball', () => new THREE.Mesh(new THREE.SphereGeometry(1, 40, 24), glowMat('kinetic')));
  const marker = get('marker', () => new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1, 16), glowMat('potential')));
  const rod = get('rod', () => new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 1, 8), dark));
  const arrow = get('arrow', () => new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 1, 0x1a1a1a, 0.12, 0.07));
  const trail = get('trail', () => new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: '#1a1a1a' })));

  // ---------------------------------------------------------------- post: half-float, ink + bloom tint, no tone mapping
  const composer = new EffectComposer(renderer, { frameBufferType: THREE.HalfFloatType });
  composer.addPass(new RenderPass(scene, camera));
  const normalPass = new NormalPass(scene, camera);
  composer.addPass(normalPass);
  const bloom = new BloomEffect({ mipmapBlur: true, luminanceThreshold: 1.0, luminanceSmoothing: 0.03, intensity: 1.4 });
  bloom.blendMode.opacity.value = 0;                          // its own SCREEN blend is invisible on white paper
  const inkEffect = new InkEffect(normalPass.texture, bloom.texture);
  const lineWeight = () => { inkEffect.uniforms.get('thickness').value = 1.4 * renderer.getPixelRatio(); };   // CSS-pixel weight at any DPR
  lineWeight();
  composer.addPass(new EffectPass(camera, bloom, inkEffect));

  // ---------------------------------------------------------------- render on demand
  let dirty = true, running = 0, rise = 1, riseFrom = 0, frameMs = 16;
  const invalidate = () => { dirty = true; };
  function loop(time) {
    if (rise < 1) { rise = Math.min(1, (time - riseFrom) / 600); diagram.scale.y = 0.02 + 0.98 * (1 - (1 - rise) ** 3); dirty = true; if (rise >= 1) running--; }
    if (!dirty && running === 0) return;                      // idle: no GPU work
    dirty = false;
    const t0 = performance.now();
    composer.render();
    frameMs = 0.9 * frameMs + 0.1 * (performance.now() - t0);
    if (touch && frameMs > 25 && pixelRatio > 1.25) { pixelRatio = 1.25; renderer.setPixelRatio(pixelRatio); lineWeight(); resize(); }
  }
  renderer.setAnimationLoop(loop);
  const onVis = () => { renderer.setAnimationLoop(document.hidden ? null : loop); if (!document.hidden) invalidate(); };
  document.addEventListener('visibilitychange', onVis);
  function resize() {
    const r = host.getBoundingClientRect();
    const w = Math.max(320, r.width), h = Math.max(220, r.height);
    renderer.setSize(w, h, false); composer.setSize(w, h);
    camera.aspect = w / h; camera.updateProjectionMatrix(); invalidate();
  }
  const ro = new ResizeObserver(resize); ro.observe(host); resize();

  let scale = 1, cx = 0, last = null;
  return {
    kind: '3d',
    renderer,
    nextAngle() { viewIndex = (viewIndex + 1) % views.length; placeCamera(); invalidate(); },
    setLesson(lesson, { animate }) {
      if (animate) { rise = 0; riseFrom = performance.now(); running++; diagram.scale.y = 0.02; } else { rise = 1; diagram.scale.y = 1; }
      invalidate();
    },
    draw(f) {
      last = f;
      const b = f.bounds;
      scale = Math.min(4.6 / (b.x1 - b.x0), 1.9 / (b.y1 - b.y0));   // fit the experiment across the open book
      cx = (b.x0 + b.x1) / 2;
      floor.scale.set((b.x1 - b.x0) * scale + 0.2, 1, 1);
      floor.position.set(0, -0.03, 0);
      floor.visible = f.floor != null;
      const X = (x) => (x - cx) * scale, Y = (y) => (y - (f.floor ?? 0)) * scale;
      const emissive = (m, g) => {                         // no glow when the store reads 0
        if (g > 0) m.color.set(STORE_COLOR[m.userData.store]).multiplyScalar(1.5 + 4 * g); else m.color.copy(PAPER);
      };
      f.balls.forEach((bd, i) => {
        const m = ball(i); m.visible = true;
        m.position.set(X(bd.x), Y(bd.y), (bd.z || 0) * scale); m.scale.setScalar(Math.max(bd.r * scale, 0.05));
        m.material.userData.store = bd.store || 'kinetic'; emissive(m.material, f.glow[bd.store || 'kinetic'] || 0);
      });
      pools.ball.slice(f.balls.length).forEach((m) => { m.visible = false; });
      (f.markers || []).forEach((md, i) => {
        const m = marker(i); m.visible = true;
        const h = Math.max((md.y1 - md.y0) * scale, 0.001);
        m.scale.set(1, h, 1); m.position.set(X(md.x), Y(md.y0) + h / 2, -0.25); emissive(m.material, f.glow[md.store] || 0);
      });
      pools.marker.slice((f.markers || []).length).forEach((m) => { m.visible = false; });
      (f.rods || []).forEach((rd, i) => {
        const m = rod(i); m.visible = true;
        const a = new THREE.Vector3(X(rd.x1), Y(rd.y1), 0), b = new THREE.Vector3(X(rd.x2), Y(rd.y2), 0);
        m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(1, a.distanceTo(b), 1);
        m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
      });
      pools.rod.slice((f.rods || []).length).forEach((m) => { m.visible = false; });
      (f.arrows || []).forEach((ad, i) => {
        const a = arrow(i); a.visible = true;
        const v = new THREE.Vector3(ad.dx * scale, ad.dy * scale, 0), len = v.length();
        a.position.set(X(ad.x), Y(ad.y), 0.05); a.setDirection(v.normalize()); a.setLength(Math.max(len, 0.02), Math.min(0.12, len * 0.4), 0.07);
      });
      pools.arrow.slice((f.arrows || []).length).forEach((a) => { a.visible = false; });
      (f.trails || []).forEach((tr, i) => {
        const l = trail(i); l.visible = true;
        // r170's setFromPoints reuses the old buffer and reads past the end when the point count shrinks: rebuild instead
        l.geometry.dispose();
        l.geometry = new THREE.BufferGeometry().setFromPoints(tr.points.map(([x, y]) => new THREE.Vector3(X(x), Y(y), (tr.z || 0) * scale)));
      });
      pools.trail.slice((f.trails || []).length).forEach((l) => { l.visible = false; });
      pools.heat.visible = f.floor != null && (f.glow.lost || 0) > 0;
      pools.heat.position.set(X(f.heatX ?? 0), 0.006, 0);
      pools.heat.scale.setScalar(0.4 + 0.6 * (f.glow.lost || 0));
      emissive(pools.heat.material, f.glow.lost || 0);
      invalidate();
    },
    redraw() { if (last) this.draw(last); },
    destroy() {
      renderer.setAnimationLoop(null);
      document.removeEventListener('visibilitychange', onVis);
      ro.disconnect(); composer.dispose(); renderer.dispose(); host.replaceChildren();
    }
  };
}
