"""
Give stat from an assembly
"""

import os
from enum import Enum
import click

# pylint: disable=relative-beyond-top-level
from ..utils import check_system, check_system_verbose
from ..helper_sw import open_app_and_file, is_temp, is_assembly


class TypeOutput(str, Enum):
    """Class represeting an output type"""

    TREE = "tree"
    LIST = "list"


class TypeSort(str, Enum):
    """Class represeting an output type"""

    MASS = "mass"
    MASS_PART = "mass-part"
    NAME = "name"


if check_system():
    # pylint: disable=import-error
    import win32com.client
    import pythoncom

    Views = []
    VT_Views = win32com.client.VARIANT(pythoncom.VT_VARIANT, Views)
    VT_BYREF = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, -1)


def filter_density_list(struct: dict) -> None:
    """
    Filter element from a list struct to get only the ones with a density differnt from 1000
    """
    return {k: v for k, v in struct.items() if abs(v["density"] - 1000) < 1e-3}


def filter_density_tree(struct: dict) -> None:
    """
    Filter element from a tree struct to get only the ones with a density differnt from 1000
    """
    return_struct = {}
    for k, v in struct.items():
        if (v["density"] - 1000) < 1e-4:
            return_struct[k] = v
            filter_density_tree(return_struct[k]["children"])
    struct = return_struct


def remove_conf_tree(tree_struct: dict, dict_of_comp: dict) -> None:
    """
    Clean the name of a tree struct.
    If there is only one configuration for a component, remove the configuration
    Otherwise keep it.
    """
    remove_conf_with_list(tree_struct, dict_of_comp)
    for elem in tree_struct:
        remove_conf_tree(tree_struct[elem]["children"], dict_of_comp)


def remove_conf_with_list(list_struct: dict, dict_of_comp: dict) -> None:
    """
    Clean the name of a tree struct with an additional list.
    If the stripped name is in the list, remove the configuration
    """
    if len(list_struct) == 0:
        return

    list_of_name = list(list_struct.keys())

    for name in list_of_name:
        if strip_conf(name) in dict_of_comp:
            list_struct[strip_conf(name)] = list_struct[name]
            del list_struct[name]


def remove_conf(list_struct: dict) -> None:
    """
    Clean the name of a list struct.
    If there is only one configuration for a component, remove the configuration
    Otherwise keep it.
    """
    if len(list_struct) == 0:
        return

    # Always strip one elem list
    if len(list_struct) == 1:
        name = list(list_struct.keys())[0]
        list_struct[strip_conf(name)] = list_struct[name]
        del list_struct[name]
        return

    # Get keys sorted by name
    sorted_list = sort_key_struct(list_struct, TypeSort.NAME)

    # Check first case
    if strip_conf(sorted_list[0]) != strip_conf(sorted_list[1]):
        # Rename
        list_struct[strip_conf(sorted_list[0])] = list_struct[sorted_list[0]]
        del list_struct[sorted_list[0]]

    # Check last case
    if strip_conf(sorted_list[-1]) != strip_conf(sorted_list[-2]):
        # Rename
        list_struct[strip_conf(sorted_list[-1])] = list_struct[sorted_list[-1]]
        del list_struct[sorted_list[-1]]

    for idx, name in enumerate(sorted_list[1:-1]):
        # Check all middle cases
        if strip_conf(name) != strip_conf(sorted_list[idx]) and strip_conf(
            name
        ) != strip_conf(sorted_list[idx + 2]):
            list_struct[strip_conf(name)] = list_struct[name]
            del list_struct[name]


