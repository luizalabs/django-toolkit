# -*- coding: utf-8 -*-
import logging

from .shortcuts import get_oauth2_app
from .toolkit_settings import API_VERSION, MIDDLEWARE_ACCESS_LOG_FORMAT

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


logger = logging.getLogger(__name__)


class VersionHeaderMiddleware(MiddlewareMixin):
    """
    Add a X-API-Version header to the response. The version is taken from
    TOOLKIT['API_VERSION'] setting.
    """

    def process_response(self, request, response):
        response['X-API-Version'] = API_VERSION
        return response


class AccessLogMiddleware(MiddlewareMixin):

    LOG_FORMAT = MIDDLEWARE_ACCESS_LOG_FORMAT
    UNKNOWN_APP_NAME = 'unknown'

    def process_response(self, request, response):
        app = get_oauth2_app(request)

        app_name = getattr(app, 'name', self.UNKNOWN_APP_NAME)

        logger.info(
            self.LOG_FORMAT.format(app_name=app_name,
                                   request=request,
                                   response=response)
        )

        return response
