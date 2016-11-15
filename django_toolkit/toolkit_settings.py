from django.conf import settings

_toolkit_settings = getattr(settings, 'TOOLKIT', {})

ACCESS_TOKEN_CACHE_BACKEND = _toolkit_settings.get(
    'ACCESS_TOKEN_CACHE_BACKEND',
    'access_token'
)

API_VERSION = _toolkit_settings.get('API_VERSION')

MIDDLEWARE_ACCESS_LOG_FORMAT = _toolkit_settings.get(
    'MIDDLEWARE_ACCESS_LOG_FORMAT',
    u'[{app_name}] {response.status_code} {request.method} {request.path}'
)
