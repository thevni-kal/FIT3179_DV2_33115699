const embedOptions = {
  actions: false,
  renderer: "svg"
};


// Visualisation 1
vegaEmbed("#vis1", "js/chart1.json", embedOptions)
  .catch(error => console.error("Chart 1 error:", error));


// Visualisation 2
vegaEmbed("#vis2", "js/chart2.json", embedOptions)
  .catch(error => console.error("Chart 2 error:", error));


// Visualisation 3
vegaEmbed("#vis3", "js/chart3.json", embedOptions)
  .catch(error => console.error("Chart 3 error:", error));


// Visualisation 4
vegaEmbed("#vis4", "js/chart4.json", embedOptions)
  .catch(error => console.error("Chart 4 error:", error));


// Visualisation 5
vegaEmbed("#vis5", "js/chart5.json", embedOptions)
  .catch(error => console.error("Chart 5 error:", error));