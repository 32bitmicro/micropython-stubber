import json
from typing import List

import rich_click as click
from rich import print

from .cli_group import cli
from .common import filtered_comports
from .list import list_mcus, show_mcus
from .logger import make_quiet


@cli.command("list", help="List the connected MCU boards.")
@click.option(
    "--json",
    "-j",
    "as_json",
    is_flag=True,
    default=False,
    show_default=True,
    help="""Output in json format""",
)
@click.option(
    "--serial",
    "--serial-port",
    "-s",
    "serial",
    default=["*"],
    multiple=True,
    show_default=True,
    help="Which serial port(s) to list. ",
    metavar="SERIALPORT",
)
@click.option(
    "--ignore",
    "-i",
    is_eager=True,
    help="Serial port(s) to ignore. Defaults to MPFLASH_IGNORE.",
    multiple=True,
    default=[],
    envvar="MPFLASH_IGNORE",
    show_default=True,
    metavar="SERIALPORT",
)
@click.option(
    "--bluetooth/--no-bluetooth",
    "-b/-nb",
    is_flag=True,
    default=False,
    show_default=True,
    help="""Include bluetooth ports in the list""",
)
@click.option(
    "--progress/--no-progress",
    # "-p/-np", -p is already used for --port
    "progress",
    is_flag=True,
    default=True,
    show_default=True,
    help="""Show progress""",
)
def cli_list_mcus(serial: List[str], ignore: List[str], bluetooth: bool, as_json: bool, progress: bool = True) -> int:
    """List the connected MCU boards, and output in a nice table or json."""
    if as_json:
        # avoid noise in json output
        make_quiet()
    # TODO? Ask user to select a serialport if [?] is given ?

    conn_mcus = list_mcus(ignore=ignore, include=serial, bluetooth=bluetooth)
    if as_json:
        print(json.dumps([mcu.__dict__ for mcu in conn_mcus], indent=4))
        progress = False
    if progress:
        show_mcus(conn_mcus, refresh=False)
    return 0 if conn_mcus else 1
