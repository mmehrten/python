import time

from python_core_example import common


def test_time_api_fast_call_no_log(caplog):
    @common.time_api
    def fast_fn():
        return 1

    fast_fn()

    assert "TIMING" not in caplog.text


def test_time_api_slow_call_logs(caplog):
    @common.time_api
    def slow_fn():
        time.sleep(1)

    slow_fn()

    assert "TIMING" in caplog.text


def test_stats_single():
    assert common.stats([1]) == {
        "25th": 1,
        "50th": 1,
        "75th": 1,
        "90th": 1,
        "95th": 1,
        "99th": 1,
        "99.9th": 1,
        "mean": 1,
        "stdev": 0,
        "median": 1,
        "count": 1,
        "total": 1,
        "max": 1,
        "min": 1,
    }


def test_shared_session_caches_and_sets_keepalive():
    assert common.shared_session() is common.shared_session()
    import socket

    from urllib3.connection import HTTPConnection

    assert (
        socket.IPPROTO_TCP,
        socket.TCP_KEEPINTVL,
        10,
    ) in HTTPConnection.default_socket_options
