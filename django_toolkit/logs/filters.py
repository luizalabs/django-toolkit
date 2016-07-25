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
