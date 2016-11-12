# -*- coding: utf-8 -*-
import pytest
from django.conf import settings
from django.http import HttpResponse
from mock import Mock, PropertyMock, patch

from django_toolkit import middlewares


@pytest.fixture
def http_request(rf):
    return rf.get('/')


@pytest.fixture
def http_response():
    return HttpResponse()


class TestVersionHeaderMiddleware(object):

    @pytest.fixture(autouse=True)
    def settings(self, settings):
        settings.TOOLKIT = {
            'API_VERSION': '1.2.3',
        }
        return settings

    @pytest.fixture
    def middleware(self):
        return middlewares.VersionHeaderMiddleware()

    def test_should_return_a_response(
        self,
        middleware,
        http_request,
        http_response
    ):
        response = middleware.process_response(http_request, http_response)
        assert isinstance(response, HttpResponse)

    def test_should_add_a_version_header_to_the_response(
        self,
        middleware,
        http_request,
        http_response
    ):
        response = middleware.process_response(http_request, http_response)

        assert 'X-API-Version' in response
        assert response['X-API-Version'] == settings.TOOLKIT['API_VERSION']


@pytest.mark.django_db
class TestAccessLogMiddleware(object):

    @pytest.fixture
    def middleware(self):
        return middlewares.AccessLogMiddleware()

    @pytest.fixture
    def patched_logger(self):
        return patch('django_toolkit.middlewares.logger')

    @pytest.fixture
    def patched_format(self):
        return patch(
            'django_toolkit.middlewares.AccessLogMiddleware.LOG_FORMAT',
            new_callable=PropertyMock
        )

    @pytest.fixture
    def authenticated_http_request(self, http_request):
        http_request.user = u'jovem'
        http_request.auth = Mock(application=Mock(name='myapp'))
        return http_request

    def test_should_return_a_response(
        self,
        middleware,
        http_request,
        http_response
    ):
        response = middleware.process_response(http_request, http_response)
        assert isinstance(response, HttpResponse)

    def test_should_log_responses(
        self,
        middleware,
        http_request,
        http_response,
        patched_logger,
        patched_format
    ):
        with patched_logger as mock_logger:
            middleware.process_response(http_request, http_response)

        assert mock_logger.info.called

    def test_should_include_request_and_response_in_the_message(
        self,
        middleware,
        http_request,
        http_response,
        patched_logger,
        patched_format
    ):
        with patched_logger as mock_logger:
            with patched_format as mock_format_property:
                middleware.process_response(http_request, http_response)

        mock_format_string = mock_format_property.return_value

        assert mock_format_string.format.called
        mock_format_string.format.assert_called_once_with(
            app_name=middleware.UNKNOWN_APP_NAME,
            request=http_request,
            response=http_response
        )
        mock_logger.info.assert_called_once_with(
            mock_format_string.format.return_value
        )

    def test_should_include_the_authenticated_app_in_the_message(
        self,
        middleware,
        authenticated_http_request,
        http_response,
        patched_logger,
        patched_format
    ):
        with patched_format as mock_format_property:
            middleware.process_response(
                authenticated_http_request,
                http_response
            )

        mock_format_string = mock_format_property.return_value

        assert mock_format_string.format.called
        mock_format_string.format.assert_called_once_with(
            app_name=authenticated_http_request.auth.application.name,
            request=authenticated_http_request,
            response=http_response
        )
