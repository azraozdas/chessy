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

def resize_and_center_background(image, screen_width, screen_height):
    bg_width, bg_height = image.get_size()

    # Resmi oranı bozmadan ekranı dolduracak şekilde ölçekle
    if bg_width / bg_height > screen_width / screen_height:
        new_height = screen_height
        new_width = int(bg_width * (screen_height / bg_height))
    else:
        new_width = screen_width
        new_height = int(bg_height * (screen_width / bg_width))

    # Resmi orantılı şekilde yeniden boyutlandır
    scaled_image = p.transform.smoothscale(image, (new_width, new_height))

    # Yeni bir siyah arkaplan oluştur
    final_surface = p.Surface((screen_width, screen_height))
    final_surface.fill((0, 0, 0))  # Siyah arkaplan

    # Resmi ortala
    x_offset = (screen_width - new_width) // 2
    y_offset = (screen_height - new_height) // 2
    final_surface.blit(scaled_image, (x_offset, y_offset))

    return final_surface
