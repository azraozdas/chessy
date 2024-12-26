import sys
import pygame as p
from ChessConstants import screen, click_sound, clock

p.init()

# SFX Durumu İçin Global Değişken
is_sfx_on = True  # Varsayılan olarak ses efektleri açık

# Arka Plan Yükleme
SETTINGS_BACKGROUND = p.image.load("images/settingsphoto.png")


def resize_background():
    global SETTINGS_BACKGROUND
    SETTINGS_BACKGROUND = p.transform.smoothscale(SETTINGS_BACKGROUND, screen.get_size())



def settingsScreen():
    global is_sfx_on  # Sound kontrolü için global değişkeni al
    running = True

    # İlk Başlangıçta Arka Planı Ekran Boyutuna Göre Ayarla
    resize_background()

    while running:
        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True
            elif event.type == p.VIDEORESIZE:
                p.display.set_mode((event.w, event.h), p.RESIZABLE)  # Ekranı yeniden boyutlandırılabilir yap
                resize_background()  # Arka planı yeniden boyutlandır

        # Arka Planı Tam Ekrana Yay
        screen.blit(SETTINGS_BACKGROUND, (0, 0))

        # Sound/SFX Butonu Ortalanması
        button_text = "Sound/SFX: ON" if is_sfx_on else "Sound/SFX: OFF"
        button_color = (0, 255, 0) if is_sfx_on else (128, 128, 128)

        # Butonu Dinamik Olarak Ortala
        sound_button = p.Rect(0, 0, 300, 100)
        sound_button.center = (screen.get_width() // 2, screen.get_height() // 2)

        # Butonu ve Metni Çiz
        p.draw.rect(screen, button_color, sound_button)

        # Metin Dinamik Font Ayarı (Taşmayı Engelleme)
        font_size = 50
        while True:
            font = p.font.SysFont("comicsans", font_size, True)
            text_surface = font.render(button_text, True, (0, 0, 0))
            if text_surface.get_width() <= sound_button.width - 40:
                break
            font_size -= 1  # Font boyutunu küçült

        screen.blit(text_surface, (sound_button.centerx - text_surface.get_width() // 2,
                                   sound_button.centery - text_surface.get_height() // 2))

        # Butona Tıklama Kontrolü
        if sound_button.collidepoint(mouse_pos) and mouse_click:
            is_sfx_on = not is_sfx_on  # Ses efektini tersine çevir (ON <-> OFF)
            if is_sfx_on:
                click_sound.play()  # Ses açıldığında bir tıklama sesi çal

        # Geri Dön Butonu
        return_font = p.font.SysFont("comicsans", 30, True)
        return_text_surface = return_font.render("Return to Menu", True, (255, 255, 0))
        return_button = p.Rect(0, 0, 250, 60)
        return_button.topleft = (20, 20)  # Sol üst köşe

        p.draw.rect(screen, (123, 6, 158), return_button)
        screen.blit(return_text_surface, (return_button.centerx - return_text_surface.get_width() // 2,
                                          return_button.centery - return_text_surface.get_height() // 2))

        # Geri Dön Tıklama Kontrolü (Ana Menüye Dön)
        if return_button.collidepoint(mouse_pos) and mouse_click:
            from ChessMenu import mainMenu  # Ana menü fonksiyonunu içe aktar
            mainMenu()
            return  # Fonksiyondan çık

        # Ekranı Güncelle
        p.display.flip()
        clock.tick(60)

