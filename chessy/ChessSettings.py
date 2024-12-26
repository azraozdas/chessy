import sys

import pygame as p



def settingsScreen():
    global is_sfx_on  # Sound kontrolü için global değişkeni al
    running = True

    while running:
        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        screen.fill((0, 0, 0))  # Arkaplanı siyah yap
        font = p.font.SysFont("comicsans", 50, True)

        # Sound/SFX Butonu
        button_text = "Sound/SFX: ON" if is_sfx_on else "Sound/SFX: OFF"
        button_color = (0, 255, 0) if is_sfx_on else (128, 128, 128)
        sound_button = p.Rect(100, 200, 300, 100)
        p.draw.rect(screen, button_color, sound_button)
        text_surface = font.render(button_text, True, (0, 0, 0))
        screen.blit(text_surface, (sound_button.centerx - text_surface.get_width() // 2,
                                   sound_button.centery - text_surface.get_height() // 2))

        if sound_button.collidepoint(mouse_pos) and mouse_click:
            is_sfx_on = not is_sfx_on  # Ses efektini tersine çevir (ON <-> OFF)
            if is_sfx_on:
                click_sound.play()  # Ses açıldığında bir tıklama sesi çal

        p.display.flip()
        clock.tick(60)

# Settings ekranı arka plan fotoğrafı
SETTINGS_BACKGROUND = p.image.load("images/settingsphoto.png")
SETTINGS_BACKGROUND = p.transform.scale(SETTINGS_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Settings menüsü
def settingsMenu(screen):
    """Settings ekranını çizen ve Sound/SFX ayarını kontrol eden fonksiyon."""
    global sound_on  # Global ses değişkenini kullan
    running = True

    while running:
        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        # 🔥 Settings arka planını çiz
        screen.blit(SETTINGS_BACKGROUND, (0, 0))

        # Sound/SFX Butonu
        sound_text = "Sound/SFX: ON" if sound_on else "Sound/SFX: OFF"
        sound_color = (0, 255, 0) if sound_on else (128, 128, 128)  # Yeşil açık, gri kapalı

        font_size = 50  # İlk font boyutunu ayarla
        font = p.font.SysFont("comicsans", font_size, True)

        # Metin boyutunu kontrol et, sığmıyorsa küçült
        while True:
            sound_text_surface = font.render(sound_text, True, sound_color)
            if sound_text_surface.get_width() <= 280:  # Butonun genişliğinden daha küçükse
                break
            font_size -= 1  # Font boyutunu küçült
            font = p.font.SysFont("comicsans", font_size, True)

        # Buton genişliğini ve yüksekliğini metne göre ayarla
        sound_width = sound_text_surface.get_width() + 40  # 40 piksel boşluk (20 sağ, 20 sol)
        sound_height = sound_text_surface.get_height() + 20  # 20 piksel boşluk (10 yukarı, 10 aşağı)
        sound_x = (screen.get_width() // 2) - (sound_width // 2)
        sound_y = (screen.get_height() // 2) - (sound_height // 2)

        sound_button = p.Rect(sound_x, sound_y, sound_width, sound_height)
        p.draw.rect(screen, (123, 6, 158), sound_button)

        # Yazıyı butonun tam ortasına yerleştirin
        text_x = sound_button.x + (sound_button.width // 2) - (sound_text_surface.get_width() // 2)
        text_y = sound_button.y + (sound_button.height // 2) - (sound_text_surface.get_height() // 2)
        screen.blit(sound_text_surface, (text_x, text_y))

        # Fare tıklama kontrolü
        if sound_button.collidepoint(mouse_pos) and mouse_click:
            sound_on = not sound_on  # Ses durumunu tersine çevir

        # Geri dön butonu
        return_font = p.font.SysFont("comicsans", 30, True)
        return_text_surface = return_font.render("Return to Menu", True, (255, 255, 0))
        return_button = p.Rect(20, 20, 200, 50)
        p.draw.rect(screen, (123, 6, 158), return_button)
        screen.blit(return_text_surface, (30, 30))

        # Geri dön kontrolü
        if return_button.collidepoint(mouse_pos) and mouse_click:
            return  # Ayarlardan çık ve ana menüye dön

        # Ekranı güncelle
        p.display.flip()
        clock.tick(60)
