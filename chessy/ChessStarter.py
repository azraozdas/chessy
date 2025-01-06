import ChessStartScreen
import ChessMenu

def start_game():

    ChessStartScreen.intro_screen()

    ChessMenu.mainMenu(first_time=True)

if __name__ == "__main__":
    start_game()
#