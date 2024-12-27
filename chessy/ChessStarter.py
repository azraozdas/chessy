import subprocess
import sys
import ChessMenu

def start_game():
    try:
        # sys.executable kullanarak doğru Python yorumlayıcısını belirle
        subprocess.run([sys.executable, "ChessStartScreen.py"], check=True)
    except FileNotFoundError:
        print("ChessStartScreen.py bulunamadı.")
    except subprocess.CalledProcessError as e:
        print(f"ChessStartScreen.py çalıştırılırken bir hata oluştu: {e}")

    # Ana Menü'yü başlat
    ChessMenu.mainMenu()

if __name__ == "__main__":
    start_game()

#