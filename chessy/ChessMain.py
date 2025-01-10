import random
import sys
from multiprocessing import Queue
from threading import Thread

import pygame as p

import ChessAI
import ChessEngine
import ChessGlobals
from ChessAnimations import animateMove, drawBreathingRectWithColorTransition
from ChessConstants import screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock, start_sound, check_sound, click_sound, \
    piece_select_sound
from ChessMenu import mainMenu

# Sesler ve ekran bilgileri ChessConstants.py'de tanımlı

# Dinamik boyutlandırma
BOARD_WIDTH = min(SCREEN_WIDTH, SCREEN_HEIGHT)
BOARD_HEIGHT = BOARD_WIDTH
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION

# Tahtayı ekranda nereye çizmek istiyoruz?
# Şu anda sol üst köşeden başlatıyoruz. (0, 0)
# İsterseniz ortalamak için:
#   BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
#   BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
BOARD_X = 0
BOARD_Y = 0

MOVE_LOG_PANEL_WIDTH = SCREEN_WIDTH - BOARD_WIDTH
MOVE_LOG_PANEL_HEIGHT = SCREEN_HEIGHT
MAX_FPS = 60  # 144 yerine 60 kullanmak daha stabil olabilir

IMAGES = {}

def loadImages():
    """Taşların görsellerini yükler ve ölçekler."""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        image_path = "images/" + piece + ".png"
        IMAGES[piece] = p.transform.scale(p.image.load(image_path), (SQUARE_SIZE, SQUARE_SIZE))

