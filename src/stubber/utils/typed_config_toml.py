"""
typed-config-toml

Extend typed-config to read configuration from .toml files

"""
# TODO : extend support for . notation in section names

from typing import Dict, List, Optional
from pathlib import Path

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib

from typedconfig.config import Config, key, section
from typedconfig.source import ConfigSource, EnvironmentConfigSource

import logging

log = logging.getLogger(__name__)


class TomlConfigSource(ConfigSource):
    """Read configuration from a .toml file

    prefix is used to allow for toml nested configuration
    a common prefix = "tool."

    ```
    #pyproject.toml
    [tool.deadparrot]
    species = "Norwegian Blue"
    state = "resting"
    details = ["pinging","Lovely plumage","3"]
    ```
    The use the below code to retrieve:
    ```
    # TODO
    ```
    """

    def __init__(self, filename: str, prefix: Optional[str] = None, must_exist: bool = True):
        self.filename = filename
        toml_dict = {}
        if Path(self.filename).exists():
            # Read data - will raise an exception if problem with file
            try:
                with open(filename, "rb") as f:
                    toml_dict = tomllib.load(f)
            except tomllib.TOMLDecodeError:  # pragma: no cover
                log.warning("unable to read ")
        elif must_exist:
            raise FileNotFoundError(f"Could not find config file {self.filename}")
        if not prefix or len(prefix) == 0:
            self.data = toml_dict
        else:
            # common prefix = "tool."
            try:
                self.data = toml_dict[prefix.rstrip(".")]
            except KeyError:  # pragma: no cover
                self.data = {}

        # Quick checks on data format

        assert isinstance(self.data, Dict)
        for k, v in self.data.items():
            assert isinstance(k, str)
            assert isinstance(v, Dict)
            for v_k, v_v in v.items():
                assert isinstance(v_k, str)
                # do not assume/require that all values are strings
                # assert isinstance(v_v, str)
        # Convert all keys to lowercase
        self.data = {k.lower(): {v_k.lower(): v_v for v_k, v_v in v.items()} for k, v in self.data.items()}

    def get_config_value(self, section_name: str, key_name: str) -> Optional[str]:
        # Extract info from data which we read in during __init__
        section = self.data.get(section_name.lower(), None)
        if section is None:
            return None
        return section.get(key_name.lower(), None)


# pyproject.toml
# """
# [tool.deadparrot]
# species = "Norwegian Blue"
# state = "resting"
# details = ["pinging","Lovely plumage","3",4]
# store_owner = "Michael Palin"
# interval = 5
# """

# @section("deadparrot")
# class ParrotConfig(Config):
#     name = key(cast=str, default="polly", required=False)
#     species = key(cast=str, default="bird")
#     state = key(cast=str)
#     details = key(cast=list[str])
#     store_owner = key(cast=str)


# # One Step

# config = ParrotConfig()
# config.add_source(EnvironmentConfigSource())
# config.add_source(TomlConfigSource("pyproject.toml", prefix="tool.", must_exist=False))  # ,"tools.micropython-stubber"))
# config.read()
# print(config)

# for x in config.details:
#     print(x)
