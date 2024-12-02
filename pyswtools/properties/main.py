"""
Give stat from an assembly
"""

import os
import click
import copy

# pylint: disable=relative-beyond-top-level
from ..utils import check_system, check_system_verbose, do_windows_clipboard
from ..helper_sw import open_app_and_file, is_temp, is_assembly, is_file, open_file

if check_system():
    # pylint: disable=import-error
    import win32com.client
    import pythoncom

    Views = []
    VT_Views = win32com.client.VARIANT(pythoncom.VT_VARIANT, Views)
    VT_BYREF = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, -1)


def fetch_properties(sw_doc):
    """
    Get all the properties from a solidworks document and return them
    """

    props = {}
    for conf in sw_doc.getConfigurationNames:
        ext = sw_doc.Extension.CustomPropertyManager(conf)

        names_props = ext.GetNames
        if names_props is None:
            continue

        print(f"Using configuration '{conf}':")
        for name_prop in names_props:
            type_prop = ext.GetType2(name_prop)

            value_prop = win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_BSTR, ""
            )
            resolved_value_prop = win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_BSTR, ""
            )

            was_resolved = win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_BOOL, bool()
            )
            link_to_property = win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_BOOL, bool()
            )

            ext.Get6(
                name_prop,
                False,
                value_prop,
                resolved_value_prop,
                was_resolved,
                link_to_property,
            )
            print(f"- {name_prop}: {value_prop.value}")
            props[name_prop] = {"type": type_prop, "value": value_prop.value}
        return props


def apply_props_to_doc(sw_doc, props):
    """
    Apply the props to sw_doc
    """

    for conf in sw_doc.getConfigurationNames:
        ext = sw_doc.Extension.CustomPropertyManager(conf)

        for k, v in props.items():
            ext.Add3(k, v["type"], v["value"], 0)

    # Need to save the document
    sw_doc.save3(1, VT_BYREF, VT_BYREF)


def apply_props_to_children(sw_comp_children, props):
    """
    Apply the props to all the sw_comp_children
    """

    for sw_child in sw_comp_children:

        sw_doc = sw_child.GetModelDoc2

        if sw_doc is not None:
            apply_props_to_doc(sw_doc, props)


@click.command()
@click.help_option("-h", "--help")
@click.argument(
    "template_path",
    type=click.Path(
        exists=True,
        dir_okay=False,
    ),
)
@click.argument(
    "apply_path",
    type=click.Path(
        exists=True,
        dir_okay=False,
    ),
)
def properties(
    template_path: str,
    apply_path: str,
) -> None:
    """
    Act on properties
    """
    if not check_system_verbose():
        return

    if not is_file(template_path) or is_temp(template_path):
        click.echo("Please select a part file (.SLDPRT)")
        click.echo(f"{template_path} is not an assembly file")
        return

    if is_temp(apply_path):
        click.echo("Please select a part (.SLDPRT) or an asssembly file (.SLDASM)")
        click.echo(f"{template_path} is not an part or an assembly file")
        return

    sw_app, sw_doc, _ = open_app_and_file(template_path)

    props = fetch_properties(sw_doc)

    if is_file(apply_path):
        sw_doc, _ = open_file(sw_app, apply_path)
        apply_props_to_doc(sw_doc, props)
    else:
        sw_doc, _ = open_file(sw_app, apply_path)
        sw_comps = sw_doc.GetComponents(False)
        apply_props_to_children(sw_comps, props)
