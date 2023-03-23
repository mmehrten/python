import copy
import json
import logging
from typing import Dict, List, Union

import munch
import yaml

logger = logging.getLogger(__name__)


class Config(munch.Munch, dict):
    def union(self, other: Dict, clone=False) -> "Config":
        """Union two configurations, optionally deepcopying to return an new config.

        For values that are dictionaries, method will take the union of the left and right dictionaries.
        For values that are lists, method will concatenate left and right lists.

        :param other: The configuration to union into the base config
        """
        if clone:
            self = copy.deepcopy(self)
        for k in self.keys() & other.keys():
            if isinstance(self[k], Dict):
                self[k].update(other[k])
            elif isinstance(self[k], List):
                self[k] += other[k]
            else:
                self[k] = other[k]
        for k in other.keys() - self.keys():
            self[k] = other[k]
        return self

    @staticmethod
    def _read_yaml_or_json(data: Union[str, bytes]) -> Dict:
        """Read a config string as either JSON or YAML, accepting either working format."""
        try:
            return yaml.safe_load(data)
        except Exception:
            logger.debug("Failed to read config as yaml, trying json.")

        try:
            return json.loads(data)
        except Exception:
            logger.debug("Failed to read config as JSON, failed to load any config")

        return {}

    @classmethod
    def read(
        cls,
        name: str = "config.yaml",
    ) -> "Config":
        """Read a config file from a local path.

        Returns an empty config if none can be loaded.

        :param name: The config file name in S3, or the local path containing the config file.
        :returns: A Config (dict-like) object.
        """
        try:
            with open(name, "r") as f:
                return cls(cls.fromDict(cls._read_yaml_or_json(f.read())))
        except Exception as e:
            logger.info(
                "Failed to load config local file (%s). Proceeding without config. Error: %s",
                name,
                e,
            )
        return cls()
