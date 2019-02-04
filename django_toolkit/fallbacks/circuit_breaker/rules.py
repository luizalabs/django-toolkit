# -*- coding: utf-8 -*-
import abc
import logging

logger = logging.getLogger(__name__)


class Rule(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, failure_cache_key, request_cache_key=None):
        self.failure_cache_key = failure_cache_key
        self.request_cache_key = request_cache_key

    @abc.abstractmethod
    def should_open_circuit(self, total_failures, total_requests):
        pass

    def should_increase_failure_count(self):
        return self.failure_cache_key is not None

    def should_increase_request_count(self):
        return self.request_cache_key is not None

    @abc.abstractmethod
    def log_increase_failures(self, total_failures, total_requests):
        pass


class MaxFailuresRule(Rule):

    def __init__(self, max_failures, failure_cache_key):
        super(MaxFailuresRule, self).__init__(
            failure_cache_key=failure_cache_key,
        )
        self.max_failures = max_failures

    def should_open_circuit(self, total_failures, total_requests):
        return total_failures >= self.max_failures

    def log_increase_failures(self, total_failures, total_requests):
        logger.info(
            'Increase failure for: {key} - '
            'max failures {max_failures} - '
            'total requests {total_requests} - '
            'total failures {total_failures}'.format(
                key=self.failure_cache_key,
                max_failures=self.max_failures,
                total_requests=total_requests,
                total_failures=total_failures
            )
        )


class PercentageFailuresRule(Rule):

    def __init__(
        self,
        max_failures_percentage,
        failure_cache_key,
        min_accepted_requests,
        request_cache_key,
    ):
        super(PercentageFailuresRule, self).__init__(
            failure_cache_key=failure_cache_key,
            request_cache_key=request_cache_key,
        )
        self.max_failures_percentage = max_failures_percentage
        self.min_accepted_requests = min_accepted_requests

    def _get_percentage_failures(self, total_failures, total_requests):
        if total_requests > 0:
            return (total_failures * 100) / total_requests
        return 0

    def should_open_circuit(self, total_failures, total_requests):
        percentage_failures = self._get_percentage_failures(
            total_failures=total_failures,
            total_requests=total_requests
        )
        return all([
            total_requests > self.min_accepted_requests,
            percentage_failures >= self.max_failures_percentage
        ])

    def log_increase_failures(self, total_failures, total_requests):
        logger.info(
            'Increase failure for: {key} - '
            'max failures {max_failures_percentage}% - '
            'total failures {total_failures} - '
            'min accepted requests {min_accepted_requests} - '
            'total requests {total_requests} - '
            'percentage failures {percentage_failures}%'.format(
                key=self.failure_cache_key,
                max_failures_percentage=self.max_failures_percentage,
                total_failures=total_failures,
                min_accepted_requests=self.min_accepted_requests,
                total_requests=total_requests,
                percentage_failures=self._get_percentage_failures(
                    total_failures=total_failures,
                    total_requests=total_requests
                ),
            )
        )
