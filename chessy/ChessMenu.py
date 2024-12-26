import random
import sys
import ChessStarter
import pygame as p

p.init()
p.mixer.init()

click_sound = p.mixer.Sound("sounds/click.mp3")
start_game_sound = p.mixer.Sound("sounds/game-start.mp3")

SCREEN_WIDTH = p.display.Info().current_w
SCREEN_HEIGHT = p.display.Info().current_h

stars = []
sound_on = True

BACKGROUND_IMAGE = p.image.load("images/backgroundphoto.png")
BACKGROUND_IMAGE = p.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))


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


def draw_button(text, font, x, y, width, height, hover, clicked, screen):
    if hover:
        width += 20
        height += 20
    if clicked:
        width -= 10
        height -= 10

    rect = p.Rect(x - width // 2, y - height // 2, width, height)
    p.draw.rect(screen, (123, 6, 158), rect)
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.centery - text_surface.get_height() // 2))
    return rect



def drawMenu(screen):
    global BACKGROUND_IMAGE
    running = True
    font = p.font.SysFont("comicsans", 50, True)
    title_font = p.font.SysFont("comicsans", 180, True)
    creators_font = p.font.SysFont("comicsans", 20, True)
    copyright_font = p.font.SysFont("arial", 20)  # Telif yazısı için font

    play_button = None
    settings_button = None
    exit_button = None

    while running:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)

        # CHESSY Başlık
        title_surface = title_font.render('CHESSY', True, (255, 255, 255))
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, SCREEN_HEIGHT // 10))

        mouse_pos = p.mouse.get_pos()

        # Butonları çiz
        play_button = draw_button('Play', font, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, 200, 100, play_button and play_button.collidepoint(mouse_pos), False, screen)
        settings_button = draw_button('Settings', font, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, 200, 100, settings_button and settings_button.collidepoint(mouse_pos), False, screen)
        exit_button = draw_button('Exit', font, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 190, 200, 100, exit_button and exit_button.collidepoint(mouse_pos), False, screen)

        # The Creators Bölümü
        creators_title = creators_font.render("The creators of Chessy:", True, (255, 255, 0))
        screen.blit(creators_title, (20, 20))

        names = ["Müslüm Selim Aksahin", "Azra Özdas", "Dilay Tarhan"]
        y_offset = 60
        for name in names:
            name_surface = creators_font.render(f"- {name}", True, (255, 255, 0))
            screen.blit(name_surface, (40, y_offset))
            y_offset += 30

        # Telif Hakkı (Copyright) Metni
        copyright_surface = copyright_font.render(
            "© 2025 King's Gambit Team. All rights reserved.",
            True,
            (200, 200, 200)
        )
        copyright_x = (SCREEN_WIDTH // 2) - (copyright_surface.get_width() // 2)
        copyright_y = SCREEN_HEIGHT - 5  # Ekranın altından 30 piksel yukarı
        screen.blit(copyright_surface, (copyright_x, copyright_y))

        p.display.flip()

        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.VIDEORESIZE:
                screen = p.display.set_mode((event.w, event.h), p.FULLSCREEN)
                BACKGROUND_IMAGE = p.transform.scale(p.image.load("images/backgroundphoto.png"), (event.w, event.h))
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        # Buton tıklamalarını kontrol et
        if play_button.collidepoint(mouse_pos) and mouse_click:
            startButtonAnimation(screen, play_button)
            from ChessStarter import start_game
            start_game()
            return

        if settings_button and settings_button.collidepoint(mouse_pos) and mouse_click:
            click_sound.play()
            from ChessSettings import settingsScreen
            settingsScreen()
            return

        elif exit_button.collidepoint(mouse_pos) and mouse_click:
            click_sound.play()
            p.quit()
            sys.exit()

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



def mainMenu():
    screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.FULLSCREEN)
    drawMenu(screen)


if __name__ == "__main__":
    mainMenu()  # `mainMenu()` işlevi çağrılır.
