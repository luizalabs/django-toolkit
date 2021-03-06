# -*- coding: utf-8 -*-
SECRET_KEY = 'test'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
MIDDLEWARE_CLASSES = (
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'oauth2_provider',

    'django_toolkit.oauth2',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'locks': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'access_token': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'explicit_timeout': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 300,
    },
}

TOOLKIT = {
    'API_VERSION': '1.2.3',
}
