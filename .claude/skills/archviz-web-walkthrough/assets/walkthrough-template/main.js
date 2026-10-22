// Archviz walkthrough template — three r186, no build step.
// Reads tour data from glTF node extras (Blender Custom Properties):
//   spawn, yaw, hotspot, room, lightmap, lightmapIntensity, collider (or name COL_*), nocollide
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { Octree } from 'three/addons/math/Octree.js';
import { Capsule } from 'three/addons/math/Capsule.js';

const params = new URLSearchParams(location.search);
const MODEL_URL = params.get('model') || './model.glb';
// Decoders: CDN for prototyping. Self-host the same three version before shipping.
const LIBS = 'https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/libs/';

const EYE = 1.6, RADIUS = 0.25, WALK = 1.6, GRAVITY = 30, STEPS = 5, COLLIDE_LAYER = 1;
const COARSE = matchMedia('(pointer: coarse)').matches;

const $ = (id) => document.getElementById(id);
const statusEl = $('status'), roomEl = $('room'), hotspotLayer = $('hotspots');

// ---------- renderer / scene ----------
const renderer = new THREE.WebGLRenderer({ antialias: !COARSE });
renderer.setPixelRatio(Math.min(devicePixelRatio, COARSE ? 1.5 : 2));
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.NeutralToneMapping;
document.body.prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xdfe3e6);
const camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 0.05, 500);
camera.rotation.order = 'YXZ';
const hemi = new THREE.HemisphereLight(0xffffff, 0x8a8170, 1.2); // dimmed to a fill once lightmaps load
scene.add(hemi);

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ---------- loading ----------
const ktx2 = new KTX2Loader().setTranscoderPath(LIBS + 'basis/').detectSupport(renderer);
const draco = new DRACOLoader().setDecoderPath(LIBS + 'draco/gltf/');
const loader = new GLTFLoader().setKTX2Loader(ktx2).setDRACOLoader(draco).setMeshoptDecoder(MeshoptDecoder);

const octree = new Octree();
octree.layers.set(COLLIDE_LAYER);
const player = new Capsule(new THREE.Vector3(), new THREE.Vector3(), RADIUS);
const velocity = new THREE.Vector3();
const spawn = { pos: new THREE.Vector3(), yaw: 0, found: false };
const hotspots = [];   // { el, pos }
const roomMeshes = []; // meshes with a room name (own or inherited)
let floorY = 0, onFloor = false, tween = null, yaw = 0, pitch = 0;

loader.loadAsync(MODEL_URL).then(async (gltf) => {
  const root = gltf.scene;
  scene.add(root);
  root.updateMatrixWorld(true);

  const colliders = [], visual = [], lightmapJobs = [];
  root.traverse((o) => {
    const d = o.userData;
    if (o.isMesh) (d.collider || /^COL_/i.test(o.name) || /^COL_/i.test(o.parent?.name ?? '') ? colliders : visual).push(o);
    if (d.spawn) { spawn.found = true; o.getWorldPosition(spawn.pos); spawn.yaw = THREE.MathUtils.degToRad(Number(d.yaw) || 0); }
    if (d.hotspot) addHotspot(String(d.hotspot), o.getWorldPosition(new THREE.Vector3()));
    if (o.isMesh && inherited(o, 'room')) roomMeshes.push(o);
    if (d.lightmap) lightmapJobs.push(applyLightmap(o, String(d.lightmap), Number(d.lightmapIntensity) || Math.PI));
  });

  // Colliders exist only on the collision layer (never rendered). Without colliders,
  // every visual mesh except `nocollide` ones collides (works, but slower and snaggy).
  if (colliders.length) colliders.forEach((m) => m.layers.set(COLLIDE_LAYER));
  else {
    console.warn('No COL_* / collider meshes: using visual meshes for collision.');
    visual.filter((m) => !inherited(m, 'nocollide')).forEach((m) => m.layers.enable(COLLIDE_LAYER));
  }
  octree.fromGraphNode(root);

  const box = new THREE.Box3().setFromObject(root);
  floorY = box.min.y;
  if (!spawn.found) { console.warn('No spawn extra: starting at the model centre.'); box.getCenter(spawn.pos).setY(floorY); }

  const results = await Promise.allSettled(lightmapJobs);
  if (results.some((r) => r.status === 'fulfilled' && r.value)) hemi.intensity = 0.15;
  results.filter((r) => r.status === 'rejected').forEach((r) => console.warn('Lightmap failed:', r.reason));

  respawn();
  statusEl.classList.add('hidden');
  window.tour = { ready: true, scene, camera, renderer, player, hotspots, teleport, frame }; // readiness/test hook (threejs-testing)
  renderer.setAnimationLoop(frame);
}).catch((err) => {
  statusEl.textContent = 'Could not load ' + MODEL_URL + ' — ' + err.message;
  console.error(err);
});

