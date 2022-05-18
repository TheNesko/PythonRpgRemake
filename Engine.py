import msvcrt, os


class Game:
    @staticmethod
    def get_input():
        answer = msvcrt.getwche()
        return answer
    
    @staticmethod
    def wait_for_input():
        msvcrt.getch()
    
    @staticmethod
    def window(Title:str="Window",Colums:int=50,Lines:int=30):
        os.system('mode con: cols=%i lines=%i' %(Colums,Lines))
        os.system("title %s" % Title)
    
    @staticmethod
    def Clear():
        os.system('cls')