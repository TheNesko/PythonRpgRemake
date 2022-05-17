import msvcrt


class Game:
    @staticmethod
    def get_input():
        answer = msvcrt.getwche()
        return answer
    
    @staticmethod
    def wait_for_input():
        msvcrt.getch()