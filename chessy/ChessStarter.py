import subprocess
import ChessMenu  # Ana menü için

def start_game():
    # ChessStartScreen.py dosyasını çalıştır (Tanıtım Ekranı)
    subprocess.run(["python3", "ChessStartScreen.py"])  # Sisteminizde `python3` yerine gerekirse `python` yazın

    # Tanıtım ekranı tamamlandıktan sonra Ana Menü'yü başlat
    ChessMenu.mainMenu()

if __name__ == "__main__":
    start_game()