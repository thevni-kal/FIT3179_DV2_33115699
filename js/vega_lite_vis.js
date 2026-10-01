const embedOptions = {
  actions: false,
  renderer: "svg"
};

for (let i = 1; i <= 11; i += 1) {
  vegaEmbed(`#vis${i}`, `js/chart${i}.json`, embedOptions)
    .catch(error => console.error(`Chart ${i} error:`, error));
}
