import random
import sys

import pygame as p

p.init()
p.mixer.init()

click_sound = p.mixer.Sound("sounds/click.mp3")
start_game_sound = p.mixer.Sound("sounds/game-start.mp3")

SCREEN_WIDTH = p.display.Info().current_w
SCREEN_HEIGHT = p.display.Info().current_h

stars = []
sound_on = True


overlay = p.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), p.SRCALPHA)
overlay.fill((0, 0, 0, 180))  # Şeffaf siyah



BACKGROUND_IMAGE = p.image.load("images/backgroundphoto.png")
BACKGROUND_IMAGE = p.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))

overlay = p.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), p.SRCALPHA)
overlay.fill((0, 0, 0, 180))  # Şeffaf siyah overlay

def generateStars(x, y, count=30):
    for _ in range(count):
        stars.append({
            'x': x,
            'y': y,
            'dx': random.uniform(-3, 3),
            'dy': random.uniform(-3, 3),
            'size': random.randint(2, 5),
            'life': random.randint(40, 100)
        })


def drawStars(screen):
    for star in stars:
        p.draw.circle(screen, (255, 255, 0), (int(star['x']), int(star['y'])), star['size'])
        star['x'] += star['dx']
        star['y'] += star['dy']
        star['life'] -= 1
    for star in stars[:]:
        if star['life'] <= 0:
            stars.remove(star)

def drawMenu(screen):
    global BACKGROUND_IMAGE
    running = True
    submenu_open = False  # Alt menü başlangıçta kapalı
    scale_factor = SCREEN_HEIGHT / 1080

    font = p.font.SysFont("comicsans", int(50 * scale_factor), True)
    title_font = p.font.SysFont("comicsans", int(180 * scale_factor), True)
    creators_font = p.font.SysFont("comicsans", int(20 * scale_factor), True)
    copyright_font = p.font.SysFont("arial", int(20 * scale_factor))  # Telif yazısı için font

    play_button = None
    settings_button = None
    exit_button = None

    while running:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)

        # Başlık metni
        title_surface = title_font.render('CHESSY', True, (255, 255, 255))
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, SCREEN_HEIGHT // 10))

        # The Creators Bölümü
        creators_title = creators_font.render("The creators of Chessy:", True, (255, 255, 0))
        screen.blit(creators_title, (int(20 * scale_factor), int(20 * scale_factor)))

        names = ["Müslüm Selim Aksahin", "Azra Özdas", "Dilay Tarhan"]
        y_offset = int(60 * scale_factor)
        for name in names:
            name_surface = creators_font.render(f"- {name}", True, (255, 255, 0))
            screen.blit(name_surface, (int(40 * scale_factor), y_offset))
            y_offset += int(30 * scale_factor)

        # Telif Hakkı (Copyright) Metni
        copyright_surface = copyright_font.render(
            "© 2025 King's Gambit Team. All rights reserved.",
            True,
            (200, 200, 200)
        )
        copyright_x = (SCREEN_WIDTH // 2) - (copyright_surface.get_width() // 2)
        copyright_y = SCREEN_HEIGHT - int(30 * scale_factor)
        screen.blit(copyright_surface, (copyright_x, copyright_y))

        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        # Alt menü açık değilse, ana butonları çiz
        if not submenu_open:
            play_button = draw_button('Play', font, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                                      300, 100, play_button and play_button.collidepoint(mouse_pos), False, screen)
            settings_button = draw_button('Settings', font, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
                                          300, 100, settings_button and settings_button.collidepoint(mouse_pos), False, screen)
            exit_button = draw_button('Exit', font, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 210,
                                      300, 100, exit_button and exit_button.collidepoint(mouse_pos), False, screen)

            # "Play" butonuna tıklandığında alt menüyü aç
            if play_button.collidepoint(mouse_pos) and mouse_click:
                submenu_open = True  # Alt menü açılır

        # Alt menü butonları
        if submenu_open:
            screen.blit(overlay, (0, 0))  # Şeffaf arkaplanı overlay olarak ekle

            play_with_computer = draw_button("Play with Computer", font, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70,
                                             400, 100, False, False, screen)
            play_with_friend = draw_button("Play with Friend", font, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70,
                                           400, 100, False, False, screen)

            # "Play with Friend" butonuna basıldığında oyunu başlat
            if play_with_friend.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, play_button)

                # Döngüsel importu önlemek için burada import yapılıyor
                from ChessMain import main
                main()  # Satranç tahtasını başlat
                running = False  # Menü döngüsünden çık

        p.display.flip()

        # Ayarlar butonu
        if settings_button and settings_button.collidepoint(mouse_pos) and mouse_click:
            startButtonAnimation(screen, settings_button, skip_loading=True)
            from ChessSettings import settingsScreen
            settingsScreen()
            return

        # Çıkış butonu
        if exit_button and exit_button.collidepoint(mouse_pos) and mouse_click:
            startButtonAnimation(screen, exit_button, skip_loading=True)
            p.quit()
            sys.exit()

def draw_button(text, font, x, y, width, height, hover, clicked, screen):
    scale_factor = SCREEN_HEIGHT / 1080  # Referans yüksekliği 1080 olarak alıyoruz
    width = int(width * scale_factor)
    height = int(height * scale_factor)

    if hover:
        width += int(20 * scale_factor)
        height += int(20 * scale_factor)
    if clicked:
        width -= int(10 * scale_factor)
        height -= int(10 * scale_factor)

    rect = p.Rect(x - width // 2, y - height // 2, width, height)
    p.draw.rect(screen, (123, 6, 158), rect)
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.centery - text_surface.get_height() // 2))
    return rect



def startButtonAnimation(screen, button, skip_loading=False):
    click_sound.play()
    generateStars(button.centerx, button.centery)
    start_time = p.time.get_ticks()

    while p.time.get_ticks() - start_time < 1000:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)
        p.display.flip()
        p.time.Clock().tick(60)

    # Yükleme ekranı sadece skip_loading False olduğunda gösterilir
    if not skip_loading:
        screen.fill((0, 0, 0))
        loading_font = p.font.SysFont("comicsans", 60, True)
        loading_surface = loading_font.render("Loading...", True, (255, 255, 255))
        screen.blit(loading_surface, ((SCREEN_WIDTH // 2) - (loading_surface.get_width() // 2),
                                      (SCREEN_HEIGHT // 2) - (loading_surface.get_height() // 2)))
        p.display.flip()
        p.time.wait(1000)

def mainMenu():

    screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.FULLSCREEN)
    drawMenu(screen)


if __name__ == "__main__":
    mainMenu()  # `mainMenu()` işlevi çağrılır.
#