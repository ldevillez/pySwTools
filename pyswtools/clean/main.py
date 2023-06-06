"""
Give stat from an assembly
"""

import os
import click

# pylint: disable=relative-beyond-top-level
from ..utils import check_system, check_system_verbose
from ..helper_sw import open_app_and_file, is_assembly, is_temp, is_file

if check_system():
    # pylint: disable=import-error
    import win32com.client
    import pythoncom

    Views = []
    VT_Views = win32com.client.VARIANT(pythoncom.VT_VARIANT, Views)
    VT_BYREF = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, -1)


def list_component(sw_comps, list_of_comps):
    """
    Add to `list_of_comps` the elements of sw_comps recursively
    """
    for sw_comp in sw_comps:
        sw_path = sw_comp.GetPathName

        if sw_path not in list_of_comps:
            list_of_comps.append(sw_path)

        sw_comp_children = sw_comp.GetChildren
        list_component(sw_comp_children, list_of_comps)


@click.command()
@click.help_option("-h", "--help")
@click.argument(
    "dir_path",
    type=click.Path(
        exists=True,
        file_okay=False,
    ),
)
@click.argument(
    "assembly_path",
    type=click.Path(
        exists=True,
        dir_okay=False,
    ),
)
def clean(dir_path: str, assembly_path: str) -> None:
    """
    Display stat about an assembly
    """
    if not check_system_verbose():
        return

    if not is_assembly(assembly_path) or is_temp(assembly_path):
        click.echo("Please select an assembly file (.SLDASM)")
        click.echo(f"{assembly_path} is not an assembly file")
        return

    _, sw_doc, _ = open_app_and_file(assembly_path)

    list_of_comps = [os.path.abspath(assembly_path)]

    sw_comps = sw_doc.GetComponents(True)
    list_component(sw_comps, list_of_comps)

    for root, _, files in os.walk(dir_path):
        for file in files:
            curr_path = os.path.abspath(os.path.join(root, file))
            if (is_assembly(file) or is_file(file)) and not is_temp(file):
                if curr_path not in list_of_comps:
                    click.echo(f"- {os.path.join(root, file)} can be removed")
