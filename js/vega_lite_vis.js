const embedOptions = {
  actions: false,
  renderer: "svg"
};

for (let i = 1; i <= 14; i += 1) {
  const target = document.querySelector(`#vis${i}`);
  if (!target) continue;

  vegaEmbed(`#vis${i}`, `js/chart${i}.json`, embedOptions)
    .catch(error => {
      console.error(`Chart ${i} error:`, error);
      target.innerHTML = `<div class="chart-error">Visualisation ${i} could not be loaded. Check the browser console for details.</div>`;
    });
}