def showPromotionUI(screen):
    """Piyon terfi ekranını göster."""
    overlay = p.Surface(screen.get_size(), p.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Yarı saydam siyah arkaplan
    screen.blit(overlay, (0, 0))
    p.display.flip()

    button_width, button_height = 100, 100
    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2
    piece_types = ["B", "N", "R", "Q"]  # Bishop, Knight, Rook, Queen
    spacing = 20
    start_x = center_x - (2 * button_width + spacing + button_width // 2)

    buttons = []
    for i, ptype in enumerate(piece_types):
        rect_x = start_x + i * (button_width + spacing)
        rect_y = center_y - button_height // 2
        rect = p.Rect(rect_x, rect_y, button_width, button_height)
        buttons.append((rect, ptype))

    def drawButtons():
        """Butonları çizer."""
        for rect, ptype in buttons:
            p.draw.rect(screen, (200, 200, 200), rect)  # Buton arka planı
            font = p.font.SysFont("Times New Roman", 40, True)
            text_surface = font.render(ptype, True, (0, 0, 0))  # Buton yazısı
            tx = rect.centerx - text_surface.get_width() // 2
            ty = rect.centery - text_surface.get_height() // 2
            screen.blit(text_surface, (tx, ty))
        p.display.flip()

    drawButtons()
    chosen_type = None

    while chosen_type is None:  # Seçim yapılana kadar bekle
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                for rect, ptype in buttons:
                    if rect.collidepoint(mouse_pos):
                        chosen_type = ptype  # Seçim yapıldı
                        break
        drawButtons()

    # Tercih ekranından çıkış ve temizleme
    screen.fill((0, 0, 0))  # Ekranı temizle
    p.display.flip()
    return chosen_type

def main(player_one=True, player_two=True):
    # Taş görsellerini yükle
    loadImages()

    # Ses ayarları
    if ChessGlobals.is_sfx_on:
        start_sound.play()

    # Arka plan müziği
    if ChessGlobals.is_sfx_on:
        p.mixer.music.load("sounds/chessgamesong.mp3")
        p.mixer.music.set_volume(0.2)
        p.mixer.music.play(-1)

    # Oyun durumunu yükle
    if player_two:
        if ChessGlobals.saved_friend_game_state:
            game_state = ChessGlobals.saved_friend_game_state
            saved_friend_game_state = None
        else:
            game_state = ChessEngine.GameState()
    else:
        if ChessGlobals.saved_ai_game_state:
            game_state = ChessGlobals.saved_ai_game_state
            ChessGlobals.saved_ai_game_state = None
        else:
            game_state = ChessEngine.GameState()

    valid_moves = game_state.getValidMoves()
    move_made = False
    animate = False
    running = True
    square_selected = ()
    player_clicks = []
    game_over = False
    in_check_prev = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Times New Roman", 25, False, False)

    while running:
        # Beyazın sırası mı, siyahın sırası mı?
        human_turn = (game_state.white_to_move and player_one) or \
                     (not game_state.white_to_move and player_two)

        # Oyun durumunu ekrana çiz
        drawGameState(screen, game_state, valid_moves, square_selected)
        return_button = drawMoveLog(screen, game_state, move_log_font)

        for e in p.event.get():
            handleScroll(e)
            if e.type == p.QUIT:
                p.quit()
                sys.exit()

            elif e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                # "Return to Menu" butonuna tıklandı mı?
                if return_button.collidepoint(mouse_pos):
                    if e.button == 1:
                        button_color = (90, 3, 120)
                        if ChessGlobals.is_sfx_on:
                            click_sound.play()  # Tıklama sesi buraya eklendi
                        # Mevcut oyun durumunu kaydet
                        if player_two:
                            ChessGlobals.saved_friend_game_state = game_state
                        else:
                            ChessGlobals.saved_ai_game_state = game_state

                        check_sound.stop()
                        mainMenu()
                        return

                if e.button == 1:
                    # Tahtadaki bir kareye tıklandı mı?
                    col = (mouse_pos[0]) // SQUARE_SIZE
                    row = (mouse_pos[1]) // SQUARE_SIZE
                    # row, col hesaplanırken BOARD_X, BOARD_Y devreye girebilir.
                    # Ancak şu an BOARD_X=0 ve BOARD_Y=0 kullandığımız için çıkarma yapmıyoruz.
                    # Eğer BOARD_X veya BOARD_Y != 0 olsaydı:
                    #   col = (mouse_pos[0] - BOARD_X) // SQUARE_SIZE
                    #   row = (mouse_pos[1] - BOARD_Y) // SQUARE_SIZE
                    if human_turn:
                        if 0 <= row < 8 and 0 <= col < 8:
                            piece = game_state.board[row][col]
                            if piece != "--":
                                if ((game_state.white_to_move and piece[0] == 'w') or
                                    (not game_state.white_to_move and piece[0] == 'b')):
                                    if piece_select_sound and ChessGlobals.is_sfx_on:
                                        piece_select_sound.play()

                        if not game_over:
                            if square_selected == (row, col) or col >= 8:
                                square_selected = ()
                                player_clicks = []
                            else:
                                square_selected = (row, col)
                                player_clicks.append(square_selected)

                            if len(player_clicks) == 2 and human_turn:
                                move = ChessEngine.Move(
                                    player_clicks[0], player_clicks[1], game_state.board
                                )
                                for i in range(len(valid_moves)):
                                    if move == valid_moves[i]:
                                        animateMove(valid_moves[i], screen, game_state.board,
                                                    clock, IMAGES, SQUARE_SIZE, drawBoard, drawPieces)
                                        game_state.makeMove(valid_moves[i])
                                        move_made = True
                                        square_selected = ()
                                        player_clicks = []
                                        break
                                if not move_made:
                                    player_clicks = [square_selected]

            elif e.type == p.KEYDOWN:
                # Hamle geri alma (Z)
                if e.key == p.K_z:
                    if len(game_state.move_log) > 0:
                        game_state.undoMove()
                        move_made = True
                        animate = False
                        game_over = False
                        move_undone = True
                # Oyunu resetleme (R)
                if e.key == p.K_r:
                    check_sound.stop()
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    move_undone = True

        # Eğer AI sırasıysa
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                move_finder_thread = Thread(
                    target=ChessAI.findBestMove,
                    args=(game_state, valid_moves, return_queue)
                )
                move_finder_thread.start()

            while ai_thinking:
                clock.tick(60)
                if not move_finder_thread.is_alive():
                    ai_move = return_queue.get()
                    if ai_move is None or len(valid_moves) == 0:
                        game_over = True
                        drawEndGameText(screen, "Stalemate or Checkmate")
                        break

                    animateMove(ai_move, screen, game_state.board,
                                clock, IMAGES, SQUARE_SIZE, drawBoard, drawPieces)
                    game_state.makeMove(ai_move)
                    move_made = True
                    ai_thinking = False

            drawGameState(screen, game_state, valid_moves, square_selected)
            p.display.flip()

        # Bir hamle yapıldıktan sonra
        if move_made:
            if len(game_state.move_log) > 0:
                last_move = game_state.move_log[-1]
                # Piyon terfi
                if last_move.is_pawn_promotion:
                    if human_turn:
                        promoted_piece_type = showPromotionUI(screen)
                        row, col = last_move.end_row, last_move.end_col
                        game_state.board[row][col] = last_move.piece_moved[0] + promoted_piece_type
                        last_move.promotion_choice = promoted_piece_type
                    else:
                        promoted_piece_type = random.choice(["Q", "R", "B", "N"])
                        row, col = last_move.end_row, last_move.end_col
                        game_state.board[row][col] = last_move.piece_moved[0] + promoted_piece_type
                        last_move.promotion_choice = promoted_piece_type

            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

            # Şah tehdit kontrolleri (check)
            in_check_now = game_state.inCheck()
            if in_check_now and not in_check_prev:
                # Müzik durdurulabilir veya ses çalınabilir
                p.mixer.music.pause()
                if ChessGlobals.is_sfx_on:
                    check_sound.play()
            elif not in_check_now and in_check_prev:
                check_sound.stop()
                p.mixer.music.unpause()
            in_check_prev = in_check_now

        # Oyun ekranını çiz
        drawGameState(screen, game_state, valid_moves, square_selected)
        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        # Oyun döngüsünün oyun sonu kısmında yapılan değişiklikler:
        if game_state.checkmate or game_state.stalemate:
            if not game_over:
                check_sound.stop()
                p.mixer.music.stop()
                game_over = True

                # Oyun moduna göre mesaj belirleme
                if game_state.checkmate:
                    if game_state.white_to_move:
                        end_text = "Black wins by checkmate"
                    else:
                        end_text = "White wins by checkmate"
                elif game_state.stalemate:
                    end_text = "Stalemate"

            # Oyun sonu mesajını ve ekranı çiz
            drawEndGameText(screen, end_text)

            # Oyun sonrasında da log ve "Return to Menu" tuşu çizilmeye devam eder
            drawMoveLog(screen, game_state, move_log_font)
            return_button = drawMoveLog(screen, game_state, move_log_font)
        else:
            # Normal oyun durumu için ekranı güncelle
            drawGameState(screen, game_state, valid_moves, square_selected)
            if not game_over:
                drawMoveLog(screen, game_state, move_log_font)

        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, game_state, valid_moves, square_selected):
    """Tahta, taşlar ve vurgulamalar dahil genel oyun durumunu çizer."""
    # Önce tüm ekranı temizleyin
    screen.fill((0, 0, 0))

    # Daha sonra tahtayı ve taşları çizin
    drawBoard(screen)
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)