function inherited(o, key) {
  for (let p = o; p; p = p.parent) if (p.userData[key] !== undefined) return p.userData[key];
  return undefined;
}

// Lightmaps: glTF has no lightmap slot, so they are separate files on UV1 (TEXCOORD_1).
const textureLoader = new THREE.TextureLoader();
async function applyLightmap(obj, url, intensity) {
  const tex = await textureLoader.loadAsync(new URL(url, new URL(MODEL_URL, location.href)).href);
  tex.channel = 1;                       // use uv1
  tex.flipY = false;                     // glTF UV convention
  tex.colorSpace = THREE.SRGBColorSpace; // 8-bit PNG/JPG; use Linear for EXR/HDR (compare with Blender)
  // Intensity π: three.js divides diffuse light by π, so π makes result = albedo × lightmap (measured, r186).
  let applied = false;
  obj.traverse((m) => {
    if (!m.isMesh) return;
    if (!m.geometry.attributes.uv1) { console.warn(m.name, 'has no TEXCOORD_1; lightmap skipped'); return; }
    const mats = Array.isArray(m.material) ? m.material : [m.material];
    const out = mats.map((mat) => {
      const c = mat.clone();             // materials can be shared between rooms with different lightmaps
      c.lightMap = tex; c.lightMapIntensity = intensity;
      return c;
    });
    m.material = Array.isArray(m.material) ? out : out[0];
    applied = true;
  });
  return applied;
}

// ---------- hotspots and room label ----------
function addHotspot(label, pos) {
  const el = document.createElement('button');
  el.className = 'hotspot';
  el.textContent = label;
  el.addEventListener('click', (e) => { e.stopPropagation(); teleport(pos); });
  hotspotLayer.append(el);
  hotspots.push({ el, pos });
}

const _v = new THREE.Vector3();
function updateHotspots() {
  for (const h of hotspots) {
    _v.copy(h.pos).setY(h.pos.y + 1.0).project(camera);
    const dist = camera.position.distanceTo(h.pos);
    const show = _v.z < 1 && Math.abs(_v.x) < 1.1 && Math.abs(_v.y) < 1.1 && dist < 25 && dist > 0.8;
    h.el.style.display = show ? '' : 'none';
    if (show) h.el.style.transform = `translate(${(_v.x + 1) / 2 * innerWidth}px, ${(1 - _v.y) / 2 * innerHeight}px)`;
  }
}

const downRay = new THREE.Raycaster(new THREE.Vector3(), new THREE.Vector3(0, -1, 0), 0, 3);
let roomTimer = 0;
function updateRoom(dt) {
  if ((roomTimer -= dt) > 0) return;
  roomTimer = 0.2;
  downRay.ray.origin.copy(player.start);
  const hit = downRay.intersectObjects(roomMeshes, false)[0];
  roomEl.textContent = hit ? inherited(hit.object, 'room') : '';
}

// ---------- player ----------
function placeAt(feet) {
  player.start.set(feet.x, feet.y + RADIUS + 0.02, feet.z);
  player.end.set(feet.x, feet.y + EYE, feet.z);
  velocity.set(0, 0, 0);
}
function respawn() { placeAt(spawn.pos); yaw = spawn.yaw; pitch = 0; }
function teleport(feet) {
  // While the tween runs it is the only writer of the player position.
  tween = { from: player.start.clone().setY(player.start.y - RADIUS - 0.02), to: feet.clone(), t: 0 };
}

function collide() {
  const hit = octree.capsuleIntersect(player);
  onFloor = false;
  if (!hit) return;
  onFloor = hit.normal.y >= 0.15; // games_fps: slopes up to ~81° are floor, so stair ramps work
  if (!onFloor) velocity.addScaledVector(hit.normal, -hit.normal.dot(velocity));
  if (hit.depth >= 1e-10) player.translate(hit.normal.multiplyScalar(hit.depth));
}

// ---------- input: keyboard + pointer lock ----------
const keys = new Set();
addEventListener('keydown', (e) => {
  keys.add(e.code);
  const n = /^Digit([1-9])$/.exec(e.code); // 1–9 jump to hotspots (buttons can't be clicked while locked)
  if (n && hotspots[n[1] - 1]) teleport(hotspots[n[1] - 1].pos);
});
addEventListener('keyup', (e) => keys.delete(e.code));
addEventListener('blur', () => keys.clear());

