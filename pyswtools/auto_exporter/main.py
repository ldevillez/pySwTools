"""
Auto export of solidworks files to other extensions
"""

import os
import math
import click

# pylint: disable=relative-beyond-top-level
from ..utils import check_system, check_system_verbose
from ..config import get_config

if check_system():
    # pylint: disable=import-error
    import win32com.client
    import pythoncom

    Views = []
    VT_Views = win32com.client.VARIANT(pythoncom.VT_VARIANT, Views)
    VT_BYREF = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, -1)

    from stl import mesh


def open_active_sw_file(sw_app, path, filename):
    """
    Open a sw part file and focus it
    """
    sw_doc = sw_app.OpenDoc6(path, 1, 1, "", VT_BYREF, VT_BYREF)

    sw_app.ActivateDoc3(filename, True, 2, VT_BYREF)

    return sw_doc


def export_stl(sw_doc, path, output_filename):
    """
    Export the current doc to a STL file
    """

    stl_path = f"{os.path.join(path,output_filename)}.stl".replace(".SLDPRT", "")
    click.echo(stl_path)
    sw_doc.SaveAs3(stl_path, 0, 2)

    my_mesh = mesh.Mesh.from_file(stl_path, True)
    my_mesh.rotate(
        [
            1.0,
            0.0,
            0.0,
        ],
        math.radians(-90),
    )
    my_mesh.save(stl_path)


def export_dxf(sw_doc, path, output_filename, curr_filename):
    """
    Export the current doc to a DXF file
    """

    # Get list of bodies. Should be exactly one
    sw_bodies = sw_doc.GetBodies2(0, True)
    if sw_bodies is None or len(sw_bodies) < 1:
        # TODO: add red when errors
        click.echo("  No bodies - Aborting")
        return
    if len(sw_bodies) > 1:
        click.echo("  Too much boodies - Aborting")
        return

    dxf_path = f"{os.path.join(path,output_filename)}.dxf".replace(".SLDPRT", "")

    # The face to export must be planar and it will be the one with the biggest surface
    sw_body = sw_bodies[0]
    sw_faces = sw_body.GetFaces()

    sw_face = None  # Face selected to export
    surface_face = 0  # Surface of sw_face
    for face in sw_faces:
        corners = face.GetBox
        min_err = 1

        # A planar surface should be flat
        for i in range(3):
            err = abs(corners[i] - corners[i + 3])
            if err < min_err:
                min_err = err

        if min_err < 1e-4:
            cur_surface = face.GetArea
            if cur_surface > surface_face:
                surface_face = cur_surface
                sw_face = face

    if sw_face is None:
        click.echo("  No face compatible were found - Aborting")

    # TODO deselect all
    # Create a selection manager and put the face in it
    sw_select = sw_doc.SelectionManager.CreateSelectData
    sw_doc.SelectionManager.AddSelectionListObject(sw_face, sw_select)

    ret = sw_doc.ExportToDWG2(
        dxf_path,
        curr_filename,
        2,
        True,
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        False,
        False,
        0,
        VT_Views,
    )
    if ret:
        click.echo("  Ok")
    else:
        click.echo("  Could not save the selection")


def export_file(sw_doc, paths, filename, mode):
    """
    Export the file sw_doc corresponding to the current mode
    """
    if mode == "Auto":
        if "STL" in filename:
            file_mode = "STL"
        elif "DXF" in filename:
            file_mode = "DXF"
        else:
            click.echo(f"- {filename}: IGNORED")
            return
    else:
        file_mode = mode
    click.echo(f"- {filename}: {file_mode}")

    sw_confs = sw_doc.GetConfigurationNames
    for sw_conf in sw_confs:
        sw_doc.ShowConfiguration2(sw_conf)

        output_filename = filename
        if len(sw_confs) != 1:
            output_filename += f"_{sw_conf}"
            click.echo(f"  - {sw_conf}")

        if file_mode == "STL":
            export_stl(sw_doc, paths["stl_path"], output_filename)
        elif file_mode == "DXF":
            export_dxf(sw_doc, paths["dxf_path"], output_filename, filename)


@click.command()
@click.help_option("-h", "--help")
@click.argument("input_path", type=click.Path(exists=True, file_okay=False))
@click.argument("mode", type=click.Choice(["Auto", "STL", "DXF"]))
def auto_export(input_path, mode) -> None:
    """
    Export a part or a directory of part to other extensions
    """
    if not check_system_verbose():
        pass
        # return

    # Prepare folder
    # TODO create only the one needed ?
    paths = {
        "dxf_path": os.path.abspath(os.path.join(input_path, "DXF")),
        "stl_path": os.path.abspath(os.path.join(input_path, "STL")),
    }

    if not os.path.isdir(paths["dxf_path"]):
        os.mkdir(paths["dxf_path"])

    if not os.path.isdir(paths["stl_path"]):
        os.mkdir(paths["stl_path"])

    conf = get_config()

    sw_app = win32com.client.Dispatch(
        f"SldWorks.Application.{(int(conf.sw_version)-2012+20)}"
    )

    for root, _, files in os.walk(input_path):
        if "/STL" in root or "/DXF" in root:
            continue
        for file in files:
            curr_path = os.path.abspath(os.path.join(root, file))

            # Focus only on part and avoid tmp file
            if ".SLDPRT" not in file or "~$" in file:
                continue

            sw_doc = open_active_sw_file(sw_app, curr_path, file)
            export_file(sw_doc, paths, file, mode)

            sw_app.CloseDoc(file)
            # TODO close the file if not pen initially
