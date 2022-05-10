import ezdxf

def clean(doc):
    remove_SWK(doc)

def remove_SWK(doc):
    blocks = doc.blocks
    for bloc in blocks:
        for entity in bloc:
            if(entity.dxftype() == "MTEXT"):
                if("SOLIDWORKS" in entity.text):
                    bloc.delete_entity(entity)
