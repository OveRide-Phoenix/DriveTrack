// script.js

document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
    const searchTerm = document.getElementById('search-input').value;
    searchFiles(searchTerm);
});

function searchFiles(searchTerm) {
    // Perform an AJAX request to the server to search for files with the given tag
    // Display search results in the #search-results container
    const searchResultsContainer = document.getElementById('search-results');
    searchResultsContainer.innerHTML = ''; // Clear previous search results
    // Example:
    const searchResult = document.createElement('div');
    searchResult.textContent = `Search results for tag: ${searchTerm}`;
    searchResultsContainer.appendChild(searchResult);
    // Add logic to fetch and display actual search results here
}
