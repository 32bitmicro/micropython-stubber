from pathlib import Path
from typing import Dict, List, Optional

import jsonlines
from loguru import logger as log

from mpflash.common import FWInfo
from mpflash.vendor.versions import clean_version

from .config import config


# #########################################################################################################
def downloaded_firmwares(fw_folder: Path) -> List[FWInfo]:
    """Load a list of locally downloaded firmwares from the jsonl file"""
    firmwares: List[FWInfo] = []
    try:
        with jsonlines.open(fw_folder / "firmware.jsonl") as reader:
            firmwares.extend(iter(reader))
    except FileNotFoundError:
        log.error(f"No firmware.jsonl found in {fw_folder}")
    # sort by filename
    firmwares.sort(key=lambda x: x["filename"])
    return firmwares


def find_downloaded_firmware(
    *,
    board_id: str,
    version: str = "",
    port: str = "",
    variants: bool = False,
    fw_folder: Optional[Path] = None,
    trie: int = 1,
    selector: Optional[Dict[str, str]] = None,
) -> List[FWInfo]:
    if selector is None:
        selector = {}
    fw_folder = fw_folder or config.firmware_folder
    # Use the information in firmwares.jsonl to find the firmware file
    fw_list = downloaded_firmwares(fw_folder)
    if not fw_list:
        log.error("No firmware files found. Please download the firmware first.")
        return []
    # filter by version
    version = clean_version(version, drop_v=True)
    fw_list = filter_downloaded_fwlist(fw_list, board_id, version, port, variants, selector)

    if not fw_list and trie < 3:
        log.info(f"Try ({trie+1}) to find a firmware for the board {board_id}")
        if trie == 1:
            # ESP board naming conventions have changed by adding a PORT refix
            if port.startswith("esp") and not board_id.startswith(port.upper()):
                board_id = f"{port.upper()}_{board_id}"
            # RP2 board naming conventions have changed by adding a _RPIprefix
            if port == "rp2" and not board_id.startswith("RPI_"):
                board_id = f"RPI_{board_id}"
        elif trie == 2:
            board_id = board_id.replace("_", "-")

        fw_list = find_downloaded_firmware(
            fw_folder=fw_folder,
            board_id=board_id,
            version=version,
            port=port,
            trie=trie + 1,
            selector=selector,
        )
        # hope we have a match now for the board
    # sort by filename
    fw_list.sort(key=lambda x: x["filename"])
    return fw_list


def filter_downloaded_fwlist(
    fw_list: List[FWInfo],
    board_id: str,
    version: str,
    port: str,
    # preview: bool,
    variants: bool,
    selector: dict,
) -> List[FWInfo]:
    """Filter the downloaded firmware list based on the provided parameters"""
    if "preview" in version:
        # never get a preview for an older version
        fw_list = [fw for fw in fw_list if fw["preview"]]
    else:
        fw_list = [fw for fw in fw_list if fw["version"] == version]

    # filter by port
    if port:
        fw_list = [fw for fw in fw_list if fw["port"] == port]

    if board_id:
        if variants:
            # any variant of this board_id
            fw_list = [fw for fw in fw_list if fw["board"] == board_id]
        else:
            # the firmware variant should match exactly the board_id
            fw_list = [fw for fw in fw_list if fw["variant"] == board_id]
    if selector and port in selector:
        fw_list = [fw for fw in fw_list if fw["filename"].endswith(selector[port])]
    return fw_list


# #########################################################################################################
#