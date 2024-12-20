import pygame as p
import random
import sys

import os
import chessEngine  # chessEngine modülünü doğru bir şekilde içe aktardık

# Oyun Ayarları
p.init()
p.mixer.init()
check_sound = p.mixer.Sound("sounds/tension.MP3")
move_sound = p.mixer.Sound("sounds/move-pieces.mp3")
start_game_sound = p.mixer.Sound("sounds/game-start.mp3")
click_sound = p.mixer.Sound("sounds/click.mp3")
sound_on = True  # Ses varsayılan olarak açık

# 🔥 2️⃣ Ekran boyutunu (çözünürlüğü) alın
SCREEN_WIDTH = p.display.Info().current_w  # Mevcut ekran genişliği
SCREEN_HEIGHT = p.display.Info().current_h  # Mevcut ekran yüksekliği

# Ekranın %100'ini kaplayacak şekilde tahtayı ayarla
BOARD_WIDTH = int(SCREEN_WIDTH * 1)
BOARD_HEIGHT = int(SCREEN_HEIGHT * 1)

# Eğer tahtayı kare olarak tutmak isterseniz
BOARD_WIDTH = min(BOARD_WIDTH, BOARD_HEIGHT)
BOARD_HEIGHT = BOARD_WIDTH

MOVE_LOG_PANEL_WIDTH = int(BOARD_WIDTH * 0.25)
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Satranç tahtası 8x8'dir
SQUARE_SIZE = BOARD_WIDTH // DIMENSION
MAX_FPS = 120

# Ekranı oluştur
screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.FULLSCREEN)
p.display.set_caption('CHESSY')
clock = p.time.Clock()

# Renkler ve Offsetler
LIGHT_COLOR = (255, 102, 242)
DARK_COLOR = (123, 6, 158)
BACKGROUND_COLOR = (0, 0, 0)
X_OFFSET = 0
Y_OFFSET = 0

IMAGES = {}

# Yıldız animasyonu için liste
stars = []

# 🔥 Menünün arka plan fotoğrafı
BACKGROUND_IMAGE = p.image.load("images/backgroundphoto.png")
BACKGROUND_IMAGE = p.transform.scale(BACKGROUND_IMAGE, (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))

def play_sound(sound):
    """Sesleri kontrol eder. Eğer ses kapalıysa çalmaz."""
    if sound_on:
        sound.play()

# Görüntüleri yükle
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


# Yıldızları oluşturur
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


# Yıldızları çizer ve hareket ettirir
def drawStars():
    for star in stars:
        p.draw.circle(screen, (255, 255, 0), (int(star['x']), int(star['y'])), star['size'])
        star['x'] += star['dx']
        star['y'] += star['dy']
        star['life'] -= 1
    for star in stars[:]:
        if star['life'] <= 0:
            stars.remove(star)

# Ana menüyü çizer
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
            drawStars()  # Sadece Return to Menu'den gelinmediğinde yıldızları ekrana çiz

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
                drawStars()
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
                drawStars()
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
                drawStars()  # Yıldızları ekrana çiz
                p.display.flip()
                clock.tick(60)

            is_returning_from_game = False  # Return to Menu bayrağını sıfırla
            p.quit()
            sys.exit()


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
def settingsMenu():
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

def loadSounds():
    """Ses dosyalarını yükleyen fonksiyon."""
    global move_sound
    p.mixer.init()  # Pygame ses motorunu başlat
    check_sound = p.mixer.Sound("sounds/tension.MP3")  # Ses dosyasını yükle

# En üstte global değişkeni tanımlayın
is_returning_from_game = False  # Return to Menu'den dönüldüğünü kontrol eder
is_sfx_on = True  # Ses efekti açık mı kontrolü

