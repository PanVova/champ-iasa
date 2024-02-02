from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry
import tensorflow as tf
import numpy as np
import joblib

cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
forecast_cache = {}

lstm_year = tf.keras.models.load_model('models/lstm_year.hdf5')

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
    days_train = 3*365 + 2
    
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    cache_key = f"{lat},{lon},{days_train}"
    if cache_key in forecast_cache:
        print("Found cached forecast.")
        return jsonify(forecast_cache[cache_key])
    
    today = datetime.utcnow()
    end_date = today.strftime("%Y-%m-%d")
    years_before = today - timedelta(days=days_train)
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
                "forecast_days": 0,
                "date": end_date
            }
        }
    }
    
    
    df_archive = get_data(req['archive'])
    df_forecast = get_data(req['forecast'])
    df_archive.set_index('date', inplace=True)
    df_forecast.set_index('date', inplace=True)
    df = df_archive.combine_first(df_forecast)
    df.reset_index(inplace=True)
    
    df = df.iloc[-1095:]
    wind_direction_radians = np.radians(270 - df['wind_direction_10m_dominant'])
    df['wind_speed_10m_max_X'] = df['wind_speed_10m_max'] * np.cos(wind_direction_radians)
    df['wind_speed_10m_max_Y'] = df['wind_speed_10m_max'] * np.sin(wind_direction_radians)
    timestamp = df['date'].map(pd.Timestamp.timestamp)
    day = 24*60*60
    year = (365.2425)*day

    df['Year sin'] = np.sin(timestamp * (2 * np.pi / year))
    df['Year cos'] = np.cos(timestamp * (2 * np.pi / year))
    df.drop(columns=['wind_direction_10m_dominant', 'wind_speed_10m_max', 'date'], inplace=True)
    scaler = joblib.load('models/scaler.save')
    
    df = scaler.transform(df)
    df = np.expand_dims(df, axis=0)
    
    predictions = lstm_year.predict(df)
    predictions = predictions.reshape(365, 10)
    
    predictions = scaler.inverse_transform(predictions)
    
    
    columns = ['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum', 
           'relative_humidity_2m', 'pressure_msl', 'cloud_cover', 
           'wind_speed_10m_max_X', 'wind_speed_10m_max_Y', 
           'Year sin', 'Year cos']
    df = pd.DataFrame(predictions, columns=columns)
    
    df.drop(['Year sin', 'Year cos'], axis=1, inplace=True)

    start_date = 'YYYY-MM-DD'
    date_range = pd.date_range(start=end_date, periods=len(df), freq='D')

    df['date'] = date_range

    df = df[['date'] + [col for col in df.columns if col != 'date']]
    df['wind_speed_10m_max'], df['wind_direction_10m_dominant'] = wind_cartesian_to_polar(df['wind_speed_10m_max_X'], df['wind_speed_10m_max_Y'])
    df.drop(['wind_speed_10m_max_X', 'wind_speed_10m_max_Y'], axis=1, inplace=True)
    forecast_cache[cache_key] = df.to_dict(orient='records')
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


def wind_cartesian_to_polar(X, Y):
    speed = np.sqrt(X**2 + Y**2)
    dir_radians = np.arctan2(Y, X)
    dir_degrees = np.degrees(dir_radians)
    dir = (270 - dir_degrees) % 360
    return speed, dir
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
