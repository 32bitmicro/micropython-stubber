##########################################################################################
# minify
##########################################################################################
import logging
from pathlib import Path
from typing import Union

import click
from stubber.minify import minify
from stubber.utils.my_version import __version__

from .stubber_cli import stubber_cli

##########################################################################################
log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(name="minify")
@click.option(
    "--source", "-s", default="board/createstubs.py", type=click.Path(exists=True, file_okay=True, dir_okay=False), show_default=True
)
@click.option("--target", "-t", default="./minified", type=click.Path(exists=True, file_okay=True, dir_okay=True), show_default=True)
@click.option("--diff", "-d", help="Show the functional changes made to the source script.", default=False, is_flag=True)
@click.option("--compile", "-c", "-xc", "cross_compile", help="Cross compile after minification.", default=False, is_flag=True)
@click.option("--all", "-a", help="Minify all variants (normal, _mem and _db).", default=False, is_flag=True)
@click.option(
    "--report/--no-report",
    "keep_report",
    help="Keep or disable minimal progress reporting in the minified version.",
    default=True,
    show_default=True,
)
@click.pass_context
def cli_minify(
    ctx,
    source: Union[str, Path],
    target: Union[str, Path],
    keep_report: bool,
    diff: bool,
    cross_compile: bool,
    all: bool,
) -> int:
    """
    Minify createstubs*.py.

    Creates a minified version of the SOURCE micropython file in TARGET (file or folder).
    The goal is to use less memory / not to run out of memory, while generating Firmware stubs.
    """
    if all:
        sources = ["board/createstubs.py", "board/createstubs_mem.py", "board/createstubs_db.py"]
    else:
        sources = [source]

    for source in sources:
        print(f"\nMinifying {source}...")
        result = minify(source, target, keep_report, diff, cross_compile)

    print("\nDone!")
    return 0