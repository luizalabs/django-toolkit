# -*- coding: utf-8 -*-
from django.apps import AppConfig


class OAuth2AppConfig(AppConfig):
    name = 'django_toolkit.oauth2'
    verbose_name = 'OAuth2'

    def ready(self):
        super(OAuth2AppConfig, self).ready()
        from . import receivers  # noqa
