
/**
 * Shows a loading spinner while FitFindr processes a search.
 */

const searchForm = document.getElementById("search-form");

// Only attach the listener on pages that contain the search form.
if (searchForm) {
    searchForm.addEventListener("submit", function () {
        const query = document.getElementById("query").value.trim();

        // Don't show the loader for an empty query.
        if (!query) {
            return;
        }

        document.getElementById("button-spinner").hidden = false;
        document.getElementById("button-text").textContent = "Searching...";
        document.getElementById("loading-message").hidden = false;

        // Prevent duplicate submissions while the request is running.
        document.getElementById("search-button").disabled = true;
    });
}
