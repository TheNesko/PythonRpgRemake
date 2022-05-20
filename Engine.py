import msvcrt, os

class Game:
    @staticmethod
    def get_input():
        answer = msvcrt.getwch()
        print(answer)
        return answer

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
