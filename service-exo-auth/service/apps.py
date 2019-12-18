# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'health_check',
    'django.contrib.staticfiles',
    'exo_auth.apps.ExoAuthConfig',
    'rest_framework',
    'drf_yasg',
    'guardian',
    'corsheaders',
    'django_celery_results',
    'populate',
    'dj_anonymizer',
    'exo_changelog',
]
