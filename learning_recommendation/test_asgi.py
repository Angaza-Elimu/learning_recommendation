from django.test import TestCase
from learning_recommendation import asgi

class AsgiTest(TestCase):
    def test_application(self):
        self.assertTrue(callable(asgi.application))