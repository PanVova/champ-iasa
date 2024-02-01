function getSuggestions() {
    const citySuggestions = document.querySelector('#city-suggestions');
    const inputCity = document.querySelector('#city');
    const inputLat = document.querySelector('#lat');
    const inputLon = document.querySelector('#lon');
    inputLat.value = '';
    inputLon.value = '';
    const city = inputCity.value;
    if (inputCity.value.length < 3) {
        return;
    }
    
    fetch(`${url_get_suggestions}?city=${city}`)
        .then(response => response.json())
        .then(data => {
            const suggestions = data.results;
            citySuggestions.innerHTML = '';
            if (!suggestions) {
                citySuggestions.classList.remove('show');
                return;
            }
            suggestions.forEach(suggestion => {
                const suggestionItem = document.createElement('li');
                const suggestionLink = document.createElement('a');
                suggestionLink.href = 'javascript:void(0)';
                suggestionItem.appendChild(suggestionLink);
                suggestionLink.className = 'dropdown-item';
                suggestionLink.innerText = `${suggestion.name}, ${suggestion.country}`;
                suggestionLink.setAttribute('data-lat', suggestion.latitude);
                suggestionLink.setAttribute('data-lon', suggestion.longitude);
                suggestionLink.onclick = () => {
                    inputCity.value = `${suggestion.name}, ${suggestion.country}`;
                    inputLat.value = suggestion.latitude;
                    inputLon.value = suggestion.longitude;
                    citySuggestions.classList.remove('show');
                };
                citySuggestions.appendChild(suggestionItem);
                citySuggestions.classList.add('show');
            });
        })
        .catch(error => console.error('Error fetching suggestions:', error));
}

function validateWeatherForm() {
    const lat = document.querySelector('#lat').value;
    const lon = document.querySelector('#lon').value;
    const alertCity = document.querySelector('#alert-city');

    if (!lat || !lon) {
        alertCity.classList.remove('d-none');
        return false;
    }

    alertCity.classList.add('d-none');
    getForecast(lat, lon);
    return false;
}

function getForecast(lat, lon) {
    const spinnerForecastResults = document.querySelector('#spinner-forecast-results');
    const headerCity = document.querySelector('#header-city');
    spinnerForecastResults.classList.remove('d-none');

    fetch(`${url_get_forecast}?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then((data) => {
            console.log(data);
            updateForecastList(
                processProphetForecast(data)
            )
            spinnerForecastResults.classList.add('d-none');
            headerCity.innerText = document.querySelector('#city').value;
        })
        .catch(error => console.error('Error fetching forecast:', error));
}

function processProphetForecast(data) {
    return data.map(entry => {
        return {
            date: new Date(entry.ds).toISOString().split('T')[0],
            temperatureMax: entry.temperature_max,
            temperatureMin: entry.temperature_min,
            precipitation: entry.precipitation,
            windSpeedMax: entry.wind_speed_max,
            windDirection: entry.wind_direction
        };
    });
}

function updateForecastList(forecastData) {
    const forecastList = document.querySelector('#forecast-list');
    forecastList.innerHTML = '';

    for (let i = 0; i < forecastData.length; i++) {
        const internalForecast = forecastData[i];

        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `
            <strong>Date:</strong> ${internalForecast.date}<br>
            Max Temp: ${internalForecast.temperatureMax}°C, Min Temp: ${internalForecast.temperatureMin}°C, Precipitation: ${internalForecast.precipitation}mm, Wind Speed: ${internalForecast.windSpeedMax}, Wind Direction: ${internalForecast.windDirection}`;

        forecastList.appendChild(listItem);
    }
}

document.addEventListener('click', function (event) {
    const cityInput = document.querySelector('#city');
    const citySuggestions = document.querySelector('#city-suggestions');
    if (!cityInput.contains(event.target) && !citySuggestions.contains(event.target)) {
        citySuggestions.classList.remove('show');
    }
});