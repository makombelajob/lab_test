const container = document.getElementById("load-timer");

// Récupère l'objet navigation (moderne)
function getNavigationTiming() {
    const [nav] = performance.getEntriesByType("navigation");
    return nav || null;
}

// Mettre à jour le temps total
const intervalId = setInterval(() => {
    const nav = getNavigationTiming();
    if (!nav) return;

    // temps total approximatif : loadEventEnd - startTime
    const tempsTotal = nav.loadEventEnd || performance.now(); // si loadEventEnd pas encore disponible

    container.textContent = `Temps de chargement : ${Math.round(tempsTotal)} ms`;

    if (document.readyState === "complete" && nav.loadEventEnd) {
        clearInterval(intervalId);
        container.textContent = `✅ Page chargée en ${Math.round(nav.loadEventEnd)} ms`;
    }
}, 100);

getNavigationTiming() 