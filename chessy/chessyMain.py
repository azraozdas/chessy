import pygame as p
import random
import sys
import chessEngine  # chessEngine modülünü doğru bir şekilde içe aktardık

# Oyun Ayarları
p.init()
p.mixer.init()
check_channel = p.mixer.Channel(1)
check_sound = p.mixer.Sound("sounds/tension.MP3")
move_sound = p.mixer.Sound("sounds/move-pieces.mp3")
start_game_sound = p.mixer.Sound("sounds/game-start.mp3")
click_sound = p.mixer.Sound("sounds/click.mp3")

# Ekran çözünürlüğünü otomatik algıla
screen_info = p.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

# Ekranın %95'ini kaplayacak şekilde tahtayı ayarla
BOARD_WIDTH = int(SCREEN_WIDTH * 0.95)
BOARD_HEIGHT = int(SCREEN_HEIGHT * 0.95)

# Eğer tahtayı kare olarak tutmak isterseniz
BOARD_WIDTH = min(BOARD_WIDTH, BOARD_HEIGHT)
BOARD_HEIGHT = BOARD_WIDTH

MOVE_LOG_PANEL_WIDTH = int(BOARD_WIDTH * 0.25)
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Satranç tahtası 8x8'dir
SQUARE_SIZE = BOARD_WIDTH // DIMENSION
MAX_FPS = 120

