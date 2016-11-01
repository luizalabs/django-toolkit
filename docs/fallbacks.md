# Fallbacks

### Circuit Breaker

A simple implementation of [Circuit Breaker](http://martinfowler.com/bliki/CircuitBreaker.html) pattern.

#### Arguments

`cache`

Django cache object.

`failure_cache_key`

Cache key where the number of errors is incremented.

`max_failures`

Maximum number of errors.

`max_failure_exception`

Exception raised when exceded maximum number of errors and when circuit is open.

`max_failure_timeout`

This value is set on first error. It is used to validate number of errors by time.

`circuit_timeout`

Time that the circuit will be open.

`catch_exceptions`

List of exception that is catched to incrase number of errors.


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
