
import pygame as p
import random
import sys
import os
import ChessEngine  # chessEngine modülünü doğru bir şekilde içe aktardık


# Oyun Ayarları
p.init()
p.mixer.init()
check_sound = p.mixer.Sound("sounds/tension.MP3")
move_sound = p.mixer.Sound("sounds/move-pieces.mp3")
start_game_sound = p.mixer.Sound("sounds/game-start.mp3")
click_sound = p.mixer.Sound("sounds/click.mp3")
sound_on = True  # Ses varsayılan olarak açık

# 🔥 2️⃣ Ekran boyutunu (çözünürlüğü) alın
SCREEN_WIDTH = p.display.Info().current_w  # Mevcut ekran genişliği
SCREEN_HEIGHT = p.display.Info().current_h  # Mevcut ekran yüksekliği

# Ekranın %100'ini kaplayacak şekilde tahtayı ayarla
BOARD_WIDTH = int(SCREEN_WIDTH * 1)
BOARD_HEIGHT = int(SCREEN_HEIGHT * 1)

# Eğer tahtayı kare olarak tutmak isterseniz
BOARD_WIDTH = min(BOARD_WIDTH, BOARD_HEIGHT)
BOARD_HEIGHT = BOARD_WIDTH

MOVE_LOG_PANEL_WIDTH = int(BOARD_WIDTH * 0.25)
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Satranç tahtası 8x8'dir
SQUARE_SIZE = BOARD_WIDTH // DIMENSION
MAX_FPS = 120

# Ekranı oluştur
screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.FULLSCREEN)
p.display.set_caption('CHESSY')
clock = p.time.Clock()

# Renkler ve Offsetler
LIGHT_COLOR = (255, 102, 242)
DARK_COLOR = (123, 6, 158)
BACKGROUND_COLOR = (0, 0, 0)
X_OFFSET = 0
Y_OFFSET = 0

IMAGES = {}

# Yıldız animasyonu için liste
stars = []

# 🔥 Menünün arka plan fotoğrafı
BACKGROUND_IMAGE = p.image.load("images/backgroundphoto.png")
BACKGROUND_IMAGE = p.transform.scale(BACKGROUND_IMAGE, (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))



