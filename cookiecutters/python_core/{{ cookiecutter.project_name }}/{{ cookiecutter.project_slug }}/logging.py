import json
import logging
import os
import sys
from contextlib import contextmanager
from typing import Optional

# Modules we want to set to WARNING log level to prevent unnecessarily verbose logs
KNOWN_VERBOSE_LOGGERS = (
    "msrest",
    "urllib3",
    "azure",
    "uamqp",
    "parso",
    "snscrape",
    "botocore",
    "awswrangler",
    "py4j",
    "s3transfer",
)


def _get_common_logging_format(use_json: bool = False):  # pragma: nocover
    # TODO: Decide if we want to use JSON logging?
    if use_json:
        return "%(levelname)s: " + json.dumps(
            {
                "time": "%(asctime)s",
                "context": "[%(process)d/%(thread)d] %(name)s %(filename)s:%(lineno)d",
                "message": "%(message)s",
            }
        )
    return "%(asctime)s [%(process)d/%(thread)d] %(name)s %(filename)s:%(lineno)d %(levelname)-8s %(message)s"


def _get_common_date_format():  # pragma: nocover
    return "%Y-%m-%d %H:%M:%S"


def configure_logging(
    level: Optional[str] = None, use_json: Optional[bool] = None
):  # pragma: nocover
    """Set logging at the provided level.

    Ensures that known verbose loggers are set to WARNING level to suppress unnecessary logging."""
    # Cache options in environment for subprocesses
    if level is not None:
        os.environ["LOG_LEVEL"] = level
        level = getattr(logging, level)
    else:
        _default_log_level_str = os.environ.get("LOG_LEVEL", "INFO")
        level = getattr(logging, _default_log_level_str)
    if use_json is not None:
        os.environ["LOG_JSON"] = str(int(use_json))
    else:
        use_json = bool(int(os.environ.get("LOG_JSON", "0")))

    logging.basicConfig(
        stream=sys.stdout,
        format=_get_common_logging_format(use_json=use_json),
        level=level,
        datefmt=_get_common_date_format(),
        force=True,  # Always flush
    )
    # Set known-verbose loggers to log at WARNING level
    for handler in KNOWN_VERBOSE_LOGGERS:
        logging.getLogger(handler).setLevel(logging.WARNING)
    # Azure credentials log at WARNING level every time they fail, which is annoying and unnecessary
    # given the DefaultAzureCredential's access pattern
    for handler in ("azure.identity",):
        logging.getLogger(handler).setLevel(logging.ERROR)


# From: https://gist.github.com/simon-weber/7853144
@contextmanager
def all_logging_disabled():
    """A context manager that will prevent any logging messages
    triggered during the body from being processed."""
    # Hacks here:
    #  * can't get the current module-level override => use an undocumented
    #    (but non-private!) interface

    previous_level = logging.root.manager.disable

    logging.disable(logging.CRITICAL)

    try:
        yield
    finally:
        logging.disable(previous_level)
