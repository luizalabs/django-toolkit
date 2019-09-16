# -*- coding: utf-8 -*-
import inspect
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitBreaker:

    def __init__(
        self,
        rule,
        cache,
        failure_exception,
        failure_timeout=None,
        circuit_timeout=None,
        catch_exceptions=None,
    ):
        self.rule = rule
        self.cache = cache
        self.failure_timeout = failure_timeout
        self.circuit_timeout = circuit_timeout
        self.circuit_cache_key = 'circuit_{}'.format(rule.failure_cache_key)
        self.failure_exception = failure_exception
        self.catch_exceptions = catch_exceptions or (Exception,)

    @property
    def is_circuit_open(self):
        return self.cache.get(self.circuit_cache_key) or False

    @property
    def total_failures(self):
        return self.cache.get(self.rule.failure_cache_key) or 0

    @property
    def total_requests(self):
        return self.cache.get(self.rule.request_cache_key) or 0

    def open_circuit(self):
        self.cache.set(self.circuit_cache_key, True, self.circuit_timeout)

        # Delete the cache key to mitigate multiple sequentials openings
        # when a key is created accidentally without timeout (from an incr
        # operation)
        self.cache.delete(self.rule.failure_cache_key)
        self.cache.delete(self.rule.request_cache_key)

        logger.critical(
            'Open circuit for {failure_cache_key} {cicuit_cache_key}'.format(
                failure_cache_key=self.rule.failure_cache_key,
                cicuit_cache_key=self.circuit_cache_key
            )
        )

    def __enter__(self):
        if self.is_circuit_open:
            raise self.failure_exception

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._increase_request_count()
        if inspect.isclass(exc_type) and any(
            issubclass(exc_type, exception_class)
            for exception_class in self.catch_exceptions
        ):

            self._increase_failure_count()

            if self.rule.should_open_circuit(
                total_failures=self.total_failures,
                total_requests=self.total_requests
            ):
                self.open_circuit()

                logger.info(
                    'Max failures exceeded by: {}'.format(
                        self.rule.failure_cache_key
                    )
                )

                raise self.failure_exception

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner

    def _increase_failure_count(self):
        if (
            self.is_circuit_open or
            not self.rule.should_increase_failure_count()
        ):
            return

        # Between the cache.add and cache.incr, the cache MAY expire,
        # which will lead to a circuit that will eventually open
        self.cache.add(self.rule.failure_cache_key, 0, self.failure_timeout)
        total = self.cache.incr(self.rule.failure_cache_key)

        self.rule.log_increase_failures(
            total_failures=total,
            total_requests=self.total_requests
        )

    def _increase_request_count(self):
        if (
            self.is_circuit_open or
            not self.rule.should_increase_request_count()
        ):
            return

        self.cache.add(self.rule.request_cache_key, 0, self.failure_timeout)
        # To calculate the exact percentage, the cache of requests and the
        # cache of failures must expire at the same time.
        if self.rule.should_increase_failure_count():
            self.cache.add(
                self.rule.failure_cache_key, 0, self.failure_timeout
            )

        self.cache.incr(self.rule.request_cache_key)


circuit_breaker = CircuitBreaker
