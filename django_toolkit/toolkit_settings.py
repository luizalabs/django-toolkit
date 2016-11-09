from django.conf import settings

_toolkit_settings = getattr(settings, 'TOOLKIT', {})

ACCESS_TOKEN_CACHE_BACKEND = _toolkit_settings.get(
    'ACCESS_TOKEN_CACHE_BACKEND',
    'access_token'
)
