"""
Main file of the package which define the CLI and each submodule
"""

import click

from .config import config
from .ready_dxf.main import ready_dxf
from .copy_full_assembly.main import copy_full_assembly
from .auto_exporter.main import auto_export
from .stat.main import stat


__version__ = "0.6.0"
__author__ = "Devillez Louis"
__maintainer__ = "Deville Louis"
__email__ = "louis.devillez@gmail.com"


@click.group()
@click.version_option(__version__, "-v", "--version")
@click.help_option("-h", "--help")
def cli() -> None:
    """
    Combination of commands to help you work with solidworks
    """


cli.add_command(config)
cli.add_command(ready_dxf)
cli.add_command(copy_full_assembly)
cli.add_command(auto_export)
cli.add_command(stat)

if __name__ == "__main__":
    cli()
