"""Driver module for mail-org."""
from pathlib import Path

import click

from .map_engine import MapEngine


@click.command()
@click.option(
    "--config-file",
    "-c",
    required=False,
    type=str,
    default="mail-org.json",
)
def main(config_file):
    """Driver routine for using mail-org."""
    with MapEngine() as me:
        me.apply(Path(config_file))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
