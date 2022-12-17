from typing import List, Union

import click
from loguru import logger as log
from stubber.commands.cli import stubber_cli
from stubber.publish.publish import publish_multiple
from tabulate import tabulate
from stubber.utils.config import CONFIG


@stubber_cli.command(name="publish")
@click.option("--family", default="micropython", type=str, show_default=True)
@click.option(
    "--version",
    "--Version",
    "-V",
    "versions",
    multiple=True,
    default=[CONFIG.STABLE_VERSION],
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--port",
    "-p",
    "ports",
    multiple=True,
    default=["auto"],
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--board",
    "-b",
    "boards",
    multiple=True,
    default=["GENERIC"],  # or "auto" ?
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--pypi/--test-pypi",
    "production",
    is_flag=True,
    default=False,
    show_default=True,
    prompt="Publish to PYPI (y) or Test-PYPI (n)",
    help="publish to PYPI or Test-PYPI",
)
@click.option(
    "--dry-run",
    "dryrun",
    is_flag=True,
    default=False,
    help="go though the motions but do not publish",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="create new post release even if no changes detected",
)
@click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="clean folders after processing and publishing",
)

# @click.option(
#     "--type",
#     "-t",
#     "stub_type",
#     default=ALL_TYPES[0],
#     show_default=True,
#     type=click.Choice(ALL_TYPES),
#     help="stub type to publish",
# )


def cli_publish(
    family: str,
    versions: Union[str, List[str]],
    ports: Union[str, List[str]],
    boards: Union[str, List[str]],
    production: bool,
    dryrun: bool,
    force: bool,
    clean: bool,
    # stub_type: str,
):
    """
    Commandline interface to publish stubs.
    """
    # force overrules dryrun
    if force:
        dryrun = False
    # lists please
    versions = list(versions)
    ports = list(ports)
    boards = list(boards)

    # db = get_database(publish_path=CONFIG.publish_path, production=production)
    destination = "pypi" if production else "test-pypi"
    log.info(f"Publish {family} {versions} {ports} {boards} to {destination}")

    results = publish_multiple(
        frozen=True,
        family=family,
        versions=versions,
        ports=ports,
        boards=boards,
        production=production,
        dryrun=dryrun,
        force=force,
        clean=clean,
    )
    log.info(tabulate(results, headers="keys"))