def remove_duplicate_conf(struct: dict) -> None:
    """
    Filter element from struct (tree or list) which have only different configuration names but same Mass
    """

    # Get elements sorted by mass part
    sorted_list = sort_key_struct(struct, TypeSort.MASS_PART)
    for idx, name in enumerate(sorted_list[:-1]):
        # If the elem was removed
        if name not in struct:
            continue

        # We test the following elements
        for name_test in sorted_list[idx + 1 :]:
            # if we do not have the same mass, we end
            if abs(struct[name]["mass"] - struct[name_test]["mass"]) > 1e-5:
                break
            # We compare the names
            if strip_conf(name_test) == strip_conf(name):
                # We fused data
                struct[name]["number"] += struct[name_test]["number"]
                del struct[name_test]
        if "children" in struct[name]:
            remove_duplicate_conf(struct[name]["children"])


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
    if type_sort is TypeSort.MASS_PART:
        return sorted(
            struct.keys(),
            key=lambda i: struct[i]["mass"],
            reverse=True,
        )

    return struct.keys()


def print_header():
    """
    Display the header of the output
    """
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
        if idx == n - 1:
            char = "┕━"
        click.echo(
            f"{indent + char + ' ' + elem :<50} | {tree_struct_mass[elem]['mass'] * tree_struct_mass[elem]['number']:5.3f} | {tree_struct_mass[elem]['number']:3d} | {tree_struct_mass[elem]['mass']:6.4f} | {tree_struct_mass[elem]['density']:6.4f}"
        )
        if len(tree_struct_mass[elem]["children"]) > 0:
            char = "│ "
            if idx == n - 1:
                char = "  "
            display_tree(tree_struct_mass[elem]["children"], type_sort, indent + char)


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
    Get the cleaned name from a component.
    Rremove the number from the component.
    Append the configuration
    """
    return (
        sw_comp.Name2.rpartition("-")[0].rpartition("/")[-1]
        + "@"
        + sw_comp.ReferencedConfiguration
    )


def strip_conf(name: str) -> str:
    """
    Get the name without the configuration
    """
    return name.split("@")[0]


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
        # set the configuration
        sw_comp_doc = sw_comp.GetModelDoc2
        sw_comp_doc.ShowConfiguration2(sw_comp.ReferencedConfiguration)
        # Get extension manager
        sw_comp_doc_ext = sw_comp_doc.Extension
        sw_mass_property = sw_comp_doc_ext.CreateMassProperty2
        # Get mass and density
        sw_mass = sw_mass_property.Mass if sw_mass_property is not None else 0
        sw_density = sw_mass_property.Density if sw_mass_property is not None else 0

        # Create an new entity in the general dict
        dict_of_comp[sw_comp_name] = {
            "number": 1,
            "mass": sw_mass,
            "density": sw_density,
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
@click.option(
    "--type-output",
    "type_output",
    type=click.Choice(TypeOutput),
    default=TypeOutput.TREE,
)
@click.option(
    "--type-sort", "type_sort", type=click.Choice(TypeSort), default=TypeSort.MASS
)
@click.option("--only-default-density", "only_default_density", is_flag=True)
def stat(
    input_path: str,
    type_output: TypeOutput,
    type_sort: TypeSort,
    only_default_density: bool,
) -> None:
    """
    Display stat about an assembly
    """
    if not check_system_verbose():
        return

    if not is_assembly(input_path) or is_temp(input_path):
        click.echo("Please select an assembly file (.SLDASM)")
        click.echo(f"{input_path} is not an assembly file")
        return

    _, sw_doc, filename = open_app_and_file(input_path)

    # Get list of components
    sw_comps = sw_doc.GetComponents(True)

    # Empty struct to fill
    assembly_name = filename.rpartition(".")[-0] + "@" + sw_doc.GetConfigurationNames[0]
    dict_of_comp = {
        f"{assembly_name}": {
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

    remove_duplicate_conf(dict_of_comp)
    remove_conf(dict_of_comp)
    if type_output is TypeOutput.TREE:
        remove_duplicate_conf(tree_of_comp)
        remove_conf_tree(tree_of_comp, dict_of_comp)
        display_tree(tree_of_comp, type_sort)
    elif type_output is TypeOutput.LIST:
        if only_default_density:
            dict_of_comp = filter_density_list(dict_of_comp)
        display_list(dict_of_comp, type_sort)
    else:
        click.echo(
            f"Type output {type_output} is unknown {type_output is TypeOutput.TREE} {type(type_output)}"
        )
