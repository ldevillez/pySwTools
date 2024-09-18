"""
Module of generic functions
"""

import platform
import click
import ctypes


def check_system_verbose() -> bool:
    """
    Check if the system is windows otherwise print a message
    """
    if platform.system() != "Windows":
        click.echo("Sorry but you need windows to execute this function")
        return False
    return True


def check_system() -> bool:
    """
    Check if the system is windows
    """
    return platform.system() == "Windows"


def do_windows_clipboard(text):
    """
    Put text into the clipboard
    """
    # from http://pylabeditor.svn.sourceforge.net/viewvc/pylabeditor/trunk/src/shells.py?revision=82&view=markup

    cf_unicode_text = 13
    ghnd = 66

    ctypes.windll.kernel32.GlobalAlloc.restype = ctypes.c_void_p
    ctypes.windll.kernel32.GlobalLock.restype = ctypes.c_void_p

    buffer_size = (len(text) + 1) * 2
    h_global_mem = ctypes.windll.kernel32.GlobalAlloc(
        ctypes.c_uint(ghnd), ctypes.c_size_t(buffer_size)
    )
    lp_global_mem = ctypes.windll.kernel32.GlobalLock(ctypes.c_void_p(h_global_mem))
    ctypes.cdll.msvcrt.memcpy(
        ctypes.c_void_p(lp_global_mem),
        ctypes.c_wchar_p(text),
        ctypes.c_int(buffer_size),
    )
    ctypes.windll.kernel32.GlobalUnlock(ctypes.c_void_p(h_global_mem))
    if ctypes.windll.user32.OpenClipboard(0):
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.SetClipboardData(
            ctypes.c_int(cf_unicode_text), ctypes.c_void_p(h_global_mem)
        )
        ctypes.windll.user32.CloseClipboard()
        return True
    return False
