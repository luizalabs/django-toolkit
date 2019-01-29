# Fallbacks

## Circuit Breaker

An implementation of [Circuit Breaker](http://martinfowler.com/bliki/CircuitBreaker.html) pattern.

#### class CircuitBreaker(rule, cache, failure_exception, failure_timeout=None, circuit_timeout=None, catch_exceptions=None)

#### Arguments

`rule`

Instance of class [Rule](#rule).

`cache`

Django cache object.

`failure_exception`

Exception to be raised when it exceeds the maximum number of errors and when the circuit is open.

`failure_timeout`

This value is set on first error. It is used to validate the number of errors by time.

`circuit_timeout`

Time that the circuit will be open.

`catch_exceptions`

List of exceptions catched to increase the number of errors.

## Rule

Abstract Base Class that defines rules to open circuit

### MaxFailuresRule
Rule to open circuit based on maximum number of failures

#### class MaxFailuresRule(max_failures, failure_cache_key)

#### Arguments

`max_failures`

Maximum number of errors.

`failure_cache_key`

Cache key where the number of errors is incremented.

#### Maximum failures example

```python
from django_toolkit.failures.circuit_breaker import CircuitBreaker
from django_toolkit.failures.circuit_breaker.rules import MaxFailuresRule
from django.core.cache import caches

cache = caches['default']

class MyException(Exception):
    pass

with CircuitBreaker(
    rule=MaxFailuresRule(
        max_failures=1000,
        failure_cache_key='failure_cache_key',
    ),
    cache=cache,
    failure_exception=MyException,
    failure_timeout=3600,
    circuit_timeout=5000,
    catch_exceptions=(ValueError, StandardError, LookupError),
) as circuit_breaker:
    assert not circuit_breaker.is_circuit_open
```

### PercentageFailuresRule
Rule to open circuit based on a percentage of failures.

#### class PercentageFailuresRule(max_failures_percentage, failure_cache_key, min_accepted_requests, request_cache_key)

#### Arguments

`max_failures_percentage`

Maximum percentage of errors.

`failure_cache_key`

Cache key where the number of errors is incremented.

`min_accepted_requests`

Minimum number of requests accepted to not open circuit breaker.

`request_cache_key`

Cache key where the number of requests is incremented.

#### Maximum percentage failures example

```python
from django_toolkit.failures.circuit_breaker import CircuitBreaker
from django_toolkit.failures.circuit_breaker.rules import (
    PercentageFailuresRule
)
from django.core.cache import caches

cache = caches['default']

class MyException(Exception):
    pass


with CircuitBreaker(
    rule=PercentageFailuresRule(
        max_failures_percentage=60,
        failure_cache_key='failure_cache_key',
        min_accepted_requests=100,
        request_cache_key='request_cache_key',
    ),
    cache=cache,
    failure_exception=MyException,
    failure_timeout=3600,
    circuit_timeout=5000,
    catch_exceptions=(ValueError, StandardError, LookupError),
) as circuit_breaker:
    assert not circuit_breaker.is_circuit_open
```
