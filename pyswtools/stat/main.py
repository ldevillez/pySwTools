"""
Give stat from an assembly
"""

import os
import click

# pylint: disable=relative-beyond-top-level
from ..utils import check_system, check_system_verbose, do_windows_clipboard
from ..helper_sw import open_app_and_file, is_temp, is_assembly

from .definitions import (
    TypeComponent,
    TypeExport,
    TypeOutput,
    TypeSort,
    StatComponent,
    StatComponentTree,
)


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
    return {k: v for k, v in struct.items() if abs(v.density - 1000) < 1e-3}


def filter_density_tree(struct: dict) -> None:
    """
    Filter element from a tree struct to get only the ones with a density differnt from 1000
    """
    return_struct = {}
    for k, v in struct.items():
        if (v.density - 1000) < 1e-4:
            return_struct[k] = v
            filter_density_tree(return_struct[k].children)
    struct = return_struct


def filter_component_type(
    tree_struct: dict, list_struct: dict, type_component=TypeComponent.ALL
) -> None:
    """
    Filter element from a list and tree struct to get one the ones with the matching TypeComponent
    """
    if type_component.value == TypeComponent.ALL.value:
        return

    if type_component.value == TypeComponent.ASSEMBLY.value:
        filter_component_type_tree(tree_struct, list_struct)

    for k, v in list(list_struct.items()):
        if v.typeComponent.value != type_component.value:
            list_struct.pop(k)


def filter_component_type_tree(tree_struct: dict, list_struct: dict) -> None:
    """
    Filter elements from a list
    """
    for k, v in list(tree_struct.items()):
        if list_struct[k].typeComponent.value == TypeComponent.PART.value:
            tree_struct.pop(k)
        else:
            filter_component_type_tree(v.children, list_struct)


def clean_confs(tree_struct: dict, dict_struct: dict) -> None:
    """
    Clean the name of the tree and list struct of the conf and remove duplicate.
    """

    remove_duplicate_conf_list(dict_struct, dict_struct)
    remove_duplicate_conf_tree(tree_struct, dict_struct)

    remove_conf_list(dict_struct)
    remove_conf_tree(tree_struct, dict_struct)


def remove_conf_tree(tree_struct: dict, dict_of_comp: dict) -> None:
    """
    Clean the name of a tree struct.
    If there is only one configuration for a component, remove the configuration
    Otherwise keep it.
    """
    remove_conf_with_list(tree_struct, dict_of_comp)
    for elem in tree_struct:
        remove_conf_tree(tree_struct[elem].children, dict_of_comp)


def remove_conf_with_list(list_struct: dict, dict_of_comp: dict) -> None:
    """
    Clean the name of a tree struct with an additional list.
    If the stripped name is in the list, remove the configuration
    """
    if len(list_struct) == 0:
        return

    list_of_name = list(list_struct.keys())

    for name in list_of_name:
        stripped_name = strip_conf(name)
        if stripped_name in dict_of_comp:
            if stripped_name not in list_struct:
                list_struct[stripped_name] = list_struct[name]
            else:
                list_struct[stripped_name].number += list_struct[name].number
            del list_struct[name]


def remove_conf_list(list_struct: dict) -> None:
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


def remove_duplicate_conf_tree(tree_struct: dict, dict_struct: dict) -> None:
    """
    Filter element from struct (tree or list) which have only different configuration names but same Mass
    """

    remove_conf_with_list(tree_struct, dict_struct)
    for name in list(tree_struct.keys()):
        remove_duplicate_conf_tree(tree_struct[name].children, dict_struct)


def remove_duplicate_conf_list(struct: dict, mass_struct: dict) -> None:
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
            if abs(mass_struct[name].mass - mass_struct[name_test].mass) > 1e-5:
                break
            # We compare the names
            if strip_conf(name_test) == strip_conf(name):
                # We fused data
                struct[name].number += struct[name_test].number
                del struct[name_test]


def sort_tulpe(
    struct: list, mass_struct: dict, type_sort: TypeSort = TypeSort.MASS
) -> list:
    """
    Sort a list of tuple struct following a given sort
    The first element of a tuple is the name and the second is the structure
    """

    if type_sort is TypeSort.NAME:
        return sorted(
            struct,
            key=lambda i: i[0],
            reverse=True,
        )
    if type_sort is TypeSort.MASS:
        return sorted(
            struct,
            key=lambda i: mass_struct[i[0]].mass * i[1].number,
            reverse=True,
        )
    if type_sort is TypeSort.MASS_PART:
        return sorted(
            struct,
            key=lambda i: mass_struct[i[0]].mass,
            reverse=True,
        )

    return struct


def sort_key_struct(struct: dict, type_sort: TypeSort = TypeSort.MASS) -> list:
    """
    Sort a dict struct following a given sort
    """
    if type_sort is TypeSort.NAME:
        return sorted(struct.keys(), key=str.lower)
    if type_sort is TypeSort.MASS:
        return sorted(
            struct.keys(),
            key=lambda i: struct[i].mass * struct[i].number,
            reverse=True,
        )
    if type_sort is TypeSort.MASS_PART:
        return sorted(
            struct.keys(),
            key=lambda i: struct[i].mass,
            reverse=True,
        )

    return struct.keys()


