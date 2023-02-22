from django.test import TestCase
from django.conf import settings
from pathlib import Path

class SettingsTest(TestCase):
    def test_secret_key(self):
        self.assertTrue(settings.SECRET_KEY)

    def test_debug(self):
        self.assertTrue(settings.DEBUG)

    def test_allowed_hosts(self):
        self.assertIn('*', settings.ALLOWED_HOSTS)

    def test_installed_apps(self):
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        self.assertIn('api', settings.INSTALLED_APPS)
        self.assertIn('corsheaders', settings.INSTALLED_APPS)

    def test_middleware(self):
        self.assertIn('django.middleware.security.SecurityMiddleware', settings.MIDDLEWARE)
        self.assertIn('corsheaders.middleware.CorsMiddleware', settings.MIDDLEWARE)
        self.assertIn('django.middleware.csrf.CsrfViewMiddleware', settings.MIDDLEWARE)

    def test_cors_origin_allow_all(self):
        self.assertTrue(settings.CORS_ORIGIN_ALLOW_ALL)

    def test_root_urlconf(self):
        self.assertEqual(settings.ROOT_URLCONF, 'learning_recommendation.urls')

    def test_template_dirs(self):
        self.assertEqual(settings.TEMPLATES[0]['DIRS'], [])

    def test_wsgi_application(self):
        self.assertEqual(settings.WSGI_APPLICATION, 'learning_recommendation.wsgi.application')

    def test_database(self):
        self.assertEqual(settings.DATABASES['default']['ENGINE'], 'django.db.backends.mysql')
        self.assertEqual(settings.DATABASES['default']['NAME'], 'staging_server')
        self.assertEqual(settings.DATABASES['default']['USER'], 'root')
        self.assertEqual(settings.DATABASES['default']['PASSWORD'], '1091997sc')
        self.assertEqual(settings.DATABASES['default']['HOST'], 'localhost')
        self.assertEqual(settings.DATABASES['default']['PORT'], '3306')
        self.assertEqual(settings.DATABASES['default']['OPTIONS'], {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"})

    def test_auth_password_validators(self):
        self.assertEqual(len(settings.AUTH_PASSWORD_VALIDATORS), 4)

    def test_static_files(self):
        self.assertEqual(settings.STATIC_URL, '/static/')
        self.assertEqual(settings.STATIC_ROOT, str(Path(settings.BASE_DIR, 'static')))