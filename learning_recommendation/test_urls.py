from django.test import SimpleTestCase
from django.urls import reverse, resolve
from api import views
from . import urls

class TestUrls(SimpleTestCase):

    def test_admin_url_resolves(self):
        url = reverse('admin')
        self.assertEqual(resolve(url).func, admin.site.urls)

    def test_api_url_resolves(self):
        url = reverse('api')
        self.assertEqual(resolve(url).func.view_class, views.APIView)