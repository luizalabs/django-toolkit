Oauth2
======

Oauth2 is a django app that will can be used to cache your `django-oauth-toolkit`
access token model.


Usage
-----
To start caching your api access tokens, add `django_toolkit.oauth2` to your
`INSTALLED_APPS` and then add the oauth2 validator class in the `OAUTH2_PROVIDER`
settings.


Example:
```python
OAUTH2_PROVIDER = {
    'OAUTH2_VALIDATOR_CLASS': 'django_toolkit.oauth2.validators.CachedOAuth2Validator',
}
```

You can specify wich cache you want to use by setting the cache name
in the `TOOLKIT` settings variable. If no name is specified, `access_token` will be used.
Example:
```python
# toolkit settings
TOOLKIT = {
    'ACCESS_TOKEN_CACHE_BACKEND': 'access_token'
}

# django cache settings
CACHES = {
    'access_token': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'KEY_PREFIX': 'token',
    }
}
```