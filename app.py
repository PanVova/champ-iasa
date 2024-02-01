from flask import Flask, render_template, request, jsonify
import requests
from prophet import Prophet
from prophet.plot import plot, plot_components
import pandas as pd
from datetime import datetime, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
forecast_cache = {}


app = Flask(__name__)


def get_data(request):
    url = request["url"]
    params = request["params"]
    responses = openmeteo.weather_api(url, params)
    response = responses[0]

    hourly = response.Hourly()
    hourly_relative_humidity_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_pressure_msl = hourly.Variables(1).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s"),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["pressure_msl"] = hourly_pressure_msl
    hourly_data["cloud_cover"] = hourly_cloud_cover

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dataframe.dropna(how="any", inplace=True)
    hourly_dataframe.set_index('date', inplace=True)
    aggregated_dataframe = hourly_dataframe.resample('D').mean()

    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()
    daily_wind_direction_10m_dominant = daily.Variables(4).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s"),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s"),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
    daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant

    daily_dataframe = pd.DataFrame(data = daily_data)
    daily_dataframe.dropna(how="any", inplace=True)
    
    df = daily_dataframe.join(aggregated_dataframe, on='date', how='inner')
    return df


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/forecast', methods=['GET'])
def get_forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    years_train = request.args.get('years_train', 3)
    
    if lat is None or lon is None:
        return jsonify({'error': 'Invalid coordinates'})
    
    cache_key = f"{lat},{lon},{years_train}"
    if cache_key in forecast_cache:
        return jsonify(forecast_cache[cache_key])
    
    today = datetime.utcnow()
    end_date = today.strftime("%Y-%m-%d")
    years_before = today - timedelta(days=365*years_train)
    start_date = years_before.strftime("%Y-%m-%d")
    
    req = {
        "archive": {
            "url": "https://archive-api.open-meteo.com/v1/archive",
            "params": {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "hourly": ["relative_humidity_2m", "pressure_msl", "cloud_cover"],
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"],
                "timezone": "GMT"
            }
        },
        "forecast": {
            "url": "https://api.open-meteo.com/v1/forecast",
            "params": {
                "latitude": lat,
                "longitude": lon,
                "hourly": ["relative_humidity_2m", "pressure_msl", "cloud_cover"],
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"],
                "timezone": "GMT",
                "past_days": 1,
                "forecast_days": 1
            }
        }
    }
    
    df_archive = get_data(req['archive'])
    df_forecast = get_data(req['forecast'])
    df_archive.set_index('date', inplace=True)
    df_forecast.set_index('date', inplace=True)
    df = df_archive.combine_first(df_forecast)
    df.reset_index(inplace=True)
    
    dataframes = {
        'temperature_max': pd.DataFrame({'ds': df['date'], 'y': df['temperature_2m_max']}),
        'temperature_min': pd.DataFrame({'ds': df['date'], 'y': df['temperature_2m_min']}),
        'precipitation': pd.DataFrame({'ds': df['date'], 'y': df['precipitation_sum']}),
        'wind_speed_max': pd.DataFrame({'ds': df['date'], 'y': df['wind_speed_10m_max']}),
        'wind_direction': pd.DataFrame({'ds': df['date'], 'y': df['wind_direction_10m_dominant']})
    }
    models = {}

    for param, df in dataframes.items():
        model = Prophet()
        model.fit(df)
        models[param] = model
        
    future = models['temperature_max'].make_future_dataframe(periods=6)
    
    forecasts = {}
    for param, model in models.items():
        forecasts[param] = model.predict(future)
    
    forecast_combined = future[['ds']].copy()

    for param, forecast in forecasts.items():
        forecast_combined[param] = forecast['yhat']
    
    last_7_forecast_combined = forecast_combined.tail(7)
    forecast_cache[cache_key] = last_7_forecast_combined.to_dict(orient='records')
    return jsonify(forecast_cache[cache_key])


@app.route('/suggestions', methods=['GET'])
def get_suggestions():
    city = request.args.get('city')
    url = f'https://geocoding-api.open-meteo.com/v1/search'
    response = requests.get(
        url,
        params={
            "name": city,
            "count": 10,
            "language": "en",
            "format": "json"
        }
    )
    return response.json()
    

if __name__ == '__main__':
    app.run(debug=True)
