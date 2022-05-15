import ezdxf
import os

from src.file_utilities import check_file, append_name

def check_file_and_folder(path, save_path, warning=False, save=True):
    if os.path.isdir(path):
        list_dir = os.listdir(path)
        try:
            os.mkdir(save_path)
        except FileExistsError:
            pass

        for name in list_dir:
            npath = os.path.join(path,name)
            check_file_and_folder(npath, os.path.join(save_path, name))
    else:
        if check_file(path):
            doc = ezdxf.readfile(path)
            clean(doc)
            if save:
                doc.saveas(save_path)
        else:
            print(f"{path} is not a dxf file")

def clean(doc):
    remove_SWK(doc)

def remove_SWK(doc):
    blocks = doc.blocks
    for bloc in blocks:
        for entity in bloc:
            if(entity.dxftype() == "MTEXT"):
                if("SOLIDWORKS" in entity.text):
                    bloc.delete_entity(entity)
