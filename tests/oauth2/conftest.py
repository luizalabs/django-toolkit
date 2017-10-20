# -*- coding: utf-8 -*-
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.utils import timezone
from oauth2_provider.models import get_application_model

from django_toolkit.oauth2.compat import AccessToken


@pytest.fixture(autouse=True)
def cache():
    cache = caches['access_token']
    yield cache
    cache.clear()


@pytest.fixture
def scopes():
    return ['permission:read', 'permission:write']


@pytest.fixture
def user():
    UserModel = get_user_model()

    return UserModel.objects.create_user(
        'my-user', 'my@user.com', '123456'
    )


@pytest.fixture
def application(user):
    Application = get_application_model()
    application = Application.objects.first()

    if application:
        return application

    application = Application.objects.create(
        user=user,
        name='Test Application',
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
    )

    return application


@pytest.fixture
def access_token(application, scopes):
    return AccessToken.objects.create(
        scope=' '.join(scopes),
        expires=timezone.now() + timedelta(seconds=300),
        token='secret-access-token-key',
        application=application
    )
