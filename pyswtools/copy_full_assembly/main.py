"""
Make a copy of a directory but update all the paths to reference the new paths
"""

import os
import click

# pylint: disable=relative-beyond-top-level
from ..utils import check_system_verbose
from ..helper_sw import open_app, is_file, is_temp


@click.command()
@click.help_option("-h", "--help")
@click.argument(
    "input_path",
    type=click.Path(exists=True),
)
@click.argument(
    "src_replace",
    type=click.STRING,
)
@click.argument(
    "target_replace",
    type=click.STRING,
)
def copy_full_assembly(input_path, src_replace, target_replace) -> None:
    """
    Make a copy of a directory but update all the paths to reference the new paths
    """

    if not check_system_verbose():
        return

    # Open app
    sw_app = open_app()

    # Walk though the directory and each subdirectory
    for root, _, files in os.walk(input_path):
        for file in files:
            curr_path = os.path.abspath(os.path.join(root, file))
            if not is_file(file) or is_temp(file):
                continue
            print(f"- {file}")

            # Open the new doc
            sw_doc = sw_app.OpenDoc(curr_path, 1)

            # Get the equation manager
            sw_e_mgr = sw_doc.GetEquationMgr

            # Replace the property with link to the file
            sw_e_mgr.FilePath = sw_e_mgr.FilePath.replace(src_replace, target_replace)

            # Save the doc
            sw_doc.SaveAs3(curr_path, 0, 2)

            # No check if open as it is a new document
            sw_app.CloseDoc(file)
