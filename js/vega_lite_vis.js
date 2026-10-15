const embedOptions = { actions: false, renderer: "svg" };

// Keep the Vega view's native dimensions for readability when there is room,
// but shrink the SVG proportionally inside the white card on smaller screens.
function fitChartSvg(target) {
  const svg = target.querySelector('svg');
  if (!svg) return;
  const originalWidth = parseFloat(svg.getAttribute('width'));
  const originalHeight = parseFloat(svg.getAttribute('height'));
  if (!originalWidth || !originalHeight) return;
  if (!svg.hasAttribute('viewBox')) {
    svg.setAttribute('viewBox', `0 0 ${originalWidth} ${originalHeight}`);
  }
  svg.setAttribute('preserveAspectRatio', 'xMinYMin meet');
  svg.style.width = `min(100%, ${originalWidth}px)`;
  svg.style.height = 'auto';
  svg.style.maxWidth = '100%';
  svg.style.display = 'block';
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
