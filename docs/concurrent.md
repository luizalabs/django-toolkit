# Concurrent

## Locks

The lock context are used to ensure that piece of code run only once.

### Local memory lock

Use in memory lock.

#### Example

```python
from django_toolkit.concurrent.locks import LocalMemoryLock

def run(*args, **kwargs):
    with LocalMemoryLock() as lock:
        assert lock.active is True
        # do some stuff
```

### Cache lock

`CacheLock` uses django cache system and `default` cache alias by default.
If the context of lock is `active`, by default, `LockActiveError` is raised.

#### Example

Django cache config

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'locks': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}
```

Basic usage.

```python
from django_toolkit.concurrent.locks import CacheLock

def run(*args, **kwargs):
    with CacheLock(key='key') as lock:
        assert lock.is_active
        # do some stuff
```

You can set the timeout and alias of cache.

```python
from django_toolkit.concurrent.locks import CacheLock

def run(*args, **kwargs):
    with CacheLock(key='key', cache_alias='lock', expire=10):
        # do some stuff
```

You can control lock to don't raise `LockActiveError` exception.

```python
from django_toolkit.concurrent.locks import CacheLock

def run(*args, **kwargs):
    with CacheLock(key='key', raise_exception=False) as lock:
        assert lock.is_active

    with CacheLock(key='key', raise_exception=False) as lock:
        if lock.is_active:
            # do some stuff
        else:
            # do some stuff
```
