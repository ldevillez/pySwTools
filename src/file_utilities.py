"""Docstring"""


def check_file(path):
    """Docstring"""
    exts = ["dxf", "DXF"]
    path_splitted = path.split(".")
    if len(path_splitted) < 2:
        return False
    ext = path_splitted[len(path_splitted) - 1]
    return ext in exts


def append_name(path, text):
    """Docstring"""
    path_splitted = path.split(".")
    if len(path_splitted) < 2:
        return path + text
    ext = path_splitted[len(path_splitted) - 1]
    return path.replace(f".{ext}", f"{text}.{ext}")
