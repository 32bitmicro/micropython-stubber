import logging
from pathlib import Path

from .typed_config_toml import Config, EnvironmentConfigSource, TomlConfigSource, key, section

log = logging.getLogger(__name__)


@section("micropython-stubber")
class StubberConfig(Config):
    "stubber confguration class"
    stub_path = key(key_name="stub-path", cast=Path, required=False, default=Path("./stubs"))
    "a Path to the stubs directory"
    # relative to stubs folder
    fallback_path = key(key_name="fallback-path", cast=Path, required=False, default=Path("typings/fallback"))
    "a Path to the fallback stubs directory"

    repo_path = key(key_name="repo-path", cast=Path, required=False, default=Path("./repos"))
    "a Path to the repo directory"
    # micropython and micropython-lib are relative to ./repo folder
    mpy_path = key(key_name="mpy-path", cast=Path, required=False, default=Path("micropython"))
    "a Path to the micropython folder in the repos directory"

    mpy_lib_path = key(key_name="mpy-lib-path", cast=Path, required=False, default=Path("micropython-lib"))
    "a Path to the micropython-lib folder in the repos directory"

    def post_read_hook(self) -> dict:
        config_updates = dict()
        # relative to stubs
        config_updates.update(fallback_path=self.stub_path / self.fallback_path)

        # relative to repo path
        config_updates.update(mpy_path=self.repo_path / self.mpy_path)
        config_updates.update(mpy_lib_path=self.repo_path / self.mpy_lib_path)
        return config_updates


def readconfig(filename: str = "pyproject.toml", prefix: str = "tool.", must_exist: bool = True):
    config = StubberConfig()
    config.add_source(EnvironmentConfigSource())
    config.add_source(TomlConfigSource(filename, prefix=prefix, must_exist=must_exist))  # ,"tools.micropython-stubber"))
    config.read()
    return config


CONFIG = readconfig()
