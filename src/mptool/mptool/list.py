import json
from typing import List

import rich_click as click
from rich import print
from rich.progress import track
from rich.table import Table

# TODO: - refactor so that we do not need the entire stubber package
from stubber.bulk.mpremoteboard import MPRemoteBoard

from .cli_group import cli


@cli.command("list", help="List the connected boards.")
@click.option(
    "--json",
    "-j",
    "as_json",
    is_flag=True,
    default=False,
    show_default=True,
    help="""Output in json format""",
)
def list_boards(as_json: bool):
    conn_boards = [MPRemoteBoard(p) for p in MPRemoteBoard.connected_boards()]
    for mcu in track(conn_boards, description="Getting board info"):
        try: 
            mcu.get_mcu_info()
        except ConnectionError as e:
            print(f"Error: {e}")
            continue
    if as_json:
        print(json.dumps([mcu.__dict__ for mcu in conn_boards], indent=4))
    else:
        show_boards(conn_boards, refresh=False)


def show_boards(conn_boards: List[MPRemoteBoard], title: str = "Connected boards", refresh: bool = True):
    """Show the list of connected boards in a nice table"""
    table = Table(title=title)
    table.add_column("Serial")
    table.add_column("Family")
    table.add_column("Port")
    table.add_column("Board")
    table.add_column("CPU")
    table.add_column("Version")
    table.add_column("build")

    for mcu in track(conn_boards, transient=True, description="Updating board info"):
        if refresh:
            try:
                mcu.get_mcu_info()
            except ConnectionError:
                continue
        table.add_row(mcu.serialport, mcu.family, mcu.port, mcu.board, mcu.cpu, mcu.version, mcu.build)
    print(table)