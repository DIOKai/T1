# Ball experiments: physics, numerics, misconceptions and a ready template

Read this before building any lesson with a moving ball: bouncing, projectile/throwing, collisions, pendulum (the same rules cover carts, skaters and blocks). The working template is `assets/ball-lab/`; start from it instead of writing physics from scratch.

Research date: 2026-10-28. Tags: **[S]** confirmed from a search-result summary of the page (the page itself could not be opened from the build machine), **[S-2nd]** only a secondary source, **[D]** derived or computed here and checked by `tests/physics.test.mjs`, **UNVERIFIED** not confirmed.

Contents: 0 Template · 1 Models and formulas · 2 Numerics · 3 Misconceptions (distractors) · 4 What good simulations show · 5 2D or 3D · Sources

---

## 0. The template (`assets/ball-lab/`)

| File | What it is |
|---|---|
| `physics.js` | Pure ES module, no DOM: fixed-step stepper, `createBounce`, `createProjectile` (optional quadratic drag), `collide1D` / `collide2D` / `createCollision`, `createPendulum` (full nonlinear), exact helpers (`bounceHeights`, `bounceRestTime`, `projectileAnalytic`, `pendulumPeriod` via AGM), `fmt` for SI readouts. Every sim has `energy()` returning `{total, kinetic, potential, lost}` that always sums to the start energy. |
| `lessons.js` | Five lessons (bounce, thrown vs dropped, basketball free throw, collision, pendulum), zh + en: hook, prediction from sourced misconceptions, ≤3 controls then "explore more", explanation built from the student's own run, stamp, "what this model ignores", 3-item quiz, teacher notes. |
| `loop.js` | Predict (locks) → test → flap → stamp for completing the loop (right or wrong), quiz, one state driving every view, readout, bar, graph and the canvas description in the same frame, polite live region, `?debug`-only test hook. |
| `view2d.js` | Ink-on-paper SVG view. Light, prints well, and is the fallback when WebGL fails. |
| `view3d.js` | Book-on-desk 3D view following SKILL.md: WebGLRenderer, `NoToneMapping`, half-float composer, depth+normal Sobel ink, bloom threshold 1.0 composited as a tint, glow colour scaled by the energy share, render on demand, `visibilitychange`. Unlit (`MeshBasicMaterial`) surfaces so blank paper renders exactly its colour; glow = store colour × (1.5 + 4·share), so it exceeds 1.0 only while the store holds energy. |
| `lesson.html`, `styles.css`, `main.js` | Page shell, 2D/3D toggle (`?view=3d`), language toggle, import map pinned to three 0.170.0 + postprocessing 6.36.4. |

Both views draw the same primitives returned by `lesson.frame(sim, params)` (balls, markers, rods, trails, arrows, floor, in metres), so 2D and 3D can never disagree. A ball or marker glows by its `store` (`kinetic`, `potential`, `lost`); give decorative balls (strobe ghosts, labels) `store: 'none'` and they never glow. Readout values may be plain strings or `{zh, en}` words. To add an experiment, add a lesson object; you normally don't touch the views.

Checks: `node tests/physics.test.mjs` (exact-formula checks), `python scripts/check_lesson.py assets/ball-lab`, `node tests/ball-lab.e2e.cjs <dir with three + postprocessing in node_modules> <shots>` (browser checks in 2D and 3D, CDN routed to local packages, phone layout after the whole loop).

---

## 1. Models and formulas

### Bouncing ball
- Coefficient of restitution e = rebound speed / impact speed. Rebound heights h_n = h₀·e²ⁿ; each bounce keeps **e²** of the kinetic energy **[D]**.
- Time until rest in the ideal model: t = √(2h₀/g)·(1+e)/(1−e) **[S]** (LibreTexts, Tatum §5.2). h₀ = 1 m: 3.16 s at e = 0.75, 8.58 s at e = 0.9 **[D]**.
- The ideal model bounces **infinitely often in finite time** (Zeno). Simulations stop it with a threshold: here a rebound below 1 mm counts as rest (the threshold value is a design choice, not from a source) **[S]** (MathWorks/Ptolemy "Life after Zeno").
- Real e (back-calculated from competition specs) **[D]**: basketball (FIBA, 1800 mm drop → 1200–1400 mm, top of ball) ≈ 0.73–0.80 **[S-2nd]**; tennis (ITF, 254 cm → 135–147 cm) ≈ 0.73–0.76 **[S]**; table tennis (305 mm → 240–260 mm) ≈ 0.89–0.93 **[S-2nd]**; superball ≈ 0.85–0.9 **[S-2nd]**.

