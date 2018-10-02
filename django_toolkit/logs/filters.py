# -*- coding: utf-8 -*-
import logging
import socket


class AddHostName(logging.Filter):
    """
    Add the %(hostname)s entry to log record, so that it can be included in the
    logs using a formatter
    """
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = self.hostname
        return True


class IgnoreIfContains(logging.Filter):
    """
    Ignore log record if message entry contains any substring set on
    log filter configuration.
    """

    def __init__(self, substrings=None):
        self.substrings = substrings or []

    def filter(self, record):
        message = record.getMessage()

        return not any(
            substring in message
            for substring in self.substrings
        )
