import pytest
from django.core.cache import caches
from mock import mock

from django_toolkit.fallbacks.circuit_breaker import CircuitBreaker
from django_toolkit.fallbacks.circuit_breaker.rules import (
    MaxFailuresRule,
    PercentageFailuresRule
)
from tests.fake.fallbacks.circuit_breaker.rules import (
    FakeRuleShouldNotIncreaseFailure,
    FakeRuleShouldNotIncreaseRequest,
    FakeRuleShouldNotOpen,
    FakeRuleShouldOpen
)

cache = caches['default']


class MyException(Exception):
    pass


def success_function():
    return True


def fail_function():
    raise ValueError()


class TestCircuitBreaker:

    @pytest.fixture
    def failure_cache_key(self):
        return 'fail'

    @pytest.fixture
    def request_cache_key(self):
        return 'request'

    @pytest.fixture
    def rule_should_open(self, failure_cache_key, request_cache_key):
        return FakeRuleShouldOpen(
            failure_cache_key=failure_cache_key,
            request_cache_key=request_cache_key,
        )

    @pytest.fixture
    def rule_should_not_open(self, failure_cache_key, request_cache_key):
        return FakeRuleShouldNotOpen(
            failure_cache_key=failure_cache_key,
            request_cache_key=request_cache_key,
        )

    @pytest.fixture
    def rule_should_not_increase_failure(
        self,
        failure_cache_key,
        request_cache_key
    ):
        return FakeRuleShouldNotIncreaseFailure(
            failure_cache_key=failure_cache_key,
            request_cache_key=request_cache_key,
        )

    @pytest.fixture
    def rule_should_not_increase_request(
        self,
        failure_cache_key,
        request_cache_key
    ):
        return FakeRuleShouldNotIncreaseRequest(
            failure_cache_key=failure_cache_key,
            request_cache_key=request_cache_key,
        )

    @pytest.fixture
    def max_failures_rule(self, failure_cache_key):
        return MaxFailuresRule(
            max_failures=3,
            failure_cache_key=failure_cache_key
        )

    @pytest.fixture
    def percentage_failures_rule(self, failure_cache_key, request_cache_key):
        return PercentageFailuresRule(
            max_failures=50,
            failure_cache_key=failure_cache_key,
            max_accepted_failures=2,
            request_cache_key=request_cache_key
        )

    @pytest.fixture(autouse=True)
    def clear_cache(self, request_cache_key, failure_cache_key):
        cache.delete(request_cache_key)
        cache.delete(failure_cache_key)
        cache.delete('circuit_{}'.format(failure_cache_key))

    def test_success_result(self, rule_should_not_open):
        with CircuitBreaker(
            rule=rule_should_not_open,
            cache=cache,
            failure_exception=None,
            catch_exceptions=None,
        ):
            success_function()

    def test_should_raise_error(self, rule_should_open):
        with pytest.raises(MyException):
            with CircuitBreaker(
                rule=rule_should_open,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

    def test_should_increase_fail_cache_count(
        self,
        failure_cache_key,
        rule_should_not_open
    ):
        cache.set(failure_cache_key, 1)

        with pytest.raises(ValueError):
            with CircuitBreaker(
                rule=rule_should_not_open,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

        assert cache.get(failure_cache_key) == 2

    def test_should_increase_request_cache_count(
        self,
        request_cache_key,
        rule_should_not_open
    ):
        cache.set(request_cache_key, 0)

        with CircuitBreaker(
            rule=rule_should_not_open,
            cache=cache,
            failure_exception=MyException,
            catch_exceptions=(ValueError,),
        ):
            success_function()

        with pytest.raises(ValueError):
            with CircuitBreaker(
                rule=rule_should_not_open,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

        assert cache.get(request_cache_key) == 2

    def test_should_open_circuit_when_failures_exceeds(
        self,
        rule_should_open,
        failure_cache_key,
    ):
        cache.set(failure_cache_key, 3)

        with pytest.raises(MyException):
            with CircuitBreaker(
                rule=rule_should_open,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                fail_function()

            assert circuit_breaker.is_circuit_open

    def test_should_raise_exception_when_circuit_is_open(
        self,
        rule_should_open,
        failure_cache_key
    ):
        circuit_cache_key = 'circuit_{}'.format(failure_cache_key)
        cache.set(circuit_cache_key, True)

        with pytest.raises(MyException):
            with CircuitBreaker(
                rule=rule_should_open,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                success_function()

            assert circuit_breaker.is_circuit_open

    def test_should_not_call_exit_when_circuit_is_open(
        self,
        rule_should_open,
        failure_cache_key
    ):
        circuit_cache_key = 'circuit_{}'.format(failure_cache_key)
        cache.set(circuit_cache_key, True)

        with pytest.raises(MyException):
            with mock.patch(
                'django_toolkit.fallbacks.circuit_breaker.CircuitBreaker.__exit__'  # noqa
            ) as exit:
                with CircuitBreaker(
                    rule=rule_should_open,
                    cache=cache,
                    failure_exception=MyException,
                    catch_exceptions=(ValueError,),
                ):
                    success_function()

        assert not exit.called

    def test_should_not_increment_fail_when_circuit_is_open(
        self,
        rule_should_open,
        failure_cache_key
    ):
        """
        It should not increment fail count over the max failures limit, when
        circuit breaker is open after a successful enter.
        """
        cache.set(failure_cache_key, 3)

        with pytest.raises(MyException):
            with CircuitBreaker(
                rule=rule_should_open,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

        assert not cache.get(failure_cache_key)

    def test_should_not_increment_request_when_circuit_is_open(
        self,
        rule_should_open,
        failure_cache_key,
        request_cache_key
    ):
        """
        It should not increment request count over the max failures limit, when
        circuit breaker is open after a successful enter.
        """
        cache.set(failure_cache_key, 2)
        cache.set(request_cache_key, 5)

        with pytest.raises(MyException):
            with CircuitBreaker(
                rule=rule_should_open,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

        assert not cache.get(request_cache_key)

    def test_should_not_increment_request_when_rule_is_false(
        self,
        rule_should_not_increase_request,
        request_cache_key
    ):
        cache.set(request_cache_key, 5)

        with pytest.raises(ValueError):
            with CircuitBreaker(
                rule=rule_should_not_increase_request,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

        assert cache.get(request_cache_key) == 5

    def test_should_not_increment_failure_when_rule_is_false(
        self,
        rule_should_not_increase_failure,
        failure_cache_key
    ):
        cache.set(failure_cache_key, 5)

        with pytest.raises(ValueError):
            with CircuitBreaker(
                rule=rule_should_not_increase_failure,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ):
                fail_function()

        assert cache.get(failure_cache_key) == 5

    def test_should_delete_count_key_when_circuit_is_open(
        self,
        rule_should_open,
        failure_cache_key,
        request_cache_key
    ):
        cache.set(failure_cache_key, 2)
        cache.set(request_cache_key, 5)

        with pytest.raises(MyException):
            with CircuitBreaker(
                rule=rule_should_open,
                cache=cache,
                failure_exception=MyException,
                catch_exceptions=(ValueError,),
            ) as circuit_breaker:
                fail_function()

            assert circuit_breaker.is_circuit_open

        assert cache.get(failure_cache_key) is None
        assert cache.get(request_cache_key) is None

    def test_should_create_failure_cache_when_increase_request_count(
        self,
        rule_should_not_increase_failure,
        failure_cache_key,
        request_cache_key,
    ):
        assert cache.get(failure_cache_key) is None

        with CircuitBreaker(
            rule=rule_should_not_increase_failure,
            cache=cache,
            failure_exception=MyException,
            catch_exceptions=(ValueError,),
        ):
            success_function()

        assert cache.get(failure_cache_key) == 0
