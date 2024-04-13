"""
Module to download MicroPython firmware for specific boards and versions.
Uses the micropython.org website to get the available versions and locations to download firmware files.
"""

import functools
import itertools
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

# #########################################################################################################
# make sure that jsonlines does not mistake the MicroPython ujson for the CPython ujson
import jsonlines
import requests
from bs4 import BeautifulSoup
from loguru import logger as log
from rich.progress import track

from mpflash.common import PORT_FWTYPES

jsonlines.ujson = None  # type: ignore
# #########################################################################################################


MICROPYTHON_ORG_URL = "https://micropython.org/"

# Regexes to remove dates and hashes in the filename that just get in the way
RE_DATE = r"(-\d{8}-)"
RE_HASH = r"(.g[0-9a-f]+\.)"
# regex to extract the version from the firmware filename
RE_VERSION_PREVIEW = r"(\d+\.\d+(\.\d+)?(-\w+.\d+)?)"


# use functools.lru_cache to avoid needing to download pages multiple times
@functools.lru_cache(maxsize=500)
def get_page(page_url: str) -> str:
    """Get the HTML of a page and return it as a string."""
    response = requests.get(page_url)
    return response.content.decode()


@functools.lru_cache(maxsize=500)
def get_board_urls(page_url: str) -> List[Dict[str, str]]:
    """
    Get the urls to all the board pages listed on this page.
    Assumes that all links to firmware  have "class": "board-card"

    Args:
        page_url (str): The url of the page to get the board urls from.
    """
    downloads_html = get_page(page_url)
    soup = BeautifulSoup(downloads_html, "html.parser")
    tags = soup.findAll("a", recursive=True, attrs={"class": "board-card"})
    # assumes that all links are relative to the page url
    boards = [tag.get("href") for tag in tags]
    if "?" in page_url:
        page_url = page_url.split("?")[0]
    return [{"board": board, "url": page_url + board} for board in boards]


def board_firmware_urls(board_url: str, base_url: str, ext: str) -> List[str]:
    """
    Get the urls to all the firmware files for a board.
    Args:
        page_url (str): The url of the page to get the board urls from.
    ??? base_url (str): The base url to join the relative urls to.
        ext (str): The extension of the firmware files to get. (with or withouth leading .)

    the urls are relative urls to the site root

    """
    html = get_page(board_url)
    soup = BeautifulSoup(html, "html.parser")
    # get all the a tags:
    #  1. that have a url that starts with `/resources/firmware/`
    #  2. end with a matching extension for this port.
    tags = soup.findAll(
        "a",
        recursive=True,
        attrs={"href": re.compile(r"^/resources/firmware/.*\." + ext.lstrip(".") + "$")},
    )
    if "?" in base_url:
        base_url = base_url.split("?")[0]
    links: List = [urljoin(base_url, tag.get("href")) for tag in tags]
    return links


# type alias for the firmware info
FirmwareInfo = Dict[str, str]


# boards we are interested in ( this avoids getting a lot of boards we don't care about)
# The first run takes ~60 seconds to run for 4 ports , all boards
# so it makes sense to cache the results and skip boards as soon as possible
def get_boards(ports: List[str], boards: List[str], clean: bool) -> List[FirmwareInfo]:
    """
    Retrieves a list of firmware information for the specified ports and boards.

    Args:
        ports (List[str]): The list of ports to check for firmware.
        boards (List[str]): The list of boards to retrieve firmware information for.
        clean (bool): A flag indicating whether to perform a clean retrieval.

    Returns:
        List[FirmwareInfo]: A list of firmware information for the specified ports and boards.

    """
    board_urls: List[FirmwareInfo] = []
    for port in ports:
        download_page_url = f"{MICROPYTHON_ORG_URL}download/?port={port}"
        _urls = get_board_urls(download_page_url)
        # filter out boards we don't care about
        _urls = [board for board in _urls if board["board"] in boards]
        # add the port to the board urls
        for board in _urls:
            board["port"] = port

        for board in track(_urls, description=f"Checking {port} download pages", transient=True):
            # add a board to the list for each firmware found
            firmwares = []
            for ext in PORT_FWTYPES[port]:
                firmwares += board_firmware_urls(board["url"], MICROPYTHON_ORG_URL, ext)

            for _url in firmwares:
                board["firmware"] = _url
                board["preview"] = "preview" in _url  # type: ignore
                if ver_match := re.search(RE_VERSION_PREVIEW, _url):
                    board["version"] = ver_match[1]
                else:
                    board["version"] = ""
                if "preview." in board["version"]:
                    board["build"] = board["version"].split("preview.")[-1]
                else:
                    board["build"] = "0"
                fname = Path(board["firmware"]).name
                if clean:
                    # remove date from firmware name
                    fname = re.sub(RE_DATE, "-", fname)
                    # remove hash from firmware name
                    fname = re.sub(RE_HASH, ".", fname)
                board["filename"] = fname
                board["ext"] = Path(board["firmware"]).suffix
                board["variant"] = board["filename"].split("-v")[0] if "-v" in board["filename"] else ""
                board_urls.append(board.copy())
    return board_urls


