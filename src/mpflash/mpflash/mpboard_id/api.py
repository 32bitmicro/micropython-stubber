import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple, TypedDict, Union

from mpflash.common import PORT_FWTYPES, clean_version


# Board  based on the dataclass Board but changed to TypedDict
# - source : get_boardnames.py
class Board(TypedDict):
    """MicroPython Board definition"""

    description: str
    port: str
    board: str
    board_name: str
    mcu_name: str
    path: Union[Path, str]
    version: str
    cpu: str


@lru_cache(maxsize=None)
def read_boardinfo() -> List[Board]:
    """Reads the board_info.json file and returns the data as a list of Board objects"""
    with open(Path(__file__).parent / "board_info.json", "r") as file:
        return json.load(file)


def known_mp_ports() -> List[str]:
    # TODO: Filter for Version
    mp_boards = read_boardinfo()
    # select the unique ports from info
    ports = set({board["port"] for board in mp_boards if board["port"] in PORT_FWTYPES.keys()})
    return sorted(list(ports))


def get_mp_boards_for_port(port: str, versions: Optional[List[str]] = None):
    """
    Returns a list of boards for the given port and version(s)

    port : str : The Micropython port to filter for
    versions : List[str] : The Micropython versions to filter for (actual versions required)"""
    mp_boards = read_boardinfo()

    # filter for 'preview' as they are not in the board_info.json
    # instead use stable version
    versions = versions or []
    if "preview" in versions:
        versions.remove("preview")
        versions.append("stable")
    if versions:
        # make sure of the v prefix
        versions = [clean_version(v) for v in versions]
        # filter for the version(s)
        mp_boards = [board for board in mp_boards if board["version"] in versions]
    # filter for the port
    mp_boards = [board for board in mp_boards if board["port"] == port]
    return mp_boards


def known_mp_boards(port: str, versions: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """
    Returns a list of tuples with the description and board name for the given port and version

    port : str : The Micropython port to filter for
    versions : List[str] : The Micropython versions to filter for (actual versions required)
    """
    mp_boards = get_mp_boards_for_port(port, versions)

    boards = set(
        {(f'{board["description"]} [board["board"]] {board["version"]}', board["board"]) for board in mp_boards}
    )
    return sorted(list(boards))


def find_mp_board(board: str) -> Board:
    """Find the board for the given board"""
    info = read_boardinfo()
    for board_info in info:
        if board_info["board"] == board:
            if "cpu" not in board_info or not board_info["cpu"]:
                if " with " in board_info["description"]:
                    board_info["cpu"] = board_info["description"].split(" with ")[-1]
                else:
                    board_info["cpu"] = board_info["port"]
            return board_info
    raise LookupError(f"Board {board} not found")
