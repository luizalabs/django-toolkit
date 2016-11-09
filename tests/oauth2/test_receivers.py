# -*- coding: utf-8 -*-
import pytest


@pytest.mark.django_db
class TestDeleteAccessTokenCache(object):

    def test_should_delete_token_cache(self, cache, access_token):
        key = 'my-token'
        access_token.token = key
        access_token.save()
        cache.set(key, 'a value')

        access_token.delete()

        assert cache.get(key) is None
