import os
import sys
from pathlib import Path

import pytest

# pylint: disable=wrong-import-position,import-error
import stubber.basicgit as git

# Module Under Test
import stubber.get_mpy as get_mpy
import stubber.utils as utils

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses

from mock import MagicMock

# Mostly: No Mocks, does actual extraction from repro
from pytest_mock import MockerFixture


def checkout_repos(mpy_version, mpy_path, mpy_lib):
    "checkout the repos"
    version = git.get_tag(mpy_path)
    if not version or version < mpy_version:
        git.checkout_tag(mpy_version, mpy_path)
        version = git.get_tag(mpy_path)
        assert version == mpy_version, "prep: could not checkout version {} of {}".format(mpy_version, mpy_path)
    get_mpy.match_lib_with_mpy(version_tag=mpy_version, lib_folder=mpy_lib)


@pytest.mark.parametrize(
    "path, port, board",
    [
        (
            "C:\\develop\\MyPython\\TESTREPO-micropython\\ports\\esp32\\modules\\_boot.py",
            "esp32",
            None,
        ),
        (
            "/develop/MyPython/TESTREPO-micropython/ports/esp32/modules/_boot.py",
            "esp32",
            None,
        ),
        ("../TESTREPO-micropython/ports/esp32/modules/_boot.py", "esp32", None),
        (
            "C:\\develop\\MyPython\\TESTREPO-micropython\\ports\\stm32\\boards\\PYBV11\\modules\\_boot.py",
            "stm32",
            "PYBV11",
        ),
        (
            "/develop/MyPython/TESTREPO-micropython/ports/stm32/boards/PYBV11/modules/_boot.py",
            "stm32",
            "PYBV11",
        ),
        (
            "../TESTREPO-micropython/ports/stm32/boards/PYBV11/modules/_boot.py",
            "stm32",
            "PYBV11",
        ),
    ],
)
def test_extract_target_names(path, port, board):
    _port, _board = get_mpy.get_target_names(path)
    assert _board == board
    assert _port == port


def test_one_manifest_uasync(tmp_path: Path, testrepo_micropython: Path, testrepo_micropython_lib: Path):
    "test if task.py is included with the uasyncio frozen module"
    mpy_version = "1.18"
    mpy_folder = testrepo_micropython.absolute().as_posix()
    lib_folder = testrepo_micropython_lib.absolute().as_posix()
    stub_folder = tmp_path.absolute().as_posix()

    checkout_repos(mpy_version, mpy_folder, lib_folder)

    manifest = Path(mpy_folder + "/ports/esp32/boards/manifest.py")
    get_mpy.get_frozen_from_manifest([manifest.as_posix()], stub_folder, mpy_folder, lib_folder, mpy_version)

    assert (tmp_path / "esp32/GENERIC" / "uasyncio/task.py").exists()
    # check if the task.py is included


@pytest.mark.skipif(os.getenv("CI", "local") != "local", reason="cant test in CI/CD")
@pytest.mark.slow
@pytest.mark.parametrize("mpy_version", ["v1.16", "v1.18", "master"])  # "v1.12", "v1.13", "v1.15",
def test_freezer_mpy_manifest(mpy_version: str, tmp_path: Path, testrepo_micropython: Path, testrepo_micropython_lib: Path):
    "test if we can freeze source using manifest.py files"
    # mpy_path = Path(testrepo_micropython)
    # mpy_lib = Path(testrepo_micropython_lib)
    mpy_folder = testrepo_micropython.as_posix()
    lib_folder = testrepo_micropython_lib.as_posix()

    checkout_repos(mpy_version, mpy_folder, lib_folder)

    get_mpy.get_frozen(str(tmp_path), version=mpy_version, mpy_folder=mpy_folder, lib_folder=lib_folder)
    scripts = list(tmp_path.rglob("*.py"))

    assert scripts is not None, "can freeze scripts from manifest"
    assert len(scripts) > 10, "expect at least 50 files, only found {}".format(len(scripts))

    result = utils.generate_pyi_files(tmp_path)
    assert result == True


# Some mocked tests to improve the coverage
def test_freezer_mpy_manifest_mocked(
    tmp_path: Path,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    mocker: MockerFixture,
):
    "mocked test if we can freeze source using manifest.py files"
    mpy_version: str = "master"

    mock_get_frozen_from: MagicMock = mocker.patch("stubber.get_mpy.get_frozen_from_manifest", autospec=True, return_value=0)
    get_frozen_folders: MagicMock = mocker.patch("stubber.get_mpy.get_frozen_folders", autospec=True)
    mpy_folder = testrepo_micropython.as_posix()
    lib_folder = testrepo_micropython_lib.as_posix()

    # call with folders
    mock_glob: MagicMock = mocker.patch(
        "stubber.get_mpy.glob.glob",
        autospec=True,
        return_value=[Path("./repos/micropython/ports\\esp32\\boards\\manifest.py")],
    )

    get_mpy.get_frozen(str(tmp_path), version=mpy_version, mpy_folder=mpy_folder, lib_folder=lib_folder)
    assert get_frozen_folders.called == 0
    assert mock_get_frozen_from.called
    assert mock_glob.called


# def test_freezer_mpy_manifest_m2(
#     tmp_path: Path,
#     testrepo_micropython: Path,
#     testrepo_micropython_lib: Path,
#     mocker: MockerFixture,
# ):
#     "mocked test if we can freeze source oldstyle"

#     mpy_version: str = "master"
#     mock_get_frozen_from: MagicMock = mocker.patch("stubber.get_mpy.get_frozen_from_manifest", autospec=True, return_value=0)
#     get_frozen_folders: MagicMock = mocker.patch("stubber.get_mpy.get_frozen_folders", autospec=True)
#     mpy_path = testrepo_micropython.as_posix()
#     mpy_lib = testrepo_micropython_lib.as_posix()

#     # fake with no manifest.py folders
#     mock_glob: MagicMock = mocker.patch("stubber.get_mpy.glob.glob")

#     get_mpy.get_frozen(str(tmp_path), version=mpy_version, mpy_folder=mpy_path, lib_folder=mpy_lib)

#     get_mpy.get_frozen(str(tmp_path), version=mpy_version)
#     assert get_frozen_folders.called
#     assert mock_get_frozen_from.called == 0
#     assert mock_glob.called


@pytest.mark.skipif(os.getenv("CI", "local") != "local", reason="cant test in CI/CD")
# @pytest.mark.basicgit
@pytest.mark.slow
@pytest.mark.parametrize("mpy_version", ["v1.10", "v1.9.4"])
def test_freezer_mpy_folders(mpy_version, tmp_path, testrepo_micropython: Path, testrepo_micropython_lib: Path):
    "test if we can freeze source using modules folders"
    mpy_folder = testrepo_micropython.as_posix()
    lib_folder = testrepo_micropython_lib.as_posix()
    stub_path = tmp_path

    checkout_repos(mpy_version, mpy_folder, lib_folder)

    get_mpy.get_frozen_folders(stub_path, mpy_folder, lib_folder=testrepo_micropython_lib.as_posix(), version=mpy_version)

    result = utils.generate_pyi_files(tmp_path)
    assert result == True
