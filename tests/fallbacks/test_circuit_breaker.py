import pytest
from django.core.cache import caches

from django_toolkit.fallbacks.circuit_breaker import CircuitBreaker

cache = caches['default']


class MyException(Exception):
    pass


def success_function():
    return True


def fail_function():
    raise ValueError()


class TestCircuitBreaker:

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        cache.clear()

    def test_success_result(self):
        with CircuitBreaker(
            cache=cache,
            failure_cache_key='success',
            max_failures=1,
            max_failure_exception=None,
            catch_exceptions=None,
        ):
            success_function()

    def test_should_raise_error_when_max_failures_is_exceeded(self):
        with pytest.raises(MyException):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key='fail',
                max_failures=0,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

    def test_should_increase_fail_cache_count(self):
        failure_cache_key = 'fail_count'

        cache.set(failure_cache_key, 171)

        with pytest.raises(ValueError):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key=failure_cache_key,
                max_failures=5000,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

        assert cache.get(failure_cache_key, 172)

    def test_should_open_circuit_when_max_failures_exceeds(self):
        failure_cache_key = 'circuit'

        cache.set(failure_cache_key, 1)

        with pytest.raises(MyException):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key=failure_cache_key,
                max_failures=2,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                fail_function()

            assert circuit_breaker.is_circuit_open

        assert cache.get(failure_cache_key, 2)

    def test_should_raise_exception_when_circuit_is_open(self):
        cache.set('circuit_circuit_open', True)

        with pytest.raises(MyException):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key='circuit_open',
                max_failures=10,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                success_function()

            assert circuit_breaker.is_circuit_open

    def test_should_not_increment_fail_when_circuit_is_open(self):
        """
        It should not increment fail count over the max failures limit, when
        circuit breaker is open after a successful enter.
        """
        failure_cache_key = 'fail_count'
        max_failures = 10

        with pytest.raises(MyException):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key=failure_cache_key,
                max_failures=max_failures,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                cache.set(failure_cache_key, max_failures)
                circuit_breaker.open_circuit()

                fail_function()

        assert not cache.get(failure_cache_key)

    def test_should_delete_count_key_when_circuit_is_open(self):
        failure_cache_key = 'circuit'

        cache.set(failure_cache_key, 1)

        with pytest.raises(MyException):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key=failure_cache_key,
                max_failures=2,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                fail_function()

            assert circuit_breaker.is_circuit_open

        assert cache.get(failure_cache_key) is None

    @pytest.mark.parametrize(
        (
            'failures_by_percentage,max_percentage_failures,'
            'max_accepted_failures,max_failures'
        ),
        [
            (False, 10, 20, None),
            (True, None, 10, 0),
            (True, 10, None, 0),
        ]
    )
    def test_should_raise_value_error_with_invalid_arguments(
        self,
        failures_by_percentage,
        max_percentage_failures,
        max_accepted_failures,
        max_failures
    ):
        with pytest.raises(ValueError):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key='fail',
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
                failures_by_percentage=failures_by_percentage,
                max_percentage_failures=max_percentage_failures,
                max_accepted_failures=max_accepted_failures,
                max_failures=max_failures,
            ):
                success_function()

    def test_should_not_open_circuit_with_accepted_number_of_failures(
        self
    ):
        try:
            with CircuitBreaker(
                cache=cache,
                failure_cache_key='fail',
                failures_by_percentage=True,
                max_percentage_failures=50,
                max_accepted_failures=1,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                try:
                    fail_function()
                except ValueError:
                    pass

        except MyException as e:
            pytest.fail('It should not have raised: {}'.format(e))

        assert circuit_breaker.is_circuit_open is False

    def test_should_open_circuit_by_percentage(
        self
    ):
        def call_with_circuit(should_success):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key='fail',
                failures_by_percentage=True,
                max_percentage_failures=50,
                max_accepted_failures=2,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                if should_success:
                    success_function()
                else:
                    fail_function()

        call_with_circuit(should_success=True)
        call_with_circuit(should_success=True)
        try:
            call_with_circuit(should_success=False)
        except ValueError:
            pass

        try:
            call_with_circuit(should_success=False)
        except ValueError:
            pass

        with pytest.raises(MyException):
            call_with_circuit(should_success=False)

        with pytest.raises(MyException):
            call_with_circuit(should_success=True)

    def test_should_increase_request_cache_count(self):
        with CircuitBreaker(
            cache=cache,
            failure_cache_key='fail_count',
            failures_by_percentage=True,
            max_percentage_failures=10,
            max_accepted_failures=0,
            max_failure_exception=MyException,
            catch_exceptions=(ValueError,),
        ) as circuit_breaker:
            success_function()

        assert cache.get(circuit_breaker.request_cache_key) > 0

    def test_should_not_increment_request_when_circuit_is_open(self):
        """
        It should not increment request count over the max failures limit, when
        circuit breaker is open after a successful enter.
        """
        failure_cache_key = 'fail_count'
        max_failures = 10

        with pytest.raises(MyException):
            with CircuitBreaker(
                cache=cache,
                failure_cache_key=failure_cache_key,
                failures_by_percentage=True,
                max_percentage_failures=10,
                max_accepted_failures=0,
                max_failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                cache.set(failure_cache_key, max_failures)
                circuit_breaker.open_circuit()

                fail_function()

        assert not cache.get(circuit_breaker.request_cache_key)
