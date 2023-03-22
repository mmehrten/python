import enum
import logging
import multiprocessing
import os
from typing import Callable, Iterable, Optional, Type, Union

import click
import munch
import {{ cookiecutter.project_slug }}
from tqdm import tqdm

logger = logging.getLogger(__name__)


def _get_from_env(
    env_name: str, default: Optional[str], required: bool = True
) -> Optional[str]:
    """Get a variable from the environment, or use a default."""
    # Prefer environment variable to user passed default
    env_name = env_name.upper().replace("-", "_")
    if env_name in os.environ:
        return os.environ[env_name]
    if default:
        return default
    if required:
        raise ValueError(f"No input recieved for required variable: {env_name}")
    return None


@click.group()
@click.option(
    "--log-level",
    type=str,
    default=None,
    required=False,
    help="The log level, if not provided in the LOG_LEVEL environment variable.",
)
@click.option(
    "--log-json/--no-log-json",
    default=False,
    required=False,
    help="Whether or not to use JSON log format.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    log_level: str,
    log_json: bool,
):  # pragma: nocover # TODO: unit tests
    """Main CLI entrypoint."""
    {{ cookiecutter.project_slug }}.configure_logging(level=log_level, use_json=log_json)
    try:
        tqdm.pandas(mininterval=5)
    except ModuleNotFoundError:
        logger.debug("Pandas not installed, not configuring tqdm for pandas")


def parse_enum(
    enum_type: Type[enum.Enum], subset: Optional[Iterable[enum.Enum]] = None
) -> Callable[[Union[str, int]], enum.Enum]:
    """Return a function that will parse a string/integer into an enum of the given type."""

    def _parse_enum(value: Union[str, int]) -> enum.Enum:
        """Parse a string or integer into an enum.

        :param value: The enum key name or value name - e.g. `MY_ENUM_KEY = 1` could be parsed with `"MY_ENUM_KEY"` or `1`.
        :returns: The parsed enum.
        :raises: A ValueError if the enum can't be parsed.
        """
        values = [value]
        if isinstance(value, str):
            values = [value, value.upper()]
        for value in values:
            try:
                return enum_type(value)
            except ValueError:
                pass
            try:
                return enum_type[value]  # type: ignore # Only works for strings, but it's a simple fallback
            except KeyError:
                pass
        raise ValueError(f"Failed to parse {value} as {enum_type.__qualname__}")

    if not subset:
        subset = list(enum_type)
    _parse_enum.__name__ = f"[{'|'.join(i.name.lower() for i in subset)}]"
    return _parse_enum


def main():  # pragma: nocover # TODO: unit tests
    # Set multiprocessing to use spawn method - only runs once per Python session
    multiprocessing.set_start_method("spawn")
    cli(obj=munch.munchify({"config": {}, "sessions": {}}))
