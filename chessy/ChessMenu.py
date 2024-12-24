import sys

import pygame as p

from ChessAnimations import drawStars, generateStars
from ChessConstants import click_sound, clock, start_game_sound
from ChessSettings import settingsMenu


def draw_button(text, font, button_x, button_y, button_width, button_height, hover, clicked):
    """Buton çizen genel fonksiyon"""
    if hover:
        button_width += 20  # Genişlik büyür
        button_height += 20  # Yükseklik büyür
    if clicked:
        button_width -= 10  # Click edildiğinde küçülür
        button_height -= 10  # Click edildiğinde küçülür

    # 🔥 **Merkezden büyüme efekti**
    button_x = button_x - ((button_width - 200) // 2)  # X pozisyonunu büyümeye göre ayarla
    button_y = button_y - ((button_height - 100) // 2)  # Y pozisyonunu büyümeye göre ayarla

    button_rect = p.Rect(button_x, button_y, button_width, button_height)
    p.draw.rect(screen, (123, 6, 158), button_rect)  # Butonun arka planı

    text_surface = font.render(text, True, (255, 255, 255))
    text_x = button_x + (button_width // 2) - (text_surface.get_width() // 2)
    text_y = button_y + (button_height // 2) - (text_surface.get_height() // 2)
    screen.blit(text_surface, (text_x, text_y))  # Metni butonun ortasına yerleştir

    return button_rect  # Butonun Rect nesnesini döndür


def drawMenu(play_button, settings_button, exit_button, hover_play, hover_settings, hover_exit, clicked_play, clicked_settings, clicked_exit):
    """Ana menüyü çizer"""
    global screen, BACKGROUND_IMAGE
    screen.blit(BACKGROUND_IMAGE, (0, 0))

    # CHESSY Başlığı
    title_font = p.font.SysFont("comicsans", 180, True)
    title_surface = title_font.render('CHESSY', True, (255, 255, 255))
    title_x = (screen.get_width() // 2) - (title_surface.get_width() // 2)
    title_y = (screen.get_height() // 6)
    screen.blit(title_surface, (title_x, title_y))

    # **Buton Fontu**
    font = p.font.SysFont("comicsans", 50, True)

    # 🟢 **Play Butonu**
    play_width, play_height = 200, 100
    play_x = (screen.get_width() // 2) - (play_width // 2)
    play_y = (screen.get_height() // 2) - (play_height // 2)
    play_button = draw_button('Play', font, play_x, play_y, play_width, play_height, hover_play, clicked_play)

    # 🟢 **Settings Butonu**
    settings_width, settings_height = 200, 100
    settings_x = (screen.get_width() // 2) - (settings_width // 2)
    settings_y = play_y + 150  # Play butonunun altına ekleyin
    settings_button = draw_button('Settings', font, settings_x, settings_y, settings_width, settings_height, hover_settings, clicked_settings)

    # 🟢 **Exit Butonu**
    exit_width, exit_height = 200, 100
    exit_x = (screen.get_width() // 2) - (exit_width // 2)
    exit_y = settings_y + 150  # Settings butonunun altına ekleyin
    exit_button = draw_button('Exit', font, exit_x, exit_y, exit_width, exit_height, hover_exit, clicked_exit)

    # The Creators Bölümü (Sol Tarafta)
    creators_font = p.font.SysFont("comicsans", 15, True)
    creators_title = creators_font.render("The creators of Chessy:", True, (255, 255, 0))
    screen.blit(creators_title, (20, 20))  # Sol üst köşeye başlık yazılır

    # İsimler Listesi
    names = ["Müslüm Selim Aksahin", "Azra Özdas", "Dilay Tarhan"]
    y_offset = 60  # Başlangıçta başlıktan biraz aşağı
    for name in names:
        name_surface = creators_font.render(f"- {name}", True, (255, 255, 0))
        screen.blit(name_surface, (40, y_offset))  # İsimleri çiz
        y_offset += 40  # Her bir isim için 40 piksel aşağı kaydır

    # Telif Hakkı Yazısı (En Alt Orta)
    copyright_font = p.font.SysFont("arial", 20)  # Küçük ve düz bir font
    copyright_surface = copyright_font.render("© 2025 King's Gambit Team. All rights reserved.", True, (200, 200, 200))
    copyright_x = (screen.get_width() // 2) - (copyright_surface.get_width() // 2)
    copyright_y = screen.get_height() - 30  # Ekranın en altından 30 piksel yukarıda
    screen.blit(copyright_surface, (copyright_x, copyright_y))

    # 🔥 **3 buton da geri döndürülüyor**
    return play_button, settings_button, exit_button

# En üstte global değişkeni tanımlayın
is_returning_from_game = False  # Return to Menu'den dönüldüğünü kontrol eder


def startButtonAnimation(screen, button):
    click_sound.play()
    generateStars(button.centerx, button.centery)
    start_time = p.time.get_ticks()

    while p.time.get_ticks() - start_time < 1000:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)
        p.display.flip()
        p.time.Clock().tick(60)

    # Yükleme ekranı
    screen.fill((0, 0, 0))
    loading_font = p.font.SysFont("comicsans", 60, True)
    loading_surface = loading_font.render("Loading...", True, (255, 255, 255))
    screen.blit(loading_surface, ((SCREEN_WIDTH // 2) - (loading_surface.get_width() // 2),
                                  (SCREEN_HEIGHT // 2) - (loading_surface.get_height() // 2)))
    p.display.flip()
    p.time.wait(1000)


# Ana menü
def mainMenu():
    global screen, BACKGROUND_IMAGE, is_returning_from_game  # Tüm global değişkenleri en başta tanımla

    running = True
    play_button = None
    settings_button = None
    exit_button = None

    hover_play = False
    clicked_play = False

    hover_settings = False
    clicked_settings = False

    hover_exit = False
    clicked_exit = False

    while running:
        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.VIDEORESIZE:  # Ekran boyutu değiştirildiğinde
                screen = p.display.set_mode((event.w, event.h), p.FULLSCREEN)
                BACKGROUND_IMAGE = p.transform.scale(p.image.load("images/backgroundphoto.png"), (event.w, event.h))
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        # Buton çizimi ve animasyon kontrolü
        hover_play = play_button and play_button.collidepoint(mouse_pos)
        clicked_play = hover_play and mouse_click

        hover_settings = settings_button and settings_button.collidepoint(mouse_pos)
        clicked_settings = hover_settings and mouse_click

        hover_exit = exit_button and exit_button.collidepoint(mouse_pos)
        clicked_exit = hover_exit and mouse_click

        # Arkaplanı yeniden çiz
        screen.blit(BACKGROUND_IMAGE, (0, 0))

        # Butonları çiz
        play_button, settings_button, exit_button = drawMenu(
            play_button,
            settings_button,
            exit_button,
            hover_play,
            hover_settings,
            hover_exit,
            clicked_play,
            clicked_settings,
            clicked_exit
        )

        # Yıldızları çizerken Return to Menu'den gelindiğini kontrol et
        if not is_returning_from_game:
            drawStars(screen)  # Sadece Return to Menu'den gelinmediğinde yıldızları ekrana çiz

        p.display.flip()
        clock.tick(60)

        # 🔥 **Play Butonuna Tıklandıysa**
        if clicked_play:
            is_returning_from_game = False  # Return to Menu'den dönmüyoruz, bu yüzden bayrağı sıfırla
            generateStars(play_button.centerx, play_button.centery)
            click_sound.play()  # 🔊 Butona tıklama sesi çal
            start_time = p.time.get_ticks()
            while p.time.get_ticks() - start_time < 1000:  # Yıldız animasyonu 1 saniye
                screen.blit(BACKGROUND_IMAGE, (0, 0))  # Arka planı çiz
                drawMenu(
                    play_button,
                    settings_button,
                    exit_button,
                    hover_play,
                    hover_settings,
                    hover_exit,
                    clicked_play,
                    clicked_settings,
                    clicked_exit
                )
                drawStars(screen)
                p.display.flip()
                clock.tick(60)

            # Loading ekranı
            screen.fill((0, 0, 0))
            loading_font = p.font.SysFont("comicsans", 60, True)
            loading_surface = loading_font.render("Loading...", True, (255, 255, 255))
            screen.blit(loading_surface, ((screen.get_width() // 2) - (loading_surface.get_width() // 2),
                                          (screen.get_height() // 2) - (loading_surface.get_height() // 2)))
            p.display.flip()
            p.time.wait(1000)  # Loading ekranında 1 saniye bekle

            start_game_sound.play()  # 🎉 Oyun başlıyor, sesi çal
            main()

        # 🔥 **Settings Butonuna Tıklandıysa**
        if clicked_settings:
            click_sound.play()  # 🔊 Click sesi ekleniyor
            generateStars(settings_button.centerx, settings_button.centery)
            start_time = p.time.get_ticks()
            while p.time.get_ticks() - start_time < 1000:  # Yıldız animasyonu 1 saniye
                screen.blit(BACKGROUND_IMAGE, (0, 0))  # Arka planı çiz
                drawMenu(
                    play_button,
                    settings_button,
                    exit_button,
                    hover_play,
                    hover_settings,
                    hover_exit,
                    clicked_play,
                    clicked_settings,
                    clicked_exit
                )
                drawStars(screen)
                p.display.flip()
                clock.tick(60)

            settingsMenu()  # Ayarlar menüsüne geç

        # 🔥 **Exit Butonuna Tıklandıysa**
        if clicked_exit:
            click_sound.play()  # 🔊 Click sesi ekleniyor
            generateStars(exit_button.centerx, exit_button.centery)  # Yıldız animasyonu çıkış butonunun merkezinde olur
            start_time = p.time.get_ticks()
            while p.time.get_ticks() - start_time < 1000:  # Yıldız animasyonu 1 saniye sürsün
                screen.blit(BACKGROUND_IMAGE, (0, 0))  # Arka planı çiz
                drawMenu(
                    play_button,
                    settings_button,
                    exit_button,
                    hover_play,
                    hover_settings,
                    hover_exit,
                    clicked_play,
                    clicked_settings,
                    clicked_exit
                )
                drawStars(screen)  # Yıldızları ekrana çiz
                p.display.flip()
                clock.tick(60)

            is_returning_from_game = False  # Return to Menu bayrağını sıfırla
            p.quit()
            sys.exit()



if __name__ == "__main__":
    mainMenu()
