const embedOptions = { actions: false, renderer: "svg" };

// The viewBox is set from the original Vega drawing dimensions, then the
// entire drawing (including axes, legends and labels) is scaled to the card.
function fitChartSvg(target) {
  const svg = target.querySelector('svg');
  if (!svg) return;
  const nativeWidth = Number(svg.getAttribute('width')) || svg.getBoundingClientRect().width;
  const nativeHeight = Number(svg.getAttribute('height')) || svg.getBoundingClientRect().height;
  if (!(nativeWidth > 0 && nativeHeight > 0)) return;
  svg.setAttribute('viewBox', `0 0 ${nativeWidth} ${nativeHeight}`);
  svg.setAttribute('preserveAspectRatio', 'xMinYMin meet');
  const container = target.closest('.chart-wrap') || target;
  const resize = () => {
    const available = Math.max(1, container.clientWidth - 2);
    const renderedWidth = Math.min(nativeWidth, available);
    svg.style.setProperty('width', `${renderedWidth}px`, 'important');
    svg.style.setProperty('height', `${renderedWidth * nativeHeight / nativeWidth}px`, 'important');
    svg.style.setProperty('max-width', '100%', 'important');
    svg.style.display = 'block';
  };
  resize();
  if (typeof ResizeObserver !== 'undefined') {
    const observer = new ResizeObserver(resize);
    observer.observe(container);
  } else window.addEventListener('resize', resize);
}

for (let i = 1; i <= 14; i += 1) {
  const target = document.querySelector(`#vis${i}`);
  if (!target) continue;
  vegaEmbed(`#vis${i}`, `js/chart${i}.json`, embedOptions)
    .then(() => fitChartSvg(target))
    .catch(error => {
      console.error(`Chart ${i} error:`, error);
      target.innerHTML = `<div class="chart-error">Visualisation ${i} could not be loaded. Check the browser console for details.</div>`;
    });
}
