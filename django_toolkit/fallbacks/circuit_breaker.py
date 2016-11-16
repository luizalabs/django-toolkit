# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:

    def __init__(
        self,
        cache,
        failure_cache_key,
        max_failures,
        max_failure_exception,
        max_failure_timeout=None,
        circuit_timeout=None,
        catch_exceptions=None,
    ):
        self.cache = cache
        self.failure_cache_key = failure_cache_key
        self.max_failure_timeout = max_failure_timeout
        self.circuit_timeout = circuit_timeout
        self.circuit_cache_key = 'circuit_{}'.format(failure_cache_key)
        self.max_failure_exception = max_failure_exception
        self.catch_exceptions = catch_exceptions or (Exception,)
        self.max_failures = max_failures

    @property
    def is_circuit_open(self):
        return self.cache.get(self.circuit_cache_key) or False

    @property
    def total_failures(self):
        return self.cache.get(self.failure_cache_key) or 0

    def open_circuit(self):
        self.cache.set(self.circuit_cache_key, True, self.circuit_timeout)

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
        if exc_type in self.catch_exceptions:
            if self.is_circuit_open:
                raise self.max_failure_exception

            self._increase_failure_count()

            if self.total_failures >= self.max_failures:
                self.open_circuit()

                logger.info(
                    'Max failures exceeded by: {}'.format(
                        self.failure_cache_key
                    )
                )

                raise self.max_failure_exception

    def _increase_failure_count(self):
        self.cache.add(self.failure_cache_key, 0, self.max_failure_timeout)
        total = self.cache.incr(self.failure_cache_key)

        logger.info(
            'Increase failure for: {key} - '
            'max failures {max_failures} - '
            'total {total}'.format(
                key=self.failure_cache_key,
                max_failures=self.max_failures,
                total=total
            )
        )
