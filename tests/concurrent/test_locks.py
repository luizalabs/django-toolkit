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
                assert lock.active is True
                pass