# Ekranı oluştur
screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.RESIZABLE)
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
def drawMenu(play_button, exit_button, hover_play=False, clicked_play=False, hover_exit=False, clicked_exit=False):
    screen.blit(BACKGROUND_IMAGE, (0, 0))

    # CHESSY Başlığı
    title_font = p.font.SysFont("comicsans", 180, True)
    title_surface = title_font.render('CHESSY', True, (255, 255, 255))
    title_x = (screen.get_width() // 2) - (title_surface.get_width() // 2)
    title_y = (screen.get_height() // 6)
    screen.blit(title_surface, (title_x, title_y))

    # Sabit konumlar
    play_center_x = (screen.get_width() // 2)
    play_center_y = (screen.get_height() // 2)
    exit_center_y = play_center_y + 150  # Exit butonu Play butonunun altına sabit yerleştir

    # Play Butonu
    font = p.font.SysFont("comicsans", 50, True)
    play_text_surface = font.render('Play', True, (255, 255, 255))

    play_width, play_height = 200, 100
    if hover_play:
        play_width += 20
        play_height += 20
    if clicked_play:
        play_width -= 10
        play_height -= 10

    play_x = play_center_x - (play_width // 2)
    play_y = play_center_y - (play_height // 2)
    play_button = p.Rect(play_x, play_y, play_width, play_height)

    p.draw.rect(screen, (123, 6, 158), play_button)
    screen.blit(play_text_surface, (play_center_x - (play_text_surface.get_width() // 2),
                                    play_center_y - (play_text_surface.get_height() // 2)))

    # Exit Butonu
    exit_text_surface = font.render('Exit', True, (255, 255, 255))

    exit_width, exit_height = 200, 100
    if hover_exit:
        exit_width += 20
        exit_height += 20
    if clicked_exit:
        exit_width -= 10
        exit_height -= 10

    exit_x = play_center_x - (exit_width // 2)
    exit_y = exit_center_y - (exit_height // 2)
    exit_button = p.Rect(exit_x, exit_y, exit_width, exit_height)

    p.draw.rect(screen, (123, 6, 158), exit_button)
    screen.blit(exit_text_surface, (play_center_x - (exit_text_surface.get_width() // 2),
                                    exit_center_y - (exit_text_surface.get_height() // 2)))

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

    return play_button, exit_button

# En üstte global değişkeni tanımlayın
is_returning_from_game = False  # Return to Menu'den dönüldüğünü kontrol eder
# Ana menü
def mainMenu():
    global screen, BACKGROUND_IMAGE, is_returning_from_game  # Tüm global değişkenleri en başta tanımla

    running = True
    play_button = None
    exit_button = None
    clicked_play = False
    clicked_exit = False

    while running:
        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.VIDEORESIZE:  # Ekran boyutu değiştirildiğinde
                screen = p.display.set_mode((event.w, event.h), p.RESIZABLE)
                BACKGROUND_IMAGE = p.transform.scale(p.image.load("images/backgroundphoto.png"), (event.w, event.h))
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True

        hover_play = play_button and play_button.collidepoint(mouse_pos)
        clicked_play = hover_play and mouse_click

        hover_exit = exit_button and exit_button.collidepoint(mouse_pos)
        clicked_exit = hover_exit and mouse_click

        # Arkaplanı yeniden çiz
        screen.blit(BACKGROUND_IMAGE, (0, 0))

        # Butonları çiz
        play_button, exit_button = drawMenu(play_button, exit_button, hover_play, clicked_play, hover_exit, clicked_exit)

        # Yıldızları çizerken Return to Menu'den gelindiğini kontrol et
        if not is_returning_from_game:
            drawStars()  # Sadece Return to Menu'den gelinmediğinde yıldızları ekrana çiz

        p.display.flip()
        clock.tick(60)

        # Play Butonuna Tıklandıysa
        if clicked_play:
            is_returning_from_game = False  # Return to Menu'den dönmüyoruz, bu yüzden bayrağı sıfırla
            generateStars(play_button.centerx, play_button.centery)
            click_sound.play()  # 🔊 Butona tıklama sesi çal
            start_time = p.time.get_ticks()
            while p.time.get_ticks() - start_time < 1000:  # Yıldız animasyonu 1 saniye
                screen.blit(BACKGROUND_IMAGE, (0, 0))  # Arka planı çiz
                drawMenu(play_button, exit_button, hover_play, clicked_play, hover_exit, clicked_exit)
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

        # Exit Butonuna Tıklandıysa
        if clicked_exit:
            click_sound.play()  # 🔊 Click sesi ekleniyor
            generateStars(exit_button.centerx,
                          exit_button.centery)  # Yıldız animasyonu sadece çıkış butonunun merkezinde olur
            start_time = p.time.get_ticks()
            while p.time.get_ticks() - start_time < 1000:  # Yıldız animasyonu 1 saniye sürsün
                screen.fill((0, 0, 0))  # Ekranı temizle (ana menüden bağımsız yıldızlar)
                drawMenu(play_button, exit_button, hover_play, clicked_play, hover_exit,
                         clicked_exit)  # Yalnızca menüyü çiz
                drawStars()  # Yıldızları ekrana çiz
                p.display.flip()
                clock.tick(60)

            is_returning_from_game = False  # Return to Menu bayrağını sıfırla
            p.quit()
            sys.exit()

def loadSounds():
    """Ses dosyalarını yükleyen fonksiyon."""
    global move_sound
    p.mixer.init()  # Pygame ses motorunu başlat
    check_sound = p.mixer.Sound("sounds/tension.MP3")  # Ses dosyasını yükle


def main():
    """Satranç oyununun ana döngüsü."""
    global screen, BOARD_WIDTH, BOARD_HEIGHT, SQUARE_SIZE  # Global değişkenler
    p.init()
    loadImages()
    loadSounds()  # 🎉 Sesleri yükle

    # Başlangıç ekran ayarları
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.RESIZABLE)
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
                screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.RESIZABLE)
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

            if game_state.inCheck():
                if not is_check:  # Şah durumu yeni başladıysa
                    check_channel.play(check_sound, loops=-1)  # Şah müziğini başlat
                    is_check = True
                elif not check_channel.get_busy():  # Eğer müzik bitmişse, tekrar başlat
                    check_channel.play(check_sound, loops=-1)
            else:
                if is_check:  # Şah durumu sona erdiğinde
                    check_channel.stop()  # Şah müziğini durdur
                    is_check = False

        drawGameState(screen, game_state, square_selected)
        return_button = drawMoveLog(screen, game_state.move_log)  # Hamle logunu ve butonu çiz
        p.display.flip()
        clock.tick(MAX_FPS)


def drawValidMoves(screen, moves, board):
    """
    Taşın geçerli hamlelerini sadece doğru karelere çizen fonksiyon.
    """
    for move in moves:
        row, col = move.end_row, move.end_col
        piece = board[move.start_row][move.start_col]
        target_square = board[row][col]

        # Piyon hareketi için kontrol
        if piece[1] == "p":  # Eğer taş bir piyon ise
            # Çapraz hareket kontrolü: sadece rakip taş varsa veya en passant hareketi ise
            if abs(move.start_col - move.end_col) == 1 and move.start_row != move.end_row:
                if target_square == "--" and not move.is_enpassant_move:
                    continue  # Eğer çaprazda taş yoksa highlight etme
            # Düz hareket kontrolü: boş kare olmalı
            elif move.start_col == move.end_col:
                if target_square != "--":  # Boş olmayan kareleri geçersiz say
                    continue

        # Boş kareler için mavi, yenebilecek taşlar için turuncu renk
        if target_square == "--":
            color = (110, 203, 245)  # Mavi (boş kare)
        else:
            color = (255, 186, 0)  # Turuncu (rakip taş)

        # Highlight yüzeyi
        highlight_surface = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        highlight_surface.set_alpha(150)
        highlight_surface.fill(color)

        # Kareyi ekrana çiz
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
                drawValidMoves(screen, valid_moves, game_state.board)  # board parametresi eklendi

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
    recent_moves = move_log[-max_lines:]  # Move log'un son kısmını al

    for i, move in enumerate(recent_moves):  # Son hamleleri göster
        text_surface = font.render(move, True, (255, 255, 0))  # Sarı renk
        text_x = move_log_rect.centerx - text_surface.get_width() // 2  # Yatayda ortala
        screen.blit(text_surface, (text_x, text_y + i * (font.get_height() + padding)))

    return return_button  # Return to Menu butonunu döndür

# Ana kodda is_returning_from_game kontrolü
if not is_returning_from_game:  # Eğer Return to Menu'den gelinmiyorsa çiz

    if __name__ == "__main__":
        mainMenu()
        main()
