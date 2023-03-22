import logging
from typing import Dict, Optional, Tuple, Type

import requests
import requests.exceptions
import retry
import urllib3.exceptions

from .common import time_api

SLEEPTIME = 90

RETRYABLE_ERROR_CODES = (429, 560, 502, 503, 500)
RETRYABLE_ERROR_MESSAGES = (
    "retry in a few",
    "wait a few",
    "trying again",
    "try again",
)

RETRYABLE_EXCEPTIONS = (
    TimeoutError,
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
    urllib3.exceptions.ProtocolError,
    urllib3.exceptions.HTTPError,
    urllib3.exceptions.TimeoutError,
)


class RetryableError(Exception):
    """An exception indicating a retryable HTTP error."""


def request_with_retry(
    logger: logging.Logger,
    retryable_exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    retryable_error_messages: Tuple[str, ...] = RETRYABLE_ERROR_MESSAGES,
    retryable_error_codes: Tuple[int, ...] = RETRYABLE_ERROR_CODES,
    sleep_time: float = SLEEPTIME,
    backoff: float = 1.25,
    max_delay: float = 60 * 5,
    max_tries: int = 5,
    raise_exception_on_faiure_status: bool = True,
):
    @retry.retry(
        exceptions=RetryableError,
        backoff=backoff,
        delay=sleep_time,
        max_delay=max_delay,
        tries=max_tries,
        logger=logger,
    )
    @time_api
    def _request_with_retry(
        session: requests.Session,
        url: str,
        method: str = "GET",
        stream: bool = False,
        headers: Optional[Dict] = None,
        proxies: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> requests.Response:
        try:
            logger.debug("Running request for url (%s).", url)
            resp = session.request(
                method,
                url,
                headers=headers,
                proxies=proxies,
                stream=stream,
                params=params,
            )
        except retryable_exceptions as e:
            raise RetryableError(
                f"Encountered retryable exception in request ({url}): {e}"
            )
        if resp.status_code == 200:
            return resp
        if resp.status_code in retryable_error_codes:
            raise RetryableError(
                f"Encountered retryable backoff request from request ({url}): {resp.status_code}. Response: {resp.text}"
            )
        text_lowercase = resp.text.lower()
        if any(i in text_lowercase for i in retryable_error_messages):
            raise RetryableError(
                f"Encountered an error messages that looks retryable for request ({url}): {resp.status_code}. Message: {resp.text}"
            )
        if raise_exception_on_faiure_status:
            raise RuntimeError(
                f"Invalid response code: {resp.status_code}. Response: {resp.text}"
            )
        return resp

    return _request_with_retry