def main():
    """Satranç oyununun ana döngüsü."""
    global screen, BOARD_WIDTH, BOARD_HEIGHT, SQUARE_SIZE  # Global değişkenler
    p.init()
    loadImages()
    loadSounds()  # 🎉 Sesleri yükle

    # Başlangıç ekran ayarları
    screen_width = p.display.Info().current_w
    screen_height = p.display.Info().current_h
    screen = p.display.set_mode((screen_width, screen_height), p.FULLSCREEN)  # Ekranı tam ekran yap
    p.display.set_caption('CHESSY')  # Pencere başlığı

    running = True
    game_state = chessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    square_selected = ()
    player_clicks = []
    game_over = False
    return_button = None  # Return to Menu butonunu başlat
    is_check = False  # Şah durumunu takip etmek için BAŞLANGIÇ DEĞERİ EKLENDİ
    settings_button = None  # Yeni Settings butonu
    clicked_settings = False

    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.VIDEORESIZE:  # Pencere boyutu değiştirildiğinde
                new_width = event.w - MOVE_LOG_PANEL_WIDTH
                new_height = event.h
                BOARD_WIDTH = BOARD_HEIGHT = min(new_width, new_height)
                SQUARE_SIZE = BOARD_WIDTH // DIMENSION
                screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.FULLSCREEN)
                loadImages()
            elif event.type == p.MOUSEBUTTONDOWN:  # Taş hareketlerini işleme
                mouse_pos = p.mouse.get_pos()

                if return_button and return_button.collidepoint(mouse_pos):
                    click_sound.play()  # 🔊 Click sesi ekleniyor
                    generateStars(return_button.centerx,
                                  return_button.centery)  # Yıldız animasyonu butonun ortasında başlat
                    start_time = p.time.get_ticks()
                    while p.time.get_ticks() - start_time < 1000:  # Yıldız animasyonu 1 saniye sürsün
                        screen.fill((0, 0, 0))  # Ekranı temizle (ana menüden bağımsız yıldızlar)
                        drawMoveLog(screen, [])  # Sadece return to menu kısmını çiz
                        drawStars()  # Yıldızları ekrana çiz
                        p.display.flip()
                        clock.tick(60)
                    mainMenu()  # Yıldız animasyonu tamamlandıktan sonra ana menüye dön
                    return  # Ana menüye dönmek için döngüyü sonlandır

                col = mouse_pos[0] // SQUARE_SIZE
                row = mouse_pos[1] // SQUARE_SIZE

                if 0 <= row < DIMENSION and 0 <= col < DIMENSION:
                    if square_selected == (row, col):
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)

                    if len(player_clicks) == 2:
                        move = chessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                move_sound.play()  # 🔊 Hareket sesi çalıyor
                                animateMove(move, game_state, screen, clock)
                                game_state.board[move.start_row][move.start_col] = "--"

                                if move.piece_captured != "--":
                                    celebratePiece(move.piece_moved, move.end_row, move.end_col, screen, clock,
                                                   game_state)

                                game_state.makeMove(valid_moves[i])

                                if move.getMoveSummary() not in game_state.move_log:
                                    game_state.move_log.append(move.getMoveSummary())

                                move_made = True
                                square_selected = ()
                                player_clicks = []
                                break
                        if not move_made:
                            player_clicks = [square_selected]

            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    game_state.undoMove()
                    move_made = True
                elif event.key == p.K_r:
                    game_state = chessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    game_over = False

        if move_made:
            valid_moves = game_state.getValidMoves()
            move_made = False

            # Şah durumunu kontrol et
            if game_state.inCheck():
                if not is_check:  # Şah durumu yeni başladıysa
                    check_sound.play()  # Şah sesini çal
                    is_check = True
            else:
                if is_check:  # Şah durumu sona erdiğinde
                    check_sound.stop()  # Şah sesini durdur
                    is_check = False

        drawGameState(screen, game_state, square_selected)
        return_button = drawMoveLog(screen, game_state.move_log)  # Hamle logunu ve butonu çiz
        p.display.flip()
        clock.tick(MAX_FPS)


def drawValidMoves(screen, moves):
    """Taşın geçerli hamlelerini ekrana çizen fonksiyon."""
    for move in moves:
        row, col = move.end_row, move.end_col

        if move.piece_captured != "--":
            color = (255, 186, 0)  # Taş yenebiliyorsa bu renk
        else:
            color = (110, 203, 245)  # Koyumsu cyan renk

        # Yeni bir yüzey (Surface) oluştur
        highlight_surface = p.Surface((SQUARE_SIZE, SQUARE_SIZE))  # Her kare için ayrı bir yüzey
        highlight_surface.set_alpha(150)  # Şeffaflık: 0 (tam şeffaf) - 255 (tam opak)
        highlight_surface.fill(color)  # Renk ayarı (ya sarı ya da mor)

        # Yüzeyi tahtanın doğru konumuna çiz
        screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def drawGameState(screen, game_state, square_selected):
    """Tahta ve taşları çizen fonksiyon."""
    drawBoard(screen)  # Tahtayı çiz
    drawPieces(screen, game_state.board)  # Taşları çiz

    if square_selected != ():  # Eğer bir taş seçildiyse
        row, col = square_selected
        if game_state.board[row][col] != "--":  # Seçilen kare boş değilse (taş varsa)
            piece_color = game_state.board[row][col][0]
            if (piece_color == 'w' and game_state.white_to_move) or (piece_color == 'b' and not game_state.white_to_move):
                valid_moves = [move for move in game_state.getValidMoves() if move.start_row == row and move.start_col == col]
                drawValidMoves(screen, valid_moves)  # Geçerli hamleleri sarıya renklendir

