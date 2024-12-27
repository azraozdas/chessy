import ChessStartScreen
import ChessMenu

def start_game():
    # Intro ekranını çalıştır
    ChessStartScreen.intro_screen()

    # Ana Menü'yü başlat
    ChessMenu.mainMenu(first_time=True)

if __name__ == "__main__":
    start_game()

##