const canvas = renderer.domElement;
const look = (dx, dy, k) => {
  yaw -= dx * k;
  pitch = THREE.MathUtils.clamp(pitch - dy * k, -1.45, 1.45);
};
canvas.addEventListener('click', () => {
  if (!COARSE && canvas.requestPointerLock && document.pointerLockElement !== canvas) canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
  $('hint').style.visibility = document.pointerLockElement === canvas ? 'hidden' : '';
});
document.addEventListener('mousemove', (e) => {
  if (document.pointerLockElement === canvas) look(e.movementX, e.movementY, 0.0022);
});

// ---------- input: touch (drag to look + inline joystick) ----------
const stick = { id: null, x: 0, y: 0 };
const stickEl = $('stick'), knob = $('knob');
const capture = (el, id) => { try { el.setPointerCapture(id); } catch { /* synthetic or stale pointer */ } };
stickEl.addEventListener('pointerdown', (e) => { stick.id = e.pointerId; capture(stickEl, e.pointerId); moveStick(e); });
stickEl.addEventListener('pointermove', (e) => { if (e.pointerId === stick.id) moveStick(e); });
const endStick = (e) => {
  if (e.pointerId !== stick.id) return;
  stick.id = null; stick.x = stick.y = 0; knob.style.transform = '';
};
stickEl.addEventListener('pointerup', endStick);
stickEl.addEventListener('pointercancel', endStick);
function moveStick(e) {
  const r = stickEl.getBoundingClientRect(), max = r.width / 2;
  let x = e.clientX - (r.left + max), y = e.clientY - (r.top + max);
  const len = Math.hypot(x, y);
  if (len > max) { x *= max / len; y *= max / len; }
  knob.style.transform = `translate(${x}px, ${y}px)`;
  stick.x = x / max; stick.y = y / max;
}

const drags = new Map();
canvas.addEventListener('pointerdown', (e) => {
  if (e.pointerType === 'mouse' && canvas.requestPointerLock && !COARSE) return; // desktop uses pointer lock
  drags.set(e.pointerId, { x: e.clientX, y: e.clientY });
  capture(canvas, e.pointerId);
});
canvas.addEventListener('pointermove', (e) => {
  const p = drags.get(e.pointerId);
  if (!p) return;
  look(e.clientX - p.x, e.clientY - p.y, 0.005);
  p.x = e.clientX; p.y = e.clientY;
});
const endDrag = (e) => drags.delete(e.pointerId);
canvas.addEventListener('pointerup', endDrag);
canvas.addEventListener('pointercancel', endDrag);

// ---------- loop ----------
const timer = new THREE.Timer(); // THREE.Clock is deprecated in r186
const fwd = new THREE.Vector3(), side = new THREE.Vector3(), wish = new THREE.Vector3();

function frame(time) {
  timer.update(time);
  const dt = Math.min(0.05, timer.getDelta());
  camera.rotation.set(pitch, yaw, 0);

  if (tween) {
    tween.t = Math.min(1, tween.t + dt / 0.6);
    const k = tween.t * tween.t * (3 - 2 * tween.t); // smoothstep
    placeAt(_v.lerpVectors(tween.from, tween.to, k));
    if (tween.t === 1) tween = null;
  } else {
    fwd.set(-Math.sin(yaw), 0, -Math.cos(yaw));
    side.set(-fwd.z, 0, fwd.x);
    wish.set(0, 0, 0);
    if (keys.has('KeyW') || keys.has('ArrowUp')) wish.add(fwd);
    if (keys.has('KeyS') || keys.has('ArrowDown')) wish.sub(fwd);
    if (keys.has('KeyD') || keys.has('ArrowRight')) wish.add(side);
    if (keys.has('KeyA') || keys.has('ArrowLeft')) wish.sub(side);
    wish.addScaledVector(fwd, -stick.y).addScaledVector(side, stick.x);
    if (wish.lengthSq() > 1) wish.normalize();
    const speed = WALK * (keys.has('ShiftLeft') || keys.has('ShiftRight') ? 2 : 1);

    const h = dt / STEPS;
    for (let i = 0; i < STEPS; i++) {
      // Exponential damping (k = 4) with accel 4·speed → terminal speed = speed.
      let damping = Math.exp(-4 * h) - 1;
      if (onFloor) velocity.addScaledVector(wish, 4 * speed * h);
      else { velocity.y -= GRAVITY * h; damping *= 0.1; } // as games_fps: little air drag
      velocity.addScaledVector(velocity, damping);
      player.translate(_v.copy(velocity).multiplyScalar(h));
      collide();
    }
    if (player.start.y < floorY - 10) respawn(); // fell out of the world
  }

  camera.position.copy(player.end);
  updateHotspots();
  updateRoom(dt);
  renderer.render(scene, camera);
}
