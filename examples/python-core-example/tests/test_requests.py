from contextlib import ExitStack as DoesNotRaise
from unittest.mock import Mock, call, sentinel

import pytest
from python_core_example import request_with_retry


@pytest.fixture
def patch_path():
    return "python_core_example.requests"


@pytest.mark.parametrize(
    "status_code, expectation",
    [(sentinel.not_200, pytest.raises(RuntimeError)), (200, DoesNotRaise())],
)
def test_request_with_retry(
    mock_requests, mock_requests_response, status_code, expectation
):
    _request_with_retry = request_with_retry(logger=Mock())
    mock_requests_response.status_code = status_code
    mock_requests_response.text = "Error"
    with expectation:
        assert (
            _request_with_retry(
                session=mock_requests,
                url=sentinel.url,
                headers=sentinel.headers,
                proxies=sentinel.proxies,
                params=sentinel.params,
                stream=sentinel.stream,
            )
            == mock_requests_response
        )
    assert mock_requests.mock_calls == [
        call.request(
            "GET",
            sentinel.url,
            headers=sentinel.headers,
            proxies=sentinel.proxies,
            params=sentinel.params,
            stream=sentinel.stream,
        ),
    ]
