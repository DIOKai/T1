// The four ball lessons. Each lesson = one idea, a prediction built from documented misconceptions
// (sources in the teacher notes), ≤3 controls on the first step, the student's own numbers in the
// explanation, and a stamp for finishing the loop. Text is zh + en; add a language by adding keys.
import { createBounce, createProjectile, createCollision, createPendulum, collide1D, bounceHeights, bounceRestTime,
  pendulumPeriod, pendulumPeriodSmall, speedToHit, easiestAngle, fmt, G } from './physics.js';

const t2 = (zh, en) => ({ zh, en });
const pick = (lang, o) => o[lang] ?? o.en;
const num = (v, d = 2) => fmt(v, '', d);

/** Teacher notes as DOM nodes: objectives, Wrong Track / Right Lines, model, discussion, sources. */
function notes(lang, n) {
  const h = (tag, text) => Object.assign(document.createElement(tag), { textContent: text });
  const out = [];
  out.push(h('h4', pick(lang, t2('学习目标', 'Learning objectives'))));
  const ul = document.createElement('ul'); n.objectives.forEach((o) => ul.append(h('li', pick(lang, o)))); out.push(ul);
  out.push(h('p', pick(lang, t2('考试大纲编号：请按你用的大纲（SPM、IGCSE、GCSE…）自己填写，不要猜。',
    'Specification codes: fill in from the syllabus you teach (SPM, IGCSE, GCSE…); do not guess them.'))));
  out.push(h('h4', pick(lang, t2('常见错误想法（Wrong Track / Right Lines）', 'Misconceptions (Wrong Track / Right Lines)'))));
  const table = document.createElement('table');
  const head = document.createElement('tr');
  [t2('选项', 'Option'), t2('错误想法', 'Wrong track'), t2('正确想法', 'Right lines'), t2('出处', 'Source')].forEach((c) => head.append(h('th', pick(lang, c))));
  table.append(head);
  n.misconceptions.forEach((m) => {
    const tr = document.createElement('tr');
    [m.option, pick(lang, m.wrong), pick(lang, m.right)].forEach((c) => tr.append(h('td', c)));
    const td = document.createElement('td');
    m.sources.forEach(([label, url], i) => { if (i) td.append(' · '); td.append(Object.assign(document.createElement('a'), { href: url, textContent: label, target: '_blank', rel: 'noopener' })); });
    tr.append(td); table.append(tr);
  });
  out.push(table);
  out.push(h('h4', pick(lang, t2('模型和简化', 'Model and simplifications'))), h('p', pick(lang, n.model)));
  out.push(h('h4', pick(lang, t2('讨论题', 'Discussion'))));
  const dl = document.createElement('ul'); n.discussion.forEach((d) => dl.append(h('li', pick(lang, d)))); out.push(dl);
  out.push(h('p', pick(lang, t2('建议时间：引入 3 分钟、预测 3、实验 8–10、掀开解释 5、讨论 8、小测验 5（经验值）。',
    'Suggested timing: hook 3 min, predict 3, test 8–10, flap 5, discussion 8, quiz 5 (rule of thumb).'))));
  return out;
}

