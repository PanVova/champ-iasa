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

    const apiUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant&timezone=GMT`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const forecastData = processForecastData(data);
            updateForecastList(forecastData);
            spinnerForecastResults.classList.add('d-none');
        })
        .catch(error => console.error('Error fetching forecast:', error));
}

function processForecastData(data) {
    const forecast = data.daily;
    return forecast.time.map((date, index) => {
        return {
            date: date,
            temperatureMax: forecast.temperature_2m_max[index],
            temperatureMin: forecast.temperature_2m_min[index],
            precipitation: forecast.precipitation_sum[index],
            windSpeedMax: forecast.wind_speed_10m_max[index],
            windDirection: forecast.wind_direction_10m_dominant[index]
        };
    });
}

function updateForecastList(forecastData) {
    const forecastList = document.getElementById('forecast-list');
    forecastList.innerHTML = '';

    forecastData.forEach(dayForecast => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `Date: ${dayForecast.date}, Max Temp: ${dayForecast.temperatureMax}°C, Min Temp: ${dayForecast.temperatureMin}°C, Precipitation: ${dayForecast.precipitation}mm, Max Wind Speed: ${dayForecast.windSpeedMax}km/h, Wind Direction: ${dayForecast.windDirection}°`;
        forecastList.appendChild(listItem);
    });
}

document.addEventListener('click', function (event) {
    const cityInput = document.querySelector('#city');
    const citySuggestions = document.querySelector('#city-suggestions');
    if (!cityInput.contains(event.target) && !citySuggestions.contains(event.target)) {
        citySuggestions.classList.remove('show');
    }
});