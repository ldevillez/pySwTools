"""
Module of generic functions
"""

import platform
import click


def check_system_verbose() -> bool:
    """
    Check if the system is windows otherwise print a message
    """
    if platform.system() != "Windows":
        click.echo("Sorry but you need windows to execute this function")
        return False
    return True


def check_system() -> bool:
    """
    Check if the system is windows
    """
    return platform.system() == "Windows"
