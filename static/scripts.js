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
            data_processed = processForecast(data)
            console.log(data_processed)
            updateForecastList(data_processed)
            spinnerForecastResults.classList.add('d-none');
            headerCity.innerText = document.querySelector('#city').value;
        })
        .catch(error => console.error('Error fetching forecast:', error));
}

function processForecast(data) {
    return data.map(entry => {
        return {
            date: formatDate(entry.date),
            temperatureMax: Math.round(entry.temperature_2m_max),
            temperatureMin: Math.round(entry.temperature_2m_min),
            precipitation: Math.round(entry.precipitation_sum),
            windSpeedMax: Math.round(entry.wind_speed_10m_max),
            windDirection: Math.round(entry.wind_direction_10m_dominant),
            cloudCover: Math.round(entry.cloud_cover),
            pressure: Math.round(entry.pressure_msl),
            relativeHumidity: Math.round(entry.relative_humidity_2m)
        };
    });
}

function formatDate(dateString) {
    const options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
    const formattedDate = new Date(dateString).toLocaleDateString('en-US', options);
    return formattedDate;
}

function updateForecastList(forecastData) {
    const forecastList = document.querySelector('#forecast-table tbody');
    forecastList.innerHTML = ''

    for (let i = 0; i < forecastData.length; i++) {
        const forecast = forecastData[i];

        const listItem = document.createElement('tr');
        listItem.className = 'forecast-item';

        const dateItem = document.createElement('td');
        dateItem.className = 'forecast-date'
        dateItem.innerHTML = `${forecast.date}`

        const temperatureItem = document.createElement('td');
        temperatureItem.className = 'forecast-temperature'

        const temperatureMaxItem = document.createElement('span');
        temperatureMaxItem.className = 'forecast-temperature-max'
        temperatureMaxItem.innerHTML = `${forecast.temperatureMax}°`

        const temperatureMinItem = document.createElement('span');
        temperatureMinItem.className = 'forecast-temperature-min'
        temperatureMinItem.innerHTML = `/${forecast.temperatureMin}°`

        temperatureItem.appendChild(temperatureMaxItem)
        temperatureItem.appendChild(temperatureMinItem)

        const relativeHumidityItem = document.createElement('td');
        relativeHumidityItem.className = 'forecast-relative-humidity'
        relativeHumidityItem.innerHTML = `<img class="icon" src="/static/icons/humidity.svg" alt="Humidity">${forecast.relativeHumidity}%`

        const windItem = document.createElement('td');
        windItem.className = 'forecast-wind'
        windItem.innerHTML = `<img class="icon" src="/static/icons/wind.svg" alt="Wind">${forecast.windSpeedMax} km/h, ${forecast.windDirection}°`

        const pressureItem = document.createElement('td');
        pressureItem.className = 'forecast-pressure'
        pressureItem.innerHTML = `${forecast.pressure} hPa`

        listItem.appendChild(dateItem)
        listItem.appendChild(temperatureItem)
        listItem.appendChild(relativeHumidityItem)
        listItem.appendChild(windItem)
        listItem.appendChild(pressureItem)

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