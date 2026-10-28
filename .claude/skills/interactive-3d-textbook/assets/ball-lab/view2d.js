// 2D view: the diagram as black-ink SVG on white paper, the same primitives the 3D view draws.
// Light enough for old phones and printing; also the fallback when WebGL is unavailable.
const NS = 'http://www.w3.org/2000/svg';
const s = (tag, attrs = {}) => { const n = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v); return n; };

// one hue per energy store, used by bars, glow and the 3D view alike
export const STORE_COLOR = { kinetic: '#e8590c', potential: '#1c7ed6', lost: '#c2255c' };

export async function createView2D(host) {
  host.replaceChildren();
  const svg = s('svg', { class: 'diagram-2d', role: 'img', 'aria-hidden': 'true', preserveAspectRatio: 'xMidYMid meet' });
  const defs = s('defs');
  defs.innerHTML = `
    <filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="6"/></filter>
    <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="6" stroke="#222" stroke-width="1"/></pattern>`;
  svg.append(defs);
  const layer = s('g');
  svg.append(layer);
  host.append(svg);
  let W = 800, H = 450, map = null;

  function fit(b) {
    const pad = 40, sx = (W - 2 * pad) / (b.x1 - b.x0), sy = (H - 2 * pad) / (b.y1 - b.y0), k = Math.min(sx, sy);
    const ox = (W - k * (b.x1 - b.x0)) / 2, oy = (H - k * (b.y1 - b.y0)) / 2;
    map = { k, X: (x) => ox + (x - b.x0) * k, Y: (y) => H - oy - (y - b.y0) * k };
  }

  return {
    kind: '2d',
    setLesson(lesson, { animate }) {
      svg.classList.toggle('rise', !!animate);           // pop-up feel: the drawing rises in; skipped under reduced motion
      void svg.getBoundingClientRect(); svg.classList.add('ready');
    },
    draw(f) {
      const r = host.getBoundingClientRect();
      W = Math.max(320, r.width); H = Math.max(220, r.height);
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
      fit(f.bounds);
      const { X, Y, k } = map;
      layer.replaceChildren();
      const ink = { stroke: '#1a1a1a', 'stroke-width': 2, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
      if (f.floor != null) {
        layer.append(s('rect', { x: X(f.bounds.x0) - 20, y: Y(f.floor), width: W, height: 14, fill: 'url(#hatch)' }));
        layer.append(s('line', { x1: X(f.bounds.x0) - 20, y1: Y(f.floor), x2: W, y2: Y(f.floor), ...ink }));
      }
      for (const m of f.markers || []) {                  // height column: glows with the potential store
        const g = f.glow[m.store] || 0;
        if (g > 0) layer.append(s('rect', { x: X(m.x) - 6, y: Y(m.y1), width: 12, height: Math.max(0, Y(m.y0) - Y(m.y1)), fill: STORE_COLOR[m.store], opacity: 0.25 + 0.6 * g, filter: 'url(#glow)' }));
        layer.append(s('line', { x1: X(m.x), y1: Y(m.y0), x2: X(m.x), y2: Y(m.y1), ...ink, 'stroke-dasharray': '4 5' }));
        if (m.label) { const t = s('text', { x: X(m.x) + 8, y: (Y(m.y0) + Y(m.y1)) / 2, class: 'ink-label' }); t.textContent = m.label; layer.append(t); }
      }
      for (const tr of f.trails || []) {
        if (tr.points.length < 2) continue;
        layer.append(s('polyline', { points: tr.points.map(([x, y]) => `${X(x).toFixed(1)},${Y(y).toFixed(1)}`).join(' '), ...ink, 'stroke-width': 1.2, 'stroke-dasharray': tr.dashed ? '3 5' : '' }));
      }
      for (const rod of f.rods || []) {
        layer.append(s('line', { x1: X(rod.x1), y1: Y(rod.y1), x2: X(rod.x2), y2: Y(rod.y2), ...ink }));
        layer.append(s('circle', { cx: X(rod.x1), cy: Y(rod.y1), r: 4, fill: '#1a1a1a' }));
      }
      if (f.floor != null && f.glow.lost > 0) {           // warmed floor/air: the "lost" (thermal + sound) store
        layer.append(s('ellipse', { cx: X(f.heatX ?? 0), cy: Y(f.floor), rx: 40 + 60 * f.glow.lost, ry: 8, fill: STORE_COLOR.lost, opacity: 0.2 + 0.6 * f.glow.lost, filter: 'url(#glow)' }));
      }
      for (const b of f.balls) {
        const g = f.glow[b.store || 'kinetic'] || 0;
        const R = Math.max(4, b.r * k);
        if (g > 0) layer.append(s('circle', { cx: X(b.x), cy: Y(b.y), r: R * (1.2 + g), fill: STORE_COLOR[b.store || 'kinetic'], opacity: 0.3 + 0.6 * g, filter: 'url(#glow)' }));
        layer.append(s('circle', { cx: X(b.x), cy: Y(b.y), r: R, fill: '#fff', ...{ stroke: '#1a1a1a', 'stroke-width': 2 } }));
        layer.append(s('path', { d: `M ${X(b.x) - R * 0.55} ${Y(b.y) - R * 0.2} q ${R * 0.55} ${R * 0.45} ${R * 1.1} 0`, ...ink, 'stroke-width': 1 }));   // seam, so rolling/spin reads
        if (b.label) { const t = s('text', { x: X(b.x), y: Y(b.y) - R - 8, 'text-anchor': 'middle', class: 'ink-label' }); t.textContent = b.label; layer.append(t); }
      }
      for (const a of f.arrows || []) {
        const x1 = X(a.x), y1 = Y(a.y), x2 = X(a.x + a.dx), y2 = Y(a.y + a.dy);
        const ang = Math.atan2(y2 - y1, x2 - x1), h = 9;
        layer.append(s('line', { x1, y1, x2, y2, ...ink, 'stroke-width': 3 }));
        layer.append(s('path', { d: `M ${x2} ${y2} l ${-h * Math.cos(ang - 0.45)} ${-h * Math.sin(ang - 0.45)} M ${x2} ${y2} l ${-h * Math.cos(ang + 0.45)} ${-h * Math.sin(ang + 0.45)}`, ...ink, 'stroke-width': 3 }));
        if (a.label) { const t = s('text', { x: x2 + 6 * Math.sign(x2 - x1 || 1), y: y2 - 8, class: 'ink-label', 'text-anchor': x2 < x1 ? 'end' : 'start' }); t.textContent = a.label; layer.append(t); }
      }
    },
    destroy() { host.replaceChildren(); }
  };
}
