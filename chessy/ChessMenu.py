import random
import sys
import pygame as p
from chessy import ChessGlobals

p.init()
p.mixer.init()

# SFX yüklemesi
if ChessGlobals.is_sfx_on:
    click_sound = p.mixer.Sound("sounds/click.mp3")
    start_game_sound = p.mixer.Sound("sounds/piece-select.mp3")

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
    """Ekrana rastgele yıldızlar ekler."""
    for _ in range(count):
        stars.append({
            'x': x,
            'y': y,
            'dx': random.uniform(-3, 3),
            'dy': random.uniform(-3, 3),
            'size': random.randint(2, 5),
            'life': random.randint(40, 100)
        })


def fade_in(screen, background, duration=2000):
    """Arka planı kararmış hâlden görünür hâle getirir (fade-in)."""
    fade_surface = p.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    clock = p.time.Clock()
    alpha = 255
    start_time = p.time.get_ticks()

    while alpha > 0:
        elapsed_time = p.time.get_ticks() - start_time
        alpha = max(255 - (elapsed_time / duration) * 255, 0)
        fade_surface.set_alpha(alpha)
        screen.blit(background, (0, 0))
        screen.blit(fade_surface, (0, 0))
        p.display.flip()
        clock.tick(60)


def drawStars(screen):
    """Ekrandaki yıldızları çizer ve yaşam sürelerini günceller."""
    for star in stars:
        p.draw.circle(screen, (255, 255, 0), (int(star['x']), int(star['y'])), star['size'])
        star['x'] += star['dx']
        star['y'] += star['dy']
        star['life'] -= 1

    # Yaşamı sıfır olan yıldızları listeden çıkar
    for star in stars[:]:
        if star['life'] <= 0:
            stars.remove(star)


def play_menu_music():
    """Menüde sonsuz döngüde müzik çalar."""
    if ChessGlobals.is_sfx_on:
        p.mixer.music.load("sounds/menuchessysong.mp3")
        p.mixer.music.play(-1)


def stop_menu_music():
    """Menü müziğini durdurur."""
    p.mixer.music.stop()


