// Usage: node tests/physics.test.mjs
// Checks assets/ball-lab/physics.js against exact formulas, so the numbers a lesson shows are right.
import * as P from '../assets/ball-lab/physics.js';

const fails = [];
const ok = (name, cond, detail = '') => { console.log((cond ? 'PASS ' : 'FAIL ') + name + (cond ? '' : '  -> ' + detail)); if (!cond) fails.push(name); };
const near = (a, b, tol) => Math.abs(a - b) <= tol;
const run = (sim, seconds, dt = 1 / 240) => { const st = P.createStepper(sim.step, { dt }); for (let t = 0; t < seconds; t += 0.05) st.advance(0.05); return sim; };

// ---------------------------------------------------------------- stepper
{
  let n = 0; const st = P.createStepper(() => n++, { dt: 0.01 });
  st.advance(0.035); st.advance(0.035);
  ok('stepper runs whole steps and carries the remainder', n === 7, n);
  st.advance(5); ok('stepper clamps a long pause (background tab)', n === 17, n);
  n = 0; st.reset(); st.speed = 0.5; st.advance(0.1); ok('slow motion halves the steps', n === 5, n);
}

// ---------------------------------------------------------------- A. bounce
{
  const h0 = 1.5, e = 0.8;
  const sim = run(P.createBounce({ h0, e }), 3);
  const want = P.bounceHeights(h0, e, 4);
  ok('rebound heights = h0·e^(2n)', want.every((h, i) => near(sim.state.peaks[i], h, 1e-6)), JSON.stringify([sim.state.peaks.slice(0, 4), want]));
  const first = Math.sqrt(2 * h0 / P.G);
  const s2 = P.createBounce({ h0, e }); const st = P.createStepper(s2.step, { dt: 1 / 240 });
  while (s2.state.bounces === 0) st.advance(1 / 240);
  ok('first impact at √(2h0/g)', near(s2.state.t, first, 1 / 240), [s2.state.t, first]);
  ok('ball never below the floor', (() => { const b = P.createBounce({ h0, e }); const s = P.createStepper(b.step, { dt: 1 / 60 }); for (let i = 0; i < 600; i++) { s.advance(1 / 60); if (b.state.y < -1e-12) return false; } return true; })());
  const rest = run(P.createBounce({ h0, e }), 12);
  const tRest = P.bounceRestTime(h0, e);
  ok('stops (minRebound) close to the ideal rest time', rest.state.atRest && rest.state.t > tRest, [tRest]);
  const en = rest.energy();
  ok('at rest: all energy in the "lost" store', near(en.lost, en.total, 1e-9) && en.kinetic === 0 && near(en.potential, 0, 1e-12), JSON.stringify(en));
  const mid = P.createBounce({ h0, e, m: 0.6 }); const sm = P.createStepper(mid.step);
  let worst = 0;
  for (let i = 0; i < 200; i++) { sm.advance(0.01); const q = mid.energy(); worst = Math.max(worst, Math.abs(q.kinetic + q.potential + q.lost - q.total)); }
  ok('energy ledger always sums to the start', worst < 1e-9, worst);
  const lostPerBounce = (() => { const b = P.createBounce({ h0, e, m: 1 }); const s = P.createStepper(b.step); while (b.state.bounces < 1) s.advance(0.001); return b.state.lost / (1 * P.G * h0); })();
  ok('first bounce keeps e² of the energy', near(lostPerBounce, 1 - e * e, 1e-9), lostPerBounce);
  ok('e = 1 never stops', P.bounceRestTime(1, 1) === Infinity && !run(P.createBounce({ h0: 1, e: 1 }), 10).state.atRest);
}

// ---------------------------------------------------------------- B. projectile
{
  for (const [v0, angle, h0] of [[10, 45, 0], [8, 30, 2], [12, 70, 0.5], [6, 0, 1.8]]) {
    const a = P.projectileAnalytic({ v0, angle, h0 });
    const sim = run(P.createProjectile({ v0, angle, h0 }), a.tFlight + 0.5);
    ok(`no drag v0=${v0} ${angle}° h0=${h0}: range and time exact`, sim.state.landed && near(sim.state.x, a.range, 1e-3) && near(sim.state.t, a.tFlight, 1e-3), [sim.state.x, a.range]);
    ok(`no drag v0=${v0} ${angle}°: top height`, near(sim.state.top, a.maxHeight, 2e-3), [sim.state.top, a.maxHeight]);
  }
  ok('45° gives the longest range from the ground (no drag)', [30, 40, 50, 60].every((ang) => P.projectileAnalytic({ v0: 10, angle: ang }).range < P.projectileAnalytic({ v0: 10, angle: 45 }).range));
  const plain = run(P.createProjectile({ v0: 20, angle: 45 }), 4), dragged = run(P.createProjectile({ v0: 20, angle: 45, drag: true }), 4);
  ok('drag shortens the range', dragged.state.landed && dragged.state.x < plain.state.x, [dragged.state.x, plain.state.x]);
  const best = [30, 35, 40, 45].map((ang) => [ang, run(P.createProjectile({ v0: 30, angle: ang, drag: true, m: 0.057, radius: 0.033 }), 8).state.x]).sort((p, q) => q[1] - p[1])[0][0];
  ok('with drag the best angle is below 45° (tennis ball, 30 m/s)', best < 45, best);
  const coarse = run(P.createProjectile({ v0: 20, angle: 45, drag: true }), 4, 1 / 60), fine = run(P.createProjectile({ v0: 20, angle: 45, drag: true }), 4, 1 / 960);
  ok('RK4 drag result converges (1/60 s vs 1/960 s within 1 cm)', near(coarse.state.x, fine.state.x, 0.01), [coarse.state.x, fine.state.x]);
  const fall = P.createProjectile({ v0: 0, angle: 0, h0: 200, drag: true, m: 0.6, radius: 0.12 });
  run(fall, 30);
  const vt = Math.sqrt((2 * 0.6 * P.G) / (P.AIR_DENSITY * P.SPHERE_CD * Math.PI * 0.12 ** 2));
  ok('long drop approaches terminal velocity √(2mg/ρC_dA)', Math.abs(fall.state.vy) < vt && Math.abs(fall.state.vy) > 0.85 * vt, [fall.state.vy, vt]);
  const e2 = run(P.createProjectile({ v0: 15, angle: 50, drag: true }), 3).energy();
  ok('drag: energy ledger sums and loss is positive', near(e2.kinetic + e2.potential + e2.lost, e2.total, 1e-9) && e2.lost > 0);
}

