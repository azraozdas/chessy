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

def wrap_lines(lines, font, max_width):
    """
    Satırları 'max_width' içine sığacak şekilde kelime kelime böler.
    lines: Orijinal satır listesi
    font:  Yazıyı çizmekte kullandığımız font
    max_width: kutu içinde izin verdiğimiz max piksel genişlik
    """
    wrapped = []
    for line in lines:
        words = line.split()
        current_line = ""
        for word in words:
            test_line = (current_line + " " + word).strip() if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                wrapped.append(current_line)
                current_line = word
        if current_line:
            wrapped.append(current_line)
    return wrapped

def learnScreen(screen):
    """
    Learn ekranı: 'Return' butonu aynı oval stile sahip, tıklayınca animasyon + menüye dönüş.
    İçeride mor/pembe kutu çizip, başlık (büyük) + satırlar (küçük) ve
    satırları kutuya sığdırmak için wrap_lines yapıyoruz.
    """
    running = True
    clock = p.time.Clock()

    button_width = 300
    button_height = 100
    scale_factor = SCREEN_HEIGHT / 1080

    # Return butonu
    font_return = p.font.SysFont("comicsans", int(50 * scale_factor), True)
    return_x = int(SCREEN_WIDTH * 0.10)
    return_y = int(SCREEN_HEIGHT * 0.08)
    return_button_rect = None

    # İki farklı font: başlık, satır
    title_font = p.font.SysFont("comicsans", int(40 * scale_factor), True)
    line_font  = p.font.SysFont("comicsans", int(25 * scale_factor), False)

    # Örnek veriler
    bird_opening_title = "BİRD AÇILIŞI"
    bird_opening_lines = [
        "f4 – Beyaz, piyonunu f2’den f4’e sürerek merkeze dolaylı baskı yapar.",
        "d5 – Siyah, merkezi piyon d7’den d5’e sürerek karşılık verir. Bu aşamada siyah merkeze hakim olmak ister.",
        "Nf3 – Beyaz, atını g1’den f3’e getirir ve piyon f4'ü desteklemeye devam eder.",
        "g6 – Siyah, filini g7'ye geliştirmek için g6 sürer (fianchetto planı).",
        "g3 – Beyaz da benzer şekilde g2'ye filini yerleştirmek isteyebilir.",
        "Bg2 – Fil g2'de konumlanır ve çaprazdan merkeze baskı yapar.",
    ]

    # Kutunun boyutu
    rect_width = int(600 * scale_factor)
    rect_height = int(400 * scale_factor)
    rect_x = SCREEN_WIDTH // 2 - rect_width // 2
    rect_y = SCREEN_HEIGHT // 2 - rect_height // 2

    def draw_text_in_box(surface, title, lines, box_rect, big_font, small_font, margin=20):
        """
        'Temaya uygun' mor/pembe kutu çiz, üstüne başlık (büyük) + satır metinleri (küçük).
        Yazılar beyaz.
        """
        # 1) Kutuyu mor/pembe renkte çiz (örn. (123,6,158)) ve border_radius ekleyelim
        p.draw.rect(surface, (123, 6, 158), box_rect, border_radius=15)

        # 2) Başlık
        title_surf = big_font.render(title, True, (255, 255, 255))
        tx = box_rect.x + margin
        ty = box_rect.y + margin
        surface.blit(title_surf, (tx, ty))

        # 3) Satır metinleri: önce wrap
        max_text_width = box_rect.width - margin*2
        wrapped_lines = wrap_lines(lines, small_font, max_text_width)

        line_spacing = small_font.get_height() + 5
        current_y = ty + big_font.get_height() + 10

        for w_line in wrapped_lines:
            line_surf = small_font.render(w_line, True, (255,255,255))
            surface.blit(line_surf, (box_rect.x + margin, current_y))
            current_y += line_spacing

    while running:
        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        screen.fill((0, 0, 0))  # Arka plan siyah

        # Return butonu (oval)
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

        # Mor/pembe kutu + başlık + satır metinleri
        draw_text_in_box(
            screen,
            bird_opening_title,
            bird_opening_lines,
            p.Rect(rect_x, rect_y, rect_width, rect_height),
            title_font,
            line_font
        )

        p.display.flip()
        clock.tick(60)
