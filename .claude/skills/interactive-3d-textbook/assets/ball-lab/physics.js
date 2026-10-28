// Ball physics for lesson pages: bounce, projectile, collision, pendulum.
// Pure ES module (no DOM, no three.js) so the 2D page, the 3D page and the Node tests share one model.
// SI units throughout: metres, seconds, kilograms, joules. Angles in the API are degrees.
// Every simulation keeps an energy ledger whose stores always add up to the starting energy,
// so energy bars, glow and readouts can never disagree with each other.

export const G = 9.81;            // m/s², standard gravity rounded the way school textbooks use it
export const AIR_DENSITY = 1.2;   // kg/m³, air near sea level at ~20 °C
export const SPHERE_CD = 0.47;    // drag coefficient of a smooth sphere, roughly 1e3 < Re < 2e5

const rad = (deg) => (deg * Math.PI) / 180;

// ------------------------------------------------------------------ fixed time step
/**
 * Runs `step(dt)` at a fixed rate however fast the browser draws (Fiedler, "Fix Your Timestep!").
 * `speed` < 1 is slow motion (label it on screen). Frame gaps are clamped so a background tab
 * doesn't fast-forward the experiment when it comes back.
 */
export function createStepper(step, { dt = 1 / 240, maxFrame = 0.1 } = {}) {
  let acc = 0;
  return {
    dt,
    speed: 1,
    advance(frameSeconds) {
      acc += Math.min(Math.max(frameSeconds, 0), maxFrame) * this.speed;
      let n = 0;
      while (acc >= dt - 1e-9) { step(dt); acc -= dt; n++; }   // tolerance: 0.05 / 0.01 is 4.999… in floating point
      return { steps: n, alpha: Math.max(acc, 0) / dt };   // alpha: how far between the last two states, for smooth drawing
    },
    reset() { acc = 0; }
  };
}

// ------------------------------------------------------------------ A. bouncing ball
/** Rebound heights h0·e^(2n) for n = 1..count. */
export const bounceHeights = (h0, e, count) => Array.from({ length: count }, (_, i) => h0 * e ** (2 * (i + 1)));
/** Time until the ball would come to rest in the ideal model: √(2h0/g)·(1+e)/(1−e). Infinite for e = 1. */
export const bounceRestTime = (h0, e, g = G) => (e >= 1 ? Infinity : Math.sqrt((2 * h0) / g) * (1 + e) / (1 - e));

/**
 * Ball dropped from rest, height measured from the floor to the bottom of the ball.
 * Event-driven: inside each step the exact contact time is solved, so no bounce is missed
 * and the ball never sinks into the floor. The ideal model has infinitely many bounces before
 * `bounceRestTime`; we stop when a rebound would rise less than `minRebound` (default 1 mm).
 */
export function createBounce({ h0 = 1.5, e = 0.75, m = 0.6, g = G, minRebound = 0.001 } = {}) {
  const s = { t: 0, y: h0, v: 0, bounces: 0, atRest: false, peaks: [], lost: 0 };
  const E0 = m * g * h0;
  const vMin = Math.sqrt(2 * g * minRebound);

  function step(dt) {
    if (s.atRest) { s.t += dt; return; }
    let left = dt;
    while (left > 0) {
      // time to reach the floor from (y, v) under gravity: y + v·t − ½g·t² = 0
      const tHit = (s.v + Math.sqrt(s.v * s.v + 2 * g * s.y)) / g;
      if (tHit > left) {
        const vEnd = s.v - g * left;
        if (s.v > 0 && vEnd <= 0) s.peaks.push(s.y + (s.v * s.v) / (2 * g));   // passed a top
        s.y += s.v * left - 0.5 * g * left * left;
        s.v = vEnd;
        s.t += left;
        return;
      }
      s.t += tHit;
      left -= tHit;
      const vImpact = s.v - g * tHit;                 // negative, downwards
      const vOut = -e * vImpact;
      s.lost += 0.5 * m * (vImpact * vImpact - vOut * vOut);   // to heat, sound and the floor
      s.y = 0;
      s.bounces++;
      if (vOut < vMin) {
        s.lost += 0.5 * m * vOut * vOut;
        s.v = 0; s.atRest = true; s.t += left; return;
      }
      s.v = vOut;
    }
  }

  return {
    state: s,
    step,
    energy() {
      const ke = 0.5 * m * s.v * s.v, pe = m * g * s.y;
      return { total: E0, kinetic: ke, potential: pe, lost: E0 - ke - pe };   // lost from the ledger, so the sum is exact
    }
  };
}

