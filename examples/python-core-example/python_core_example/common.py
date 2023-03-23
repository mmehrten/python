import functools
import logging
import socket
import sys
import time
from typing import Any, Callable, Dict, List, TypeVar, cast

import requests
from urllib3.connection import HTTPConnection

_BaseDecoratedFunc = Callable[..., Any]
DecoratedFunc = TypeVar("DecoratedFunc", bound=_BaseDecoratedFunc)

logger = logging.getLogger(__name__)
# Let dead connections stick around for 120 seconds at most
TCP_KEEPALIVE_TIME = 60
TCP_KEEPALIVE_INTERVAL = 10
TCP_KEEPALIVE_PROBE_COUNT = 6


# https://github.com/python/mypy/issues/1927
def time_api(fn: DecoratedFunc) -> DecoratedFunc:
    """A decorator to log the duration of a function call."""
    call_name = fn.__qualname__

    @functools.wraps(fn)
    def _run(*args, **kwargs):
        t1 = time.perf_counter()
        res = fn(*args, **kwargs)
        t2 = time.perf_counter()
        delta = t2 - t1
        # Only log significant function calls (>=10 millis) to avoid unnecessary log lines
        # NOTE: This could hide methods that are called many times and lead to large runtimes
        # on aggregate. In general these aren't common, so we ignore them here. Can always
        # enable finer grained logging later if this doesn't detect perf issues (e.g. overall runtime)
        # is significantly longer than logged runtime)
        if delta < 0.01:
            return res

        logger.info(
            r"TIMING - {\"method\": \"%s\", \"duration\": %.2f}",
            call_name,
            t2 - t1,
        )
        return res

    return cast(DecoratedFunc, _run)


def stats(values: List[float]) -> Dict[str, float]:
    """Calculate percentiles and other summary statistics of a list of values.

    Note: Requires numpy to be installed.
    """
    # Don't require numpy in requirements.txt - not required for main execution and increases image size unnecessarily
    import numpy

    return {
        "25th": numpy.percentile(values, 25),  # type: ignore # https://github.com/Project-MONAI/MONAI/issues/3561
        "50th": numpy.percentile(values, 50),  # type: ignore # https://github.com/Project-MONAI/MONAI/issues/3561
        "75th": numpy.percentile(values, 70),  # type: ignore # https://github.com/Project-MONAI/MONAI/issues/3561
        "90th": numpy.percentile(values, 90),  # type: ignore # https://github.com/Project-MONAI/MONAI/issues/3561
        "95th": numpy.percentile(values, 95),  # type: ignore # https://github.com/Project-MONAI/MONAI/issues/3561
        "99th": numpy.percentile(values, 99),  # type: ignore # https://github.com/Project-MONAI/MONAI/issues/3561
        "99.9th": numpy.percentile(values, 99.9),  # type: ignore # https://github.com/Project-MONAI/MONAI/issues/3561
        "mean": float(numpy.mean(values)),
        "stdev": float(numpy.std(values)),
        "median": numpy.median(values),  # type: ignore # https://github.com/Project-MONAI/MONAI/issues/3561
        "count": len(values),
        "total": sum(values),
        "max": max(values),
        "min": min(values),
    }


def _set_socket_options():
    """Turn on TCP keepalive for the HTTPConnection object."""
    logger.debug("Current socket options: %s", HTTPConnection.default_socket_options)
    for platforms, protocol, constant, value in (
        # Keepalive on Linux
        (("linux",), socket.IPPROTO_TCP, "TCP_KEEPIDLE", TCP_KEEPALIVE_TIME),
        # Shared between Linux and Mac
        (
            ("linux", "darwin"),
            socket.IPPROTO_TCP,
            "TCP_KEEPINTVL",
            TCP_KEEPALIVE_INTERVAL,
        ),
        (
            ("linux", "darwin"),
            socket.IPPROTO_TCP,
            "TCP_KEEPCNT",
            TCP_KEEPALIVE_PROBE_COUNT,
        ),
        # Turns KeepAlive on
        (("linux", "darwin"), socket.SOL_SOCKET, "SO_KEEPALIVE", 1),
        # Keepalive on MacOS
        # Not exposed in socket library, found from tcp.h:
        # https://github.com/apple/darwin-xnu/blob/0a798f6738bc1db01281fc08ae024145e84df927/bsd/netinet/tcp.h#L206
        (("darwin",), socket.IPPROTO_TCP, 0x10, TCP_KEEPALIVE_TIME),
    ):
        if sys.platform not in platforms:
            continue
        if isinstance(constant, str) and not hasattr(socket, constant):
            continue  # pragma: nocover # Windows only case, don't test
        elif isinstance(constant, str):
            constant = getattr(socket, constant)
        opts = (protocol, constant, value)
        logger.debug("Setting socket options: %s", opts)
        HTTPConnection.default_socket_options.append(opts)


@functools.lru_cache(maxsize=1)
def shared_session() -> requests.Session:
    """Get a global requests.Session object shared by all methods, which ensures TCP keepalive is enabled."""
    _set_socket_options()
    return requests.Session()
