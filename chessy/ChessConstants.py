import pygame as p

p.init()

#Ekran Boyutları
SCREEN_WIDTH = p.display.Info().current_w
SCREEN_HEIGHT = p.display.Info().current_h

#Tam ekran modunda ekranı başlat
screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.FULLSCREEN)

#Ses efekti ve saat
click_sound = p.mixer.Sound("sounds/click.mp3")  # Ses dosyası yolu doğru olmalı
clock = p.time.Clock()