// ======================================================================= A. bouncing ball
const bounce = {
  id: 'bounce',
  title: t2('弹跳球', 'Bouncing ball'),
  hook: t2('篮球从你头顶的高度掉到地上。它会弹几下？每一次弹起来有多高？', 'A basketball drops from head height. How many times does it bounce, and how high each time?'),
  predict: {
    question: t2('跟第一次弹起来的高度比，第二次弹起来会是？', 'Compared with the first bounce, the second bounce will be…'),
    correct: 'c',
    options: [
      { id: 'a', text: t2('一样高：球的能量不会少', 'Just as high: the ball keeps its energy'),
        why: t2('能量确实没有消失，但每次撞地板，一部分动能变成了球和地板里的热能，还有声音。这些很难感觉到，所以看起来像「不见了」。',
          "Energy doesn't vanish, but each impact turns some kinetic energy into thermal energy in the ball and floor, plus sound. You can't easily feel that warming, so it looks as if nothing changed." ) },
      { id: 'b', text: t2('少一样多：每次都低同样几厘米', 'Lower by the same amount: a few centimetres less each time'),
        why: t2('如果每次少一样多，球会在某一次突然停住。实际上球每次保留的是同一个「比例」：高的弹跳少得多，低的弹跳少得少。',
          'If it lost the same height every time, it would stop suddenly at some bounce. Instead each bounce keeps the same fraction: big bounces lose a lot of height, small ones only a little.') },
      { id: 'c', text: t2('只剩第一次的同一个比例：每次都按同样比例变低', 'The same fraction of the first: each bounce shrinks by the same ratio'), why: t2('', '') }
    ]
  },
  controls: [
    { id: 'h0', label: t2('放手高度', 'Drop height'), min: 0.5, max: 2.5, step: 0.1, value: 1.8, unit: 'm', unitName: t2('米', 'metres') },
    { id: 'e', label: t2('反弹系数 e', 'Restitution e'), min: 0.3, max: 0.95, step: 0.01, value: 0.75, unit: '', decimals: 2 }
  ],
  more: [{ id: 'm', label: t2('球的质量', 'Ball mass'), min: 0.05, max: 2, step: 0.05, value: 0.6, unit: 'kg', unitName: t2('公斤', 'kilograms') }],
  moreIntro: t2('换一颗更重、但材料一样（e 不变）的球：弹起的高度会变吗？看看能量条和高度。', 'Try a heavier ball of the same material (same e). Do the bounce heights change? Watch the bars and the heights.'),
  stores: ['kinetic', 'potential', 'lost'],
  make: (p) => createBounce({ h0: p.h0, e: p.e, m: p.m }),
  sample: (sim) => [sim.state.t, sim.state.y],
  done: (sim) => sim.state.atRest || sim.state.t > 25,
  graph: { label: t2('高度（米）对时间（秒）', 'Height (m) against time (s)'), tMax: (p) => Math.min(bounceRestTime(p.h0, p.e), 25) + 0.5, yMax: (p) => p.h0 * 1.05 },
  frame(sim, p) {
    const r = 0.12, s = sim.state;
    const ticks = s.peaks.slice(0, 6).map((h, i) => ({ points: [[0.35 + i * 0.22, h + r], [0.5 + i * 0.22, h + r]] }));
    return {
      bounds: { x0: -0.9, x1: 1.9, y0: 0, y1: p.h0 + 0.45 }, floor: 0, heatX: 0,
      balls: [{ x: 0, y: s.y + r, r, store: 'kinetic' }],
      markers: [{ x: -0.7, y0: 0, y1: s.y, store: 'potential' }],   // apart from the ball so the two glows don't mix
      trails: [{ points: [[-0.25, p.h0 + r], [0.25, p.h0 + r]], dashed: true }, ...ticks]
    };
  },
  readouts(sim, p) {
    const s = sim.state;
    return [[t2('高度', 'Height'), fmt(s.y, 'm')], [t2('速度', 'Speed'), fmt(Math.abs(s.v), 'm/s')], [t2('弹跳次数', 'Bounces'), String(s.bounces)],
      [t2('第一次弹起', 'First rebound'), s.peaks[0] ? `${fmt(s.peaks[0], 'm')} (${(s.peaks[0] / p.h0 * 100).toFixed(0)} %)` : '—']];
  },
  result: (sim, p) => { const pk = sim.state.peaks; return t2(`球弹了 ${sim.state.bounces} 次后停下。第一次弹起 ${fmt(pk[0] ?? 0, 'm')}，第二次 ${fmt(pk[1] ?? 0, 'm')}。`, `The ball stopped after ${sim.state.bounces} bounces. First rebound ${fmt(pk[0] ?? 0, 'm')}, second ${fmt(pk[1] ?? 0, 'm')}.`); },
  describe: (sim, p) => t2(`弹跳球：从 ${fmt(p.h0, 'm')} 放手，e = ${num(p.e)}。现在高度 ${fmt(sim.state.y, 'm')}，已弹 ${sim.state.bounces} 次。`,
    `Bouncing ball dropped from ${fmt(p.h0, 'm')}, e = ${num(p.e)}. Now at ${fmt(sim.state.y, 'm')}, ${sim.state.bounces} bounces so far.`),
  explain(sim, p, lang) {
    const pk = sim.state.peaks.length >= 2 ? sim.state.peaks : bounceHeights(p.h0, p.e, 3);
    const r1 = pk[0] / p.h0, r2 = pk[1] / pk[0], keep = p.e * p.e;
    return [
      pick(lang, t2(`你的球从 ${fmt(p.h0, 'm')} 放手。第一次弹起 ${fmt(pk[0], 'm')}，是放手高度的 ${(r1 * 100).toFixed(0)} %；第二次弹起 ${fmt(pk[1], 'm')}，又是上一次的 ${(r2 * 100).toFixed(0)} %。每一次都是同一个比例。`,
        `Your ball dropped from ${fmt(p.h0, 'm')}. The first rebound reached ${fmt(pk[0], 'm')}, ${(r1 * 100).toFixed(0)} % of the drop; the second reached ${fmt(pk[1], 'm')}, again ${(r2 * 100).toFixed(0)} % of the one before. The same fraction every time.`)),
      pick(lang, t2(`这个比例就是 e² = ${num(p.e)}² = ${num(keep)}。每次撞地，球离开地板的速度是撞上来速度的 e 倍，动能和速度的平方成正比，所以保留 e² 的能量，其余 ${((1 - keep) * 100).toFixed(0)} % 变成热能和声音。`,
        `That fraction is e² = ${num(p.e)}² = ${num(keep)}. The ball leaves the floor at e times its impact speed; kinetic energy goes with speed squared, so e² of the energy stays and the other ${((1 - keep) * 100).toFixed(0)} % becomes thermal energy and sound.`)),
      pick(lang, t2('打开能量条：总能量一直不变，只是从动能、重力势能慢慢搬到「热能和声音」那一格。', 'Open the energy bars: the total never changes; energy moves from kinetic and gravitational into the "thermal + sound" store.'))
    ];
  },
  stamp: t2('每次弹跳保留同一个比例', 'Each bounce keeps the same fraction'),
  ignores: t2('空气阻力；球被压扁的时间（当作瞬间碰撞）；e 当作不随速度改变；弹起低于 1 毫米就当作停下（理想模型会在有限时间内弹无限多次）。',
    "Air drag; the time the ball spends squashed (impacts are instant); e is treated as the same at every speed; rebounds below 1 mm count as stopped (the ideal model bounces infinitely often in a finite time)."),
  quiz: [
    { q: t2('一颗 e = 0.8 的球从 2.0 m 放手，第一次弹起多高？', 'A ball with e = 0.8 drops from 2.0 m. How high is the first rebound?'),
      options: [t2('1.6 m', '1.6 m'), t2('1.28 m', '1.28 m'), t2('2.0 m', '2.0 m')], answer: 1,
      why: [t2('1.6 m 是用 e 乘，但高度要乘 e²（速度乘 e，高度和速度平方成正比）。', '1.6 m multiplies by e, but height scales with e² (speed scales with e, height with speed squared).'),
        t2('对：2.0 × 0.8² = 1.28 m。', 'Right: 2.0 × 0.8² = 1.28 m.'), t2('只有 e = 1 才会弹回原高度。', 'Only e = 1 would return to the start height.')] },
    { q: t2('球停下以后，它原来的能量去了哪里？', 'Once the ball has stopped, where did its energy go?'),
      options: [t2('用完了，没有了', 'Used up, gone'), t2('变成球和地板的热能，还有声音', 'Thermal energy in the ball and floor, and sound'), t2('存在地板里，之后会弹回来', 'Stored in the floor, to come back later')], answer: 1,
      why: [t2('能量不会用完；它只是换成很难察觉的形式。', "Energy isn't used up; it ends in forms that are hard to notice."), t2('对：地板和球变暖了一点点，还有碰撞声。', 'Right: the floor and ball warm up very slightly, and there is the sound of each impact.'),
        t2('地板不会把能量存起来再还给球；它散开成热了。', "The floor doesn't store it to give back; it spreads out as heat.")] },
    { q: t2('材料一样、但重两倍的球，从同样高度放手，弹起的高度会？', 'A ball of the same material but twice the mass drops from the same height. Its rebound is…'),
      options: [t2('高一倍', 'Twice as high'), t2('一样高', 'The same height'), t2('低一半', 'Half as high')], answer: 1,
      why: [t2('质量大，能量多，但要抬起的重量也多，两者抵消。', 'More mass means more energy, but also more weight to lift: they cancel.'), t2('对：高度只看 e 和放手高度。', 'Right: rebound height depends only on e and the drop height.'),
        t2('质量会抵消；用「再多玩一点」的质量滑块试试。', 'Mass cancels; try the mass slider in "Explore more".')] }
  ],
  teacher: (lang) => notes(lang, {
    objectives: [t2('说明每次弹跳保留同一比例的高度（e²）', 'Explain that each bounce keeps the same fraction of height (e²)'),
      t2('用能量守恒说明「消失」的能量变成热能和声音', 'Use energy conservation to say where the "missing" energy goes (thermal, sound)'),
      t2('由弹起高度算出 e', 'Calculate e from measured rebound heights')],
    misconceptions: [
      { option: 'a', wrong: t2('能量「用完」或球一直弹回原高度', 'Energy is "used up", or the ball keeps returning to the same height'), right: t2('能量守恒，散成热能和声音', 'Energy is conserved and dissipated as thermal energy and sound'),
        sources: [['Daane et al. 2015, PRPER 11, 010109', 'https://journals.aps.org/prper/abstract/10.1103/PhysRevSTPER.11.010109'], ['IOP Spark', 'https://spark.iop.org/energy-can-run-out']] },
      { option: 'b', wrong: t2('每次少同样的高度（线性递减）', 'Each bounce loses the same height (linear decrease)'), right: t2('每次保留同一比例（几何递减）', 'Each bounce keeps the same fraction (geometric decrease)'),
        sources: [["Teacher's judgement (no published source found)", 'https://spark.iop.org/collections/shifting-energy-between-stores-teaching-and-learning-issues']] }
    ],
    model: t2('球的高度用重力下的精确公式；每次碰撞的时间直接解出来，所以不会漏掉或「穿过」地板。离开地板速度 = e × 撞地速度。真实球的 e（反推自比赛规格）：篮球约 0.73–0.80，网球约 0.73–0.76，乒乓球约 0.89–0.93。',
      'Height follows the exact free-fall formula; each impact time is solved directly, so no bounce is missed and the ball never sinks into the floor. Rebound speed = e × impact speed. Real e values (from competition specs): basketball ≈ 0.73–0.80, tennis ≈ 0.73–0.76, table tennis ≈ 0.89–0.93.'),
    discussion: [t2('为什么有人选「少一样多」？画出两种想法的高度图来比较。', 'Why might someone pick "lower by the same amount"? Sketch both height patterns and compare.'),
      t2('用手机录一颗真球弹跳，量两次弹起的高度，算 e。', 'Film a real ball, measure two rebound heights and calculate e.')]
  })
};

