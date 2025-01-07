import random
import sys
import pygame as p
from chessy import ChessGlobals
from ChessConstants import screen

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
    for star in stars:
        p.draw.circle(screen, (255, 255, 0), (int(star['x']), int(star['y'])), star['size'])
        star['x'] += star['dx']
        star['y'] += star['dy']
        star['life'] -= 1
    for star in stars[:]:
        if star['life'] <= 0:
            stars.remove(star)

def play_menu_music():
    if ChessGlobals.is_sfx_on:
        p.mixer.music.load("sounds/menuchessysong.mp3")
        p.mixer.music.set_volume(0.02)
        p.mixer.music.play(-1)

def stop_menu_music():
    p.mixer.music.stop()

def draw_button(text, font, x, y, width, height, hover, clicked, screen):
    scale_factor = SCREEN_HEIGHT / 1080
    width = int(width * scale_factor)
    height = int(height * scale_factor)


    if hover and p.Rect(x - width // 2, y - height // 2, width, height).collidepoint(p.mouse.get_pos()):
        width += int(20 * scale_factor)
        height += int(20 * scale_factor)

    if clicked and p.Rect(x - width // 2, y - height // 2, width, height).collidepoint(p.mouse.get_pos()):
        width -= int(10 * scale_factor)
        height -= int(10 * scale_factor)

    rect = p.Rect(x - width // 2, y - height // 2, width, height)
    p.draw.rect(screen, (123, 6, 158), rect, border_radius=10)

    text_surface = font.render(text, True, (255, 255, 255))
    text_x = rect.centerx - text_surface.get_width() // 2
    text_y = rect.centery - text_surface.get_height() // 2
    screen.blit(text_surface, (text_x, text_y))

    return rect

def startButtonAnimation(screen, button, skip_loading=False):
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
        loading_font = p.font.SysFont("Times New Roman", 60, True)
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
                if current_line:
                    wrapped_lines.append(current_line)
                current_line = word
        if current_line:
            wrapped_lines.append(current_line)
        return wrapped_lines
    if title:
        wrapped_title_lines = wrap_text(title, big_font, box_rect.width - margin * 2)
    else:
        wrapped_title_lines = []
    max_text_width = box_rect.width - margin * 2
    wrapped_lines = wrap_lines(lines, small_font, max_text_width)
    max_lines = (box_rect.height - 2 * margin - len(wrapped_title_lines) * (big_font.get_height() + 5)) // (small_font.get_height() + 5)
    if len(wrapped_lines) > max_lines:
        wrapped_lines = wrapped_lines[:max_lines]
        if wrapped_lines:
            wrapped_lines[-1] += "..."

    line_spacing = small_font.get_height() + 5
    previous_clip = surface.get_clip()
    surface.set_clip(box_rect)

    current_y = box_rect.y + margin
    for title_line in wrapped_title_lines:
        title_surf = big_font.render(title_line, True, (255, 255, 255))
        surface.blit(title_surf, (box_rect.x + margin, current_y))
        current_y += big_font.get_height() + 5

    if title:
        current_y += 10

    for w_line in wrapped_lines:
        line_surf = small_font.render(w_line, True, (75, 0, 130))
        surface.blit(line_surf, (box_rect.x + margin, current_y))
        current_y += line_spacing

    surface.set_clip(previous_clip)

class Card:
    def __init__(self, title, lines, base_x, base_y, width, height, big_font, small_font):
        self.title = title
        self.lines = lines
        self.base_x = base_x
        self.base_y = base_y
        self.width = width
        self.height = height
        self.big_font = big_font
        self.small_font = small_font
        self.is_flipped = False
        self.rect = p.Rect(self.base_x, self.base_y, self.width, self.height)

    def draw(self, surface, scroll_offset):
        current_y = self.base_y - scroll_offset
        self.rect.topleft = (self.base_x, current_y)

        invisible_limit_y = 200

        if current_y < invisible_limit_y:
            return

        if self.is_flipped:
            p.draw.rect(surface, (200, 100, 255), self.rect, border_radius=15)
            draw_text_in_box(surface, "", self.lines, self.rect, self.big_font, self.small_font)
        else:
            p.draw.rect(surface, (123, 6, 158), self.rect, border_radius=15)
            wrapped_title = wrap_lines([self.title], self.big_font, self.width - 40)
            current_y_text = self.rect.y + 20
            for line in wrapped_title:
                title_surf = self.big_font.render(line, True, (255, 255, 255))
                title_x = self.rect.centerx - title_surf.get_width() // 2
                surface.blit(title_surf, (title_x, current_y_text))
                current_y_text += self.big_font.get_height() + 5

    def handle_event(self, event, mouse_pos):
        if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_flipped = not self.is_flipped

    def is_visible(self, scroll_offset, screen_height):
        # Kartın görünür olup olmadığını kontrol eder
        card_top = self.base_y - scroll_offset
        card_bottom = self.base_y + self.height - scroll_offset
        return not (card_bottom < 0 or card_top > screen_height)

def drawMenu(screen):
    global BACKGROUND_IMAGE
    running = True
    submenu_open = False
    scale_factor = SCREEN_HEIGHT / 1080

    font = p.font.SysFont("Times New Roman", int(50 * scale_factor), True)
    title_font = p.font.SysFont("Times New Roman", int(180 * scale_factor), True)
    creators_font = p.font.SysFont("Times New Roman", int(20 * scale_factor), True)
    copyright_font = p.font.SysFont("Times New Roman", int(20 * scale_factor))

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
    control_button = None

    play_with_computer = None
    play_with_friend = None
    return_submenu_button = None

    while running:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        drawStars(screen)

        title_font_surf = title_font.render('CHESSY', True, (255, 255, 255))
        screen.blit(
            title_font_surf,
            (
                SCREEN_WIDTH // 2 - title_font_surf.get_width() // 2,
                SCREEN_HEIGHT // 10
            )
        )

        creators_title = creators_font.render("The creators of Chessy:", True, (255, 255, 0))
        screen.blit(creators_title, (int(20 * scale_factor), int(20 * scale_factor)))

        names = ["Müslüm Selim Aksahin", "Azra Özdas", "Dilay Tarhan"]
        y_offset = int(60 * scale_factor)
        for name in names:
            name_surface = creators_font.render(f"- {name}", True, (255, 255, 0))
            screen.blit(name_surface, (int(40 * scale_factor), y_offset))
            y_offset += int(30 * scale_factor)

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
            control_button_x = int(SCREEN_WIDTH * 0.90)
            control_button_y = int(SCREEN_HEIGHT * 0.90)

            control_button = draw_button(
                'Controls', font,
                control_button_x, control_button_y,
                button_width, button_height,
                control_button.collidepoint(mouse_pos) if control_button else False,
                mouse_click,
                screen
            )

            if control_button and control_button.collidepoint(mouse_pos) and mouse_click:
                startButtonAnimation(screen, control_button, skip_loading=True)
                ControlScreen(screen)

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

def ControlScreen(screen):
    running = True
    clock = p.time.Clock()
    font = p.font.SysFont("Times New Roman", 90, True)  # Başlık fontu büyütüldü
    small_font = p.font.SysFont("Times New Roman", 50)

    background_image = p.image.load("images/controlscreen1.jpg")
    background_image = p.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    title_color = (138, 43, 226)  # Purple (Title color)
    control_color = (255, 255, 0)  # Yellow (Control text color)

    scale_factor = SCREEN_HEIGHT / 1080
    button_width = 550
    button_height = 120

    while running:
        screen.blit(background_image, (0, 0))
        text_y = 250

        title_surface = font.render("Control Guide", True, title_color)
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 50))

        controls = [
            "Z - Undo",
            "R - Restart",
            "Left Click - Select piece/button"
        ]

        for control in controls:
            control_surface = small_font.render(control, True, control_color)
            screen.blit(control_surface, (SCREEN_WIDTH // 2 - control_surface.get_width() // 2, text_y))
            text_y += 80

        # "Return to Menu" butonu
        button_x = SCREEN_WIDTH // 2
        button_y = SCREEN_HEIGHT - 150

        mouse_pos = p.mouse.get_pos()
        hovered_return = p.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        ).collidepoint(mouse_pos)

        return_button = draw_button(
            'Return to Menu', small_font,
            button_x, button_y,
            button_width, button_height,
            hovered_return,
            p.mouse.get_pressed()[0],
            screen
        )

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN:
                if return_button.collidepoint(mouse_pos):
                    running = False

        p.display.flip()
        clock.tick(60)

def learnScreen(screen):
    running = True
    clock = p.time.Clock()

    button_width = 300
    button_height = 100
    scale_factor = SCREEN_HEIGHT / 1080

    font_return = p.font.SysFont("Times New Roman", int(50 * scale_factor), True)
    return_x = int(SCREEN_WIDTH * 0.10)
    return_y = int(SCREEN_HEIGHT * 0.08)
    return_button_rect = None

    title_font = p.font.SysFont("Times New Roman", int(100 * scale_factor), True)  # Büyütülmüş başlık fontu
    card_title_font = p.font.SysFont("Times New Roman", int(40 * scale_factor), True)  # Kart başlık fontu
    line_font = p.font.SysFont("Times New Roman", int(20 * scale_factor), True)

    background_image = p.image.load("images/learnscreen1.jpg")
    background_image = p.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    box_data = [
        {"title": "ITALIAN GAME", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn e7 to e5",
            "2. White knight g1 to f3",
            "2...Black knight b8 to c6",
            "3. White bishop f1 to c4"]},
        {"title": "RUY LÓPEZ (SPANISH OPENING)", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn e7 to e5",
            "2. White knight g1 to f3",
            "2...Black knight b8 to c6",
            "3. White bishop f1 to b5"]},
        {"title": "SICILIAN DEFENSE", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn c7 to c5"]},
        {"title": "FRENCH DEFENSE", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn e7 to e6",
            "2. White pawn d2 to d4",
            "2...Black pawn d7 to d5"]},
        {"title": "QUEEN'S GAMBIT", "lines": [
            "1. White pawn d2 to d4",
            "1...Black pawn d7 to d5",
            "2. White pawn c2 to c4"]},
        {"title": "KING'S INDIAN DEFENSE", "lines": [
            "1. White pawn d2 to d4",
            "1...Black pawn g7 to g6",
            "2. White pawn c2 to c4",
            "2...Black knight g8 to f6"]},
        {"title": "CARO-KANN DEFENSE", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn c7 to c6",
            "2. White pawn d2 to d4",
            "2...Black pawn d7 to d5"]},
        {"title": "ENGLISH OPENING", "lines": [
            "1. White pawn c2 to c4"]},
        {"title": "PIRČ DEFENSE", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn e7 to e5",
            "2. White knight g1 to f3",
            "2...Black knight g8 to f6",
            "3. White pawn d2 to d3"]},
        {"title": "SCOTCH GAME", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn e7 to e5",
            "2. White knight g1 to f3",
            "2...Black knight b8 to c6",
            "3. White pawn d2 to d4"]},
        {"title": "NIMZO-INDIAN DEFENSE", "lines": [
            "1. White pawn d2 to d4",
            "1...Black knight g8 to f6",
            "2. White pawn c2 to c4",
            "2...Black bishop f8 to b4"]},
        {"title": "ALEKHINE DEFENSE", "lines": [
            "1. White pawn e2 to e4",
            "1...Black knight g8 to f6"]},
        {"title": "GRÜNFELD DEFENSE", "lines": [
            "1. White pawn d2 to d4",
            "1...Black knight g8 to f6",
            "2. White pawn c2 to c4",
            "2...Black pawn d7 to d5"]},
        {"title": "BENONI DEFENSE", "lines": [
            "1. White pawn d2 to d4",
            "1...Black pawn c7 to c5",
            "2. White pawn d4 to d5",
            "2...Black pawn e7 to e6"]},
        {"title": "CATALAN OPENING", "lines": [
            "1. White pawn d2 to d4",
            "1...Black pawn d7 to d5",
            "2. White pawn c2 to c4",
            "2...Black pawn e7 to e6",
            "3. White bishop f1 to g2"]},
        {"title": "LONDON SYSTEM", "lines": [
            "1. White pawn d2 to d4",
            "1...Black pawn d7 to d5",
            "2. White bishop c1 to f4"]},
        {"title": "EVANS GAMBIT", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn e7 to e5",
            "2. White knight g1 to f3",
            "2...Black knight b8 to c6",
            "3. White bishop f1 to c4",
            "3...Black pawn b7 to b5"]},
        {"title": "SCANDINAVIAN DEFENSE", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn d7 to d5"]},
        {"title": "KING'S GAMBIT", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn e7 to e5",
            "2. White pawn f2 to f4"]},
        {"title": "TARRASCH DEFENSE", "lines": [
            "1. White pawn d2 to d4",
            "1...Black pawn d7 to d5",
            "2. White pawn c2 to c4",
            "2...Black pawn e7 to e6",
            "3. White knight b1 to c3",
            "3...Black pawn c7 to c5"]},
        {"title": "VIENNA GAME", "lines": [
            "1. White pawn e2 to e4",
            "1...Black pawn e7 to e5",
            "2. White knight b1 to c3"]},
    ]

    spacing = int(60 * scale_factor)
    rect_width = int(380 * scale_factor)
    rect_height = int(250 * scale_factor)
    columns = 3
    margin_x = (SCREEN_WIDTH - (columns * rect_width + (columns - 1) * spacing)) // 2
    rect_x_left = margin_x
    rect_x_center = margin_x + rect_width + spacing
    rect_x_right = margin_x + 2 * (rect_width + spacing)
    start_y_offset = return_y + button_height + int(60 * scale_factor)
    max_scroll = max((len(box_data) + columns - 1) // columns * (rect_height + spacing) + start_y_offset - SCREEN_HEIGHT, 0)

    invisible_limit_y = return_y + button_height + 20

    scrollbar_color = (200, 50, 255)
    scroll_knob_color = (130, 50, 180)

    scroll_offset = 0

    cards = []
    for i, box in enumerate(box_data):
        column = i % columns
        row = i // columns
        if column == 0:
            x = rect_x_left
        elif column == 1:
            x = rect_x_center
        else:
            x = rect_x_right
        y = start_y_offset + row * (rect_height + spacing)
        card = Card(
            title=box["title"],
            lines=box["lines"],
            base_x=x,
            base_y=y,
            width=rect_width,
            height=rect_height,
            big_font=card_title_font,
            small_font=line_font
        )
        cards.append(card)

    def draw_scrollbar():
        if max_scroll == 0:
            return
        bar_height = max(50, int(SCREEN_HEIGHT * 0.2))
        scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
        bar_pos = int((SCREEN_HEIGHT - bar_height) * scroll_ratio)
        p.draw.rect(screen, scrollbar_color, (SCREEN_WIDTH - 20, 0, 16, SCREEN_HEIGHT))
        p.draw.rect(screen, scroll_knob_color, (SCREEN_WIDTH - 20, bar_pos, 16, bar_height))

    scroll_velocity = 0  # Scroll hızını kontrol etmek için

    while running:
        screen.blit(background_image, (0, 0))

        title_surf = title_font.render("OPENINGS", True, (255, 255, 255))
        black_outline = title_font.render("OPENINGS", True, (0, 0, 0))
        screen.blit(black_outline,
                    ((SCREEN_WIDTH // 2) - (black_outline.get_width() // 2) + 3, int(20 * scale_factor) + 3))
        screen.blit(title_surf, ((SCREEN_WIDTH // 2) - (title_surf.get_width() // 2), int(20 * scale_factor)))

        mouse_pos = p.mouse.get_pos()
        mouse_click = False
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True
                for card in cards:
                    card.handle_event(event, mouse_pos)
                if return_button_rect and return_button_rect.collidepoint(mouse_pos):
                    if ChessGlobals.is_sfx_on:
                        click_sound.play()
                    p.time.wait(300)
                    running = False
            elif event.type == p.MOUSEWHEEL:
                scroll_velocity += event.y * -5  # Daha küçük adımlarla güncelleyin

        # Scroll işlemini yavaşlat ve yumuşat
        scroll_velocity *= 0.9  # Hızı yavaşlat
        scroll_offset += scroll_velocity
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        # Sadece görünen kartları çizin
        visible_cards = [card for card in cards if card.is_visible(scroll_offset, SCREEN_HEIGHT)]
        for card in visible_cards:
            card.draw(screen, scroll_offset)

        draw_scrollbar()

        hovered_return_button = False
        if return_button_rect:
            hovered_return_button = return_button_rect.collidepoint(mouse_pos)

        return_button_rect = draw_button(
            'Return',
            font_return,
            return_x, return_y,
            button_width, button_height,
            hovered_return_button,
            mouse_click,
            screen
        )

        p.display.flip()
        clock.tick(60)

def mainMenu(first_time=False):
    p.mixer.music.stop()

    if first_time:
        fade_in(screen, BACKGROUND_IMAGE)
        if ChessGlobals.is_sfx_on:
            play_menu_music()
    else:
        if not p.mixer.music.get_busy():
            play_menu_music()

    drawMenu(screen)

if __name__ == "__main__":
    mainMenu(first_time=True)
#