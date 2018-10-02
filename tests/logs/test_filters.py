# -*- coding: utf-8 -*-
import socket

import pytest
from mock import Mock

from django_toolkit.logs.filters import AddHostName, IgnoreIfContains


class TestAddHostName(object):

    @pytest.fixture
    def hostname_filter(self):
        return AddHostName()

    def test_filter_should_add_a_hostname_to_the_given_record(
        self,
        hostname_filter
    ):
        record = Mock()
        hostname_filter.filter(record)

        assert record.hostname == socket.gethostname()

    def test_filter_should_return_true(self, hostname_filter):
        record = Mock()
        assert hostname_filter.filter(record)


class TestIgnoreIfContains(object):

    @pytest.fixture
    def log_filter(self):
        return IgnoreIfContains(substrings=['/healthcheck', '/ping'])

    @pytest.mark.parametrize('message', [
        'GET /healthcheck/',
        'GET /ping/'
    ])
    def test_should_ignore_record(self, message, log_filter):
        record = Mock()
        record.getMessage.return_value = message

        assert log_filter.filter(record) is False

    @pytest.mark.parametrize('message', [
        'GET /endpoint/',
        'GET /success/'
    ])
    def test_should_accept_record(self, message, log_filter):
        record = Mock()
        record.getMessage.return_value = message

        assert log_filter.filter(record) is True
