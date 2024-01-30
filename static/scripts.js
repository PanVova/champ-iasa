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
    const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=10&language=en&format=json`;

    fetch(url)
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
    spinnerForecastResults.classList.remove('d-none');

    fetch(`${url_get_forecast}?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then((data) => {
            console.log(data);
            updateForecastList(
                processProphetForecast(data['prophet_forecast']),
                processOpenMeteoForecast(data['open_meteo_forecast'])
            )
            spinnerForecastResults.classList.add('d-none');
        })
        .catch(error => console.error('Error fetching forecast:', error));
}

function processOpenMeteoForecast(data) {
    return data.time.map((date, index) => {
        return {
            date: date,
            temperatureMax: data.temperature_2m_max[index],
            temperatureMin: data.temperature_2m_min[index],
            precipitation: data.precipitation_sum[index],
            windSpeedMax: data.wind_speed_10m_max[index],
            windDirection: data.wind_direction_10m_dominant[index]
        };
    });
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

function updateForecastList(internalForecastData, externalForecastData) {
    const forecastList = document.getElementById('forecast-list');
    forecastList.innerHTML = '';

    for (let i = 0; i < internalForecastData.length; i++) {
        const internalForecast = internalForecastData[i];
        const externalForecast = externalForecastData[i];

        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `
            <strong>Date:</strong> ${internalForecast.date}<br>
            <strong>Prophet Forecast</strong> - Max Temp: ${internalForecast.temperatureMax}°C, Min Temp: ${internalForecast.temperatureMin}°C, Precipitation: ${internalForecast.precipitation}mm, Wind Speed: ${internalForecast.windSpeedMax}, Wind Direction: ${internalForecast.windDirection}<br>
            <strong>Open Meteo Forecast</strong> - Max Temp: ${externalForecast.temperatureMax}°C, Min Temp: ${externalForecast.temperatureMin}°C, Precipitation: ${externalForecast.precipitation}mm, Wind Speed: ${externalForecast.windSpeedMax}, Wind Direction: ${externalForecast.windDirection}
        `;

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