# -*- coding: utf-8 -*-
from django.core.cache import caches
from django.utils import timezone
from oauth2_provider.models import AccessToken
from oauth2_provider.oauth2_validators import OAuth2Validator

from django_toolkit import toolkit_settings

cache = caches[toolkit_settings.ACCESS_TOKEN_CACHE_BACKEND]


class CachedOAuth2Validator(OAuth2Validator):

    def validate_bearer_token(self, token, scopes, request):
        if not token:
            return False

        try:
            access_token = self._get_access_token(token)
            if access_token.is_valid(scopes):
                request.client = access_token.application
                request.user = access_token.user
                request.scopes = scopes

                # this is needed by django rest framework
                request.access_token = access_token
                return True
            return False
        except AccessToken.DoesNotExist:
            return False

    def _get_access_token(self, token):
        access_token = cache.get(token)

        if access_token is None:
            access_token = AccessToken.objects.select_related(
                'application',
                'user'
            ).get(
                token=token
            )
            now = timezone.now()
            if (access_token.expires > now):
                timeout = (access_token.expires - now).seconds

                cache.set(token, access_token, timeout)

        return access_token