### Projectile
- No drag, flat ground: R = v₀² sin 2θ / g, best angle 45°. To pass through a point dx ahead and dy higher: v² = g·dx²/(2cos²θ(dx·tanθ − dy)); the angle needing the least speed is 45° + ½·atan(dy/dx) — a free throw (release 2.0 m, rim 3.05 m, 4.2 m away) gives 52.0° and 7.21 m/s **[D]**, matching Brancazio, *Am. J. Phys.* 49, 356 (1981) **[S]**. Template: `speedToHit`, `easiestAngle`, lesson `shot` (rim 3.05 m, inner diameter 45.7 cm per FIBA **[S-2nd]**). From launch height h the best angle satisfies sin θ* = v₀/√(2(v₀²+gh)) (8 m/s from 2 m → 38.2°) **[D]**. Horizontal and vertical motion are independent: fall time from h is √(2h/g) whatever the sideways speed **[S]** (OpenStax UP1 §4.3).
- Air drag on a ball is **quadratic**: F = ½ρC_dAv² (ρ = 1.2 kg/m³ room air, 1.225 ISA; smooth sphere C_d ≈ 0.47 for 10³ < Re < 2×10⁵, drag crisis near 2–3.5×10⁵) **[S]**. Quadratic/linear drag ratio ≈ Re/48, so linear drag is wrong for balls in air **[S]** (Taylor problem 2.3). Terminal speed √(2mg/ρC_dA): basketball ≈ 20–21 m/s, tennis ≈ 24 m/s, table tennis ≈ 8.6 m/s **[D]**. With drag the best angle drops below 45° (tennis ball at 30 m/s ≈ 39.5°) **[D]**.