def sort_key_struct_tree(
    tree_struct: dict, dict_struct: dict, type_sort: TypeSort = TypeSort.MASS
) -> list:
    """
    Sort a dict struct following a given sort
    """
    if type_sort is TypeSort.NAME:
        return sorted(tree_struct.keys(), key=str.lower)
    if type_sort is TypeSort.MASS:
        return sorted(
            tree_struct.keys(),
            key=lambda i: dict_struct[i].mass * tree_struct[i].number,
            reverse=True,
        )
    if type_sort is TypeSort.MASS_PART:
        return sorted(
            tree_struct.keys(),
            key=lambda i: dict_struct[i].mass,
            reverse=True,
        )

    return tree_struct.keys()


def export_struct(
    struct, mass_struct, type_export: TypeExport, type_sort: TypeSort, root_dir: str
):
    """
    export struct
    """
    delim = "\t"
    if type_export is TypeExport.CSV:
        delim = ";"
    cols = ["Name", "Mtot", "n", "Mpart", "Density", "Comp", "Drw"]
    txt = delim.join(cols) + "\n"
    stacks = sort_tulpe(list(struct.items()), mass_struct, type_sort)

    while len(stacks) > 0:
        k, v = stacks.pop(0)

        values = [
            k,
            f"{mass_struct[k].mass * v.number:.3f}",
            str(v.number),
            f"{mass_struct[k].mass:.3f}",
            f"{mass_struct[k].density:.3f}",
            str(
                "Part" if mass_struct[k].typeComponent == TypeComponent.PART else "Ass."
            ),
            str(mass_struct[k].numberDrawing),
        ]
        txt += delim.join(values) + "\n"

        if hasattr(v, "children"):
            stacks = (
                sort_tulpe(list(v.children.items()), mass_struct, type_sort) + stacks
            )

    if type_export is TypeExport.CLIPBOARD:
        do_windows_clipboard(txt)
    elif type_export is TypeExport.CSV:
        with open(os.path.join(root_dir, "bom.csv"), "w+", encoding="utf8") as f:
            f.write(txt)


def print_header():
    """
    Display the header of the output
    """
    header = f"{'Name':<50} | {'Mtot':<5} | {'n':<3} | {'Mpart':<6} | {'Density':<7} | {'Comp':<4} | {'Drw':<3}"
    click.echo(header)
    click.echo("-" * len(header))


def display_tree(
    tree_struct_mass: dict,
    dict_struct_mass: dict,
    type_sort: TypeSort = TypeSort.NAME,
    indent: str = "",
) -> None:
    """
    Display a tree struct recursively
    """
    sorted_list = sort_key_struct_tree(tree_struct_mass, dict_struct_mass, type_sort)
    n = len(sorted_list)
    if indent == "":
        print_header()
    for idx, elem in enumerate(sorted_list):
        char = "┝━"
        if idx == n - 1:
            char = "┕━"
        click.echo(
            f"{indent + char + ' ' + elem :<50} | {dict_struct_mass[elem].mass * tree_struct_mass[elem].number:5.3f} | {tree_struct_mass[elem].number:3d} | {dict_struct_mass[elem].mass:6.4f} | {dict_struct_mass[elem].density:6.2f} | {'Part' if dict_struct_mass[elem].typeComponent == TypeComponent.PART else 'Ass.'} | {dict_struct_mass[elem].numberDrawing:3d}"
        )
        if len(tree_struct_mass[elem].children) > 0:
            char = "│ "
            if idx == n - 1:
                char = "  "
            display_tree(
                tree_struct_mass[elem].children,
                dict_struct_mass,
                type_sort,
                indent + char,
            )


