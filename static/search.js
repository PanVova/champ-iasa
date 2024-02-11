const grid = document.querySelector('#search-results');
const spinnerSearchResults = document.querySelector('#spinner-search-results');
const inputQuery = document.querySelector('#input-query');
const inputDuration = document.querySelector('#input-duration');
const headingMatches = document.querySelector('#heading-matches');

inputQuery.value = searchData.query;
inputDuration.value = searchData.duration;

headingMatches.textContent = `Search results for "${inputQuery.value}"`;

getMatches()


function getMatches() {
    spinnerSearchResults.classList.remove('d-none');
    return fetch(`${url_get_matches}?q=${inputQuery.value}&duration=${inputDuration.value}`)
        .then(response => response.ok ? response.json() : Promise.reject(response))
        .then(data => {
            updateSearchResults(data)
            return data;
        })
        .then(data => {
            content = preprocessData(data)
            return fetch(`${url_analyze_content}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: content
                })
            })
        })
        .then(response => response.ok ? response.json() : Promise.reject(response))
        .then(data => updateAnalysis(data))
        .catch(error => console.error('Error:', error));
}


function updateSearchResults(data) {
    matches = data.articles;
    const searchResults = document.querySelector('#search-results');
    searchResults.innerHTML = '';

    matches.forEach(match => {
        const card = document.createElement('div');
        card.classList.add('grid-item');
        card.innerHTML = `
                    <div class="card">
                        ${match.urlToImage ? `<img src="${match.urlToImage}" class="card-img-top" alt="${match.title}">` : ''}
                        <div class="card-body">
                            <h5 class="card-title">${match.title}</h5>
                            <p class="card-text">${match.description}</p>
                            <a href="${match.url}" target="_blank" class="btn btn-primary">Read More</a>
                        </div>
                        <div class="card-footer text-body-secondary">
                            ${moment(match.publishedAt).fromNow()}
                        </div>
                    </div>
                `;
        searchResults.appendChild(card);
    });

    imagesLoaded(searchResults, function () {
        msnry = new Masonry(grid, {
            itemSelector: '.grid-item',
            columnWidth: 300,
            fitWidth: true,
            gutter: 20
        });

        msnry.on('layoutComplete', function () {
            spinnerSearchResults.classList.add('d-none');
        });

        msnry.layout();
    });
}


function updateAnalysis(data) {
    const alertAnalysis = document.querySelector('#alert-analysis');

    let sentimentScore = data['sentiment'] * 100;
    let sentimentLabel, barColor;
    if (sentimentScore > 66) {
        sentimentLabel = 'Positive';
        barColor = 'bg-success';
    } else if (sentimentScore < 33) {
        sentimentLabel = 'Negative';
        barColor = 'bg-danger';
    } else {
        sentimentLabel = 'Neutral';
        barColor = 'bg-warning';
    }

    let summaryHTML = `<div>${data['summary']}</div>`;

    let sentimentHTML = `
            <div><strong>${sentimentLabel}</strong></div>
            <div class="progress">
                <div class="progress-bar ${barColor}" role="progressbar" style="width: ${sentimentScore}%;" aria-valuenow="${sentimentScore}" aria-valuemin="0" aria-valuemax="100"></div>
            </div>`;

    let keywordsHTML = data['keywords'].map(keyword =>
        `<button type="button" class="btn btn-outline-primary mb-1" onclick="fillSearch('${keyword}')">${keyword}</button>`
    ).join(' ');

    alertAnalysis.innerHTML = `
            <h3>AI Analysis</h3>
            <h4>Summary</h4>
            ${summaryHTML}
            <h4>Sentiment</h4>
            ${sentimentHTML}
            <h4>Keywords</h4>
            <div>${keywordsHTML}</div>`;
}


function fillSearch(keyword) {
    const searchInput = document.querySelector('#input-query');
    searchInput.value = keyword;
}


function preprocessData(data) {
    let content = data['articles'].map(match => match.description).join(' ');
    return content;
}