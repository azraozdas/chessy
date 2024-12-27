import pygame as p

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
clock = p.time.Clock()

#
