"""Module to help handling with files"""


def check_file(path: str) -> bool:
    """Check if the file has the dxf extension"""
    exts = ["dxf", "DXF"]
    path_splitted = path.split(".")
    if len(path_splitted) < 2:
        return False
    ext = path_splitted[len(path_splitted) - 1]
    return ext in exts


def append_name(path: str, text: str) -> str:
    """
    Add the value of text at the end of the path but before the extension
    """
    path_splitted = path.split(".")
    if len(path_splitted) < 2:
        return path + text
    ext = path_splitted[len(path_splitted) - 1]
    return path.replace(f".{ext}", f"{text}.{ext}")
