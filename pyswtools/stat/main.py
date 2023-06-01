"""
Give stat from an assembly
"""

import click

"""
Auto export of solidworks files to other extensions
"""

import os
import math
import click

# pylint: disable=relative-beyond-top-level
from ..utils import check_system, check_system_verbose
from ..config import get_config

if check_system():
    # pylint: disable=import-error
    import win32com.client
    import pythoncom

    Views = []
    VT_Views = win32com.client.VARIANT(pythoncom.VT_VARIANT, Views)
    VT_BYREF = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, -1)

#TODO define type_sort and type_output as dataclass

def sort_key_struct(struct, type_sort):
    if type_sort == "name":
        return sorted(struct.keys(),key=str.lower)
    if type_sort == "mass":
        return sorted(struct.keys(), key=lambda i: struct[i]["mass"]*struct[i]["number"],reverse=True )

    return struct.keys()

def print_header():
    header = f"{'Name':<50} | {'Mtot':<5} | {'n':<3} | {'Mpart':<6} | {'Density':<7}  "
    click.echo(header)
    click.echo("-" * len(header))

def display_tree(tree_struct_mass, type_sort="name", indent=""):
    sorted_list = sort_key_struct(tree_struct_mass, type_sort)
    n = len(sorted_list)
    if indent == "":
        print_header()
    for idx, elem in enumerate(sorted_list):
        char = "┝━"
        if idx == n-1:
            char= "┕━"
        click.echo(f"{indent + char + ' ' + elem :<50} | {tree_struct_mass[elem]['mass'] * tree_struct_mass[elem]['number']:5.3f} | {tree_struct_mass[elem]['number']:3d} | {tree_struct_mass[elem]['mass']:6.4f} | {tree_struct_mass[elem]['density']:6.4f}")
        if len(tree_struct_mass[elem]["children"]) > 0:
            char = "│ "
            if idx == n-1:
                char= "  "
            display_tree(tree_struct_mass[elem]["children"],type_sort, indent + char)

def display_list(list_struct, type_sort="name"):
    print_header()
    for elem in sort_key_struct(list_struct, type_sort):
        if abs(list_struct[elem]['density'] -1000) < 1e-4 or True:
            click.echo(f"{'- ' + elem :<50} | {list_struct[elem]['mass'] * list_struct[elem]['number']:5.3f} | {list_struct[elem]['number']:3d} | {list_struct[elem]['mass']:6.4f} | {list_struct[elem]['density']:6.4f}")

def get_clean_name(sw_comp):
    return sw_comp.Name2.rpartition("-")[0].rpartition("/")[-1]

def complete_info_on_list(sw_comp_children, dict_of_comp):
    children = {}
    for sw_child in sw_comp_children:
        sw_child_name = get_clean_name(sw_child)
        child = complete_info_assembly(sw_child, dict_of_comp)
        if sw_child_name not in children.keys():
            children[sw_child_name] = child
        else:
            children[sw_child_name]["number"] += 1

    return children

def complete_info_assembly(sw_comp, dict_of_comp):
    sw_comp_name = get_clean_name(sw_comp)

    if sw_comp_name in dict_of_comp:
        dict_of_comp[sw_comp_name]["number"] += 1
    else:
        sw_comp_doc_ext = sw_comp.GetModelDoc2.Extension
        sw_mass = sw_comp_doc_ext.CreateMassProperty2.Mass

        dict_of_comp[sw_comp_name] = {
            "mass": sw_mass,
            "density": sw_comp_doc_ext.CreateMassProperty2.density,
            "number": 1,
        }
    
    sw_comp_children = sw_comp.GetChildren
    children = complete_info_on_list(sw_comp_children, dict_of_comp)


    return {
        "mass": dict_of_comp[sw_comp_name]["mass"],
        "density": dict_of_comp[sw_comp_name]["density"],
        "number": 1,
        "children": children,
    }

@click.command()
@click.help_option("-h", "--help")
@click.argument(
    "input_path",
    type=click.Path(
        exists=True,
        dir_okay=False,
        ),
)
@click.option('--tree', 'type_output', flag_value='tree', default=True)
@click.option('--list', 'type_output', flag_value='list')
@click.option('--mass', 'type_sort', flag_value='mass', default=True)
@click.option('--name', 'type_sort', flag_value='name')
def stat(input_path, type_output, type_sort) -> None:
    """
    Display stat about an assembly
    """
    if not check_system_verbose():
        return

    if ".SLDASM" not in input_path or "~$" in input_path:
        click.echo("Please select an assembly file (.SLDASM)")
        click.echo(f"{input_path} is not an assembly file")
        return

    path_directory, filename = os.path.split(input_path)

    conf = get_config()

    sw_app = win32com.client.Dispatch(
        f"SldWorks.Application.{(int(conf.sw_version)-2012+20)}"
    )

    # Open the assembly
    sw_doc = sw_app.OpenDoc6(os.path.abspath(input_path), 2, 1, "", VT_BYREF, VT_BYREF)

    # Activate it
    sw_app.ActivateDoc3(filename, True, 2, VT_BYREF)

    sw_comps = sw_doc.GetComponents(True)
 

    assembly_name = filename.rpartition('.')[-0]
    dict_of_comp = {
        f"{assembly_name}" : {
            "mass": sw_doc.Extension.CreateMassProperty2.Mass,
            "density": sw_doc.Extension.CreateMassProperty2.Density,
            "number": 1,
        }
    }

    tree_of_comp = {
        f"{assembly_name}": {
            "mass": dict_of_comp[assembly_name]["mass"],
            "density": dict_of_comp[assembly_name]["density"],
            "number": 1,
            "children": complete_info_on_list(sw_comps, dict_of_comp),
        }
    }

    if type_output == "tree":
        display_tree(tree_of_comp, type_sort)
    elif type_output == "list":
        display_list(dict_of_comp, type_sort)
    else:
        pass
