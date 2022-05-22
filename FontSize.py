from ctypes import POINTER, WinDLL, Structure, sizeof, byref
from ctypes.wintypes import BOOL, SHORT, WCHAR, UINT, ULONG, DWORD, HANDLE

LF_FACESIZE = 32
STD_OUTPUT_HANDLE = -11

class COORD(Structure):
    _fields_ = [
        ("X", SHORT),
        ("Y", SHORT),
    ]

class CONSOLE_FONT_INFOEX(Structure):
    _fields_ = [
        ("cbSize", ULONG),
        ("nFont", DWORD),
        ("dwFontSize", COORD),
        ("FontFamily", UINT),
        ("FontWeight", UINT),
        ("FaceName", WCHAR * LF_FACESIZE)
    ]

kernel32_dll = WinDLL("kernel32.dll")

get_std_handle_func = kernel32_dll.GetStdHandle
get_std_handle_func.argtypes = [DWORD]
get_std_handle_func.restype = HANDLE

get_current_console_font_ex_func = kernel32_dll.GetCurrentConsoleFontEx
get_current_console_font_ex_func.argtypes = [HANDLE, BOOL, POINTER(CONSOLE_FONT_INFOEX)]
get_current_console_font_ex_func.restype = BOOL

set_current_console_font_ex_func = kernel32_dll.SetCurrentConsoleFontEx
set_current_console_font_ex_func.argtypes = [HANDLE, BOOL, POINTER(CONSOLE_FONT_INFOEX)]
set_current_console_font_ex_func.restype = BOOL

'''
This code is used to change console font size
This is the source I found this code
https://stackoverflow.com/questions/52336257/python-programmatically-change-console-font-size
'''

def run(Font_size:int):
    stdout = get_std_handle_func(STD_OUTPUT_HANDLE)
    font = CONSOLE_FONT_INFOEX()
    font.cbSize = sizeof(CONSOLE_FONT_INFOEX)
    res = get_current_console_font_ex_func(stdout, False, byref(font))
    font.dwFontSize.X = 10
    font.dwFontSize.Y = Font_size
    res = set_current_console_font_ex_func(stdout, False, byref(font))
