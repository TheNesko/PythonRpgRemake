import msvcrt, os
from pygame import time
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.screen import Screen
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.theme import Theme

class Key:
    KEY_del = 4301
    KEY_tab = 9
    KEY_space = 32
    KEY_enter = 13
    KEY_a = 97
    KEY_d = 100
    KEY_n = 110
    KEY_s = 115
    KEY_w = 119
    KEY_y = 121
    KEY_Aup = 4401
    KEY_Adown = 4402
    KEY_Aright = 4403
    KEY_Aleft = 4404


class Game:
    @staticmethod
    def TextBoxInput(text:str,char:str):
        if char == "\x08":
            string = str(text)
            return string[:-1]
        return str(text + char)

    @staticmethod
    def get_input():
        ky = msvcrt.getch()
        if ky in [b'\x00', b'\xe0']:
            ky = msvcrt.getch()
            if ky == b'S':
                return 4301
            if ky == b'H':
                return 4401
            if ky == b'P':
                return 4402
            if ky == b'M':
                return 4403
            if ky == b'K':
                return 4404
        return ord(ky)

    @staticmethod
    def wait_for_input():
        msvcrt.getch()
    
    @staticmethod
    def window(Title:str="Window",Colums:int=80,Lines:int=30):
        os.system('mode con: cols=%i lines=%i' %(Colums,Lines))
        os.system("title %s" % Title)
    
    @staticmethod
    def Clear():
        os.system('cls')

    @staticmethod
    def disable_quickedit():
        '''Disable quickedit mode on Windows terminal. quickedit prevents script to
        run without user pressing keys..'''
        if not os.name == 'posix':
            try:
                import msvcrt
                import ctypes
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                device = r'\\.\CONIN$'
                with open(device, 'r') as con:
                    hCon = msvcrt.get_osfhandle(con.fileno())
                    kernel32.SetConsoleMode(hCon, 0x0080)
            except Exception as e:
                print('Cannot disable QuickEdit mode! ' + str(e))
    