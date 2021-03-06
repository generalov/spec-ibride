"""Django settings for spec_ibride project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from distutils.util import strtobool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# for x, y in sorted(os.environ.items(), key=lambda x: x[0]): print x, y

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yr5_gb8t!zmefdw2wr8laotc0h*g0i-rg1sbjs-zyvo(smc-@s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(os.environ.get('DJANGO_DEBUG', 'false'))

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (app_name for app_name in (
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',

    'favicon',
    'debug_toolbar' if DEBUG else '',
    'django_extensions',
    'linaro_django_pagination',
    'webpack_loader',

    'spec_ibride.gallery',
) if app_name)

MIDDLEWARE_CLASSES = (
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'spec_ibride.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'spec_ibride.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_ENV_MYSQL_DATABASE'),
        'USER': os.environ.get('DB_ENV_MYSQL_USER'),
        'PASSWORD': os.environ.get('DB_ENV_MYSQL_PASSWORD'),
        'HOST': 'db',
        'PORT': '3306',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
USE_X_FORWARDED_HOST = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    '/app/static/assets',
)
STATIC_ROOT = '/app/static-web'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'assets/',  # must end with slash
        'STATS_FILE': '/app/static/webpack-stats.json',
        'POLL_INTERVAL': 0.1,
        'IGNORE': ['.+\.hot-update.js', '.+\.map']
    }
}

# Docker container defaults
# pylint:disable=unused-wildcard-import,import-error,no-name-in-module
# from ixdjango.docker_settings import *
# pylint:enable=unused-wildcard-import,import-error,no-name-in-module

# Trust nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allowed hosts, Site domain and URL
ALLOWED_HOSTS = ['*']

if DEBUG:
    def show_toolbar(request):
        print('IP Address for debug-toolbar: ' + request.META['REMOTE_ADDR'])
        return True

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    }

    SHOW_TOOLBAR_CALLBACK = show_toolbar
