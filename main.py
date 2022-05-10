import sys
import ezdxf


if len(sys.argv) < 2:
    print("Not enough args")
    sys.exit()

path = sys.argv[1]

doc = ezdxf.readfile(path)
print(doc.dxfversion)
blocks = doc.blocks
for bloc in blocks:
    print(bloc.name)
    for entity in bloc:
        if(entity.dxftype() == "MTEXT"):
            if("SOLIDWORKS" in entity.text):
                print(entity.text)
                bloc.delete_entity(entity)
doc.saveas("Clean.dxf")
