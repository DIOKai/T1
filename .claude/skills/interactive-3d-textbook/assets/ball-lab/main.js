// Wires the page: lessons + loop + 2D/3D view. 3D loads only when asked for (or ?view=3d),
// and the page falls back to 2D when WebGL or the three.js modules are unavailable.
import { createLesson } from './loop.js';
import { createView2D } from './view2d.js';
import { LESSONS } from './lessons.js';

const $ = (id) => document.getElementById(id);
const TEXT = {
  bookTitle: { zh: '球的实验课本', en: 'The Ball Lab' },
  lock: { zh: '锁定我的预测', en: 'Lock my prediction' }, locked: { zh: '预测已锁定', en: 'Prediction locked' },
  lockedNow: { zh: '预测已锁定，现在可以做实验了。', en: 'Prediction locked. You can run the experiment now.' },
  sureQ: { zh: '你有多肯定？', en: 'How sure are you?' }, sure: { zh: '很肯定', en: 'Sure' }, unsure: { zh: '不太肯定', en: 'Not sure' },
  run: { zh: '开始实验', en: 'Run' }, running: { zh: '实验中…', en: 'Running…' }, again: { zh: '再做一次', en: 'Run again' },
  skip: { zh: '直接看结果', en: 'Show result' }, reset: { zh: '重来', en: 'Reset' },
  flap: { zh: '掀开看为什么 ↓', en: 'Lift the flap: why? ↓' },
  right: { zh: '和你预测的一样。下面是原因：', en: 'Just as you predicted. Here is why:' },
  surprised: { zh: '意外吗？来看看为什么。', en: "Surprised? Here's why." },
  ignoresTitle: { zh: '这个模型没算进去的：', en: 'What this model ignores:' },
  stamped: { zh: '盖章：', en: 'Stamp:' }, predictedRight: { zh: '预测正确', en: 'Predicted right' }, close: { zh: '收起', en: 'Hide' },
  slow: { zh: '慢动作：时间以 {x} 倍速度播放', en: 'Slow motion: time runs at {x}×' },
  showBars: { zh: '显示能量条', en: 'Show energy bars' }, showGraph: { zh: '显示图表', en: 'Show graph' },
  total: { zh: '总能量', en: 'Total' },
  store: { kinetic: { zh: '动能', en: 'Kinetic' }, potential: { zh: '重力势能', en: 'Gravitational' }, lost: { zh: '热能和声音', en: 'Thermal + sound' } },
  moreTitle: { zh: '再多玩一点', en: 'Explore more' }, quizTitle: { zh: '小测验', en: 'Quick quiz' },
  teacherTitle: { zh: '教师笔记', en: 'Teacher notes' }, angle: { zh: '换个角度', en: 'Turn the view' },
  no3d: { zh: '这台设备开不了 3D，已改用 2D。', en: "3D isn't available on this device, so the 2D view is shown." }
};

const ui = {
  text: TEXT, tabs: $('tabs'), title: $('title'), hook: $('hook'), question: $('question'), options: $('options'), sureRow: $('sureRow'),
  lock: $('lock'), controls: $('controls'), more: $('more'), moreBox: $('moreBox'), moreIntro: $('moreIntro'),
  run: $('run'), skip: $('skip'), resetBtn: $('resetBtn'), flapBtn: $('flapBtn'), flap: $('flap'), explain: $('explain'),
  ignores: $('ignores'), speedNote: $('speedNote'), readouts: $('readouts'), bars: $('bars'), graph: $('graph'), graphLabel: $('graphLabel'),
  canvasHost: $('canvasHost'), desc: $('desc'), live: $('live'), stamp: $('stamp'), stampText: $('stampText'), stampMark: $('stampMark'),
  stampClose: $('stampClose'), quiz: $('quiz'), quizBox: $('quizBox'), teacher: $('teacher'), langBtns: [...document.querySelectorAll('.lang')]
};

const params = new URLSearchParams(location.search);
const startLang = params.get('lang') === 'en' ? 'en' : 'zh';
ui.langBtns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === startLang)));

async function make3D(host) {
  const { createView3D } = await import('./view3d.js');
  return createView3D(host);
}

let current = '2d';
const lesson = createLesson({ lessons: LESSONS, ui, lang: startLang, makeView: createView2D });
await lesson.init();

async function setView(kind) {
  if (kind === current) return;
  try {
    await lesson.switchView(kind === '3d' ? make3D : createView2D);
    current = kind;
    $('viewNote').textContent = '';
  } catch (e) {
    console.warn('3D unavailable:', e);
    await lesson.switchView(createView2D);
    current = '2d';
    $('viewNote').textContent = TEXT.no3d[lesson.state.lang];
  }
  $('view2d').setAttribute('aria-pressed', String(current === '2d'));
  $('view3d').setAttribute('aria-pressed', String(current === '3d'));
  $('angle').hidden = current !== '3d';
}
$('view2d').addEventListener('click', () => setView('2d'));
$('view3d').addEventListener('click', () => setView('3d'));
$('angle').addEventListener('click', () => lesson.state.view.nextAngle?.());
if (params.get('view') === '3d') await setView('3d');