### Collisions
- 1D with restitution: v₁ = (p + m₂e(u₂−u₁))/(m₁+m₂), v₂ = (p + m₁e(u₁−u₂))/(m₁+m₂); e = 1 elastic, e = 0 stick together. Momentum always conserved; KE lost = ½μ(1−e²)(u₁−u₂)² with μ = m₁m₂/(m₁+m₂) **[D]** (OpenStax UP1 §9.4 **[S]**).
- Spheres in 2D: only the velocity component along the line of centres changes; impulse j = (1+e)·(closing speed along n)/(1/m₁+1/m₂), applied only while approaching **[D]**.
- Impulses on the two balls are equal and opposite at every instant (that *is* Newton's third law; momentum conservation follows from it).

### Pendulum
- Small angle: T₀ = 2π√(L/g), independent of mass. Exact: T = T₀ / AGM(1, cos(θ₀/2)) **[S]** (av8n). Longer than T₀ by 0.93 % at 22°, 1.7 % at 30°, 7.3 % at 60°, 18.0 % at 90° **[D]** (HyperPhysics: "<1 % below 22°" **[S]**).
- Damped: ω = √(ω₀² − (b/2m)²) **[S]** (OpenStax UP1 §15.5). The template uses θ″ = −(g/L) sin θ − bθ′.

---

## 2. Numerics: getting the numbers right

| Rule | Why | Template |
|---|---|---|
| Fixed time step with an accumulator; clamp long frame gaps; slow motion = scale the real time fed in | Frame rate must not change the physics; a background tab must not fast-forward (Fiedler, "Fix Your Timestep!" **[S]**) | `createStepper(step, {dt: 1/240})`, `speed`, `maxFrame` 0.1 s |
| Between impacts under gravity alone, use the **exact** formula and solve the impact time | Penetrate-then-push-out makes the effective e depend on dt, and fast balls tunnel through thin floors (continuous collision / time of impact, Catto GDC 2013 **[S]**) | `createBounce`, `createCollision`, projectile landing interpolation |
| Never explicit Euler for oscillators | Energy grows every swing; semi-implicit Euler and Verlet keep energy error bounded **[S]** (Hairer et al.; Heath) | — |
| RK4 for the nonlinear pendulum and drag, at 1/240 s | RK4 is not symplectic, but at this step the drift is < 0.01 % over 2 minutes (tested), far below a 2-decimal readout | `createPendulum`, `createProjectile({drag:true})` |
| Keep an **energy ledger**: compute "lost" as start − (kinetic + potential) | Bars always add up to the total, and the glow follows the same numbers | every `energy()` |
| Check against exact results before shipping: rebound heights, first-impact time, range/time/top, momentum, e·approach speed, exact pendulum periods, terminal speed | A plausible-looking animation can be 20 % wrong; students compare with their textbook | `tests/physics.test.mjs` |
| Gate glow on the *displayed* value (a store showing 0.00 J does not glow) | SKILL.md rule; prevents glow that contradicts the readout | `loop.js` `shown()` |

---

## 3. Misconceptions to use as prediction options

Write each option in the student's own words; put the source in the teacher notes (template already does). The FCI is a secured instrument: use its *ideas*, never copy its items.

| # | Wrong idea | Right idea | Source |
|---|---|---|---|
| M1 | Heavier objects fall faster (same shape) | Same g without significant drag | IOP Spark **[S]** https://spark.iop.org/many-students-think-heavier-object-will-fall-faster-lighter-one-same-general-shape-or-size ; FCI (Hestenes, Wells & Swackhamer 1992) **[S]** |
| M2 | A falling ball moves at a constant speed set by its weight | It accelerates | IOP Spark **[S]** https://spark.iop.org/many-students-think-compact-object-such-ball-or-stone-falls-constant-speed-which-depends-how-heavy |
| M3 | A ball pushed off a table lands later (or sooner) than one dropped | Vertical motion independent of horizontal | IOP Spark (cites Dilber, Karaman & Duzgun 2007) **[S]** https://spark.iop.org/many-students-think-downward-motion-projectile-will-be-affected-its-horizontal-motion |
| M4 | A thrown ball carries a "force of the throw" (impetus) | After release only gravity (+ drag) | IOP Spark **[S]**; FCI impetus codes **[S]**; Clement 1982 **[S-2nd]** |
| M5 | Impetus runs out, then the ball drops straight (cartoon cliff path) | Parabola without drag | McCloskey, Caramazza & Green, *Science* 210 (1980) **[S]** |
| M6b | "45° is always the best angle" (used for a raised target) | Only for equal launch and landing heights | Teacher's judgement (no prevalence study found); right lines from Brancazio 1981 **[S]** |
| M6 | At the top v = 0 so a = 0 | Only v_y = 0; a = g | The Physics Classroom **[S]** https://www.physicsclassroom.com/minds-on/vectors-and-projectiles/mission-vp8/help/qg4help |
| M7 | In a collision the heavier/faster object exerts the bigger force | Equal and opposite | FCI truck–car item **[S]** (pre-test figures from https://arxiv.org/pdf/1307.7177 are from a garbled table — recheck before quoting) |
| M8 | Force is a property of an object | Force is an interaction between two objects | IOP Spark **[S]** https://spark.iop.org/many-students-think-force-property-objects-not-something-arises-when-two-objects-interact |
| M9 | A pendulum's period depends on the bob's mass | It doesn't | Teacher/activity guides only **[S-2nd]**; no peer-reviewed prevalence found (UNVERIFIED) — label it so |
| M10 | The period depends strongly on amplitude (or not at all) | Almost independent below ~20°; +7 % at 60°, +18 % at 90° | PhET Pendulum Lab guide **[S]**; teach "almost", not "exactly" |
| M11 | A bouncing ball's energy is "used up", "goes into the floor" or "is stored" | Dissipated as thermal energy and sound | Daane, McKagan, Vokos & Scherr, *PRPER* 11, 010109 (2015) **[S]** |
| M12 | Momentum conservation is unrelated to Newton's third law | Equal and opposite impulses ⇒ total momentum constant | IOP Spark **[S]** |

"Each bounce loses the same height" (linear decrease) has no published source found: it is used in the template as **teacher's judgement**, labelled in the notes, per the source ladder in `lesson-design.md` §6a.

---

## 4. What good ball simulations show (PhET, explorables)

- **PhET Projectile Motion** **[S]**: screens Intro → Vectors → Drag → Lab (fading); angle, height, speed, air resistance; velocity/acceleration vectors and a free-body diagram; tape measure; a readout of time, range and height at any trajectory point; slow motion; quadratic drag.
- **PhET Collision Lab** **[S]**: Intro, Explore 1D/2D (up to 4 balls), Inelastic (stick/slip); elasticity as a % slider; drag velocity vectors directly; momentum vectors, kinetic-energy readout, values table, slow motion and step.
- **PhET Pendulum Lab** **[S]**: photogate-style period timer (starts when the bob crosses a line), stopwatch, ruler, energy graph (kinetic, potential, thermal), friction slider, gravity presets including "Planet X", two pendulums side by side.
- **Implicit scaffolding** (Podolefsky, Moore & Perkins, arXiv:1306.6544 **[S]**): guidance through what the controls allow and show, ideas layered across screens, immediate feedback. The template follows it: ≤3 controls first, "explore more" after the stamp, bars and graph closed by default.
- **Inclusive features** **[S]**: keyboard, sonification, interactive description, voicing, pan/zoom. Which features each of the three sims has is UNVERIFIED.
- Useful extensions to point teachers at (contents only, not used for numbers): 3Blue1Brown's colliding blocks that compute π; Walter Lewin riding a giant pendulum to show mass-independence; stacked-ball drop demonstrations.

Ideas worth adding next, in this order: a period timer line for the pendulum; draggable velocity arrows with a slider alternative (WCAG 2.5.7); a second pendulum side by side; a "Planet X" gravity preset; a tape measure.

---

## 5. 2D or 3D?

| Use 2D (`view2d.js`) when | Use 3D (`view3d.js`) when |
|---|---|
| Phones, old laptops, printing, a worksheet, reduced-motion users, or WebGL fails (automatic fallback) | The lesson should feel like the pop-up book; depth matters (2D collisions, a ball rolling off a table seen from the side and above) |
| The quantity is easiest read off a flat graph | The diagram is the hook |

Both are the same lesson; offer the toggle rather than choosing for the user. Keep 3D on demand: in the template the 3D canvas renders zero frames while nothing moves (tested).

## Sources
- Bounce: LibreTexts Tatum §5.2 https://phys.libretexts.org/Bookshelves/Classical_Mechanics/ · Life after Zeno https://ptolemy.berkeley.edu/projects/chess/pubs/130/Life%20after%20Zeno.pdf · restitution values https://hypertextbook.com/facts/2006/restitution.shtml · FIBA equipment https://assets.fiba.basketball/image/upload/documents-corporate-fiba-official-rules-2026-equipment-v1-0.pdf
- Projectile and drag: OpenStax UP1 §4.3 https://openstax.org/books/university-physics-volume-1/pages/4-3-projectile-motion · NASA Glenn drag equation · basketball physics https://physicstoday.aip.org/news/the-physics-of-scoring-in-basketball · drag crisis https://baseballaero.com/2019/05/03/baseball-drag-crisis/
- Collisions: OpenStax UP1 §9.4 https://openstax.org/books/university-physics-volume-1/pages/9-4-types-of-collisions · https://en.wikipedia.org/wiki/Collision_response
- Pendulum: https://av8n.com/physics/simple-pendulum.htm · HyperPhysics https://hyperphysics.gsu.edu/hbase/pendl.html · OpenStax UP1 §15.5 https://openstax.org/books/university-physics-volume-1/pages/15-5-damped-oscillations
- Numerics: Fiedler https://gafferongames.com/post/fix_your_timestep/ · https://gafferongames.com/post/integration_basics/ · Heath symplectic integrators https://heath.cs.illinois.edu/iem/ode/symplectic/ · Catto, Continuous Collision (GDC 2013) https://box2d.org/files/ErinCatto_ContinuousCollision_GDC2013.pdf
- Misconceptions: FCI https://davidhestenes.net/modeling/R&E/FCI.PDF · Halloun & Hestenes 1985 https://davidhestenes.net/modeling/R&E/Hestenes_CommonSenseConcept.pdf · IOP Spark pages in §3 · Daane et al. 2015 https://journals.aps.org/prper/abstract/10.1103/PhysRevSTPER.11.010109
- PhET: Projectile Motion guide https://phet.colorado.edu/files/teachers-guide/projectile-motion-html-guide_en.pdf · Pendulum Lab guide https://phet.colorado.edu/files/teachers-guide/pendulum-lab-html-guide_en.pdf · Collision Lab guide https://phet.colorado.edu/files/teachers-guide/collision-lab-html-guide_es.pdf · implicit scaffolding https://arxiv.org/abs/1306.6544 · inclusive features https://onlineteachinghub.education.purdue.edu/phet/
