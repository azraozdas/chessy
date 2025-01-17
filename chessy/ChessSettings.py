import sys
import pygame as p
from ChessConstants import screen, click_sound, clock
from chessy import ChessGlobals
from ChessMenu import draw_button, startButtonAnimation  # Animasyon fonksiyonunu içe aktar
from ChessGlobals import SETTINGS_BACKGROUND

p.init()


def resize_background():
    ChessGlobals.SETTINGS_BACKGROUND = p.transform.smoothscale(
        ChessGlobals.SETTINGS_BACKGROUND, screen.get_size()
    )


def settingsScreen():
    running = True

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
                p.display.set_mode((event.w, event.h), p.RESIZABLE)
                resize_background()

        # 1) Arka planı çiz
        screen.blit(ChessGlobals.SETTINGS_BACKGROUND, (0, 0))

        # 2) Arka planı karartmak için yarı saydam bir yüzey ekle
        dark_surface = p.Surface(screen.get_size(), p.SRCALPHA)
        # Alfa değerini artırıp/azaltarak karartma miktarını değiştirebilirsiniz (0 = şeffaf, 255 = tamamen opak)
        dark_surface.fill((0, 0, 0, 120))
        screen.blit(dark_surface, (0, 0))

        # 3) Sound butonu
        button_text = "Sound/SFX: ON" if ChessGlobals.is_sfx_on else "Sound/SFX: OFF"
        button_color = (0, 255, 0) if ChessGlobals.is_sfx_on else (128, 128, 128)

        # Sound butonunun konum ve boyutu
        sound_button = p.Rect(0, 0, 300, 100)
        sound_button.center = (screen.get_width() // 2, screen.get_height() // 2)

        # Sarı çerçeve ve yumuşak köşeli buton ayarları
        border_color = (255, 255, 0)      # Sarı çerçeve rengi
        border_thickness = 5             # Çerçeve kalınlığı
        corner_radius = 15               # Köşelerin yumuşaklık derecesi

        # Çerçeveyi çiz
        p.draw.rect(screen, border_color, sound_button, border_thickness, border_radius=corner_radius)
        # İç rengini çiz (butonun iç kısmı çerçevenin içine gelsin diye inflate kullanıyoruz)
        p.draw.rect(
            screen,
            button_color,
            sound_button.inflate(-border_thickness, -border_thickness),
            border_radius=corner_radius
        )

        # Sound butonu yazısını çiz
        font_size = 50
        while True:
            font = p.font.SysFont("Times New Roman", font_size, True)
            text_surface = font.render(button_text, True, (0, 0, 0))
            if text_surface.get_width() <= sound_button.width - 40:
                break
            font_size -= 1

        screen.blit(
            text_surface,
            (
                sound_button.centerx - text_surface.get_width() // 2,
                sound_button.centery - text_surface.get_height() // 2
            )
        )

        # Sound butonuna tıklama kontrolü
        if sound_button.collidepoint(mouse_pos) and mouse_click:
            ChessGlobals.is_sfx_on = not ChessGlobals.is_sfx_on
            if ChessGlobals.is_sfx_on:
                click_sound.play()
                p.mixer.music.load("sounds/menuchessysong.mp3")
                p.mixer.music.play(-1)
            else:
                p.mixer.music.stop()
                p.mixer.stop()

        # 4) Return to Menu butonu
        return_button_width = 300
        return_button_height = 80
        return_button_x = 180
        return_button_y = 70

        # draw_button kullanarak butonu çiziyoruz
        return_button_rect = draw_button(
            'Return to Menu',
            p.font.SysFont("Times New Roman", 30, True),
            return_button_x,
            return_button_y,
            return_button_width,
            return_button_height,
            return_button_rect.collidepoint(mouse_pos) if 'return_button_rect' in locals() else False,
            mouse_click,
            screen
        )

        # Return to Menu butonuna tıklama kontrolü
        if return_button_rect.collidepoint(mouse_pos) and mouse_click:
            if ChessGlobals.is_sfx_on:
                click_sound.play()
                startButtonAnimation(screen, return_button_rect, skip_loading=True)
                from ChessMenu import mainMenu
                mainMenu()
                return
            else:
                # Sound/SFX kapalı iken de menüye dönülsün
                startButtonAnimation(screen, return_button_rect, skip_loading=True)
                from ChessMenu import mainMenu
                mainMenu()
                return

        # Ekranı güncelle
        p.display.flip()
        clock.tick(60)