def drawBoard(screen):
    """Tahtayı sol üst köşeden itibaren çizer."""
    # Tahtayı çizerken eski çerçeveleri temizlemek için ekranın ilgili kısmını temizle
    board_rect = p.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
    p.draw.rect(screen, (0, 0, 0), board_rect)  # Siyah arka planla tahtayı temizle

    # Tahta kareleri için renkler
    colors = [p.Color(255, 102, 242), p.Color(123, 6, 158)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            # Board'un ekrandaki başlangıç noktaları BOARD_X, BOARD_Y
            rect = p.Rect(BOARD_X + col * SQUARE_SIZE,
                          BOARD_Y + row * SQUARE_SIZE,
                          SQUARE_SIZE, SQUARE_SIZE)
            p.draw.rect(screen, color, rect)


def highlightSquares(screen, game_state, valid_moves, square_selected):
    """Seçili kare ve hamleleri vurgular."""
    if square_selected != ():
        row, col = square_selected

        # Satır ve sütunun tahtada geçerli bir kare olduğundan emin olun
        if 0 <= row < 8 and 0 <= col < 8:
            # Seçili karenin bulunduğu kareyi temizle
            rect = p.Rect(
                BOARD_X + col * SQUARE_SIZE,
                BOARD_Y + row * SQUARE_SIZE,
                SQUARE_SIZE, SQUARE_SIZE
            )
            color = p.Color(255, 102, 242) if (row + col) % 2 == 0 else p.Color(123, 6, 158)
            p.draw.rect(screen, color, rect)

            # Geçerli hamleleri vurgula
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE), p.SRCALPHA)
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    # Normal hamle ve taş yeme kontrolü
                    if move.is_enpassant_move:
                        s.fill((255, 186, 0))   # En passant için kırmızı (örnek)
                    elif move.piece_captured != "--":
                        s.fill((255, 186, 0))  # Taş yeme için sarı
                    else:
                        s.fill((110, 203, 245))  # Normal hamle için mavi
                    s.set_alpha(100)
                    target_x = BOARD_X + move.end_col * SQUARE_SIZE
                    target_y = BOARD_Y + move.end_row * SQUARE_SIZE
                    screen.blit(s, (target_x, target_y))

            # Çerçeveyi çiz
            p.draw.rect(
                screen,
                (255, 255, 255),  # Çerçeve rengi
                p.Rect(
                    BOARD_X + col * SQUARE_SIZE - 3,
                    BOARD_Y + row * SQUARE_SIZE - 3,
                    SQUARE_SIZE + 6,
                    SQUARE_SIZE + 6
                ),
                width=3
            )