// ======================================================================= B. horizontal launch vs drop
function makePair(p) {
  const thrown = createProjectile({ v0: p.v0, angle: p.angle ?? 0, h0: p.h0, drag: !!p.drag });
  const dropped = createProjectile({ v0: 0, angle: 0, h0: p.h0, drag: !!p.drag });
  return {
    thrown, dropped,
    step(dt) { thrown.step(dt); dropped.step(dt); },
    energy: () => thrown.energy(),
    get state() { return thrown.state; }
  };
}
const launch = {
  id: 'launch',
  title: t2('平抛和自由落下', 'Thrown vs dropped'),
  hook: t2('同一时间：一颗球从桌边被横着推出去，另一颗直接从同样高度放手。谁先落地？', 'At the same instant, one ball is pushed off the edge of a table and another is simply let go from the same height. Which lands first?'),
  predict: {
    question: t2('哪一颗先落地？', 'Which one lands first?'),
    correct: 'c',
    options: [
      { id: 'a', text: t2('被推出去的先落地：它跑得比较快', 'The pushed ball: it is moving faster'),
        why: t2('它横着跑得快，但横向的速度不会让它掉得更快。往下掉只由重力决定，两颗球受的重力加速度一样。', "It is faster sideways, but sideways speed doesn't make it fall faster. Falling is set by gravity alone, and both balls have the same downward acceleration.") },
      { id: 'b', text: t2('直接放手的先落地：推出去的要走比较远', 'The dropped ball: the pushed one has further to go'),
        why: t2('推出去的球确实走了更长的路，但多出来的是横向的路。横向和竖直方向的运动互不影响：两颗球每一刻都掉到同样高度。', 'The pushed ball does travel further, but the extra distance is sideways. Sideways and vertical motion are independent: at every instant both balls have fallen the same height.') },
      { id: 'c', text: t2('同时落地', 'They land together'), why: t2('', '') }
    ]
  },
  controls: [
    { id: 'v0', label: t2('推出速度', 'Push speed'), min: 0.5, max: 6, step: 0.1, value: 3, unit: 'm/s', unitName: t2('米每秒', 'metres per second') },
    { id: 'h0', label: t2('桌子高度', 'Table height'), min: 0.5, max: 2, step: 0.05, value: 1.0, unit: 'm', unitName: t2('米', 'metres') }
  ],
  more: [
    { id: 'angle', label: t2('出手角度', 'Launch angle'), min: 0, max: 60, step: 1, value: 0, unit: '°', decimals: 0, unitName: t2('度', 'degrees') },
    { id: 'drag', label: t2('空气阻力', 'Air drag'), min: 0, max: 1, step: 1, value: 0, unit: '', decimals: 0, unitName: t2('（0 关，1 开）', '(0 off, 1 on)') }
  ],
  moreIntro: t2('把出手角度调高（往上推）：还会同时落地吗？再打开空气阻力看看差多少。', 'Tilt the launch upwards: do they still land together? Then switch on air drag and see how much it changes.'),
  speed: 0.5,
  stores: ['kinetic', 'potential', 'lost'],
  make: makePair,
  sample: (sim) => [sim.thrown.state.t, sim.thrown.state.y],
  done: (sim) => sim.thrown.state.landed && sim.dropped.state.landed,
  graph: { label: t2('推出去的球：高度（米）对时间（秒）', 'Pushed ball: height (m) against time (s)'), tMax: (p) => Math.sqrt(2 * p.h0 / G) * 1.6 + 0.2, yMax: (p) => p.h0 + (p.v0 * Math.sin((p.angle || 0) * Math.PI / 180)) ** 2 / (2 * G) + 0.05 },
  frame(sim, p) {
    const a = sim.thrown.state, b = sim.dropped.state, r = 0.06;
    const reach = p.v0 * Math.sqrt(2 * p.h0 / G) * (1 + Math.sin((p.angle || 0) * Math.PI / 180)) + 0.6;
    return {
      bounds: { x0: -1.4, x1: Math.max(reach, 1.6), y0: 0, y1: p.h0 + 0.4 + (p.v0 * Math.sin((p.angle || 0) * Math.PI / 180)) ** 2 / (2 * G) }, floor: 0, heatX: a.x,
      balls: [{ x: a.x, y: a.y + r, r, store: 'kinetic' }, { x: -1.05, y: b.y + r, r, store: 'kinetic' }],   // dropped beside the table
      rods: [{ x1: -0.8, y1: p.h0, x2: 0, y2: p.h0 }, { x1: -0.8, y1: p.h0, x2: -0.8, y2: 0 }],
      markers: [{ x: -0.55, y0: 0, y1: a.y, store: 'potential' }],
      trails: [{ points: a.trail.map(([x, y]) => [x, y + r]) }, { points: b.trail.map(([, y]) => [-1.05, y + r]), dashed: true }]
    };
  },
  readouts(sim) {
    const a = sim.thrown.state, b = sim.dropped.state;
    return [[t2('推出的球落地', 'Pushed lands at'), a.landed ? fmt(a.t, 's') : '—'], [t2('放手的球落地', 'Dropped lands at'), b.landed ? fmt(b.t, 's') : '—'],
      [t2('水平距离', 'Distance'), fmt(a.x, 'm')], [t2('两球高度差', 'Height gap'), fmt(Math.abs(a.y - b.y), 'm')]];
  },
  result: (sim) => t2(`推出去的球 ${fmt(sim.thrown.state.t, 's')} 落地，直接放手的 ${fmt(sim.dropped.state.t, 's')} 落地。`, `The pushed ball landed at ${fmt(sim.thrown.state.t, 's')}, the dropped one at ${fmt(sim.dropped.state.t, 's')}.`),
  describe: (sim, p) => t2(`平抛：桌高 ${fmt(p.h0, 'm')}，推出速度 ${fmt(p.v0, 'm/s')}。推出的球高度 ${fmt(sim.thrown.state.y, 'm')}，放手的球高度 ${fmt(sim.dropped.state.y, 'm')}。`,
    `Thrown vs dropped from ${fmt(p.h0, 'm')}, push ${fmt(p.v0, 'm/s')}. Pushed ball at ${fmt(sim.thrown.state.y, 'm')}, dropped ball at ${fmt(sim.dropped.state.y, 'm')}.`),
  explain(sim, p, lang) {
    const tf = Math.sqrt(2 * p.h0 / G), a = sim.thrown.state, b = sim.dropped.state;
    const out = [
      pick(lang, t2(`两颗球都从 ${fmt(p.h0, 'm')} 开始往下掉。往下掉需要的时间只看高度：t = √(2h/g) = √(2 × ${num(p.h0)} / 9.81) = ${fmt(tf, 's')}。`,
        `Both balls start falling from ${fmt(p.h0, 'm')}. The fall time depends only on height: t = √(2h/g) = √(2 × ${num(p.h0)} / 9.81) = ${fmt(tf, 's')}.`)),
      pick(lang, t2(`你推出去的球（${fmt(p.v0, 'm/s')}）在这段时间里横着走了 ${fmt(a.x, 'm')}，但它往下掉的方式和直接放手的那颗一模一样：图上两颗球每一刻都在同一个高度。`,
        `Your pushed ball (${fmt(p.v0, 'm/s')}) went ${fmt(a.x, 'm')} sideways in that time, but it fell exactly like the dropped ball: at every moment the two were at the same height.`))
    ];
    if ((p.angle || 0) > 0) out.push(pick(lang, t2(`你把出手角度调成 ${p.angle}°：球一开始有往上的速度，所以要更久才落地（${fmt(a.t, 's')} 对 ${fmt(b.t, 's')}）。「同时落地」只适用于横着推出。`,
      `With a ${p.angle}° launch the ball starts with upward speed, so it takes longer (${fmt(a.t, 's')} vs ${fmt(b.t, 's')}). "Together" holds only for a horizontal push.`)));
    if (p.drag) out.push(pick(lang, t2(`空气阻力打开：推出去的球比较快，受的阻力比较大，落地时间差 ${fmt(Math.abs(a.t - b.t) * 1000, 'ms', 0)}，几乎看不出来。`,
      `With drag on, the faster ball feels more drag; the landing times differ by ${fmt(Math.abs(a.t - b.t) * 1000, 'ms', 0)}, hardly noticeable.`)));
    return out;
  },
  stamp: t2('横着跑不影响往下掉', 'Sideways motion does not change the fall'),
  ignores: t2('空气阻力（可以在「再多玩一点」打开）；球的转动；桌边的摩擦。时间以 0.5 倍慢动作播放。', 'Air drag (switch it on in "Explore more"); spin; friction at the table edge. Time runs at 0.5× (slow motion).'),
  quiz: [
    { q: t2('把推出速度加倍，落地时间会？', 'Double the push speed. The landing time…'),
      options: [t2('减半', 'halves'), t2('不变', 'stays the same'), t2('加倍', 'doubles')], answer: 1,
      why: [t2('速度加倍只让球横着走得更远。', 'Doubling the speed only makes it go further sideways.'), t2('对：时间只看高度，水平距离加倍。', 'Right: time depends on height; the distance doubles.'), t2('横向速度不影响竖直下落。', "Sideways speed doesn't affect the fall.")] },
    { q: t2('球飞到最高点时，它的加速度是？', 'At the top of an upward throw, the acceleration is…'),
      options: [t2('零，因为它停了一下', 'zero, because it stops for a moment'), t2('9.81 m/s²，向下', '9.81 m/s², downwards'), t2('向上，因为还在往上飞', 'upwards, because it was going up')], answer: 1,
      why: [t2('最高点只是竖直速度为零；重力一直在，所以加速度还是 g。', 'At the top only the vertical velocity is zero; gravity is still acting, so the acceleration is still g.'),
        t2('对：放手后唯一的力是重力（不计空气）。', 'Right: after release the only force is gravity (ignoring air).'), t2('放手后没有「向上的推力」跟着球走。', 'No upward "force of the throw" travels with the ball.')] },
    { q: t2('桌子高度变成 4 倍，落地时间变成？', 'Make the table 4 times as high. The fall time becomes…'),
      options: [t2('2 倍', '2 times'), t2('4 倍', '4 times'), t2('16 倍', '16 times')], answer: 0,
      why: [t2('对：t = √(2h/g)，高度 4 倍，时间 √4 = 2 倍。', 'Right: t = √(2h/g); 4× the height gives √4 = 2× the time.'), t2('时间和高度的平方根成正比，不是正比。', 'Time goes with the square root of height, not with height.'), t2('那是把平方关系反过来了。', 'That inverts the square-root relation.')] }
  ],
  teacher: (lang) => notes(lang, {
    objectives: [t2('说明横向和竖直方向的运动互相独立', 'Explain that horizontal and vertical motion are independent'),
      t2('用 t = √(2h/g) 算落地时间', 'Calculate fall time with t = √(2h/g)'), t2('说明最高点的加速度仍是 g', 'State that the acceleration at the top is still g')],
    misconceptions: [
      { option: 'a', wrong: t2('跑得快的先落地 / 推出的力让它更快掉下', 'The faster ball lands first / the push makes it fall faster'), right: t2('竖直运动只由重力决定', 'Vertical motion is set by gravity alone'),
        sources: [['IOP Spark', 'https://spark.iop.org/many-students-think-downward-motion-projectile-will-be-affected-its-horizontal-motion'], ['Hestenes et al. 1992 (FCI)', 'https://davidhestenes.net/modeling/R&E/FCI.PDF']] },
      { option: 'b', wrong: t2('推出的球要走更远，所以更晚落地', 'The pushed ball travels further, so lands later'), right: t2('多出来的是横向路程，不影响下落', 'The extra distance is sideways and does not affect the fall'),
        sources: [['IOP Spark (cites Dilber, Karaman & Duzgun 2007)', 'https://spark.iop.org/many-students-think-downward-motion-projectile-will-be-affected-its-horizontal-motion']] },
      { option: '—', wrong: t2('最高点速度为零，所以加速度为零', 'At the top v = 0 so a = 0'), right: t2('最高点只有竖直速度为零，a = g', 'Only the vertical velocity is zero at the top; a = g'),
        sources: [['The Physics Classroom', 'https://www.physicsclassroom.com/minds-on/vectors-and-projectiles/mission-vp8/help/qg4help']] }
    ],
    model: t2('没有空气阻力时位置用精确公式；打开阻力时用 F = ½ρC_dAv²（ρ = 1.2 kg/m³，C_d = 0.47，球直径 0.24 m、质量 0.6 kg），四阶 Runge–Kutta、步长 1/240 s，落地点用最后一步内插。',
      'Without drag the position is the exact formula; with drag, F = ½ρC_dAv² (ρ = 1.2 kg/m³, C_d = 0.47, ball 0.24 m across, 0.6 kg), 4th-order Runge–Kutta at 1/240 s, landing point interpolated within the last step.'),
    discussion: [t2('为什么很多人（包括大人）觉得推出去的球比较晚落地？', 'Why do many people, adults included, expect the pushed ball to land later?'),
      t2('真实实验：用尺子同时把一枚硬币推出桌边、让另一枚掉下，听落地声。', 'Real test: use a ruler to flick one coin off a desk while another drops, and listen for the landings.')]
  })
};

