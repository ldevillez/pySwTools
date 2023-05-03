"""
Prepare an output dxf from SW to be laser cutted
"""

import click

from .dxf_utilities import check_file_and_folder
from .file_utilities import append_name


@click.command()
@click.help_option("-h", "--help")
@click.argument(
    "input_path",
    type=click.Path(exists=True),
)
def ready_dxf(input_path) -> None:
    """
    Prepare an output dxf from SW to be laser cutted
    """
    click.echo(input_path)
    check_file_and_folder(input_path, save_path=append_name(input_path, "_cleaned"))
