from django.test import TestCase
from learning_recommendation.api.views import index_page
# Create your tests here.


class predictTestCase():

    def test_prediction_correct(self):
        data = {
            "resource_access": 77,
            "announcements_view": 14,
            "abscence": 0,
            "discussion": 28,
            "raised_hands": 50
        }
        resp = self.client.post('/predict', data, format='json')
        
        self.assertEqual(resp.status_code, 200)

    def test_index_page(self):
        index = index_page({'test': 'testEP'})
        