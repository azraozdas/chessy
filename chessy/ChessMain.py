import sys
import pygame as p
import ChessEngine
from ChessAnimations import animateMove
from ChessConstants import start_sound, check_sound, click_sound, piece_select_sound
from ChessMenu import mainMenu, generateStars
from chessy import ChessGlobals

p.init()
p.mixer.init()

SCREEN_WIDTH = p.display.Info().current_w
SCREEN_HEIGHT = p.display.Info().current_h

BOARD_WIDTH = min(SCREEN_WIDTH, SCREEN_HEIGHT)
BOARD_HEIGHT = BOARD_WIDTH
MOVE_LOG_PANEL_WIDTH = SCREEN_WIDTH - BOARD_WIDTH
MOVE_LOG_PANEL_HEIGHT = SCREEN_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 144

IMAGES = {}

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.FULLSCREEN)
    clock = p.time.Clock()
    start_sound.play()

    # Müzik dosyasını yükleyin ve ses seviyesini ayarlayın
    if ChessGlobals.is_sfx_on:
        p.mixer.music.load("sounds/chessgamesong.mp3")
        p.mixer.music.set_volume(0.1)  # Ses seviyesini 0.1 olarak ayarlayın (0.0 ile 1.0 arasında)
        p.mixer.music.play(-1)  # Müzik döngüde çalsın

    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    animate = False
    loadImages()
    running = True
    square_selected = ()
    player_clicks = []
    game_over = False
    in_check_prev = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    mouse_pos = p.mouse.get_pos()
    mouse_click = False
    player_one = True
    player_two = True

    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        drawGameState(screen, game_state, valid_moves, square_selected)
        return_button = drawMoveLog(screen, game_state, move_log_font)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                if return_button.collidepoint(mouse_pos):
                    if e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                        check_sound.stop()
                        mainMenu()
                        return
                if e.button == 1:
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:
                        piece = game_state.board[row][col]
                        if piece != "--":
                            if (game_state.white_to_move and piece[0] == 'w') or (not game_state.white_to_move and piece[0] == 'b'):
                                if piece_select_sound:
                                    piece_select_sound.play()
                    if not game_over:
                        location = p.mouse.get_pos()
                        col = location[0] // SQUARE_SIZE
                        row = location[1] // SQUARE_SIZE
                        if square_selected == (row, col) or col >= 8:
                            square_selected = ()
                            player_clicks = []
                        else:
                            square_selected = (row, col)
                            player_clicks.append(square_selected)
                        if len(player_clicks) == 2 and human_turn:
                            move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:
                                    animateMove(valid_moves[i], screen, game_state.board, clock, IMAGES, SQUARE_SIZE, drawBoard, drawPieces)
                                    game_state.makeMove(valid_moves[i])
                                    move_made = True
                                    square_selected = ()
                                    player_clicks = []
                                    break
                            if not move_made:
                                player_clicks = [square_selected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    move_undone = True
                if e.key == p.K_r:
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    move_undone = True

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock, IMAGES, SQUARE_SIZE, drawBoard, drawPieces)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False
            in_check_now = game_state.inCheck()
            if in_check_now and not in_check_prev:
                p.mixer.music.pause()  # Oyun müziğini duraklat
                check_sound.play()
            elif not in_check_now and in_check_prev:
                check_sound.stop()
                p.mixer.music.unpause()  # Oyun müziğini devam ettir
            in_check_prev = in_check_now

        drawGameState(screen, game_state, valid_moves, square_selected)
        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)
        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")
        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, game_state, valid_moves, square_selected):
    """
    Responsible for all the graphics within current game state.
    """
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)  # draw pieces on top of those squares