// ------------------------------------------------------------------ B. projectile
/** No-drag results for a launch from height h0 (m) at v0 (m/s) and angle (degrees) onto flat ground. */
export function projectileAnalytic({ v0, angle, h0 = 0, g = G }) {
  const vx = v0 * Math.cos(rad(angle)), vy = v0 * Math.sin(rad(angle));
  const tFlight = (vy + Math.sqrt(vy * vy + 2 * g * h0)) / g;
  return { tFlight, range: vx * tFlight, maxHeight: h0 + (vy > 0 ? (vy * vy) / (2 * g) : 0), tTop: Math.max(vy / g, 0) };
}

/**
 * Projectile with optional quadratic air drag F = ½ρC_dA·v² opposite the velocity.
 * Without drag the position is the exact formula; with drag it is RK4 at the stepper's dt.
 * The landing point is found by interpolating the step that crossed y = 0.
 */
export function createProjectile({ v0 = 8, angle = 45, h0 = 0, g = G, m = 0.6, radius = 0.12, drag = false,
  rho = AIR_DENSITY, cd = SPHERE_CD } = {}) {
  const k = drag ? (0.5 * rho * cd * Math.PI * radius * radius) / m : 0;   // drag acceleration = k·|v|·v
  const s = { t: 0, x: 0, y: h0, vx: v0 * Math.cos(rad(angle)), vy: v0 * Math.sin(rad(angle)), landed: false, trail: [[0, h0]], top: h0 };
  const E0 = 0.5 * m * v0 * v0 + m * g * h0;
  const start = { ...s };

  const acc = (vx, vy) => { const sp = Math.hypot(vx, vy); return [-k * sp * vx, -g - k * sp * vy]; };

  function step(dt) {
    if (s.landed) return;
    const prev = { x: s.x, y: s.y, vx: s.vx, vy: s.vy, t: s.t };
    if (!drag) {
      const t = s.t + dt;
      s.x = start.vx * t;
      s.y = h0 + start.vy * t - 0.5 * g * t * t;
      s.vx = start.vx; s.vy = start.vy - g * t; s.t = t;
    } else {
      const f = (x, y, vx, vy) => [vx, vy, ...acc(vx, vy)];
      const k1 = f(s.x, s.y, s.vx, s.vy);
      const k2 = f(s.x + k1[0] * dt / 2, s.y + k1[1] * dt / 2, s.vx + k1[2] * dt / 2, s.vy + k1[3] * dt / 2);
      const k3 = f(s.x + k2[0] * dt / 2, s.y + k2[1] * dt / 2, s.vx + k2[2] * dt / 2, s.vy + k2[3] * dt / 2);
      const k4 = f(s.x + k3[0] * dt, s.y + k3[1] * dt, s.vx + k3[2] * dt, s.vy + k3[3] * dt);
      const d = (i) => (dt / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
      s.x += d(0); s.y += d(1); s.vx += d(2); s.vy += d(3); s.t += dt;
    }
    s.top = Math.max(s.top, s.y);
    if (s.y <= 0 && s.t > 0) {
      const f = prev.y / (prev.y - s.y);              // fraction of the step before touching the ground
      s.x = prev.x + (s.x - prev.x) * f; s.t = prev.t + dt * f;
      s.vx = prev.vx + (s.vx - prev.vx) * f; s.vy = prev.vy + (s.vy - prev.vy) * f;
      s.y = 0; s.landed = true;
    }
    s.trail.push([s.x, s.y]);
  }

  return {
    state: s,
    step,
    energy() {
      const ke = 0.5 * m * (s.vx * s.vx + s.vy * s.vy), pe = m * g * s.y;
      return { total: E0, kinetic: ke, potential: pe, lost: E0 - ke - pe };   // lost = work done by drag
    }
  };
}

/**
 * Launch speed needed to pass through a point dx ahead and dy higher (no drag):
 * v² = g·dx² / (2cos²θ·(dx·tanθ − dy)). Infinity when the angle can't reach it.
 */
export function speedToHit(dx, dy, angle, g = G) {
  const th = rad(angle), d = dx * Math.tan(th) - dy;
  return d <= 0 ? Infinity : Math.sqrt((g * dx * dx) / (2 * Math.cos(th) ** 2 * d));
}
/** The launch angle that needs the least speed to reach that point: 45° + half the elevation angle (Brancazio). */
export const easiestAngle = (dx, dy) => 45 + (Math.atan2(dy, dx) * 180) / Math.PI / 2;

// ------------------------------------------------------------------ C. collisions
/**
 * Head-on collision along one line. e = 1 elastic, e = 0 the balls stick together.
 * Returns velocities after, the impulse on ball 2 (equal and opposite on ball 1) and kinetic energy.
 */
export function collide1D(m1, u1, m2, u2, e = 1) {
  const p = m1 * u1 + m2 * u2;
  const v1 = (p + m2 * e * (u2 - u1)) / (m1 + m2);
  const v2 = (p + m1 * e * (u1 - u2)) / (m1 + m2);
  const keBefore = 0.5 * m1 * u1 * u1 + 0.5 * m2 * u2 * u2;
  const keAfter = 0.5 * m1 * v1 * v1 + 0.5 * m2 * v2 * v2;
  return { v1, v2, impulse: m2 * (v2 - u2), momentum: p, keBefore, keAfter, keLost: keBefore - keAfter };
}

/** Oblique collision of two smooth spheres: only the velocity along the line of centres changes. */
export function collide2D(a, b, e = 1) {
  const nx = b.x - a.x, ny = b.y - a.y, d = Math.hypot(nx, ny) || 1;
  const ux = nx / d, uy = ny / d;
  const ua = a.vx * ux + a.vy * uy, ub = b.vx * ux + b.vy * uy;
  if (ua - ub <= 0) return null;                       // already separating
  const r = collide1D(a.m, ua, b.m, ub, e);
  return {
    a: { vx: a.vx + (r.v1 - ua) * ux, vy: a.vy + (r.v1 - ua) * uy },
    b: { vx: b.vx + (r.v2 - ub) * ux, vy: b.vy + (r.v2 - ub) * uy },
    impulse: r.impulse
  };
}

/**
 * Two balls on a straight track (positions are centres, metres). Constant velocity until contact,
 * contact time solved exactly, then collide1D. Records the moment of impact for the "prove" step.
 */
export function createCollision({ m1 = 1, u1 = 2, m2 = 1, u2 = 0, e = 1, r1 = 0.1, r2 = 0.1, x1 = 0.3, x2 = 1.2 } = {}) {
  const s = { t: 0, x1, x2, v1: u1, v2: u2, hit: null };
  const E0 = 0.5 * m1 * u1 * u1 + 0.5 * m2 * u2 * u2;
  function step(dt) {
    let left = dt;
    if (!s.hit) {
      const gap = s.x2 - s.x1 - r1 - r2, closing = s.v1 - s.v2;
      if (closing > 0 && gap / closing <= left) {
        const tc = gap / closing;
        s.x1 += s.v1 * tc; s.x2 += s.v2 * tc; s.t += tc; left -= tc;
        const r = collide1D(m1, s.v1, m2, s.v2, e);
        s.hit = { t: s.t, u1: s.v1, u2: s.v2, ...r };
        s.v1 = r.v1; s.v2 = r.v2;
      }
    }
    s.x1 += s.v1 * left; s.x2 += s.v2 * left; s.t += left;
  }
  return {
    state: s,
    step,
    momentum: () => m1 * s.v1 + m2 * s.v2,
    energy() {
      const ke = 0.5 * m1 * s.v1 * s.v1 + 0.5 * m2 * s.v2 * s.v2;
      return { total: E0, kinetic: ke, potential: 0, lost: E0 - ke };   // lost: deformation, heat, sound
    }
  };
}

// ------------------------------------------------------------------ D. pendulum
/** Arithmetic–geometric mean, for the exact pendulum period. */
export function agm(a, b) {
  for (let i = 0; i < 30 && Math.abs(a - b) > 1e-15 * a; i++) [a, b] = [(a + b) / 2, Math.sqrt(a * b)];
  return a;
}
/** Small-angle period 2π√(L/g): independent of mass and amplitude. */
export const pendulumPeriodSmall = (L, g = G) => 2 * Math.PI * Math.sqrt(L / g);
/** Exact period for amplitude θ0 (degrees): 2π√(L/g) / AGM(1, cos(θ0/2)). */
export const pendulumPeriod = (L, amplitude, g = G) => pendulumPeriodSmall(L, g) / agm(1, Math.cos(rad(amplitude) / 2));

/**
 * Simple pendulum (point mass on a light rod), full nonlinear equation θ'' = −(g/L)·sin θ − b·θ'.
 * RK4 at the stepper's dt keeps energy drift far below what a readout shows. Records each time
 * the bob swings back through the centre so the page can show the measured period.
 */
export function createPendulum({ L = 1, amplitude = 20, m = 0.5, g = G, damping = 0 } = {}) {
  const s = { t: 0, theta: rad(amplitude), omega: 0, crossings: [], period: null };
  const E0 = m * g * L * (1 - Math.cos(rad(amplitude)));
  const f = (th, om) => [om, -(g / L) * Math.sin(th) - damping * om];
  function step(dt) {
    const th0 = s.theta, t0 = s.t;
    const k1 = f(s.theta, s.omega);
    const k2 = f(s.theta + k1[0] * dt / 2, s.omega + k1[1] * dt / 2);
    const k3 = f(s.theta + k2[0] * dt / 2, s.omega + k2[1] * dt / 2);
    const k4 = f(s.theta + k3[0] * dt, s.omega + k3[1] * dt);
    s.theta += (dt / 6) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]);
    s.omega += (dt / 6) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]);
    s.t += dt;
    if (th0 > 0 && s.theta <= 0) {                     // crossing the centre moving one way: one full period apart
      const tc = t0 + dt * th0 / (th0 - s.theta);
      s.crossings.push(tc);
      if (s.crossings.length >= 2) s.period = tc - s.crossings[s.crossings.length - 2];
    }
  }
  return {
    state: s,
    step,
    position: () => ({ x: L * Math.sin(s.theta), y: -L * Math.cos(s.theta) }),   // bob, pivot at the origin
    energy() {
      const ke = 0.5 * m * (L * s.omega) ** 2, pe = m * g * L * (1 - Math.cos(s.theta));
      return { total: E0, kinetic: ke, potential: pe, lost: Math.max(E0 - ke - pe, 0) };
    }
  };
}

// ------------------------------------------------------------------ readouts
/** SI readout with a space before the unit and fixed decimals, e.g. fmt(4.905, 'J') → "4.91 J". */
export function fmt(value, unit, decimals = 2) {
  const v = Math.abs(value) < 0.5 * 10 ** -decimals ? 0 : value;   // never show "-0.00"
  return `${v.toFixed(decimals)}${unit ? ' ' + unit : ''}`;
}
