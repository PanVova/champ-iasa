$(document).ready(function () {
	$.ajax({
		url: 'http://localhost:5000/languages', // Your endpoint to fetch languages
		type: 'GET',
		success: function (data) {
			var languageSelect = $('#languageSelect');
			// Populate the combobox with fetched languages
			$.each(data, function (index, language) {
				languageSelect.append($('<option>', {
					value: language, // Use language itself as both value and text
					text: language
				}));
			});
		},
		error: function (xhr, status, error) {
			console.error('Error fetching languages:', error);
		}
	});

	$('#searchButton').click(function () {
		var searchText = $('#searchText').val();
		var selectedLanguage = $('#languageSelect').val();

		
	});
});