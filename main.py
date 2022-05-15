import sys
import os
import ezdxf

from src.dxf_utilities import  check_file_and_folder
from src.file_utilities import append_name


if len(sys.argv) < 2:
    print("Not enough args")
    sys.exit()

path = os.path.abspath(sys.argv[1])

check_file_and_folder(path, save_path=append_name(path, "_cleaned"), warning=True)
