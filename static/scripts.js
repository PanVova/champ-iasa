const grid = document.querySelector('#search-results');

function getMatches(query) {
    fetch(`${url_get_matches}?q=${query}`)
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw err;
                });
            }
            return response.json();
        })
        .then(data => {
            updateSearchResults(data.articles);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


function validateSearchForm() {
    const query = document.querySelector('#input-query').value;
    const alertSearch = document.querySelector('#alert-search');

    if (!query) {
        alertSearch.classList.remove('d-none');
        return false;
    }

    alertSearch.classList.add('d-none');
    getMatches(query);
    return false;
}


function updateSearchResults(matches) {
    const searchResults = document.querySelector('#search-results');
    searchResults.innerHTML = '';
    matches.forEach(match => {
        const card = document.createElement('div');
        card.classList.add('grid-item');
        let imageHtml = '';
        if (match.urlToImage) {
            imageHtml = `<img src="${match.urlToImage}" class="card-img-top" alt="${match.title}">`;
        }
        const relativeDate = moment(match.publishedAt).fromNow();
        card.innerHTML = `
            <div class="card">
                ${imageHtml}
                <div class="card-body">
                    <h5 class="card-title">${match.title}</h5>
                    <p class="card-text">${match.description}</p>
                    <a href="${match.url}" target="_blank" class="btn btn-primary">Read More</a>
                </div>
                <div class="card-footer text-body-secondary">
                    ${relativeDate}
                </div>
            </div>
        `;

        searchResults.appendChild(card);
    });
    imagesLoaded(grid, function () {
        new Masonry(grid, {
            itemSelector: '.grid-item',
            columnWidth: 300,
            fitWidth: true,
            gutter: 20
        });
    });
}