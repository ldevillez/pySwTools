"""
Give stat from an assembly
"""

import os
from enum import Enum
import click

# pylint: disable=relative-beyond-top-level
from ..utils import check_system, check_system_verbose
from ..config import get_config


class TypeOutput(str, Enum):
    """Class represeting an output type"""

    TREE = "tree"
    LIST = "list"


class TypeSort(str, Enum):
    """Class represeting an output type"""

    MASS = "mass"
    NAME = "name"


if check_system():
    # pylint: disable=import-error
    import win32com.client
    import pythoncom

    Views = []
    VT_Views = win32com.client.VARIANT(pythoncom.VT_VARIANT, Views)
    VT_BYREF = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, -1)


def sort_key_struct(struct: dict, type_sort: TypeSort = TypeSort.MASS) -> list:
    """
    Sort a dict struct following a given sort
    """
    if type_sort is TypeSort.NAME:
        return sorted(struct.keys(), key=str.lower)
    if type_sort is TypeSort.MASS:
        return sorted(
            struct.keys(),
            key=lambda i: struct[i]["mass"] * struct[i]["number"],
            reverse=True,
        )

    return struct.keys()

def print_header():
    header = f"{'Name':<50} | {'Mtot':<5} | {'n':<3} | {'Mpart':<6} | {'Density':<7}  "
    click.echo(header)
    click.echo("-" * len(header))

def display_tree(
    tree_struct_mass: dict, type_sort: TypeSort = TypeSort.NAME, indent: str = ""
) -> None:
    """
    Display a tree struct recursively
    """
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


def display_list(list_struct: dict, type_sort: TypeSort = TypeSort.NAME) -> None:
    """
    Display a list struct
    """
    print_header()
    for elem in sort_key_struct(list_struct, type_sort):
        click.echo(
            f"{'- ' + elem :<50} | {list_struct[elem]['mass'] * list_struct[elem]['number']:5.3f} | {list_struct[elem]['number']:3d} | {list_struct[elem]['mass']:6.4f} | {list_struct[elem]['density']:6.4f}"
        )


def get_clean_name(sw_comp) -> str:
    """
    Get the cleaned name from a component. remove the number from the component
    """
    return sw_comp.Name2.rpartition("-")[0].rpartition("/")[-1]


def complete_info_on_list(sw_comp_children, dict_of_comp: dict) -> dict:
    """
    Get all the info from a list of component
    """
    children = {}
    for sw_child in sw_comp_children:
        # Get the name
        sw_child_name = get_clean_name(sw_child)

        # Get the info fo the assembly
        child = complete_info_assembly(sw_child, dict_of_comp)

        # If the child is already here, only increase the number
        if sw_child_name not in children:
            children[sw_child_name] = child
        else:
            children[sw_child_name]["number"] += 1

    return children


def complete_info_assembly(sw_comp, dict_of_comp: dict) -> dict:
    """
    Get all the information from an assembly
    """

    # Get name of component
    sw_comp_name = get_clean_name(sw_comp)

    # If already there only increase the number
    if sw_comp_name in dict_of_comp:
        dict_of_comp[sw_comp_name]["number"] += 1
    else:
        # Otherwise get the mass
        sw_comp_doc_ext = sw_comp.GetModelDoc2.Extension
        sw_mass = sw_comp_doc_ext.CreateMassProperty2.Mass

        # Create an new entity in the general dict
        dict_of_comp[sw_comp_name] = {
            "number": 1,
            "mass": sw_mass,
            "density": sw_comp_doc_ext.CreateMassProperty2.density
        }

    # Get info about children
    sw_comp_children = sw_comp.GetChildren
    children = complete_info_on_list(sw_comp_children, dict_of_comp)

    # Create the entry in the tree dict
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

@click.option("--type_output", "type_output", type=click.Choice(TypeOutput), default=TypeOutput.TREE)
@click.option("--type_sort", "type_sort", type=click.Choice(TypeSort), default=TypeSort.MASS)
def stat(input_path: str, type_output: TypeOutput, type_sort: TypeSort) -> None:
    """
    Display stat about an assembly
    """
    if not check_system_verbose():
        return

    if ".SLDASM" not in input_path or "~$" in input_path:
        click.echo("Please select an assembly file (.SLDASM)")
        click.echo(f"{input_path} is not an assembly file")
        return

    _, filename = os.path.split(input_path)

    conf = get_config()

    sw_app = win32com.client.Dispatch(
        f"SldWorks.Application.{(int(conf.sw_version)-2012+20)}"
    )

    # Open the assembly
    sw_doc = sw_app.OpenDoc6(os.path.abspath(input_path), 2, 1, "", VT_BYREF, VT_BYREF)

    # Activate it
    sw_app.ActivateDoc3(filename, True, 2, VT_BYREF)

    # Get list of components
    sw_comps = sw_doc.GetComponents(True)

    # Empty struct to fill
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

    if type_output is TypeOutput.TREE:
        display_tree(tree_of_comp, type_sort)
    elif type_output is TypeOutput.LIST:
        display_list(dict_of_comp, type_sort)
    else:
        click.echo(f"Type output {type_output} is unknown {type_output is TypeOutput.TREE} {type(type_output)}")
