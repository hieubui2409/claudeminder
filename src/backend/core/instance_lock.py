"""Single instance enforcement using file lock."""
from pathlib import Path

from filelock import FileLock, Timeout

LOCK_FILE = Path.home() / ".config" / "backend" / ".lock"

_current_lock: FileLock | None = None


def acquire_instance_lock() -> FileLock | None:
    """Acquire instance lock. Returns lock on success, None if another instance running."""
    global _current_lock
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(LOCK_FILE), timeout=0)
    try:
        lock.acquire()
        _current_lock = lock
        return lock
    except Timeout:
        return None


def release_instance_lock() -> None:
    """Release the current instance lock."""
    global _current_lock
    if _current_lock is not None:
        _current_lock.release()
        _current_lock = None


def is_another_instance_running() -> bool:
    """Check if another instance is already running."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(LOCK_FILE), timeout=0)
    try:
        lock.acquire()
        lock.release()
        return False
    except Timeout:
        return True
