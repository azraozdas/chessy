import pygame as p

from ChessConstants import SQUARE_SIZE, IMAGES
from ChessMenu import mainMenu

# Global değişkenler
sound_on = True  # Ses varsayılan olarak açık
is_returning_from_game = False  # Return to Menu'den dönüldüğünü kontrol eder
is_sfx_on = True  # Ses efekti açık mı kontrolü


def play_sound(sound):
    """Sesleri kontrol eder. Eğer ses kapalıysa çalmaz."""
    if sound_on:
        sound.play()


def loadImages():
    """Görüntüleri yükler."""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))
        except FileNotFoundError:
            print(f"HATA: {piece}.png bulunamadı!")


def loadSounds():
    """Ses dosyalarını yükler."""
    global move_sound, check_sound
    try:
        p.mixer.init()  # Pygame ses motorunu başlat
        move_sound = p.mixer.Sound("sounds/move-pieces.mp3")
        check_sound = p.mixer.Sound("sounds/tension.MP3")
    except FileNotFoundError as e:
        print(f"HATA: Ses dosyası eksik - {e}")

def main():
    """Ana oyun döngüsü"""
    pass

def start_game():
    main()  # Oyunu başlatan fonksiyon

if __name__ == "__main__":
    main()
    mainMenu()  # Ana menüye geçiş