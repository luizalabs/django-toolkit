# -*- coding: utf-8 -*-
import pytest
from mixer.backend.django import mixer
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model
)
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate

from django_toolkit import shortcuts

Application = get_application_model()
AccessToken = get_access_token_model()


@pytest.mark.django_db
class TestGetCurrentApp(object):

    @pytest.fixture
    def application(self):
        return mixer.blend(Application)

    @pytest.fixture
    def token(self, application):
        return mixer.blend(AccessToken, application=application)

    def test_should_return_the_client_applicaton(self, token):
        factory = APIRequestFactory()
        request = factory.get('/')
        force_authenticate(request, token=token)
        rest_request = Request(request)

        app = shortcuts.get_oauth2_app(rest_request)

        assert isinstance(app, Application)
        assert app == token.application

    def test_should_return_none_when_not_authenticated(self):
        factory = APIRequestFactory()
        request = factory.get('/')
        rest_request = Request(request)

        app = shortcuts.get_oauth2_app(rest_request)

        assert app is None