def drawBoard(screen):
    """
    Draw the squares on the board.
    """
    colors = [p.Color(255, 102, 242), p.Color(123, 6, 158)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            rect = p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            p.draw.rect(screen, color, rect)


def highlightSquares(screen, game_state, valid_moves, square_selected):
    """
    Highlight square selected and moves for piece selected.
    If a piece can capture, highlight its square with orange and its valid moves with light blue.
    The selected square's border is always drawn on top of pieces.
    """
    # Çerçevenin kare dışına taşmasını sağlayan dikdörtgen
    outer_border_rect = None

    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_to_move else 'b'):  # square_selected is a piece that can be moved
            # Initialize surfaces for highlighting
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            capture_highlight = False  # Flag to check if this piece can capture

            # Check if the selected piece can capture any opponent piece
            for move in valid_moves:
                if move.start_row == row and move.start_col == col and move.piece_captured != "--":
                    capture_highlight = True
                    break

            # Çerçevenin kare dışına taşmasını sağlayan dikdörtgen koordinatlarını oluştur
            outer_border_rect = p.Rect(
                (col * SQUARE_SIZE) - 3,  # Slightly offset for the outer border
                (row * SQUARE_SIZE) - 3,
                SQUARE_SIZE + 6,  # Make the border extend outside
                SQUARE_SIZE + 6
            )

            # Highlight valid moves from the selected square
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    if move.piece_captured != "--":
                        s.fill((255, 186, 0))  # Orange for capture squares
                    else:
                        s.fill((110, 203, 245))  # Light blue for normal move squares
                    s.set_alpha(100)
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))

    # Çerçeveyi taşların üstünde göstermek için buraya koyuyoruz
    if outer_border_rect:
        p.draw.rect(screen, (255, 255, 255, 150), outer_border_rect, width=3)  # Transparent white border

def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current board state.
    """
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "--":  # Eğer kare boş değilse taşı çiz
                piece_rect = p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                screen.blit(IMAGES[piece], piece_rect)


def drawMoveLog(screen, game_state, font):
    """
    Draws the move log with multiple columns.
    If the move log exceeds a certain number of lines, it continues in the next column.
    """
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = game_state.move_log
    move_texts = []

    # Logları satır satır topla
    for i in range(len(move_log)):
        move_string = str(i + 1) + ". " + str(move_log[i])
        move_texts.append(move_string)

    # Izgara yapısı için sınırlar
    max_lines = (MOVE_LOG_PANEL_HEIGHT - 80) // (font.get_height() + 10)  # Maksimum satır sayısı
    max_columns = 3  # En fazla kaç sütun olacağı
    column_width = (MOVE_LOG_PANEL_WIDTH - 40) // max_columns  # Her sütunun genişliği
    padding = 10
    line_spacing = font.get_height() + 10

    # Yazıları ızgara mantığıyla yerleştir
    for i in range(len(move_texts)):
        row = i % max_lines  # Satır sayısı
        col = i // max_lines  # Sütun sayısı (satır limiti aşılırsa yeni sütuna geçer)

        # Eğer sütun sayısı sütun limitini aşarsa, satırın başına döner (overflow önlenir)
        if col >= max_columns:
            break

        text_object = font.render(move_texts[i], True, p.Color('white'))
        text_x = padding + col * column_width  # X pozisyonu (sütuna göre kaydırma)
        text_y = padding + row * line_spacing  # Y pozisyonu (satıra göre kaydırma)

        text_location = move_log_rect.move(text_x, text_y)
        screen.blit(text_object, text_location)

    # Return to Menu Butonu
    button_width = MOVE_LOG_PANEL_WIDTH - 40
    button_height = 50
    button_x = BOARD_WIDTH + 20
    button_y = MOVE_LOG_PANEL_HEIGHT - 55

    return_button = p.Rect(button_x, button_y, button_width, button_height)
    mouse_pos = p.mouse.get_pos()

    button_color = (123, 6, 158)  # Mor
    border_color = (255, 102, 242)  # Pembe
    text_color = (255, 255, 255)  # Beyaz

    # Return to Menu butonu hover ve tıklama efekti
    if return_button.collidepoint(mouse_pos):
        button_color = (153, 51, 204)  # Hover rengi
        if p.mouse.get_pressed()[0]:  # Tıklama kontrolü
            button_color = (90, 3, 120)
            click_sound.play()  # Tıklama sesi çal
            generateStars(button_x + button_width // 2, button_y + button_height // 2)

    # Butonu Çiz
    p.draw.rect(screen, button_color, return_button)
    p.draw.rect(screen, border_color, return_button, 3)

    button_font = p.font.SysFont("Arial", 28, True)
    button_text = button_font.render("Return to Menu", True, text_color)
    screen.blit(button_text, (button_x + (button_width // 2 - button_text.get_width() // 2),
                              button_y + (button_height // 2 - button_text.get_height() // 2)))

    return return_button


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))



if __name__ == "__main__":
    mainMenu()
##