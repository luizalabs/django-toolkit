# -*- coding: utf-8 -*-
# flake8: noqa

try:
    from oauth2_provider.models import get_access_token_model
    AccessToken = get_access_token_model()
except ImportError:
    from oauth2_provider.models import AccessToken
