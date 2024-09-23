"""
Sets of functions to help using the api of solidworks
"""

import os

import win32com.client
import pythoncom


from .config import get_config

Views = []
VT_Views = win32com.client.VARIANT(pythoncom.VT_VARIANT, Views)
VT_BYREF = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, -1)


def open_app():
    """
    Read the conf and create the application object then return it
    """
    conf = get_config()

    return win32com.client.Dispatch(
        f"SldWorks.Application.{(int(conf.sw_version)-2012+20)}"
    )


def open_app_and_file(path_file: str):
    """
    Create app, open document in it and then activate it
    """
    # Open app
    sw_app = open_app()

    # Open the file
    sw_doc, filename = open_file(sw_app, path_file)

    return sw_app, sw_doc, filename


def open_file(sw_app, path_file: str):
    """
    Create open document activate it
    """
    # Open the assembly

    # Default file type is part
    type_file = 1
    if is_assembly(path_file):
        type_file = 2
    elif is_drawing(path_file):
        type_file = 3

    sw_doc = sw_app.OpenDoc6(
        os.path.abspath(path_file), type_file, 1, "", VT_BYREF, VT_BYREF
    )

    # Get the filename
    _, filename = os.path.split(path_file)

    # Activate it
    sw_app.ActivateDoc3(filename, True, 2, VT_BYREF)

    return sw_doc, filename


def is_drawing(path: str) -> bool:
    """Return True if paths point to a drawing file"""
    return ".SLDDRW" in path.upper()


def is_assembly(path: str) -> bool:
    """Return True if paths point to an assembly file"""
    return ".SLDASM" in path.upper()


def is_temp(path: str) -> bool:
    """Return True if path points to a temporary file"""
    return "~$" in path


def is_file(path: str) -> bool:
    """Return True if path points to a part file"""
    return ".SLDPRT" in path.upper()
