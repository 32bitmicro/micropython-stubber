"""mpflash is a CLI to download and flash MicroPython firmware to various boards."""

# import rich_click as click

import click
from loguru import logger as log

from .cli_download import cli_download
from .cli_flash import cli_flash_board
from .cli_group import cli
from .cli_list import cli_list_mcus


def mpflash():
    cli.add_command(cli_list_mcus)
    cli.add_command(cli_download)
    cli.add_command(cli_flash_board)

    # cli(auto_envvar_prefix="MPFLASH")
    if 1:
        result = cli(standalone_mode=False)
    else:
        try:
            result = cli(standalone_mode=False)
            exit(result)
        except AttributeError as e:
            log.error(f"Error: {e}")
            exit(-1)
        except click.exceptions.ClickException as e:
            log.error(f"Error: {e}")
            exit(-2)


if __name__ == "__main__":
    mpflash()
