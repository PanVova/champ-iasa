$(document).ready(function () {
    //request for list of languages
    fetch('http://localhost:5000/languages')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            var languageSelect = $('#languageSelect');

            data.forEach(language => {
                languageSelect.append($('<option>', {
                    value: language,
                    text: language
                }));
            });
        })
        .catch(error => {
            console.error('Error fetching languages:', error);
        });

    // request for articles
    $('#searchButton').click(function () {
        var searchText = $('#searchText').val();
        var selectedLanguage = $('#languageSelect').val();

        var url = '/articles/' + encodeURIComponent(searchText) + '/' + encodeURIComponent(selectedLanguage);

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Log the received data to the console
                console.log('Received articles:', data);
                // Handle the received data accordingly
            })
            .catch(error => {
                console.error('Error fetching articles:', error);
            });
    });
});