const embedOptions = {
  actions: false,
  renderer: "svg"
};

vegaEmbed("#vis1", "js/chart1.json", embedOptions)
  .catch(error => console.error("Chart 1 error:", error));

vegaEmbed("#vis2", "js/chart2.json", embedOptions)
  .catch(error => console.error("Chart 2 error:", error));

vegaEmbed("#vis3", "js/chart3.json", embedOptions)
  .catch(error => console.error("Chart 3 error:", error));

vegaEmbed("#vis4", "js/chart4.json", embedOptions)
  .catch(error => console.error("Chart 4 error:", error));