def display_list(list_struct: dict, type_sort: TypeSort = TypeSort.NAME) -> None:
    """
    Display a list struct
    """
    print_header()
    for elem in sort_key_struct(list_struct, type_sort):
        click.echo(
            f"{'- ' + elem :<50} | {list_struct[elem].mass * list_struct[elem].number:5.3f} | {list_struct[elem].number:3d} | {list_struct[elem].mass:6.4f} | {list_struct[elem].density:6.2f} | {'Part' if list_struct[elem].typeComponent == TypeComponent.PART else 'Ass.'} | {list_struct[elem].numberDrawing:3d}"
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


def fill_drawing_dependencies(sw_app, input_path: str, struct: dict):
    """
    Get the number of drawings related to each parts
    """
    list_of_drawings = []
    for r, _, fs in os.walk(os.path.dirname(input_path)):
        for f in fs:
            if "SLDDRW" in f and "~$" not in f:
                list_of_drawings.append(os.path.join(r, f))

    parts_in_plan_dict = {}
    for drawing_path in list_of_drawings:
        parts_in_plan = sw_app.GetDocumentDependencies2(
            os.path.abspath(drawing_path), False, True, False
        )
        for part_in_plan in parts_in_plan[::2]:
            if part_in_plan not in parts_in_plan_dict:
                parts_in_plan_dict[part_in_plan] = 1
            else:
                parts_in_plan_dict[part_in_plan] += 1

    for name in struct.keys():
        if strip_conf(name) in parts_in_plan_dict:
            struct[name].numberDrawing = parts_in_plan_dict[strip_conf(name)]
    # TODO: handle configurations
    return parts_in_plan_dict


def complete_info_on_list(sw_comp_children, dict_of_comp: dict) -> dict:
    """
    Get all the info from a list of component
    """
    children = {}

    if sw_comp_children is None:
        return children

    for sw_child in sw_comp_children:
        # Do not treat suppressed comporents
        if sw_child.GetSuppression2 == 0:
            continue

        # Get the name
        sw_child_name = get_clean_name(sw_child)

        # Get the info of the assembly
        child = complete_info_assembly(sw_child, dict_of_comp)

        # If the child is already here, only increase the number
        if sw_child_name not in children:
            children[sw_child_name] = child
        else:
            children[sw_child_name].number += 1

    return children


def complete_info_assembly(sw_comp, dict_of_comp: dict) -> dict:
    """
    Get all the information from an assembly
    """

    # Get name of component
    sw_comp_name = get_clean_name(sw_comp)

    # If already there only increase the number
    if sw_comp_name in dict_of_comp:
        dict_of_comp[sw_comp_name].number += 1
    else:
        sw_mass = 0
        sw_density = 0
        # set the configuration
        sw_comp_doc = sw_comp.GetModelDoc2
        if sw_comp_doc is not None:
            sw_comp_doc.ShowConfiguration2(sw_comp.ReferencedConfiguration)
            # Get extension manager
            sw_comp_doc_ext = sw_comp_doc.Extension
            sw_mass_property = sw_comp_doc_ext.CreateMassProperty2

            # Get mass and density
            sw_mass = sw_mass_property.Mass if sw_mass_property is not None else 0
            sw_density = sw_mass_property.Density if sw_mass_property is not None else 0
        else:
            click.echo(f"Could not evaluate {sw_comp_name}")

        print(sw_comp_name)
        # Create an new entity in the general dict
        sw_comp_children = sw_comp.GetChildren
        dict_of_comp[sw_comp_name] = StatComponent(
            mass=sw_mass,
            density=sw_density,
            number=1,
            typeComponent=(
                TypeComponent.ASSEMBLY
                if sw_comp_children is not None and len(sw_comp_children) > 0
                else TypeComponent.PART
            ),
            numberDrawing=0,
        )

    # Get info about children
    sw_comp_children = sw_comp.GetChildren
    children = complete_info_on_list(sw_comp_children, dict_of_comp)

    # Create the entry in the tree dict
    return StatComponentTree(
        number=1,
        children=children,
    )


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
@click.option(
    "--export", "export", type=click.Choice(TypeExport), default=TypeExport.NONE
)
@click.option(
    "--filter",
    "type_component",
    type=click.Choice(TypeComponent),
    default=TypeComponent.ALL,
)
@click.option("--only-default-density", "only_default_density", is_flag=True)
def stat(
    input_path: str,
    export: TypeExport,
    type_output: TypeOutput,
    type_sort: TypeSort,
    type_component: TypeComponent,
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

    sw_app, sw_doc, filename = open_app_and_file(input_path)

    # Get list of components
    sw_comps = sw_doc.GetComponents(True)

    # Empty struct to fill
    assembly_name = filename.rpartition(".")[-0] + "@" + sw_doc.GetConfigurationNames[0]
    dict_of_comp = {
        assembly_name: StatComponent(
            mass=sw_doc.Extension.CreateMassProperty2.Mass,
            density=sw_doc.Extension.CreateMassProperty2.Density,
            number=1,
            typeComponent=TypeComponent.ASSEMBLY,
            numberDrawing=0,
        )
    }

    tree_of_comp = {
        assembly_name: StatComponentTree(
            number=1,
            children=complete_info_on_list(sw_comps, dict_of_comp),
        )
    }

    fill_drawing_dependencies(sw_app, input_path, dict_of_comp)

    clean_confs(tree_of_comp, dict_of_comp)

    filter_component_type(tree_of_comp, dict_of_comp, type_component)

    if only_default_density:
        dict_of_comp = filter_density_list(dict_of_comp)

    if type_output is TypeOutput.TREE:
        display_tree(tree_of_comp, dict_of_comp, type_sort)
    elif type_output is TypeOutput.LIST:
        display_list(dict_of_comp, type_sort)
    else:
        click.echo(
            f"Type output {type_output} is unknown {type_output is TypeOutput.TREE} {type(type_output)}"
        )

    if export is not TypeExport.NONE:
        export_struct(
            tree_of_comp if type_output is TypeOutput.TREE else dict_of_comp,
            dict_of_comp,
            export,
            type_sort,
            os.path.dirname(input_path),
        )
