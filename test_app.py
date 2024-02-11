import unittest
from app import app
import json

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_search_without_query(self):
        response = self.app.get('/search')
        self.assertEqual(response.status_code, 302)

    def test_search_with_query(self):
        response = self.app.get('/search?q=test')
        self.assertEqual(response.status_code, 200)

    def test_rss_without_query(self):
        response = self.app.get('/rss')
        self.assertEqual(response.status_code, 302)

    def test_rss_with_query(self):
        response = self.app.get('/rss?q=test')
        self.assertEqual(response.status_code, 200)

    def test_get_matches(self):
        response = self.app.get('/get-matches?q=test')
        self.assertEqual(response.status_code, 200)

    def test_analyze_content(self):
        response = self.app.post('/analyze-content', data=json.dumps({'content': 'test content'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
