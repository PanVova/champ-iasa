# test_app.py
import json
import time
import unittest

import numpy as np
import requests

from app import app, wind_cartesian_to_polar


class TestRoutes(unittest.TestCase):
    """Testing Flask Routes"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_forecast_valid(self):
        response = self.app.get('/forecast?lat=40.7128&lon=-74.0060')
        self.assertEqual(response.status_code, 200)

    def test_get_forecast_invalid(self):
        response = self.app.get('/forecast?lat=abc&lon=xyz')
        self.assertEqual(response.status_code, 400)

    def test_get_suggestions_valid(self):
        response = self.app.get('/suggestions?city=New York')
        self.assertEqual(response.status_code, 200)


class TestUtilityFunctions(unittest.TestCase):
    """Testing Utility Functions"""

    def test_wind_cartesian_to_polar_basic(self):
        X, Y = 1, 1
        speed, direction = wind_cartesian_to_polar(X, Y)
        self.assertAlmostEqual(speed, np.sqrt(2))
        self.assertAlmostEqual(direction, 225)

    def test_wind_cartesian_to_polar_zero_values(self):
        X, Y = 0, 0
        speed, direction = wind_cartesian_to_polar(X, Y)
        self.assertEqual(speed, 0)
        self.assertEqual(direction, 270)

    def test_wind_cartesian_to_polar_negative_values(self):
        X, Y = -1, -1
        speed, direction = wind_cartesian_to_polar(X, Y)
        self.assertAlmostEqual(speed, np.sqrt(2))
        self.assertAlmostEqual(direction, 45)

    def test_wind_cartesian_to_polar_extreme_values(self):
        X, Y = 1000, 0
        speed, direction = wind_cartesian_to_polar(X, Y)
        self.assertEqual(speed, 1000)
        self.assertEqual(direction, 270)


class TestAPIIntegration(unittest.TestCase):
    """Testing API Integration"""

    def test_openmeteo_api_integration(self):
        response = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": 50.45466,
            "longitude": 30.5238,
            "daily": ["temperature_2m_max"]
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('daily', data)

    def test_openmeteo_api_response_format(self):
        response = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": 50.45466,
            "longitude": 30.5238,
            "daily": ["temperature_2m_max"]
        })
        data = response.json()
        self.assertIn('temperature_2m_max', data['daily'])

    def test_openmeteo_api_invalid_request(self):
        response = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": "invalid",
            "longitude": "invalid"
        })
        self.assertNotEqual(response.status_code, 200)

    def test_openmeteo_api_data_integrity(self):
        response = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": 50.45466,
            "longitude": 30.5238,
            "daily": ["temperature_2m_max", "precipitation_sum"]
        })
        data = response.json()
        self.assertTrue(all(key in data['daily'] for key in ['temperature_2m_max', 'precipitation_sum']))


class TestAPIPerformance(unittest.TestCase):
    """Testing API Request Performance"""

    def test_api_response_time(self):
        start_time = time.time()
        requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": 50.45466,
            "longitude": 30.5238,
            "daily": ["temperature_2m_max"]
        })
        end_time = time.time()

        # Test if the response time is less than a specified threshold, e.g., 5000 milliseconds
        self.assertTrue((end_time - start_time) < 5)


class TestCaching(unittest.TestCase):
    """Testing Caching Mechanism"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_forecast_caching(self):
        # First request
        first_response = self.app.get('/forecast?lat=40.7128&lon=-74.0060')
        first_data = json.loads(first_response.data)

        # Second request
        second_response = self.app.get('/forecast?lat=40.7128&lon=-74.0060')
        second_data = json.loads(second_response.data)

        # Check if the data from the first and second requests are the same, indicating caching
        self.assertEqual(first_data, second_data)

if __name__ == '__main__':
    unittest.main()
