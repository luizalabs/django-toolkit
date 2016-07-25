# -*- coding: utf-8 -*-
import socket

import pytest
from mock import Mock

from django_toolkit.logs.filters import AddHostName


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
