# Fallbacks

### Circuit Breaker

A simple implementation of [Circuit Breaker](http://martinfowler.com/bliki/CircuitBreaker.html) pattern.

#### Arguments

`cache`

Django cache object.

`failure_cache_key`

Cache key where the number of errors is incremented.

`failures_by_percentage`

Configures circuit breaker to work by percentage of errors. Default is `False`.

`max_failures`

Maximum number of errors. Is required only if `failures_by_percentage` is `False`.

`max_percentage_failures`

Maximum percent of errors. Is required only if `failures_by_percentage` is `True`.

`max_failure_exception`

Exception to be raised when it exceeds the maximum number of errors and when the circuit is open.

`max_failure_timeout`

This value is set on first error. It is used to validate the number of errors by time.

`circuit_timeout`

Time that the circuit will be open.

`catch_exceptions`

List of exceptions catched to increase the number of errors.

`max_accepted_failures`

Maximum number of errors accepted to not open circuit breaker when is configured by percentage. Is required only if `failures_by_percentage` is `True`


#### Example

```python
from django_toolkit.failures.circuit_breaker import CircuitBreaker
from django.core.cache import caches

cache = caches['default']

class MyException(Exception):
    pass


with CircuitBreaker(
    cache=cache,
    failure_cache_key='failure_cache_key',
    max_failures=1000,
    max_failure_exception=MyException,
    max_failure_timeout=3600,
    circuit_timeout=5000,
    catch_exceptions=(ValueError, StandardError, LookupError),
) as circuit_breaker:
    assert not circuit_breaker.is_circuit_open
```

#### Example by percentage

```python
from django_toolkit.failures.circuit_breaker import CircuitBreaker
from django.core.cache import caches

cache = caches['default']

class MyException(Exception):
    pass


with CircuitBreaker(
    cache=cache,
    failure_cache_key='failure_cache_key',
    failures_by_percentage=True,
    max_percentage_failures=40,
    max_accepted_failures=50,
    max_failure_exception=MyException,
    max_failure_timeout=3600,
    circuit_timeout=5000,
    catch_exceptions=(ValueError, StandardError, LookupError),
) as circuit_breaker:
    assert not circuit_breaker.is_circuit_open
```