def drawPieces(screen, board):
    """Taşları, BOARD_X ve BOARD_Y offsetlerini dikkate alarak çizer."""
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                x_coord = BOARD_X + col * SQUARE_SIZE
                y_coord = BOARD_Y + row * SQUARE_SIZE
                screen.blit(IMAGES[piece], (x_coord, y_coord))

def drawMoveLog(screen, game_state, font):

    # Log kutusu boyutları
    log_box_width = int(MOVE_LOG_PANEL_WIDTH * 0.95)
    log_box_height = int(MOVE_LOG_PANEL_HEIGHT * 0.90)
    log_box_x = BOARD_WIDTH + (MOVE_LOG_PANEL_WIDTH - log_box_width) // 2

    #log kutusunun yeri
    log_box_y = (MOVE_LOG_PANEL_HEIGHT - log_box_height) // 4

    overlay = p.Surface((log_box_width, log_box_height), p.SRCALPHA)
    overlay.fill((0, 0, 0, 70))
    screen.blit(overlay, (log_box_x, log_box_y))

    color_list = [
        (110, 203, 245),
        (255, 255, 255),
        (128, 128, 128)
    ]
    drawBreathingRectWithColorTransition(
        screen,
        colors=color_list,
        rect=(log_box_x, log_box_y, log_box_width, log_box_height),
        transition_speed=0.02,
        border_width=3,
        border_radius=15
    )

    # Taş isimleri
    piece_names = {
        "wp": "white pawn", "wR": "white rook", "wN": "white knight", "wB": "white bishop",
        "wQ": "white queen", "wK": "white king",
        "bp": "black pawn", "bR": "black rook", "bN": "black knight", "bB": "black bishop",
        "bQ": "black queen", "bK": "black king",
    }
    move_log = game_state.move_log
    raw_move_texts = []
    for i, move in enumerate(move_log):
        piece = piece_names.get(move.piece_moved, "unknown piece")
        start = move.getRankFile(move.start_row, move.start_col)
        end = move.getRankFile(move.end_row, move.end_col)
        captured_piece = (piece_names.get(move.piece_captured, "unknown piece")
                          if move.piece_captured != "--" else None)

        if move.is_castle_move:
            move_text = f"{i + 1}. Castling performed."
        else:
            if captured_piece:
                move_text = f"{i + 1}. The {piece} moved from {start} to {end} and captured the {captured_piece}."
            else:
                move_text = f"{i + 1}. The {piece} moved from {start} to {end}."

        if move.is_pawn_promotion:
            promotion_piece = move.promotion_choice if hasattr(move, 'promotion_choice') else 'Q'
            promoted_piece = piece_names.get(f"w{promotion_piece}", "unknown piece") if move.piece_moved[0] == 'w' else piece_names.get(f"b{promotion_piece}", "unknown piece")
            move_text += f" The pawn was promoted to a {promoted_piece}."


        raw_move_texts.append(move_text)

    def wrap_text(text, font, max_width):
        words = text.split(' ')
        wrapped_lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            width_test = font.size(test_line)[0]
            if width_test <= max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = word
        if current_line:
            wrapped_lines.append(current_line)
        return wrapped_lines

    line_spacing = font.get_height() + 5
    top_margin = 20
    max_text_width = log_box_width - 40
    wrapped_texts = []
    for m in raw_move_texts:
        wrapped = wrap_text(m, font, max_text_width)
        wrapped_texts.extend(wrapped)
        wrapped_texts.append("")  # Boş satır

    if not hasattr(game_state, "log_surface_cache"):
        game_state.log_surface_cache = None

    total_height = len(wrapped_texts) * line_spacing
    if game_state.move_log_updated or game_state.log_surface_cache is None:
        log_surface = p.Surface((log_box_width, total_height), p.SRCALPHA)
        log_surface.fill((0, 0, 0, 0))
        y_offset = 0
        for line_text in wrapped_texts:
            text_surface = font.render(line_text, True, p.Color('yellow'))
            text_width = text_surface.get_width()
            text_x = (log_box_width - text_width) // 2
            log_surface.blit(text_surface, (text_x, y_offset))
            y_offset += line_spacing

        game_state.log_surface_cache = log_surface
        game_state.move_log_updated = False
    else:
        log_surface = game_state.log_surface_cache

    visible_height = log_box_height - 2 * top_margin
    max_scroll = max(0, total_height - visible_height)
    ChessGlobals.scroll_offset = max(0, min(ChessGlobals.scroll_offset, max_scroll))

    clip_rect = p.Rect(0, ChessGlobals.scroll_offset, log_box_width, visible_height)
    screen.blit(log_surface, (log_box_x, log_box_y + top_margin), area=clip_rect)

    # Scroll bar
    if total_height > visible_height:
        scrollbar_width = 10
        scrollbar_x = log_box_x + log_box_width - scrollbar_width - 5
        scrollbar_y = log_box_y + top_margin
        scrollbar_height = visible_height
        handle_height = max(30, int((visible_height / total_height) * scrollbar_height))
        handle_y_ratio = ChessGlobals.scroll_offset / max_scroll if max_scroll > 0 else 0
        handle_y = scrollbar_y + int(handle_y_ratio * (scrollbar_height - handle_height))

        p.draw.rect(screen, (60, 60, 60), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        p.draw.rect(screen, (150, 150, 150), (scrollbar_x, handle_y, scrollbar_width, handle_height))

    # "Return to Menu" butonu
    button_width = log_box_width
    button_height = 50
    button_x = log_box_x
    button_y = log_box_y + log_box_height + 20
    return_button = p.Rect(button_x, button_y, button_width, button_height)

    mouse_pos = p.mouse.get_pos()
    button_color = (123, 6, 158)
    border_color = (255, 102, 242)
    text_color = (255, 255, 255)

    # Fare butonun üzerindeyse buton rengi değişir
    if return_button.collidepoint(mouse_pos):
        button_color = (153, 51, 204)

    p.draw.rect(screen, button_color, return_button)
    p.draw.rect(screen, border_color, return_button, 3)

    button_font = p.font.SysFont("Times New Roman", 28, True)
    button_text = button_font.render("Return to Menu", True, text_color)
    screen.blit(
        button_text,
        (
            button_x + (button_width // 2 - button_text.get_width() // 2),
            button_y + (button_height // 2 - button_text.get_height() // 2)
        )
    )
    return return_button


def handleScroll(event):
    if event.type == p.MOUSEBUTTONDOWN:
        if event.button == 4:  # Scroll up
            ChessGlobals.scroll_offset = max(ChessGlobals.scroll_offset - 20, 0)
        elif event.button == 5:  # Scroll down
            ChessGlobals.scroll_offset += 20

def drawEndGameText(screen, text):
    """Oyun bittiğinde gösterilen yazıyı, yarı saydam bir dikdörtgen ve nefes alan bir çerçeve içinde çizer."""
    font = p.font.SysFont("Times New Roman", 64, True, False)

    # Renkler
    neon_color = (241, 196, 15)  # Metnin asıl rengi (siyah)
    glow_color = (231,76,60)  # Glow rengi (pembe tonlarında)

    # Metin objeleri
    text_object = font.render(text, True, neon_color)
    glow_object = font.render(text, True, glow_color)

    # Metni ekranın ortasına konumlayalım
    text_rect = text_object.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))

    # Metnin etrafında biraz boşluk (padding)
    padding_x = 40
    padding_y = 30

    # Dikdörtgen boyutu
    bg_rect = p.Rect(0, 0, text_rect.width + 2 * padding_x, text_rect.height + 2 * padding_y)
    bg_rect.center = text_rect.center

    # 1) Yarı saydam beyaz arka plan (soft köşeli)
    overlay_surf = p.Surface(bg_rect.size, p.SRCALPHA)  # Transparan destekli yüzey
    overlay_surf.fill((0, 0, 0, 0))  # Şeffaf yüzey başlat

    # Soft köşeli dikdörtgeni yüzeye çiz
    rounded_rect = p.Surface(bg_rect.size, p.SRCALPHA)  # Yuvarlatılmış köşeler için yüzey
    p.draw.rect(
        rounded_rect,
        (255, 255, 255, 100),  # RGBA (Beyaz ve transparan)
        rounded_rect.get_rect(),
        border_radius=15  # Köşeleri yumuşat
    )

    # Yuvarlatılmış dikdörtgeni overlay yüzeyine blit et
    overlay_surf.blit(rounded_rect, (0, 0))

    # Yüzeyi ekrana çiz
    screen.blit(overlay_surf, bg_rect.topleft)

    # 2) “Nefes alan” (soft color transition) çerçeve
    #    drawBreathingRectWithColorTransition fonksiyonunu sizdeki örnek gibi kullanıyoruz.
    color_list = [
        (110, 203, 245),  # Neon mavi
        (255, 255, 255),  # Beyaz
        (128, 128, 128)  # Gri
    ]
    drawBreathingRectWithColorTransition(
        screen,
        colors=color_list,
        rect=bg_rect,
        transition_speed=0.02,  # Renk geçiş hızı
        border_width=5,  # Çerçeve kalınlığı
        border_radius=15  # Köşelerin yumuşaklığı
    )

    # 3) Glow efektini ekle (pembe), dikdörtgenin üstünde ama metnin altında
    for i in range(1, 5):
        screen.blit(
            glow_object,
            (
                text_rect.x + i,
                text_rect.y + i
            )
        )

    # 4) Metni çiz (siyah)
    screen.blit(text_object, text_rect)

if __name__ == "__main__":
    mainMenu()

