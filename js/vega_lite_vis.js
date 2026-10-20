const embedOptions = { actions: false, renderer: 'svg' };
// Fit the *complete* Vega drawing, including text that extends beyond the SVG's
// original viewBox. Simply hiding overflow cropped labels in earlier versions.
function fitChart(target) {
  const svg = target.querySelector('svg');
  if (!svg) return;
  const holder = target.closest('.chart-wrap') || target;
  const nativeW = Number(svg.getAttribute('width')) || 900;
  const nativeH = Number(svg.getAttribute('height')) || 550;
  let x = 0, y = 0, w = nativeW, h = nativeH;
  try {
    const bounds = svg.getBBox();
    if (bounds && bounds.width > 0 && bounds.height > 0) {
      const padding = 12;
      x = Math.min(0, bounds.x - padding);
      y = Math.min(0, bounds.y - padding);
      w = Math.max(nativeW, bounds.x + bounds.width + padding) - x;
      h = Math.max(nativeH, bounds.y + bounds.height + padding) - y;
    }
  } catch (e) { /* Use the SVG dimensions if getBBox is unavailable. */ }
  svg.setAttribute('viewBox', `${x} ${y} ${w} ${h}`);
  svg.setAttribute('preserveAspectRatio', 'xMidYMin meet');
  svg.removeAttribute('width');
  svg.removeAttribute('height');
  svg.style.setProperty('display', 'block', 'important');
  svg.style.setProperty('width', `min(100%, ${Math.ceil(w)}px)`, 'important');
  svg.style.setProperty('height', 'auto', 'important');
  svg.style.setProperty('max-width', '100%', 'important');
  svg.style.setProperty('aspect-ratio', `${w} / ${h}`, 'important');
  const outer = target.querySelector('.vega-embed');
  if (outer) {
    outer.style.setProperty('width', '100%', 'important');
    outer.style.setProperty('display', 'flex', 'important');
    outer.style.setProperty('flex-direction', 'column', 'important');
    outer.style.setProperty('align-items', 'center', 'important');
    outer.style.setProperty('max-width', '100%', 'important');
    outer.style.setProperty('min-width', '0', 'important');
  }
  // Vega sometimes wraps SVG in a width-constrained div.
  const parent = svg.parentElement;
  if (parent) {
    parent.style.setProperty('width', '100%', 'important');
    parent.style.setProperty('display', 'flex', 'important');
    parent.style.setProperty('justify-content', 'center', 'important');
    parent.style.setProperty('max-width', '100%', 'important');
    parent.style.setProperty('min-width', '0', 'important');
  }
}
for (let i = 1; i <= 14; i++) {
  const target = document.querySelector(`#vis${i}`);
  if (!target) continue;
  vegaEmbed(target, `js/chart${i}.json?v=20261020-data-sources`, embedOptions)
    .then(() => {
      fitChart(target);
      // Web fonts may load after the initial SVG layout.
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => fitChart(target));
    })
    .catch(error => {
      console.error(`Chart ${i} error`, error);
      target.textContent = `Visualisation ${i} could not be loaded. Please refresh.`;
    });
}
