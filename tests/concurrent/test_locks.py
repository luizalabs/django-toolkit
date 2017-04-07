import pytest

from django_toolkit.concurrent.locks import (
    CacheLock,
    LocalMemoryLock,
    LockActiveError
)


class TestLocalMemoryLock:

    @pytest.fixture
    def lock(self):
        return LocalMemoryLock()

    def test_should_not_be_active_on_create(self, lock):
        assert not lock.active

    def test_should_be_active_on_enter(self, lock):
        with lock:
            assert lock.active

    def test_should_not_be_active_on_exit(self, lock):
        with lock:
            pass

        assert not lock.active

    def test_should_raise_exception_when_lock_is_already_active(self, lock):
        with pytest.raises(LockActiveError):
            with lock:
                with lock:
                    pass


class TestCacheLock:

    def test_should_be_true_when_lock_is_acquired(self):
        with CacheLock(key='test') as lock:
            assert lock.active

    def test_should_release_lock(self):
        with CacheLock(key='test') as lock:
            pass

        assert not lock.active

    def test_should_raise_exception_when_try_lock_some_lock_key(self):
        with pytest.raises(LockActiveError):
            with CacheLock(key='test', expire=1000):
                with CacheLock(key='test'):
                    pass

    def test_should_not_raise_exception_when_raise_exception_is_false(self):
        with CacheLock(key='test', expire=1000) as lock:
            assert lock.active is True

            with CacheLock(key='test', raise_exception=False) as lock:
                assert lock.active is False

    def test_should_use_default_cache_timeout_when_expire_is_not_given(self):
        with CacheLock(cache_alias='explicit_timeout', key='test') as lock:
            assert lock.cache.get(lock._key)

    def test_should_expire_immediately_when_expire_is_zero(self):
        with CacheLock(key='test', expire=0) as lock:
            assert not lock.cache.get(lock._key)

    def test_should_not_release_when_lock_is_already_acquired(self):
        """
        It should release the lock only if it was acquired successfully.
        A lock that do not acquired a lock should not release it.
        """
        with CacheLock(key='test', raise_exception=False) as lock:
            with CacheLock(key='test', raise_exception=False):
                pass

            assert lock.cache.get(lock._key)

        assert not lock.cache.get(lock._key)

    def test_should_not_release_when_lock_when_lock_active_error_is_raised(
        self
    ):
        with CacheLock(key='test') as lock:
            with pytest.raises(LockActiveError):
                with CacheLock(key='test'):
                    pass

            assert lock.cache.get(lock._key)