// ======================================================================= B2. basketball shot
const RIM_H = 3.05, RIM_X = 4.2, RIM_R = 0.2286, BALL_R = 0.12;   // FIBA rim height 3.05 m, inner diameter 45.7 cm; free-throw distance ≈ 4.2 m to the rim centre
function makeShot(p) {
  const proj = createProjectile({ v0: p.v0, angle: p.angle, h0: p.h0 ?? 2.0, drag: !!p.drag, m: 0.6, radius: BALL_R });
  const s = { proj, status: 'flying', crossX: null, stopped: false };
  const boardX = RIM_X + RIM_R + 0.15 - BALL_R;                     // ball touching the backboard
  return {
    proj,
    get state() { return proj.state; },
    shot: s,
    step(dt) {
      if (s.stopped) return;
      const y0 = proj.state.y;
      proj.step(dt);
      const y1 = proj.state.y;
      if (s.status === 'flying' && y0 >= RIM_H && y1 < RIM_H && proj.state.vy < 0) {        // coming down through the rim height
        s.crossX = proj.state.x;
        s.status = Math.abs(s.crossX - RIM_X) <= RIM_R - BALL_R ? 'in' : s.crossX < RIM_X ? 'short' : 'long';
      }
      if (proj.state.x >= boardX && proj.state.y > 0) {                // no bounce model: stop at the board
        s.stopped = true;
        if (s.status === 'flying') s.status = proj.state.y >= RIM_H - 0.15 ? 'board' : 'short';   // below the board = the pole: it was short
      }
      if (s.status === 'flying' && proj.state.landed) s.status = proj.state.top < RIM_H ? 'short' : 'long';
    },
    energy: () => proj.energy()
  };
}
const shotWord = (st) => ({ in: t2('进了！', 'In!'), short: t2('太短', 'Short'), long: t2('太远', 'Long'), board: t2('撞到篮板', 'Hit the backboard'), flying: t2('飞行中', 'In the air') })[st];
const shot = {
  id: 'shot',
  title: t2('投篮', 'Basketball shot'),
  hook: t2('罚球：球从 2.0 m 高出手，篮框在 4.2 m 外、3.05 m 高。怎样投最省力？', 'A free throw: you release at 2.0 m, the rim is 4.2 m away and 3.05 m high. What is the easiest way to score?'),
  predict: {
    question: t2('要投进这个篮框，哪个出手角度需要的出手速度最小？', 'To reach this rim, which launch angle needs the smallest launch speed?'),
    correct: 'c',
    options: [
      { id: 'a', text: t2('平平地瞄准篮框投（大约 20°）', 'Aim straight at the rim, fairly flat (about 20°)'),
        why: t2('瞄准篮框直直投，球不会走直线：重力一直把它往下拉，路线是抛物线。角度太平，球要飞得非常快才不会在半路掉下去。',
          "The ball doesn't travel in a straight line: gravity pulls it down the whole way, so its path is a parabola. Too flat, and it needs a very high speed to avoid dropping short.") },
      { id: 'b', text: t2('45°：课本说 45° 投得最远', '45°: the textbook says 45° goes furthest'),
        why: t2('「45° 最远」只适用于出手点和落点一样高的情况。篮框比你的手高，最省力的角度要比 45° 再大一点：45° 加上「从手看篮框的仰角」的一半。',
          '"45° goes furthest" only holds when you land at the height you launched from. The rim is higher than your hand, so the easiest angle is a bit more than 45°: 45° plus half the angle at which you look up at the rim.') },
      { id: 'c', text: t2('比 45° 大一点（50° 多）', 'A bit more than 45° (just over 50°)'), why: t2('', '') }
    ]
  },
  controls: [
    { id: 'angle', label: t2('出手角度', 'Launch angle'), min: 20, max: 75, step: 1, value: 40, unit: '°', decimals: 0, unitName: t2('度', 'degrees') },
    { id: 'v0', label: t2('出手速度', 'Launch speed'), min: 5, max: 11, step: 0.05, value: 7.3, unit: 'm/s', decimals: 2, unitName: t2('米每秒', 'metres per second') }
  ],
  more: [
    { id: 'h0', label: t2('出手高度', 'Release height'), min: 1.6, max: 2.6, step: 0.05, value: 2.0, unit: 'm', unitName: t2('米', 'metres') },
    { id: 'drag', label: t2('空气阻力', 'Air drag'), min: 0, max: 1, step: 1, value: 0, unit: '', decimals: 0, unitName: t2('（0 关，1 开）', '(0 off, 1 on)') }
  ],
  moreIntro: t2('长得高的人出手点比较高：最省力的角度会变吗？打开空气阻力，同样的投法还会进吗？', 'A taller player releases higher: does the easiest angle change? Switch on air drag: does the same shot still go in?'),
  speed: 0.5,
  stores: ['kinetic', 'potential', 'lost'],
  make: makeShot,
  sample: (sim) => [sim.state.t, sim.state.y],
  done: (sim) => sim.shot.stopped || (sim.shot.status !== 'flying' && (sim.state.landed || sim.state.y < RIM_H - 0.6)),
  graph: { label: t2('球的高度（米）对时间（秒）', 'Ball height (m) against time (s)'), tMax: () => 1.8, yMax: () => 5 },
  frame(sim, p) {
    const s = sim.state, h0 = p.h0 ?? 2.0;
    const apex = h0 + (p.v0 * Math.sin(p.angle * Math.PI / 180)) ** 2 / (2 * G);
    return {
      bounds: { x0: -0.6, x1: RIM_X + 1.0, y0: 0, y1: Math.max(RIM_H + 1.2, apex + 0.3) }, floor: 0, heatX: s.x,
      balls: [{ x: s.x, y: s.y, r: BALL_R, store: 'kinetic' }],
      rods: [{ x1: 0, y1: 0, x2: 0, y2: h0 - BALL_R },                                          // the shooter, as a post
        { x1: RIM_X - RIM_R, y1: RIM_H, x2: RIM_X + RIM_R, y2: RIM_H },                      // rim
        { x1: RIM_X + RIM_R + 0.15, y1: RIM_H - 0.15, x2: RIM_X + RIM_R + 0.15, y2: RIM_H + 1.05 },   // backboard
        { x1: RIM_X + RIM_R + 0.15, y1: 0, x2: RIM_X + RIM_R + 0.15, y2: RIM_H - 0.15 }],     // pole
      markers: [{ x: -0.35, y0: 0, y1: s.y, store: 'potential' }],
      trails: [{ points: s.trail }]
    };
  },
  readouts(sim, p) {
    const dy = RIM_H - (p.h0 ?? 2.0);
    return [[t2('结果', 'Result'), shotWord(sim.shot.status)],
      [t2('这个角度要的速度', 'Speed needed at this angle'), Number.isFinite(speedToHit(RIM_X, dy, p.angle)) ? fmt(speedToHit(RIM_X, dy, p.angle), 'm/s') : '—'],
      [t2('最省力的角度', 'Easiest angle'), fmt(easiestAngle(RIM_X, dy), '°', 1)],
      [t2('过框高度时的位置', 'Where it crossed rim height'), sim.shot.crossX != null ? fmt(sim.shot.crossX - RIM_X, 'm') : '—']];
  },
  result: (sim) => t2(`结果：${shotWord(sim.shot.status).zh}`, `Result: ${shotWord(sim.shot.status).en}`),
  describe: (sim, p) => t2(`投篮：${p.angle}° 出手，速度 ${fmt(p.v0, 'm/s')}。球在 ${fmt(sim.state.x, 'm')} 远、${fmt(sim.state.y, 'm')} 高。`,
    `Basketball shot at ${p.angle}°, ${fmt(p.v0, 'm/s')}. Ball ${fmt(sim.state.x, 'm')} out, ${fmt(sim.state.y, 'm')} high.`),
  explain(sim, p, lang) {
    const h0 = p.h0 ?? 2.0, dy = RIM_H - h0, best = easiestAngle(RIM_X, dy), vBest = speedToHit(RIM_X, dy, best);
    const need = speedToHit(RIM_X, dy, p.angle), look = Math.atan2(dy, RIM_X) * 180 / Math.PI;
    const out = [
      pick(lang, t2(`从你手上看，篮框高 ${fmt(dy, 'm')}、远 ${fmt(RIM_X, 'm')}，仰角 ${fmt(look, '°', 1)}。最省力的角度是 45° + ${fmt(look, '°', 1)} ÷ 2 = ${fmt(best, '°', 1)}，只要 ${fmt(vBest, 'm/s')}。`,
        `From your hand the rim is ${fmt(dy, 'm')} up and ${fmt(RIM_X, 'm')} away: you look up at ${fmt(look, '°', 1)}. The easiest angle is 45° + ${fmt(look, '°', 1)} ÷ 2 = ${fmt(best, '°', 1)}, needing only ${fmt(vBest, 'm/s')}.`)),
      pick(lang, Number.isFinite(need)
        ? t2(`你用 ${p.angle}°：要投到框中心需要 ${fmt(need, 'm/s')}（你用了 ${fmt(p.v0, 'm/s')}）。角度离 ${fmt(best, '°', 0)} 越远，需要的速度越大，速度差一点点就会太短或太远。`,
          `You used ${p.angle}°: reaching the rim centre takes ${fmt(need, 'm/s')} (you used ${fmt(p.v0, 'm/s')}). The further the angle from ${fmt(best, '°', 0)}, the more speed it takes, and the less room for error in speed.`)
        : t2(`你用 ${p.angle}°：这么平的角度，再快也到不了框的高度。`, `You used ${p.angle}°: at an angle that flat the ball can't reach the rim at any speed.`)),
      pick(lang, t2('球的路线是抛物线：横向速度不变，竖直方向一直受重力往下拉，所以不能「瞄直线」。', "The path is a parabola: the sideways speed stays the same while gravity keeps pulling down, so you can't aim in a straight line."))
    ];
    if (p.drag) out.push(pick(lang, t2('空气阻力打开：球慢一点，需要稍微大一点的速度或角度。', 'With drag on, the ball slows a little; it needs a bit more speed or angle.')));
    return out;
  },
  stamp: t2('最省力的角度比 45° 大', 'The easiest angle is more than 45°'),
  ignores: t2('空气阻力（可以在「再多玩一点」打开）；球的旋转；篮板和篮框的反弹（球从框内往下穿过框的高度就算进；碰到篮板就停下）。时间以 0.5 倍慢动作播放。',
    "Air drag (switch it on in \"Explore more\"); spin; bounces off the board or rim (a shot counts as in if the ball comes down through rim height inside the rim; it stops when it touches the board). Time runs at 0.5× (slow motion)."),
  quiz: [
    { q: t2('在平地上，从地面投到地面，哪个角度投得最远（不计空气）？', 'On flat ground, launching from and landing at ground level, which angle goes furthest (no air)?'),
      options: [t2('30°', '30°'), t2('45°', '45°'), t2('60°', '60°')], answer: 1,
      why: [t2('30° 和 60° 射程一样，都比 45° 近。', '30° and 60° give the same range, both shorter than 45°.'), t2('对：起点和落点一样高时是 45°。', 'Right: 45° when launch and landing heights are equal.'), t2('60° 和 30° 一样远，比 45° 近。', '60° goes as far as 30°, less than 45°.')] },
    { q: t2('篮框比出手点高，最省力的角度会？', 'The rim is higher than the release point. The easiest angle is…'),
      options: [t2('小于 45°', 'below 45°'), t2('刚好 45°', 'exactly 45°'), t2('大于 45°', 'above 45°')], answer: 2,
      why: [t2('目标越高，角度要越大。', 'A higher target needs a steeper angle.'), t2('45° 只适用于同样高度。', '45° is only for equal heights.'), t2('对：45° + 仰角的一半。', 'Right: 45° plus half the elevation angle.')] },
    { q: t2('球在最高点时，速度是？', 'At the top of its path, the ball’s velocity is…'),
      options: [t2('零', 'zero'), t2('只剩横向速度', 'only the sideways part'), t2('只剩竖直速度', 'only the vertical part')], answer: 1,
      why: [t2('只有竖直速度变成零，横向速度还在。', 'Only the vertical part is zero; the sideways part remains.'), t2('对：横向速度从头到尾不变（不计空气）。', 'Right: the sideways velocity stays the same all the way (ignoring air).'), t2('最高点正是竖直速度为零的地方。', 'The top is exactly where the vertical part is zero.')] }
  ],
  teacher: (lang) => notes(lang, {
    objectives: [t2('说明抛体路线是抛物线，横向和竖直运动独立', 'Explain that a projectile follows a parabola with independent horizontal and vertical motion'),
      t2('说明「45° 最远」的条件，目标较高时最省力角度大于 45°', 'State when "45° goes furthest" holds, and that a higher target needs more than 45°'),
      t2('用公式算出投到某一点需要的速度', 'Calculate the speed needed to reach a given point')],
    misconceptions: [
      { option: 'a', wrong: t2('瞄直线投 / 球走直线到力用完才掉下', 'Aim in a straight line / the ball flies straight until its push runs out'), right: t2('重力一直作用，路线是抛物线', 'Gravity acts throughout; the path is a parabola'),
        sources: [['McCloskey, Caramazza & Green 1980 (curvilinear impetus)', 'https://www.science.org/doi/10.1126/science.210.4474.1139'], ['IOP Spark', 'https://spark.iop.org/most-pupils-think-if-object-moving-there-must-be-force-direction-its-motion']] },
      { option: 'b', wrong: t2('45° 永远最好', '45° is always best'), right: t2('只有起点和终点同高时成立', 'Only when launch and landing heights are equal'),
        sources: [["Teacher's judgement (common over-generalisation; no prevalence study found)", 'https://openstax.org/books/university-physics-volume-1/pages/4-3-projectile-motion']] }
    ],
    model: t2('不计空气时轨迹用精确公式；需要的速度 v² = g·dx² / (2cos²θ·(dx·tanθ − dy))，最省力角度 45° + ½·atan(dy/dx)（Brancazio 1981）。篮框高 3.05 m、内径 45.7 cm（FIBA），球直径 24 cm。打开阻力时用二次阻力、RK4。',
      'Without drag the path is the exact formula; required speed v² = g·dx² / (2cos²θ·(dx·tanθ − dy)), easiest angle 45° + ½·atan(dy/dx) (Brancazio 1981). Rim 3.05 m high, 45.7 cm inner diameter (FIBA), ball 24 cm across. With drag: quadratic drag, RK4.'),
    discussion: [t2('为什么职业球员罚球常用比最省力角度再高一点的角度？（提示：球从上面落下，框看起来比较「大」）', 'Why do players often shoot a little steeper than the easiest angle? (Hint: a ball coming down steeply "sees" a bigger rim.)'),
      t2('出手高度变高，最省力角度怎么变？用「再多玩一点」验证。', 'How does a higher release change the easiest angle? Check with "Explore more".')]
  })
};