def draw_button(text, font, x, y, width, height, hover, clicked, screen):
    """
    Ölçeklenebilir, eliptik bir buton çizer. 'hover' true ise buton biraz büyür,
    'clicked' true ise buton biraz küçülür (tıklama animasyonu).
    """
    scale_factor = SCREEN_HEIGHT / 1080
    width = int(width * scale_factor)
    height = int(height * scale_factor)

    # Hover efekti (büyütme)
    if hover:
        width += int(20 * scale_factor)
        height += int(20 * scale_factor)

    # Click animasyonu (küçültme)
    if clicked:
        width -= int(10 * scale_factor)
        height -= int(10 * scale_factor)

    rect = p.Rect(x - width // 2, y - height // 2, width, height)
    ellipse_surface = p.Surface((width, height), p.SRCALPHA)
    p.draw.ellipse(ellipse_surface, (123, 6, 158), (0, 0, width, height))
    screen.blit(ellipse_surface, (rect.x, rect.y))

    text_surface = font.render(text, True, (255, 255, 255))
    text_x = rect.centerx - text_surface.get_width() // 2
    text_y = rect.centery - text_surface.get_height() // 2
    screen.blit(text_surface, (text_x, text_y))

    return rect


def startButtonAnimation(screen, button, skip_loading=False):
    """Buton tıklanınca yıldız efekti ve isteğe bağlı 'Loading...' ekranı gösterir."""
    if ChessGlobals.is_sfx_on:
        click_sound.play()
    generateStars(button.centerx, button.centery)
    start_time = p.time.get_ticks()

    # 1 saniyelik yıldız efekti
    while p.time.get_ticks() - start_time < 1000:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)
        p.display.flip()
        p.time.Clock().tick(60)

    # Loading ekranı (skip_loading=False ise)
    if not skip_loading:
        screen.fill((0, 0, 0))
        loading_font = p.font.SysFont("comicsans", 60, True)
        loading_surface = loading_font.render("Loading...", True, (255, 255, 255))
        screen.blit(
            loading_surface,
            (
                (SCREEN_WIDTH // 2) - (loading_surface.get_width() // 2),
                (SCREEN_HEIGHT // 2) - (loading_surface.get_height() // 2)
            )
        )
        p.display.flip()
        p.time.wait(1000)


def drawMenu(screen):
    """
    Ana menüyü çizer. 'Play' butonuna basılınca alt menü (Play with Computer / Play with Friend) açılır.
    'Settings' ve 'Exit' butonları da bu menüde yer alır.
    Alt menüde ayrıca 'Return to Menu' butonu da olsun.
    """
    global BACKGROUND_IMAGE
    running = True
    submenu_open = False  # Alt menü başlangıçta kapalı
    scale_factor = SCREEN_HEIGHT / 1080

    # Yazı tipleri
    font = p.font.SysFont("comicsans", int(50 * scale_factor), True)
    title_font = p.font.SysFont("comicsans", int(180 * scale_factor), True)
    creators_font = p.font.SysFont("comicsans", int(20 * scale_factor), True)
    copyright_font = p.font.SysFont("arial", int(20 * scale_factor))

    button_width = 300
    button_height = 100
    vertical_spacing = int(50 * scale_factor)
    center_x = SCREEN_WIDTH // 2
    start_y = SCREEN_HEIGHT // 2 - ((button_height + vertical_spacing) * 0.5)

    # Ana menü buton referansları
    play_button = None
    settings_button = None
    exit_button = None

    # Alt menü buton referansları
    play_with_computer = None
    play_with_friend = None
    return_submenu_button = None  # <-- Yeni buton (Return to Menu)

    while running:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)

        # Başlık
        title_surface = title_font.render('CHESSY', True, (255, 255, 255))
        screen.blit(
            title_surface,
            (
                SCREEN_WIDTH // 2 - title_surface.get_width() // 2,
                SCREEN_HEIGHT // 10
            )
        )

        # The Creators
        creators_title = creators_font.render("The creators of Chessy:", True, (255, 255, 0))
        screen.blit(creators_title, (int(20 * scale_factor), int(20 * scale_factor)))

        names = ["Müslüm Selim Aksahin", "Azra Özdas", "Dilay Tarhan"]
        y_offset = int(60 * scale_factor)
        for name in names:
            name_surface = creators_font.render(f"- {name}", True, (255, 255, 0))
            screen.blit(name_surface, (int(40 * scale_factor), y_offset))
            y_offset += int(30 * scale_factor)

        # Telif Hakkı
        copyright_surface = copyright_font.render(
            "© 2025 King's Gambit Team. All rights reserved.",
            True,
            (200, 200, 200)
        )
        copyright_x = (SCREEN_WIDTH // 2) - (copyright_surface.get_width() // 2)
        copyright_y = SCREEN_HEIGHT - int(30 * scale_factor)
        screen.blit(copyright_surface, (copyright_x, copyright_y))

        # Mouse / tıklama kontrolü
        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        # ---------------- ANA MENÜ KISMI ----------------
        if not submenu_open:
            hovered_play_button = (play_button is not None and play_button.collidepoint(mouse_pos))
            hovered_settings_button = (settings_button is not None and settings_button.collidepoint(mouse_pos))
            hovered_exit_button = (exit_button is not None and exit_button.collidepoint(mouse_pos))

            # Ana menü butonlarını çiz
            play_button = draw_button(
                'Play', font,
                center_x, start_y,
                button_width, button_height,
                hovered_play_button,
                mouse_click,
                screen
            )
            settings_button = draw_button(
                'Settings', font,
                center_x, start_y + button_height + vertical_spacing,
                button_width, button_height,
                hovered_settings_button,
                mouse_click,
                screen
            )
            exit_button = draw_button(
                'Exit', font,
                center_x, start_y + 2 * (button_height + vertical_spacing),
                button_width, button_height,
                hovered_exit_button,
                mouse_click,
                screen
            )

            # Play butonuna tıklanınca alt menüyü aç
            if play_button and play_button.collidepoint(mouse_pos) and mouse_click:
                submenu_open = True

            # Settings butonu
            if settings_button and settings_button.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, settings_button, skip_loading=True)
                from ChessSettings import settingsScreen
                settingsScreen()
                return

            # Exit butonu
            if exit_button and exit_button.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, exit_button, skip_loading=True)
                p.quit()
                sys.exit()

            # ---------------- ALT MENÜ KISMI ----------------
        else:
            # Şeffaf arkaplan
            screen.blit(overlay, (0, 0))

            hovered_computer_button = (play_with_computer is not None and play_with_computer.collidepoint(mouse_pos))
            hovered_friend_button = (play_with_friend is not None and play_with_friend.collidepoint(mouse_pos))
            hovered_return_button = (
                        return_submenu_button is not None and return_submenu_button.collidepoint(mouse_pos))

            # Dikey konumları daha uzaklaştırmak için offseti büyütelim
            # Örn. 200 piksel arayla yerleştirelim
            offset = int(200 * scale_factor)

            # "Play with Computer" butonu (daha yukarı)
            play_with_computer = draw_button(
                "Play with Computer", font,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - offset,
                550, 120,
                hovered_computer_button,
                mouse_click,
                screen
            )

            # "Play with Friend" butonu (orta)
            play_with_friend = draw_button(
                "Play with Friend", font,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                550, 120,
                hovered_friend_button,
                mouse_click,
                screen
            )

            # "Return to Menu" butonu (daha aşağı)
            return_submenu_button = draw_button(
                "Return to Menu", font,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + offset,
                550, 120,
                hovered_return_button,
                mouse_click,
                screen
            )

            # "Play with Computer" tıklandı
            if play_with_computer and play_with_computer.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, play_with_computer)
                stop_menu_music()
                from ChessMain import main
                main(player_one=True, player_two=False)  # Beyaz insan, siyah bilgisayar
                running = False

            # "Play with Friend" tıklandı
            if play_with_friend and play_with_friend.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, play_with_friend)
                stop_menu_music()
                from ChessMain import main
                main()  # İki taraf da insan
                running = False

            # "Return to Menu" tıklandı
            if return_submenu_button and return_submenu_button.collidepoint(mouse_pos) and mouse_click:
                # Alt menüyü kapat, ana menüye dön
                submenu_open = False

        p.display.flip()  # Ekranı güncelle

    # while running döngüsünün sonu


def mainMenu(first_time=False):
    """
    Ana menüyü başlatır. Ekran boyutu ayarlanır, menü müziği yönetilir.
    """
    screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.FULLSCREEN)
    p.mixer.music.stop()

    if first_time:
        fade_in(screen, BACKGROUND_IMAGE)
        if ChessGlobals.is_sfx_on:
            play_menu_music()
    else:
        if not p.mixer.music.get_busy():
            play_menu_music()

    drawMenu(screen)

##