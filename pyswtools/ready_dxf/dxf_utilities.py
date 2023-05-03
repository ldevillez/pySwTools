"""Docstring"""

import os
import ezdxf

from .file_utilities import check_file


def check_file_and_folder(
    path, save_path, save=True
) -> list[ezdxf.document.Drawing] | None:
    """
    Handle file or folder to apply the cleaning process
    """
    if os.path.isdir(path):
        list_dir = os.listdir(path)
        try:
            os.mkdir(save_path)
        except FileExistsError:
            pass
        docs = []
        for name in list_dir:
            npath = os.path.join(path, name)

            docs.append(check_file_and_folder(npath, os.path.join(save_path, name)))
    else:
        if check_file(path):
            doc = ezdxf.readfile(path)
            clean(doc)
            if save:
                doc.saveas(save_path)
            docs = [doc]

        else:
            docs = None
            print(f"{path} is not a dxf file")
    return docs


def clean(doc: ezdxf.document.Drawing) -> None:
    """Apply functions to clean the doc"""
    remove_sw(doc)


def remove_sw(doc: ezdxf.document.Drawing) -> None:
    """Remove the text included by solidworks from the doc file"""
    blocks = doc.blocks
    for bloc in blocks:
        for entity in bloc:
            if entity.dxftype() == "MTEXT":
                if "SOLIDWORKS" in entity.text:
                    bloc.delete_entity(entity)
