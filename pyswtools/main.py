"""
Docstring
"""

import click

from .ready_dxf.main import ready_dxf


__version__ = "0.2.0"
__author__ = "Devillez Louis, Kjell Magne Fauske"
__maintainer__ = "Deville Louis"
__email__ = "louis.devillez@gmail.com"


@click.group(invoke_without_command=True)
@click.version_option(__version__, "-v", "--version")
@click.help_option("-h", "--help")
def cli() -> None:
    """
    Combination of commands to help you work with solidworks
    """
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()


cli.add_command(ready_dxf)

if __name__ == "__main__":
    cli()
