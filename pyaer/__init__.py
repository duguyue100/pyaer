from pyaer import log


# System logging level

LOG_LEVEL = log.DEBUG

try:
    from pyaer import libcaer_wrap as libcaer
except ImportError:
    raise ImportError(
        "libcaer might not be in the LD_LIBRARY_PATH "
        "or your numpy might not be the required version. "
        "Try to load _libcaer_wrap.so from the package "
        "directory, this will provide more information."
    )

from pyaer.event_camera import EventCamera  # noqa # noreorder


__all__ = ["libcaer", "EventCamera"]
