from flask import Flask, render_template, request, jsonify
import requests
from prophet import Prophet
from prophet.plot import plot, plot_components
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get-forecast', methods=['GET'])
def get_forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    years_train = request.args.get('years_train', 1)
    if lat is None or lon is None:
        return jsonify({'error': 'Invalid coordinates'})
    
    today = datetime.utcnow()
    end_date = today.strftime("%Y-%m-%d")
    years_before = today - timedelta(days=365*years_train)
    start_date = years_before.strftime("%Y-%m-%d")
    daily = 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant'
    
    response_archive = requests.get('https://archive-api.open-meteo.com/v1/archive', params={
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'daily': daily,
        'timezone': 'GMT'
    })
    data_archive = response_archive.json()
    
    response_forecast = requests.get('https://api.open-meteo.com/v1/forecast', params={
        'latitude': lat,
        'longitude': lon,
        'daily': daily,
        'timezone': 'GMT',
        'past_days': 2,
        'forecast_days': 7
    })
    data_forecast = response_forecast.json()
    data_forecast_past = {key: values[:2] for key, values in data_forecast['daily'].items()}
    data_forecast_future = {key: values[2:] for key, values in data_forecast['daily'].items()}
    
    for key in data_archive['daily']:
        if key != 'time':
            for i in range(2):
                data_archive['daily'][key][-i-1] = data_forecast_past[key][-i-1]
    
    dataframes = {
        'temperature_max': pd.DataFrame({'ds': data_archive['daily']['time'], 'y': data_archive['daily']['temperature_2m_max']}),
        'temperature_min': pd.DataFrame({'ds': data_archive['daily']['time'], 'y': data_archive['daily']['temperature_2m_min']}),
        'precipitation': pd.DataFrame({'ds': data_archive['daily']['time'], 'y': data_archive['daily']['precipitation_sum']}),
        'wind_speed_max': pd.DataFrame({'ds': data_archive['daily']['time'], 'y': data_archive['daily']['wind_speed_10m_max']}),
        'wind_direction': pd.DataFrame({'ds': data_archive['daily']['time'], 'y': data_archive['daily']['wind_direction_10m_dominant']})
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
    return jsonify({
        'prophet_forecast': last_7_forecast_combined.to_dict(orient='records'),
        'open_meteo_forecast': data_forecast_future
    })

if __name__ == '__main__':
    app.run(debug=True)
