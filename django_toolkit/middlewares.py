# -*- coding: utf-8 -*-
from django.conf import settings


class VersionHeaderMiddleware(object):
    """
    Add a X-API-Version header to the response. The version is taken from
    TOOLKIT['API_VERSION'] setting.
    """

    def process_response(self, request, response):
        response['X-API-Version'] = settings.TOOLKIT['API_VERSION']
        return response
