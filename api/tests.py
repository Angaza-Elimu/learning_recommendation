from django.test import TestCase
from rest_framework.test import APITestCase
# import api
# Create your tests here.


class predictTestCase(APITestCase):
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