// ======================================================================= C. collision
const radiusOf = (m) => 0.07 * Math.cbrt(m / 0.5);        // same material: radius grows with the cube root of mass
const collision = {
  id: 'collision',
  title: t2('两球相撞', 'Two balls collide'),
  hook: t2('一颗重球滚过去，撞上一颗静止的轻球。撞到的那一瞬间，谁推谁比较用力？', 'A heavy ball rolls into a light ball at rest. At the moment they touch, which one pushes harder?'),
  predict: {
    question: t2('碰撞那一瞬间：', 'At the moment of the collision:'),
    correct: 'c',
    options: [
      { id: 'a', text: t2('重的球推轻的球比较用力', 'The heavy ball pushes harder'),
        why: t2('看起来像，因为轻的球被撞得飞出去。但力是两颗球之间的相互作用：重球推轻球多大力，轻球就同时推回重球多大力。不同的是效果：同样的力让轻球速度变化大得多。',
          'It looks that way because the light ball flies off. But force is an interaction between the two: the heavy ball pushes the light one exactly as hard as the light one pushes back. What differs is the effect: the same force changes the light ball\'s speed far more.') },
      { id: 'b', text: t2('跑得快的那颗推得比较用力', 'The moving ball pushes harder'),
        why: t2('跑得快不代表「带着比较多的力」。力不是球自己带着的东西，是两颗球接触时才出现的，而且大小相等、方向相反。',
          "Moving faster doesn't mean it \"carries more force\". Force isn't something a ball has; it appears when the two touch, equal in size and opposite in direction.") },
      { id: 'c', text: t2('一样用力，方向相反', 'Equally hard, in opposite directions'), why: t2('', '') }
    ]
  },
  controls: [
    { id: 'm1', label: t2('重球质量', 'Heavy ball'), min: 0.5, max: 5, step: 0.1, value: 2, unit: 'kg', unitName: t2('公斤', 'kilograms') },
    { id: 'm2', label: t2('轻球质量', 'Light ball'), min: 0.1, max: 2, step: 0.05, value: 0.4, unit: 'kg', unitName: t2('公斤', 'kilograms') },
    { id: 'u1', label: t2('重球速度', 'Heavy ball speed'), min: 0.3, max: 3, step: 0.1, value: 1.5, unit: 'm/s', unitName: t2('米每秒', 'metres per second') }
  ],
  more: [{ id: 'e', label: t2('反弹系数 e', 'Restitution e'), min: 0, max: 1, step: 0.05, value: 1, unit: '', decimals: 2 }],
  moreIntro: t2('把 e 调小：撞完后动能少了一些（变成热和声音），但总动量呢？两颗球受到的推力还一样吗？', 'Lower e: some kinetic energy turns into heat and sound. What about total momentum, and are the pushes still equal?'),
  speed: 0.5,
  stores: ['kinetic', 'lost'],
  make: (p) => createCollision({ m1: p.m1, u1: p.u1, m2: p.m2, u2: 0, e: p.e ?? 1, r1: radiusOf(p.m1), r2: radiusOf(p.m2), x1: 0.2, x2: 1.1 }),
  sample: (sim) => [sim.state.t, sim.state.v1],
  done: (sim) => (sim.state.hit && sim.state.t > sim.state.hit.t + 0.8) || sim.state.t > 6,
  graph: { label: t2('重球速度（米每秒）对时间（秒）', 'Heavy ball speed (m/s) against time (s)'), tMax: (p) => 0.9 / p.u1 + 1, yMax: (p) => p.u1 * 1.1 },
  frame(sim, p) {
    const s = sim.state, r1 = radiusOf(p.m1), r2 = radiusOf(p.m2);
    const arrows = [];
    if (s.hit && s.t - s.hit.t < 0.6) {                  // show the two equal and opposite pushes just after contact
      const L = Math.min(0.5, 0.25 * Math.abs(s.hit.impulse));
      const cx = s.x1 + r1;
      arrows.push({ x: cx, y: r1 + 0.18, dx: L, dy: 0, label: 'F' }, { x: cx, y: r1 + 0.28, dx: -L, dy: 0, label: '−F' });
    }
    return {
      bounds: { x0: -0.2, x1: 2.6, y0: 0, y1: 0.75 }, floor: 0, heatX: s.hit ? s.x1 + r1 : 0,
      balls: [{ x: s.x1, y: r1, r: r1, store: 'kinetic', label: `${num(p.m1, 1)} kg` }, { x: s.x2, y: r2, r: r2, store: 'kinetic', label: `${num(p.m2, 2)} kg` }],
      arrows
    };
  },
  readouts(sim, p) {
    const s = sim.state, h = s.hit;
    return [[t2('总动量', 'Total momentum'), fmt(sim.momentum(), 'kg·m/s')], [t2('重球速度', 'Heavy ball'), fmt(s.v1, 'm/s')], [t2('轻球速度', 'Light ball'), fmt(s.v2, 'm/s')],
      [t2('互相的冲量', 'Impulse each way'), h ? `± ${fmt(Math.abs(h.impulse), 'N·s')}` : '—']];
  },
  result: (sim) => { const h = sim.state.hit; return h ? t2(`碰撞了。两颗球互相的冲量都是 ${fmt(Math.abs(h.impulse), 'N·s')}，方向相反。`, `They collided. Each ball received an impulse of ${fmt(Math.abs(h.impulse), 'N·s')}, in opposite directions.`) : t2('还没碰到。', 'Not touched yet.'); },
  describe: (sim, p) => t2(`碰撞：${num(p.m1, 1)} kg 的球以 ${fmt(p.u1, 'm/s')} 撞向静止的 ${num(p.m2, 2)} kg 球。现在速度 ${fmt(sim.state.v1, 'm/s')} 和 ${fmt(sim.state.v2, 'm/s')}。`,
    `Collision: a ${num(p.m1, 1)} kg ball at ${fmt(p.u1, 'm/s')} hits a ${num(p.m2, 2)} kg ball at rest. Speeds now ${fmt(sim.state.v1, 'm/s')} and ${fmt(sim.state.v2, 'm/s')}.`),
  explain(sim, p, lang) {
    const h = sim.state.hit || { ...collide1D(p.m1, p.u1, p.m2, 0, p.e ?? 1), u1: p.u1, u2: 0 };
    const J = Math.abs(h.impulse), dv1 = Math.abs(h.v1 - h.u1), dv2 = Math.abs(h.v2 - h.u2);
    const out = [
      pick(lang, t2(`碰撞时，重球给轻球的冲量是 ${fmt(J, 'N·s')}，轻球同时给重球 ${fmt(J, 'N·s')}，方向相反：两个推力一样大（牛顿第三定律）。`,
        `During the collision the heavy ball gave the light ball an impulse of ${fmt(J, 'N·s')}, and at the same moment the light ball gave the heavy ball ${fmt(J, 'N·s')} the other way: the two pushes are equal (Newton's third law).`)),
      pick(lang, t2(`效果不一样：同样的冲量，${num(p.m2, 2)} kg 的轻球速度改变了 ${fmt(dv2, 'm/s')}，${num(p.m1, 1)} kg 的重球只改变了 ${fmt(dv1, 'm/s')}（速度变化 = 冲量 ÷ 质量）。`,
        `The effects differ: the same impulse changed the ${num(p.m2, 2)} kg ball's speed by ${fmt(dv2, 'm/s')} but the ${num(p.m1, 1)} kg ball's by only ${fmt(dv1, 'm/s')} (change in speed = impulse ÷ mass).`)),
      pick(lang, t2(`因为两个冲量大小相等、方向相反，总动量碰撞前后都是 ${fmt(h.momentum, 'kg·m/s')}。`, `Because the two impulses are equal and opposite, the total momentum is ${fmt(h.momentum, 'kg·m/s')} before and after.`))
    ];
    if ((p.e ?? 1) < 1) out.push(pick(lang, t2(`e = ${num(p.e)}：动能少了 ${fmt(h.keLost, 'J')}，变成热和声音；动量还是守恒。`, `With e = ${num(p.e)}, ${fmt(h.keLost, 'J')} of kinetic energy became heat and sound; momentum is still conserved.`)));
    return out;
  },
  stamp: t2('作用力和反作用力一样大', 'The two pushes are always equal'),
  ignores: t2('球的滚动和转动（当作在冰面上滑动）；摩擦；碰撞时间极短，图上的箭头只表示两个推力相等、方向相反，长度不按比例。时间以 0.5 倍慢动作播放。',
    'Rolling and spin (the balls slide as if on ice); friction; the impact is instantaneous, and the arrows only show the two forces are equal and opposite, not to scale. Time runs at 0.5× (slow motion).'),
  quiz: [
    { q: t2('卡车撞上小汽车。撞击时谁受到的力比较大？', 'A truck hits a small car. During the crash, which feels the bigger force?'),
      options: [t2('卡车', 'The truck'), t2('小汽车', 'The car'), t2('一样大', 'Both the same')], answer: 2,
      why: [t2('卡车受的力和小汽车受的一样大；卡车质量大，所以速度几乎不变。', 'The truck feels the same force; its large mass means its speed hardly changes.'),
        t2('小汽车「伤得重」是因为质量小、速度变化大，不是力比较大。', 'The car is hurt more because its small mass gives a big change in speed, not because the force is bigger.'), t2('对：力大小相等、方向相反。', 'Right: equal and opposite forces.')] },
    { q: t2('两颗一样的球，一颗以 2 m/s 正面撞上静止的另一颗（e = 1）。撞完后？', 'Two identical balls: one at 2 m/s hits the other at rest head-on (e = 1). Afterwards…'),
      options: [t2('两颗都以 1 m/s 前进', 'both move on at 1 m/s'), t2('第一颗停下，第二颗以 2 m/s 前进', 'the first stops, the second moves at 2 m/s'), t2('第一颗弹回来', 'the first bounces back')], answer: 1,
      why: [t2('那是两颗黏在一起（e = 0）的情况。', 'That is what happens if they stick together (e = 0).'), t2('对：质量相同、完全弹性时速度互换。', 'Right: equal masses, elastic collision: they swap velocities.'), t2('只有撞上比自己重的球才会弹回来。', 'It only bounces back if it hits something heavier.')] },
    { q: t2('e = 0.5 的碰撞里，什么守恒？', 'In a collision with e = 0.5, what is conserved?'),
      options: [t2('动能', 'Kinetic energy'), t2('总动量', 'Total momentum'), t2('两颗球各自的速度', 'Each ball\'s speed')], answer: 1,
      why: [t2('一部分动能变成热和声音。', 'Some kinetic energy becomes heat and sound.'), t2('对：冲量相等相反，总动量不变。', 'Right: equal and opposite impulses keep total momentum fixed.'), t2('速度当然会变。', 'The speeds do change.')] }
  ],
  teacher: (lang) => notes(lang, {
    objectives: [t2('说明碰撞中两个力大小相等、方向相反', 'State that the two forces in a collision are equal and opposite'),
      t2('用冲量 = 质量 × 速度变化解释效果不同', 'Use impulse = mass × change in velocity to explain the different effects'), t2('说明动量守恒，弹性和非弹性碰撞的差别', 'Explain momentum conservation and elastic vs inelastic collisions')],
    misconceptions: [
      { option: 'a', wrong: t2('重的（大的）物体施力比较大', 'The heavier (bigger) object exerts the larger force'), right: t2('力大小相等、方向相反', 'The forces are equal and opposite'),
        sources: [['Hestenes et al. 1992 (FCI, truck–car item; do not copy the item)', 'https://davidhestenes.net/modeling/R&E/FCI.PDF'], ['arXiv 1307.7177', 'https://arxiv.org/pdf/1307.7177']] },
      { option: 'b', wrong: t2('跑得快的物体「带着比较多的力」', 'The faster object "has more force"'), right: t2('力是两个物体之间的相互作用，不是物体自己的性质', 'Force is an interaction between two objects, not a property of one'),
        sources: [['IOP Spark', 'https://spark.iop.org/many-students-think-force-property-objects-not-something-arises-when-two-objects-interact']] }
    ],
    model: t2('一维碰撞，速度常数直到接触，接触时间精确解出，然后用 v₁ = (p + m₂e(u₂−u₁))/(m₁+m₂)、v₂ = (p + m₁e(u₁−u₂))/(m₁+m₂)。同材料的球半径和质量的立方根成正比。',
      'One-dimensional collision: constant velocity until contact (contact time solved exactly), then v₁ = (p + m₂e(u₂−u₁))/(m₁+m₂), v₂ = (p + m₁e(u₁−u₂))/(m₁+m₂). Same-material balls: radius scales with the cube root of mass.'),
    discussion: [t2('如果轻球受的力比较大，动量还会守恒吗？', 'If the light ball felt the bigger force, would momentum still be conserved?'),
      t2('3Blue1Brown 的「碰撞方块算 π」影片：可以当作延伸。', '3Blue1Brown\'s "colliding blocks compute π" video works as an extension.')]
  })
};

