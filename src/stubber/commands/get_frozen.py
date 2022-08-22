##########################################################################################
# get-frozen
##########################################################################################
import logging
from pathlib import Path
from typing import List

import click
import stubber.get_mpy as get_mpy
import stubber.basicgit as git
import stubber.utils as utils

from stubber.utils.config import CONFIG
from stubber.utils.my_version import __version__

from .stubber_cli import stubber_cli

##########################################################################################
log = logging.getLogger("stubber")
#########################################################################################

@stubber_cli.command(name="get-frozen")
@click.option(
    "--stub-folder",
    "-stubs",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    show_default=True,
)
# @click.option("--path", "-p", default=config.repo_path.as_posix(), type=click.Path(file_okay=False, dir_okay=True), show_default=True)
@click.option("--version", "--tag", default="", type=str, help="Version number to use. [default: Git tag]")
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules", show_default=True)
@click.option("--black/--no-black", default=True, help="Run black on the (new) frozen modules", show_default=True)
def cli_get_frozen(
    stub_folder: str = CONFIG.stub_path.as_posix(),
    # path: str = config.repo_path.as_posix(),
    version: str = "",
    pyi: bool = True,
    black: bool = True,
):
    """
    Get the frozen stubs for MicroPython.

    Get the frozen modules for the checked out version of MicroPython
    """

    stub_paths: List[Path] = []

    if len(version) == 0:
        version = utils.clean_version(git.get_tag(CONFIG.mpy_path.as_posix()) or "0.0")
    if version:
        log.info("MicroPython version : {}".format(version))
        # folder/{family}-{version}-frozen
        family = "micropython"
        stub_path = Path(stub_folder) / f"{family}-{utils.clean_version(version, flat=True)}-frozen"
        stub_paths.append(stub_path)
        get_mpy.get_frozen(
            stub_path.as_posix(), version=version, mpy_folder=CONFIG.mpy_path.as_posix(), lib_folder=CONFIG.mpy_lib_path.as_posix()
        )
    else:
        log.warning("Unable to find the micropython repo in folder : {}".format(CONFIG.mpy_path.as_posix()))
    utils.do_post_processing(stub_paths, pyi, black)