def drawBoard(screen):
    """Tahtanın arkaplanını çizen fonksiyon."""
    colors = [p.Color(255, 102, 242), p.Color(123, 6, 158)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawPieces(screen, board):
    """Tahtadaki taşları çizen fonksiyon."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def animateMove(move, game_state, screen, clock):
    """Taşı kayarak hareket ettirir."""
    frames_per_square = 10  # Her karede kaç piksel hareket
    start_row, start_col = move.start_row, move.start_col
    end_row, end_col = move.end_row, move.end_col
    piece = move.piece_moved

    # Hareket yönü
    d_row = end_row - start_row
    d_col = end_col - start_col

    for frame in range(frames_per_square * max(abs(d_row), abs(d_col))):
        row = start_row + d_row * (frame / (frames_per_square * max(abs(d_row), abs(d_col))))
        col = start_col + d_col * (frame / (frames_per_square * max(abs(d_row), abs(d_col))))

        # Tahtayı yeniden çiz
        drawBoard(screen)
        drawPieces(screen, game_state.board)

        # Eski kareyi temizleyip yeni konumu göster
        p.draw.rect(screen, DARK_COLOR if (start_row + start_col) % 2 else LIGHT_COLOR,
                    p.Rect(start_col * SQUARE_SIZE, start_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        # Taşı güncel konumuna kaydırarak çiz
        screen.blit(IMAGES[piece], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        p.display.flip()
        clock.tick(60)  # 60 FPS

    # Hareket bittiğinde taşın nihai konumunu güncelle
    game_state.board[start_row][start_col] = piece  # Eski konuma taşı geri koy (gerekli değil ama güvenlik amaçlı)

def drawShiningEffect(screen, x, y, frame):
    """Taşın etrafında parlayan bir büyük halka ve yıldızlar oluşturur."""
    max_radius = 80  # Halkanın maksimum yarıçapı (önceden 40 idi)
    transparency = max(0, 255 - frame * 6)  # Şeffaflık her karede azalt
    color = (255, 255, 0)  # Parlak sarı

    # Halka oluşturma (Saydam yüzey kullanıyoruz)
    radius = int(max_radius * (frame / 30))  # Halka büyür (30 karede tam büyüklüğe ulaşır)
    if radius > 0:
        halo_surface = p.Surface((radius * 2, radius * 2), p.SRCALPHA)  # Saydam yüzey
        p.draw.circle(halo_surface, (color[0], color[1], color[2], transparency), (radius, radius), radius, width=8)
        # Halka, taşın merkezine yerleştirilir
        screen.blit(halo_surface, (x - radius + SQUARE_SIZE // 2, y - radius + SQUARE_SIZE // 2))

    # Yıldız efektleri
    for i in range(10):  # 10 adet yıldız (önceden 5 idi)
        star_x = x + random.randint(-40, 40)  # Yıldızlar daha geniş alana yayılıyor
        star_y = y + random.randint(-40, 40)
        star_size = random.randint(3, 6)  # Yıldız boyutunu büyüttük
        p.draw.circle(screen, (255, 255, 0, transparency), (star_x, star_y), star_size)

def celebratePiece(piece, row, col, screen, clock, game_state):
    """Taş yediğinde sevinme efekti uygular (parlayan büyük halka ve yıldızlar)."""
    frames = 45  # Toplam animasyon süresi (30'dan 45'e çıkarıldı)
    x = X_OFFSET + col * SQUARE_SIZE
    y = Y_OFFSET + row * SQUARE_SIZE

    for frame in range(frames):
        drawBoard(screen)
        drawPieces(screen, game_state.board)  # Oyun tahtasını ve taşları çiziyoruz

        # Taşın üzerine çizilecek parlaklık ve yıldız efekti
        drawShiningEffect(screen, x, y, frame)

        # Taşı çiz (Bu kısımda taş ekranda kalır)
        screen.blit(IMAGES[piece], p.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))

        p.display.flip()
        clock.tick(60)  # 60 FPS animasyon

def drawMoveLog(screen, move_log):
    """Sağdaki siyah panelde hamle logunu düzgün şekilde yazdırır ve 'Return to Menu' butonunu çizer."""
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, (0, 0, 0), move_log_rect)  # Siyah paneli çiz

    # "Return to Menu" Butonu
    button_font = p.font.SysFont("comicsans", 20, True)
    original_button_width, original_button_height = 200, 100
    button_width, button_height = original_button_width, original_button_height  # Varsayılan boyut
    button_x = move_log_rect.x + (MOVE_LOG_PANEL_WIDTH // 2) - (button_width // 2)
    button_y = 10  # Panelin üst kısmına yerleştirme

    mouse_pos = p.mouse.get_pos()
    mouse_click = p.mouse.get_pressed()[0]  # Sol tıklama kontrolü

    # Buton hover ve click efektleri
    hover = p.Rect(button_x, button_y, button_width, button_height).collidepoint(mouse_pos)
    clicked = hover and mouse_click

    if hover:
        button_width = original_button_width - 10  # Boyutu küçült
        button_height = original_button_height - 10  # Boyutu küçült

    global is_returning_from_game  # Global bayrağı fonksiyonun başında tanımla
    if clicked:
        click_sound.play()  # 🔊 Click sesi çal
        generateStars(button_x + button_width // 2, button_y + button_height // 2)  # Yıldızları butonun merkezinde başlat
        start_time = p.time.get_ticks()
        while p.time.get_ticks() - start_time < 1000:  # Yıldız animasyonu 1 saniye sürsün
            screen.fill((0, 0, 0))  # Ekranı temizle
            drawStars()  # Yıldızları ekrana çiz
            p.display.flip()
            clock.tick(60)  # 60 FPS
            is_returning_from_game = True  # Return to Menu'den ana menüye dönüyoruz, bayrağı ayarla

        button_width = original_button_width  # Boyutu normale döndür
        button_height = original_button_height  # Boyutu normale döndür
        mainMenu()  # Ana menüye geç
        return  # Ana menüye dönmek için döngüyü sonlandır

    # Sabit merkezi korumak için X ve Y konumlarını buna göre ayarla
    centered_x = button_x + (original_button_width // 2) - (button_width // 2)
    centered_y = button_y + (original_button_height // 2) - (button_height // 2)

    return_button = p.Rect(centered_x, centered_y, button_width, button_height)
    p.draw.rect(screen, (123, 6, 158), return_button)  # Mor renkli buton
    text_surface = button_font.render("Return to Menu", True, (255, 255, 0))  # Sarı metin
    screen.blit(text_surface, (centered_x + (button_width // 2) - (text_surface.get_width() // 2),
                               centered_y + (button_height // 2) - (text_surface.get_height() // 2)))

    font = p.font.SysFont("comicsans", 10)  # Daha küçük bir font
    padding = 5  # Her hamle arasındaki boşluk
    text_y = centered_y + button_height + 10  # Butonun hemen altına hamlelerin başlaması için boşluk

    max_text_height = move_log_rect.height - text_y - padding  # Panelin yazı alanı yüksekliği
    line_height = font.get_height() + padding  # Her bir hamlenin yüksekliği
    max_lines = max_text_height // line_height  # Panelin içine sığabilecek maksimum hamle sayısı

    # Son sığabilecek hamleleri göster
    recent_moves = move_log[-max_lines:]

    for i, move in enumerate(recent_moves):  # Son hamleleri göster
        text_surface = font.render(move, True, (255, 255, 0))  # Sarı renk
        text_x = move_log_rect.centerx - text_surface.get_width() // 2  # Yatayda ortala
        screen.blit(text_surface, (text_x, text_y + i * (font.get_height() + padding)))

    return return_button  # Return to Menu butonunu döndür

if __name__ == "__main__":
    mainMenu()
    main()
