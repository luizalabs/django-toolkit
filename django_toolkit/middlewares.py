# -*- coding: utf-8 -*-
import logging

from django.conf import settings

from .shortcuts import get_oauth2_app

logger = logging.getLogger(__name__)


class VersionHeaderMiddleware(object):
    """
    Add a X-API-Version header to the response. The version is taken from
    TOOLKIT['API_VERSION'] setting.
    """

    def process_response(self, request, response):
        response['X-API-Version'] = settings.TOOLKIT['API_VERSION']
        return response


class AccessLogMiddleware(object):

    LOG_FORMAT = (
        u'[{app_name}] '
        u'{response.status_code} {request.method} {request.path}'
    )

    UNKNOWN_APP_NAME = 'unknown'

    def process_response(self, request, response):
        app = get_oauth2_app(request)
        app_name = self.UNKNOWN_APP_NAME

        if app:
            app_name = app.name

        logger.info(
            self.LOG_FORMAT.format(app_name=app_name,
                                   request=request,
                                   response=response)
        )
        return response
