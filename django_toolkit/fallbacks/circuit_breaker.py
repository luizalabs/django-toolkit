# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:

    def __init__(
        self,
        cache,
        failure_cache_key,
        max_failure_exception,
        max_failures=None,
        max_percentage_failures=None,
        max_failure_timeout=None,
        circuit_timeout=None,
        catch_exceptions=None,
        max_accepted_failures=None,
        failures_by_percentage=False,
    ):
        if failures_by_percentage:
            if max_percentage_failures is None:
                raise ValueError(
                    'max_percentage_failures should not be None '
                    'if failures_by_percentage is True'
                )

            if max_accepted_failures is None:
                raise ValueError(
                    'max_accepted_failures should not be None '
                    'if failures_by_percentage is True'
                )

        else:
            if max_failures is None:
                raise ValueError(
                    'max_failures should not be None '
                    'if failures_by_percentage is False'
                )

        self.cache = cache
        self.failure_cache_key = failure_cache_key
        self.max_failure_timeout = max_failure_timeout
        self.circuit_timeout = circuit_timeout
        self.circuit_cache_key = 'circuit_{}'.format(failure_cache_key)
        self.max_failure_exception = max_failure_exception
        self.catch_exceptions = catch_exceptions or (Exception,)
        self.max_failures = max_failures
        self.max_percentage_failures = max_percentage_failures
        self.max_accepted_failures = max_accepted_failures
        self.failures_by_percentage = failures_by_percentage
        self.request_cache_key = 'circuit_request_{}'.format(failure_cache_key)

    @property
    def is_circuit_open(self):
        return self.cache.get(self.circuit_cache_key) or False

    @property
    def total_failures(self):
        return self.cache.get(self.failure_cache_key) or 0

    @property
    def total_requests(self):
        return self.cache.get(self.request_cache_key) or 0

    @property
    def total_percentage_failures(self):
        return (self.total_failures * 100) / self.total_requests

    def open_circuit(self):
        self.cache.set(self.circuit_cache_key, True, self.circuit_timeout)

        # Delete the cache key to mitigate multiple sequentials openings
        # when a key is created accidentally without timeout (from an incr
        # operation)
        self.cache.delete(self.failure_cache_key)

        logger.critical(
            'Open circuit for {failure_cache_key} {cicuit_cache_key}'.format(
                failure_cache_key=self.failure_cache_key,
                cicuit_cache_key=self.circuit_cache_key
            )
        )

    def __enter__(self):
        if self.is_circuit_open:
            raise self.max_failure_exception

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._increase_request_count()
        if exc_type in self.catch_exceptions:
            if self.is_circuit_open:
                raise self.max_failure_exception

            self._increase_failure_count()

            if self._should_open_circuit():
                self.open_circuit()

                logger.info(
                    'Max failures exceeded by: {}'.format(
                        self.failure_cache_key
                    )
                )

                raise self.max_failure_exception

    def _should_open_circuit(self):
        if self.failures_by_percentage:
            return all([
                self.total_failures > self.max_accepted_failures,
                self.total_percentage_failures >= self.max_percentage_failures
            ])

        return self.total_failures >= self.max_failures

    def _increase_failure_count(self):
        # Between the cache.add and cache.incr, the cache MAY expire,
        # which will lead to a circuit that will eventually open
        self.cache.add(self.failure_cache_key, 0, self.max_failure_timeout)
        total = self.cache.incr(self.failure_cache_key)
        max_failures = self.max_failures

        if self.failures_by_percentage:
            total = '{}%'.format(self.total_percentage_failures)
            max_failures = '{}%'.format(self.max_percentage_failures)

        logger.info(
            'Increase failure for: {key} - '
            'max failures {max_failures} - '
            'total {total}'.format(
                key=self.failure_cache_key,
                max_failures=max_failures,
                total=total
            )
        )

    def _increase_request_count(self):
        if self.is_circuit_open or not self.failures_by_percentage:
            return

        self.cache.add(self.request_cache_key, 0, self.max_failure_timeout)
        self.cache.incr(self.request_cache_key)
