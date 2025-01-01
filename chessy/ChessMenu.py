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

neon_circles = [
    {'x': SCREEN_WIDTH // 4, 'y': SCREEN_HEIGHT // 3, 'radius': 150, 'color': (255, 0, 255)},
    {'x': SCREEN_WIDTH // 2, 'y': SCREEN_HEIGHT // 2, 'radius': 200, 'color': (0, 255, 255)},
]

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
        p.mixer.music.set_volume(0.02)
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
    stars.clear()

    if ChessGlobals.is_sfx_on:
        click_sound.play()

    generateStars(button.centerx, button.centery)
    start_time = p.time.get_ticks()

    while p.time.get_ticks() - start_time < 1000:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)
        p.display.flip()
        p.time.Clock().tick(60)

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
    'Settings' ve 'Exit' butonları ortada, 'Learn' butonu sağ üst köşede olacak.
    """
    global BACKGROUND_IMAGE
    running = True
    submenu_open = False
    scale_factor = SCREEN_HEIGHT / 1080

    font = p.font.SysFont("comicsans", int(50 * scale_factor), True)
    title_font = p.font.SysFont("comicsans", int(180 * scale_factor), True)
    creators_font = p.font.SysFont("comicsans", int(20 * scale_factor), True)
    copyright_font = p.font.SysFont("arial", int(20 * scale_factor))

    button_width = 300
    button_height = 100
    vertical_spacing = int(50 * scale_factor)

    center_x = SCREEN_WIDTH // 2
    middle_button_y = SCREEN_HEIGHT // 2

    play_button_y = middle_button_y - (button_height + vertical_spacing)
    settings_button_y = middle_button_y
    exit_button_y = middle_button_y + (button_height + vertical_spacing)

    play_button = None
    settings_button = None
    exit_button = None

    play_with_computer = None
    play_with_friend = None
    return_submenu_button = None

    while running:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)

        # Başlık
        title_font_surf = title_font.render('CHESSY', True, (255, 255, 255))
        screen.blit(
            title_font_surf,
            (
                SCREEN_WIDTH // 2 - title_font_surf.get_width() // 2,
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
        copy_surf = copyright_font.render(
            "© 2025 King's Gambit Team. All rights reserved.",
            True,
            (200, 200, 200)
        )
        copy_x = (SCREEN_WIDTH // 2) - (copy_surf.get_width() // 2)
        copy_y = SCREEN_HEIGHT - int(30 * scale_factor)
        screen.blit(copy_surf, (copy_x, copy_y))

        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        learn_button_x = int(SCREEN_WIDTH * 0.90)
        learn_button_y = int(SCREEN_HEIGHT * 0.10)
        hovered_learn_button = False
        if 'learn_button' in locals():
            hovered_learn_button = learn_button.collidepoint(mouse_pos) if learn_button else False

        learn_button = draw_button(
            'Learn', font,
            learn_button_x, learn_button_y,
            button_width, button_height,
            hovered_learn_button,
            mouse_click,
            screen
        )
        if learn_button and learn_button.collidepoint(mouse_pos) and mouse_click:
            startButtonAnimation(screen, learn_button, skip_loading=True)
            learnScreen(screen)

        if not submenu_open:
            hovered_play_button = (play_button is not None and play_button.collidepoint(mouse_pos))
            hovered_settings_button = (settings_button is not None and settings_button.collidepoint(mouse_pos))
            hovered_exit_button = (exit_button is not None and exit_button.collidepoint(mouse_pos))

            play_button = draw_button(
                'Play', font,
                center_x, play_button_y,
                button_width, button_height,
                hovered_play_button,
                mouse_click,
                screen
            )
            settings_button = draw_button(
                'Settings', font,
                center_x, settings_button_y,
                button_width, button_height,
                hovered_settings_button,
                mouse_click,
                screen
            )
            exit_button = draw_button(
                'Exit', font,
                center_x, exit_button_y,
                button_width, button_height,
                hovered_exit_button,
                mouse_click,
                screen
            )

            if play_button and play_button.collidepoint(mouse_pos) and mouse_click:
                submenu_open = True

            if settings_button and settings_button.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, settings_button, skip_loading=True)
                from ChessSettings import settingsScreen
                settingsScreen()
                return

            if exit_button and exit_button.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, exit_button, skip_loading=True)
                p.quit()
                sys.exit()

        else:
            screen.blit(overlay, (0, 0))

            hovered_computer_button = (play_with_computer is not None and play_with_computer.collidepoint(mouse_pos))
            hovered_friend_button = (play_with_friend is not None and play_with_friend.collidepoint(mouse_pos))
            hovered_return_button = (return_submenu_button is not None and return_submenu_button.collidepoint(mouse_pos))

            offset = int(200 * scale_factor)

            play_with_computer = draw_button(
                "Play with Computer", font,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - offset,
                550, 120,
                hovered_computer_button,
                mouse_click,
                screen
            )
            play_with_friend = draw_button(
                "Play with Friend", font,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                550, 120,
                hovered_friend_button,
                mouse_click,
                screen
            )
            return_submenu_button = draw_button(
                "Return to Menu", font,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + offset,
                550, 120,
                hovered_return_button,
                mouse_click,
                screen
            )

            if play_with_computer and play_with_computer.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, play_with_computer)
                stop_menu_music()
                from ChessMain import main
                main(player_one=True, player_two=False)
                running = False

            if play_with_friend and play_with_friend.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, play_with_friend)
                stop_menu_music()
                from ChessMain import main
                main()
                running = False

            if return_submenu_button and return_submenu_button.collidepoint(mouse_pos) and mouse_click:
                submenu_open = False

        p.display.flip()

    # while running sonu

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

# ========================== YENİ EKLEMELER ==========================
def draw_text_in_box(surface, title, lines, box_rect, big_font, small_font, margin=20):
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        wrapped_lines = []
        current_line = ''

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = word
        wrapped_lines.append(current_line)
        return wrapped_lines

    # Metni kutunun genişliğine göre satırlara ayır
    wrapped_title_lines = wrap_text(title, big_font, box_rect.width - margin * 2)

    max_text_width = box_rect.width - margin * 2
    wrapped_lines = wrap_lines(lines, small_font, max_text_width)

    line_spacing = small_font.get_height() + 5
    total_height = (
            len(wrapped_title_lines) * (big_font.get_height() + 5) +
            (len(wrapped_lines) * line_spacing) + margin * 2
    )
    box_rect.height = max(total_height, 100)

    # Kutuyu çiz
    p.draw.rect(surface, (123, 6, 158), box_rect, border_radius=15)

    # Başlığı çok satırlı olarak yazdır
    current_y = box_rect.y + margin
    for title_line in wrapped_title_lines:
        title_surf = big_font.render(title_line, True, (255, 255, 255))
        surface.blit(title_surf, (box_rect.x + margin, current_y))
        current_y += big_font.get_height() + 5

    # İçerik satırlarını yazdır
    current_y += 10  # Başlık ve içerik arasına boşluk bırak
    for w_line in wrapped_lines:
        line_surf = small_font.render(w_line, True, (255, 255, 255))
        surface.blit(line_surf, (box_rect.x + margin, current_y))
        current_y += line_spacing


# Metni kutu içine sığdıran yardımcı fonksiyon
def wrap_lines(lines, font, max_width):
    wrapped = []
    for line in lines:
        words = line.split()
        current_line = ""
        for word in words:
            test_line = (current_line + " " + word).strip() if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    wrapped.append(current_line)
                current_line = word
        if current_line:
            wrapped.append(current_line)
    return wrapped

# Öğrenme ekranı fonksiyonu
def learnScreen(screen):
    running = True
    clock = p.time.Clock()

    button_width = 300
    button_height = 100
    scale_factor = SCREEN_HEIGHT / 1080

    font_return = p.font.SysFont("comicsans", int(50 * scale_factor), True)
    return_x = int(SCREEN_WIDTH * 0.10)
    return_y = int(SCREEN_HEIGHT * 0.08)
    return_button_rect = None

    title_font = p.font.SysFont("comicsans", int(100 * scale_factor), True)
    line_font = p.font.SysFont("comicsans", int(25 * scale_factor), False)

    background_image = p.image.load("images/backgroundphoto1.jpg")
    background_image = p.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    box_data = [
        {"title": "ITALİAN GAME", "lines": ["1, W"]},
        {"title": "İTALIAN GAME", "lines": ["White pawn e2 to e4", "1... Black pawn e7 to e5", "White knight g1 to f3", "2... Black knight b8 to c6", "White bishop f1 to c4"]},
        {"title": "SİCİLYA SAVUNMASI", "lines": ["e4 – Beyaz piyonunu merkeze sürer.", "c5 – Siyah, piyonunu c5’e sürer."]},
        {"title": "CARO-KANN SAVUNMASI", "lines": ["e4 – Beyaz merkeze oynar.", "c6 – Siyah, piyonunu c6’ya sürer."]},
        {"title": "FRANSIZ SAVUNMASI", "lines": ["e4 – Beyaz piyonunu e4’e sürer.", "e6 – Siyah, piyonunu e6’ya oynar."]},
        {"title": "İSKANDİNAV SAVUNMASI", "lines": ["e4 – Beyaz merkeze oynar.", "d5 – Siyah, piyonunu d5’e sürer."]}
    ]

    spacing = int(50 * scale_factor)
    rect_width = int(500 * scale_factor)
    rect_height = int(50 * scale_factor)
    rect_x_center = SCREEN_WIDTH // 2 - rect_width // 2
    rect_x_left = rect_x_center - rect_width - spacing
    rect_x_right = rect_x_center + rect_width + spacing
    scroll_offset = 0
    start_y_offset = return_y + button_height + int(50 * scale_factor)
    max_scroll = len(box_data) // 3 * 350 - SCREEN_HEIGHT // 2 + start_y_offset
    invisible_limit_y = return_y + button_height + 20

    def draw_scrollbar():
        bar_height = max(50, SCREEN_HEIGHT * (SCREEN_HEIGHT / (len(box_data) * 120)))
        bar_pos = (SCREEN_HEIGHT - bar_height) * (scroll_offset / max_scroll if max_scroll > 0 else 0)
        p.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH - 30, bar_pos, 20, bar_height))

    while running:
        screen.blit(background_image, (0, 0))
        mouse_pos = p.mouse.get_pos()
        mouse_click = False
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True
            elif event.type == p.MOUSEWHEEL:
                scroll_offset -= event.y * 50
                scroll_offset = max(0, min(scroll_offset, max_scroll))

        # OPENINGS Başlığı Ekleme
        title_surf = title_font.render("OPENINGS", True, (255, 255, 255))
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, int(20 * scale_factor)))

        for i, box in enumerate(box_data):
            x = [rect_x_left, rect_x_center, rect_x_right][i % 3]
            y = (i // 3) * 350 - scroll_offset + start_y_offset
            if y > invisible_limit_y:
                draw_text_in_box(screen, box["title"], box["lines"], p.Rect(x, y, rect_width, 100), title_font, line_font)
        draw_scrollbar()

        hovered_return_button = (return_button_rect is not None and return_button_rect.collidepoint(mouse_pos))
        return_button_rect = draw_button(
            'Return',
            font_return,
            return_x, return_y,
            button_width, button_height,
            hovered_return_button,
            mouse_click,
            screen
        )

        if return_button_rect and return_button_rect.collidepoint(mouse_pos) and mouse_click:
            startButtonAnimation(screen, return_button_rect, skip_loading=True)
            running = False
            return  # Ekran güncellenmeden önce fonksiyondan çık

        p.display.flip()
        clock.tick(60)

