import unittest
import requests
from app import wind_cartesian_to_polar
from app import app
import numpy as np
import json



class TestWindConversion(unittest.TestCase):
    
    def test_wind_cartesian_to_polar(self):
        X, Y = 1, 1
        speed, direction = wind_cartesian_to_polar(X, Y)
        self.assertAlmostEqual(speed, np.sqrt(2))
        self.assertAlmostEqual(direction, 225)



class TestForecast(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_forecast_endpoint(self):
        response = self.app.get('/forecast?lat=50.45466&lon=30.5238')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('temperature_2m_max', data[0])
    
    def test_forecast_error_handling(self):
        response = self.app.get('/forecast?lat=invalid&lon=invalid')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)



class TestOpenMeteoAPI(unittest.TestCase):
    
    def test_openmeteo_api_integration(self):
        response = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": 50.45466,
            "longitude": 30.5238,
            "daily": ["temperature_2m_max"]
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('daily', data)



if __name__ == '__main__':
    unittest.main()
