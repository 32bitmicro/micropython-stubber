"""mpflash is a CLI to download and flash MicroPython firmware to various boards."""

# import rich_click as click

import click
import sentry_sdk
from loguru import logger as log
from sentry_sdk.integrations.loguru import LoggingLevels, LoguruIntegration

from .cli_download import cli_download
from .cli_flash import cli_flash_board
from .cli_group import cli
from .cli_list import cli_list_mcus


def mpflash():
    start_monitor()
    cli.add_command(cli_flash_board)
    cli.add_command(cli_list_mcus)
    cli.add_command(cli_download)
    # cli(auto_envvar_prefix="MPFLASH")
    try:
        result = cli(standalone_mode=False)
        exit(result)
    except AttributeError as e:
        log.error(f"Error 1: {e}")
        exit(-1)
    except click.exceptions.ClickException as e:
        log.error(f"Error 2: {e}")
        exit(-2)


def start_monitor():
    sentry_loguru = LoguruIntegration(
        level=LoggingLevels.INFO.value,  # Capture info and above as breadcrumbs
        event_level=LoggingLevels.ERROR.value,  # Send errors as events
    )
    sentry_sdk.init(
        dsn="https://882a44352c55ae0ca79519f2aa6f5f86@o4507218888359936.ingest.de.sentry.io/4507218891046992",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        profiles_sample_rate=0,
        send_default_pii=False,
        integrations=[
            sentry_loguru,
        ],
        server_name="masked",
    )


start_monitor()
if __name__ == "__main__":

    mpflash()