def key_fw_ver_pre_ext_bld(x: FirmwareInfo):
    "sorting key for the retrieved board urls"
    return x["variant"], x["version"], x["preview"], x["ext"], x["build"]


def key_fw_var_pre_ext(x: FirmwareInfo):
    "Grouping key for the retrieved board urls"
    return x["variant"], x["preview"], x["ext"]


def download_firmwares(
    firmware_folder: Path,
    ports: List[str],
    boards: List[str],
    versions: Optional[List[str]] = None,
    *,
    force: bool = False,
    clean: bool = True,
):
    skipped = downloaded = 0
    if versions is None:
        versions = []
    unique_boards = get_firmware_list(ports, boards, versions, clean)

    for b in unique_boards:
        log.debug(b["filename"])
    # relevant

    log.info(f"Found {len(unique_boards)} relevant unique firmwares")

    firmware_folder.mkdir(exist_ok=True)

    with jsonlines.open(firmware_folder / "firmware.jsonl", "a") as writer:
        for board in unique_boards:
            filename = firmware_folder / board["port"] / board["filename"]
            filename.parent.mkdir(exist_ok=True)
            if filename.exists() and not force:
                skipped += 1
                log.debug(f" {filename} already exists, skip download")
                continue
            log.info(f"Downloading {board['firmware']}")
            log.info(f"         to {filename}")
            try:
                r = requests.get(board["firmware"], allow_redirects=True)
                with open(filename, "wb") as fw:
                    fw.write(r.content)
                board["filename"] = str(filename.relative_to(firmware_folder))
            except requests.RequestException as e:
                log.exception(e)
                continue
            writer.write(board)
            downloaded += 1
    log.info(f"Downloaded {downloaded} firmwares, skipped {skipped} existing files.")


def get_firmware_list(ports: List[str], boards: List[str], versions: List[str], clean: bool):
    """
    Retrieves a list of unique firmware information based on the specified ports, boards, versions, and clean flag.

    Args:
        ports : The list of ports to check for firmware.
        boards : The list of boards to filter the firmware by.
        versions : The list of versions to filter the firmware by.
        clean : A flag indicating whether to perform a clean check.

    Returns:
        List[FirmwareInfo]: A list of unique firmware information.

    """

    log.trace("Checking MicroPython download pages")
    preview = "preview" in versions
    board_urls = sorted(get_boards(ports, boards, clean), key=key_fw_ver_pre_ext_bld)

    log.debug(f"Total {len(board_urls)} firmwares")
    relevant = [
        board
        for board in board_urls
        if board["board"] in boards and (board["version"] in versions or board["preview"] and preview)
        # and b["port"] in ["esp32", "rp2"]
    ]
    log.debug(f"Matching firmwares: {len(relevant)}")
    # select the unique boards
    unique_boards: List[FirmwareInfo] = []
    for _, g in itertools.groupby(relevant, key=key_fw_var_pre_ext):
        # list is aleady sorted by build so we can just get the last item
        sub_list = list(g)
        unique_boards.append(sub_list[-1])
    log.debug(f"Last preview only: {len(unique_boards)}")
    return unique_boards


def download(
    destination: Path,
    ports: List[str],
    boards: List[str],
    versions: List[str],
    force: bool,
    clean: bool,
):
    """
    Downloads firmware files based on the specified destination, ports, boards, versions, force flag, and clean flag.

    Args:
        destination : The destination folder to save the downloaded firmware files.
        ports : The list of ports to check for firmware.
        boards : The list of boards to download firmware for.
        versions : The list of versions to download firmware for.
        force : A flag indicating whether to force the download even if the firmware file already exists.
        clean : A flag indicating whether to perform a clean download.

    Returns:
        None

    Raises:
        SystemExit: If no boards are found or specified.

    """
    if not boards:
        log.critical("No boards found, please connect a board or specify boards to download firmware for.")
        exit(1)
    # versions = [clean_version(v, drop_v=True) for v in versions]  # remove leading v from version
    try:
        destination.mkdir(exist_ok=True, parents=True)
    except (PermissionError, FileNotFoundError) as e:
        log.critical(f"Could not create folder {destination}\n{e}")
        exit(1)
    download_firmwares(destination, ports, boards, versions, force=force, clean=clean)