# -*- coding: utf-8 -*-
import logging
import socket


class AddHostName(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = self.hostname
        return True
