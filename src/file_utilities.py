
def check_file(path):
    exts = ["dxf", "DXF"]
    for ext in exts:
        if f".{ext}" in path and path.split(f".{ext}")[1] == "":
            return True
    return False