// ======================================================================= D. pendulum
const pendulum = {
  id: 'pendulum',
  title: t2('单摆', 'Pendulum'),
  hook: t2('同一个秋千，坐一个大人和坐一个小孩，来回一次哪个比较快？', 'On the same swing, an adult or a small child: whose swing back and forth takes less time?'),
  predict: {
    question: t2('把摆锤换成重 10 倍的，摆长不变，来回一次的时间（周期）会？', 'Swap the bob for one 10 times heavier, same length. The time for one swing (the period)…'),
    correct: 'c',
    options: [
      { id: 'a', text: t2('变短：重的摆得比较快', 'Gets shorter: heavier swings faster'),
        why: t2('重的摆锤受的重力比较大，但要推动的质量也一样大了 10 倍，两者正好抵消：加速度和质量无关。', 'A heavier bob feels a bigger pull of gravity, but it also has 10 times the mass to move; the two cancel, so the acceleration does not depend on mass.') },
      { id: 'b', text: t2('变长：重的比较难推动', 'Gets longer: heavier is harder to move'),
        why: t2('重的确实比较难推动，但重力也按同样比例变大，所以抵消了。周期只看摆长（和很大的摆角）。', 'It is harder to move, but gravity pulls it harder by the same factor, so it cancels. The period depends on the length (and, a little, on very large swings).') },
      { id: 'c', text: t2('不变', 'Stays the same'), why: t2('', '') }
    ]
  },
  controls: [
    { id: 'L', label: t2('摆长', 'Length'), min: 0.3, max: 2, step: 0.05, value: 1.0, unit: 'm', unitName: t2('米', 'metres') },
    { id: 'm', label: t2('摆锤质量', 'Bob mass'), min: 0.1, max: 5, step: 0.1, value: 0.5, unit: 'kg', unitName: t2('公斤', 'kilograms') }
  ],
  more: [
    { id: 'amplitude', label: t2('摆角', 'Swing angle'), min: 5, max: 80, step: 1, value: 15, unit: '°', decimals: 0, unitName: t2('度', 'degrees') },
    { id: 'damping', label: t2('阻力', 'Damping'), min: 0, max: 0.5, step: 0.05, value: 0, unit: '1/s', decimals: 2 }
  ],
  moreIntro: t2('把摆角调大到 60° 以上，测到的周期还和公式一样吗？再加一点阻力，看能量去哪里。', 'Raise the swing angle past 60°: does the measured period still match the formula? Add some damping and watch where the energy goes.'),
  stores: ['kinetic', 'potential', 'lost'],
  make: (p) => createPendulum({ L: p.L, m: p.m, amplitude: p.amplitude ?? 15, damping: p.damping ?? 0 }),
  sample: (sim) => [sim.state.t, sim.state.theta * 180 / Math.PI],
  done: (sim) => sim.state.crossings.length >= 3 || sim.state.t > 30,
  graph: { label: t2('摆角（度）对时间（秒），中线是 0°', 'Angle (deg) against time (s); centre line is 0°'), tMax: (p) => pendulumPeriod(p.L, p.amplitude ?? 15) * 2.6, yMax: (p) => (p.amplitude ?? 15) * 1.1, yMin: (p) => -(p.amplitude ?? 15) * 1.1 },
  frame(sim, p) {
    const pos = sim.position(), top = p.L + 0.15, r = 0.05 * Math.cbrt(p.m / 0.5) + 0.03;
    const bob = { x: pos.x, y: top + pos.y };
    return {
      bounds: { x0: -p.L - 0.45, x1: p.L + 0.4, y0: 0, y1: top + 0.2 }, floor: 0, heatX: 0,
      rods: [{ x1: 0, y1: top, x2: bob.x, y2: bob.y },                       // string
        { x1: -p.L - 0.3, y1: 0, x2: -p.L - 0.3, y2: top + 0.05 }, { x1: -p.L - 0.3, y1: top + 0.05, x2: 0, y2: top + 0.05 }, { x1: 0, y1: top + 0.05, x2: 0, y2: top }],   // stand
      balls: [{ x: bob.x, y: bob.y, r, store: 'kinetic' }],
      markers: [{ x: p.L + 0.2, y0: top - p.L, y1: Math.max(bob.y, top - p.L), store: 'potential' }],
      trails: [{ points: Array.from({ length: 33 }, (_, i) => { const a = ((i / 32) * 2 - 1) * (p.amplitude ?? 15) * Math.PI / 180; return [p.L * Math.sin(a), top - p.L * Math.cos(a)]; }), dashed: true }]
    };
  },
  readouts(sim, p) {
    const s = sim.state;
    return [[t2('测到的周期', 'Measured period'), s.period ? fmt(s.period, 's') : '—'], [t2('公式 2π√(L/g)', 'Formula 2π√(L/g)'), fmt(pendulumPeriodSmall(p.L), 's')],
      [t2('摆角', 'Angle'), fmt(s.theta * 180 / Math.PI, '°', 1)], [t2('时间', 'Time'), fmt(s.t, 's', 1)]];
  },
  result: (sim) => t2(`测到的周期是 ${sim.state.period ? fmt(sim.state.period, 's') : '—'}。`, `Measured period: ${sim.state.period ? fmt(sim.state.period, 's') : '—'}.`),
  describe: (sim, p) => t2(`单摆：摆长 ${fmt(p.L, 'm')}，摆锤 ${fmt(p.m, 'kg')}。现在摆角 ${fmt(sim.state.theta * 180 / Math.PI, '°', 0)}。`,
    `Pendulum: length ${fmt(p.L, 'm')}, bob ${fmt(p.m, 'kg')}. Angle now ${fmt(sim.state.theta * 180 / Math.PI, '°', 0)}.`),
  explain(sim, p, lang) {
    const T0 = pendulumPeriodSmall(p.L), amp = p.amplitude ?? 15, Te = pendulumPeriod(p.L, amp);
    const out = [
      pick(lang, t2(`你的摆长 ${fmt(p.L, 'm')}、摆锤 ${fmt(p.m, 'kg')}，测到周期 ${sim.state.period ? fmt(sim.state.period, 's') : fmt(Te, 's')}。公式 T = 2π√(L/g) = ${fmt(T0, 's')}：里面根本没有质量。`,
        `Your pendulum is ${fmt(p.L, 'm')} long with a ${fmt(p.m, 'kg')} bob; the measured period is ${sim.state.period ? fmt(sim.state.period, 's') : fmt(Te, 's')}. The formula T = 2π√(L/g) = ${fmt(T0, 's')} has no mass in it at all.`)),
      pick(lang, t2('原因：重力把摆锤往回拉的力和质量成正比，可是要推动摆锤也需要和质量成正比的力，两者相除，质量就消掉了。周期只由摆长决定：摆长变成 4 倍，周期变成 2 倍。',
        'Why: the pull of gravity back towards the centre is proportional to the mass, but so is the force needed to speed the bob up. Divide one by the other and the mass cancels. Only the length matters: 4× the length gives 2× the period.'))
    ];
    if (amp > 20) out.push(pick(lang, t2(`你的摆角是 ${amp}°：大角度时周期会比公式长一点，精确值是 ${fmt(Te, 's')}，长了 ${((Te / T0 - 1) * 100).toFixed(1)} %。所以要说「小角度时周期和摆角几乎无关」，不是完全无关。`,
      `Your swing angle is ${amp}°. At large angles the period is a little longer than the formula: the exact value is ${fmt(Te, 's')}, ${((Te / T0 - 1) * 100).toFixed(1)} % longer. So the period is almost, not exactly, independent of the angle for small swings.`)));
    return out;
  },
  stamp: t2('周期和质量无关', 'The period does not depend on mass'),
  ignores: t2('绳子当作没有重量、不会伸长；摆锤当作一个点；空气阻力（可以在「再多玩一点」加）。周期用完整的非线性方程算，不是小角度近似。',
    'The string is massless and does not stretch; the bob is a point; air drag (add it in "Explore more"). The swing uses the full nonlinear equation, not the small-angle approximation.'),
  quiz: [
    { q: t2('摆长变成 4 倍，周期变成？', 'Make the pendulum 4 times as long. The period becomes…'),
      options: [t2('2 倍', '2 times'), t2('4 倍', '4 times'), t2('一半', 'half')], answer: 0,
      why: [t2('对：T ∝ √L，√4 = 2。', 'Right: T ∝ √L and √4 = 2.'), t2('周期和摆长的平方根成正比。', 'The period goes with the square root of length.'), t2('摆长变长，周期变长。', 'Longer means a longer period.')] },
    { q: t2('摆角从 10° 加大到 20°，周期大约会？', 'Increase the swing from 10° to 20°. The period roughly…'),
      options: [t2('加倍', 'doubles'), t2('几乎不变（只长不到 1 %）', 'hardly changes (less than 1 % longer)'), t2('减半', 'halves')], answer: 1,
      why: [t2('小角度时周期和摆角几乎无关。', 'For small swings the period barely depends on the angle.'), t2('对：22° 以内误差小于 1 %；到 60° 才长约 7 %。', 'Right: under about 22° the change is below 1 %; at 60° it is about 7 % longer.'), t2('摆角变大只会让周期稍微变长。', 'A bigger swing only lengthens the period slightly.')] },
    { q: t2('把单摆带到月球（g 约是地球的 1/6），周期会？', 'Take the pendulum to the Moon (g about 1/6 of Earth\'s). The period…'),
      options: [t2('变短', 'gets shorter'), t2('不变', 'stays the same'), t2('变长约 2.4 倍', 'gets about 2.4 times longer')], answer: 2,
      why: [t2('g 变小，拉回来的力变小，摆得更慢。', 'Smaller g means a weaker pull back, so it swings more slowly.'), t2('周期和 g 有关：T = 2π√(L/g)。', 'The period depends on g: T = 2π√(L/g).'), t2('对：√6 ≈ 2.45。', 'Right: √6 ≈ 2.45.')] }
  ],
  teacher: (lang) => notes(lang, {
    objectives: [t2('说明单摆周期和质量无关', 'State that a pendulum\'s period does not depend on its mass'),
      t2('用 T = 2π√(L/g) 计算周期，说明小角度的条件', 'Use T = 2π√(L/g) and state the small-angle condition'), t2('说明阻尼让能量变成热', 'Explain damping as energy going to thermal stores')],
    misconceptions: [
      { option: 'a / b', wrong: t2('周期和摆锤质量有关', 'The period depends on the bob\'s mass'), right: t2('质量抵消，周期只看摆长和 g', 'Mass cancels; the period depends on length and g'),
        sources: [["Teacher guides only (no peer-reviewed prevalence found)", 'https://wardsworld.wardsci.com/k-5/ws-science-by-you-activity-pendulum-final-2'], ['PhET Pendulum Lab', 'https://phet.colorado.edu/en/simulations/pendulum-lab']] },
      { option: '—', wrong: t2('周期强烈依赖摆角（或完全无关）', 'The period depends strongly on the swing angle (or not at all)'), right: t2('小角度几乎无关；60° 时长约 7 %、90° 时长约 18 %', 'Almost independent for small swings; about 7 % longer at 60°, 18 % at 90°'),
        sources: [['PhET Pendulum Lab', 'https://phet.colorado.edu/en/simulations/pendulum-lab'], ['HyperPhysics', 'http://hyperphysics.phy-astr.gsu.edu/hbase/pendl.html']] }
    ],
    model: t2('完整非线性方程 θ″ = −(g/L) sin θ − bθ′，四阶 Runge–Kutta、步长 1/240 s（两分钟内能量误差 < 0.01 %）。周期由摆锤两次同方向通过最低点的时间差测得；精确理论值用 T = 2π√(L/g)/AGM(1, cos(θ₀/2))。',
      'Full nonlinear equation θ″ = −(g/L) sin θ − bθ′, 4th-order Runge–Kutta at 1/240 s (energy error < 0.01 % over two minutes). The period is measured between successive same-direction passes through the bottom; the exact value is T = 2π√(L/g)/AGM(1, cos(θ₀/2)).'),
    discussion: [t2('为什么物理老师 Walter Lewin 要亲自坐上大摆来示范？', 'Why did Walter Lewin swing on a giant pendulum himself to demonstrate this?'),
      t2('怎样用真实的单摆量出当地的 g？', 'How could you measure local g with a real pendulum?')]
  })
};

export const LESSONS = [bounce, launch, shot, collision, pendulum];