// ---------------------------------------------------------------- C. collisions
{
  const el = P.collide1D(1, 2, 1, 0, 1);
  ok('equal masses, elastic: velocities swap', near(el.v1, 0, 1e-12) && near(el.v2, 2, 1e-12));
  const stick = P.collide1D(2, 3, 1, 0, 0);
  ok('perfectly inelastic: common velocity p/(m1+m2)', near(stick.v1, 2, 1e-12) && near(stick.v2, 2, 1e-12));
  let worstP = 0, worstKE = 0, gained = false;
  for (let i = 0; i < 500; i++) {
    const m1 = 0.1 + Math.random() * 5, m2 = 0.1 + Math.random() * 5, u1 = Math.random() * 6 - 1, u2 = Math.random() * 4 - 3, e = Math.random();
    const r = P.collide1D(m1, u1, m2, u2, e);
    worstP = Math.max(worstP, Math.abs(m1 * r.v1 + m2 * r.v2 - (m1 * u1 + m2 * u2)));
    if (r.keLost < -1e-9) gained = true;
    const rel = (r.v2 - r.v1) - (-e * (u2 - u1));
    worstKE = Math.max(worstKE, Math.abs(rel));
  }
  ok('momentum conserved in 500 random collisions', worstP < 1e-9, worstP);
  ok('separation speed = e × approach speed', worstKE < 1e-9, worstKE);
  ok('kinetic energy never increases', !gained);
  const r3 = P.collide1D(5, 1, 0.5, -2, 0.6);
  ok("Newton's third law: impulses equal and opposite", near(5 * (r3.v1 - 1), -r3.impulse, 1e-12));
  const sim = run(P.createCollision({ m1: 2, u1: 1.5, m2: 1, u2: 0, e: 0.5, x1: 0.2, x2: 1.0 }), 2);
  ok('track: contact found exactly, momentum kept', sim.state.hit && near(sim.momentum(), 3, 1e-9) && near(sim.state.hit.t, (1.0 - 0.2 - 0.2) / 1.5, 1e-9), sim.state.hit && sim.state.hit.t);
  const o = P.collide2D({ x: 0, y: 0, vx: 1, vy: 0, m: 1 }, { x: 0.1, y: 0.1, vx: 0, vy: 0, m: 1 }, 1);
  ok('2D equal masses elastic at 45°: paths 90° apart, speed kept', near(o.a.vx * o.b.vx + o.a.vy * o.b.vy, 0, 1e-12) && near(Math.hypot(o.a.vx, o.a.vy) ** 2 + Math.hypot(o.b.vx, o.b.vy) ** 2, 1, 1e-12));
}

// ---------------------------------------------------------------- D. pendulum
{
  ok('small-angle period 2π√(L/g) for L = 1 m ≈ 2.006 s', near(P.pendulumPeriodSmall(1), 2.006, 0.001));
  // exact values: T/T0 = 2K(sin(θ0/2))/π → 1.0174 (30°), 1.0732 (60°), 1.1803 (90°)
  for (const [deg, ratio] of [[30, 1.0174], [60, 1.0732], [90, 1.1803]]) {
    ok(`exact period at ${deg}° is ${ratio}× the small-angle one`, near(P.pendulumPeriod(1, deg) / P.pendulumPeriodSmall(1), ratio, 1e-4), P.pendulumPeriod(1, deg) / P.pendulumPeriodSmall(1));
    const sim = run(P.createPendulum({ L: 1, amplitude: deg }), 9);
    ok(`simulated period at ${deg}° matches the exact one`, near(sim.state.period, P.pendulumPeriod(1, deg), 2e-4), [sim.state.period, P.pendulumPeriod(1, deg)]);
  }
  const heavy = run(P.createPendulum({ L: 0.8, amplitude: 15, m: 5 }), 6), light = run(P.createPendulum({ L: 0.8, amplitude: 15, m: 0.05 }), 6);
  ok('period does not depend on mass', near(heavy.state.period, light.state.period, 1e-9));
  const long = run(P.createPendulum({ L: 1, amplitude: 60 }), 120);
  const q = long.energy();
  ok('RK4 energy drift < 0.01 % after 2 minutes at 60°', Math.abs(q.kinetic + q.potential - q.total) / q.total < 1e-4, (q.kinetic + q.potential - q.total) / q.total);
  const damped = run(P.createPendulum({ L: 1, amplitude: 30, damping: 0.3 }), 20);
  ok('damping moves energy to the lost store', damped.energy().lost > 0.9 * damped.energy().total);
}

// ---------------------------------------------------------------- readouts
ok('fmt: space before unit, fixed decimals, no -0.00', P.fmt(4.905, 'J') === '4.91 J' && P.fmt(-0.001, 'm/s') === '0.00 m/s' && P.fmt(2, 'm/s', 1) === '2.0 m/s');

console.log(fails.length ? `\n${fails.length} failed` : '\nall passed');
process.exit(fails.length ? 1 : 0);
