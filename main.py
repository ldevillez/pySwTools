import sys
import os
import ezdxf

from src.dxf_utilities import clean
from src.file_utilities import check_file


if len(sys.argv) < 2:
    print("Not enough args")
    sys.exit()

path = sys.argv[1]

if os.path.isdir(path):
    pass
else:
    print(check_file(path))
    doc = ezdxf.readfile(path)
    doc.saveas(path.replace)
