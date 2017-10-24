# -*- coding: utf-8 -*-
from datetime import timedelta

import pytest
from django.db import connection
from django.db.models.query import QuerySet
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from oauth2_provider.models import get_access_token_model

from django_toolkit.oauth2.validators import CachedOAuth2Validator


@pytest.mark.django_db
class TestCachedOAuth2Validator(object):

    @pytest.fixture
    def validator(self):
        return CachedOAuth2Validator()

    @pytest.fixture
    def http_request(self, rf):
        return rf.get('/foo')

    def _warm_up_cache(self, validator, token, scopes, request):
        return validator.validate_bearer_token(token, scopes, request)

    def test_validate_bearer_token_should_not_reach_db_when_cached(
        self,
        access_token,
        validator,
        http_request,
        scopes
    ):
        db_result = self._warm_up_cache(
            validator,
            access_token.token,
            scopes,
            http_request
        )

        with CaptureQueriesContext(connection) as context:
            cached_result = validator.validate_bearer_token(
                access_token.token,
                scopes,
                http_request
            )

        assert len(context.captured_queries) == 0
        assert db_result == cached_result

    def test_validate_bearer_token_should_set_request_attributes(
        self,
        access_token,
        validator,
        scopes,
        rf
    ):
        self._warm_up_cache(
            validator,
            access_token.token,
            scopes,
            rf.get('/foo')
        )

        request = rf.get('/foo')
        validator.validate_bearer_token(
            access_token.token,
            scopes,
            request
        )

        assert request.client == access_token.application
        assert request.user == access_token.user
        assert request.scopes == scopes
        assert request.access_token == access_token

    def test_validate_bearer_token_should_get_cache_expiration_from_token(
        self,
        access_token,
        validator,
        scopes,
        http_request
    ):
        expires = timezone.now() - timedelta(seconds=5)
        access_token.expires = expires
        access_token.save()

        self._warm_up_cache(
            validator,
            access_token.token,
            scopes,
            http_request
        )

        with CaptureQueriesContext(connection) as context:
            validator.validate_bearer_token(
                access_token.token,
                scopes,
                http_request
            )

        assert len(context.captured_queries) == 1

    def test_validate_bearer_returns_false_when_no_token_is_provided(
        self,
        validator,
        scopes,
        http_request
    ):
        token = None
        is_valid = validator.validate_bearer_token(
            token,
            scopes,
            http_request
        )
        assert not is_valid

    def test_validate_bearer_returns_false_when_invalid_token_is_provided(
        self,
        validator,
        scopes,
        http_request
    ):
        token = 'invalid-token'
        is_valid = validator.validate_bearer_token(
            token,
            scopes,
            http_request
        )
        assert not is_valid

    def test_get_queryset_should_return_an_access_token_queryset(
        self,
        validator,
    ):
        queryset = validator.get_queryset()

        assert isinstance(queryset, QuerySet)
        assert queryset.model == get_access_token_model()
