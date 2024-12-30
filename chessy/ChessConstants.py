import pygame as p

from chessy import ChessGlobals

p.init()
p.mixer.init()

#Ekran Boyutları
SCREEN_WIDTH = p.display.Info().current_w
SCREEN_HEIGHT = p.display.Info().current_h

#Tam ekran modunda ekranı başlat
screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.FULLSCREEN)

#Ses efekti ve saat
click_sound = p.mixer.Sound("sounds/click.mp3")  # Ses dosyası yolu doğru olmalı
move_sound = p.mixer.Sound("sounds/move-pieces.mp3")
start_sound = p.mixer.Sound("sounds/game-start.mp3")
check_sound = p.mixer.Sound("sounds/tension.mp3")
captured_sound = p.mixer.Sound("sounds/captured-sound.mp3")
piece_select_sound = p.mixer.Sound("sounds/piece-select.mp3")

#Menü müziği
if ChessGlobals.is_sfx_on:
    p.mixer.music.load("sounds/menuchessysong.mp3")
    p.mixer.music.play(-1)  # Sonsuz döngüde çalar


#Saat
clock = p.time.Clock()

######
