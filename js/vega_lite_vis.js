const embedOptions = {
  actions: false,
  renderer: "svg"
};

// =====================================================
// VISUALISATION 1
// =====================================================
vegaEmbed("#vis1", "js/chart1.json", embedOptions)
  .catch(error => {
    console.error("Chart 1 error:", error);
  });


// =====================================================
// VISUALISATION 2
// =====================================================
vegaEmbed("#vis2", "js/chart2.json", embedOptions)
  .catch(error => {
    console.error("Chart 2 error:", error);
  });


// =====================================================
// VISUALISATION 3
// =====================================================
vegaEmbed("#vis3", "js/chart3.json", embedOptions)
  .catch(error => {
    console.error("Chart 3 error:", error);
  });


// =====================================================
// VISUALISATION 4
// =====================================================
vegaEmbed("#vis4", "js/chart4.json", embedOptions)
  .catch(error => {
    console.error("Chart 4 error:", error);
  });


// =====================================================
// VISUALISATION 5
// =====================================================
vegaEmbed("#vis5", "js/chart5.json", embedOptions)
  .catch(error => {
    console.error("Chart 5 error:", error);
  });


// =====================================================
// VISUALISATION 6
// PRE-1750 VEGETATION MAP
// =====================================================
vegaEmbed("#vis6", "js/chart6.json", embedOptions)
  .catch(error => {
    console.error("Chart 6 error:", error);
  });


// =====================================================
// VISUALISATION 7
// PRE-1750 VS EXTANT VEGETATION
// =====================================================
vegaEmbed("#vis7", "js/chart7.json", embedOptions)
  .catch(error => {
    console.error("Chart 7 error:", error);
  });


// =====================================================
// VISUALISATION 8
// VEGETATION GROUP CHANGE
// =====================================================
vegaEmbed("#vis8", "js/chart8.json", embedOptions)
  .catch(error => {
    console.error("Chart 8 error:", error);
  });