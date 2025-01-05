import random
import sys

import pygame as p

from threading import Thread
from multiprocessing import Queue

import ChessAI
import ChessEngine
from ChessAnimations import animateMove
from ChessConstants import start_sound, check_sound, click_sound, piece_select_sound
from ChessMenu import mainMenu, generateStars
from chessy import ChessGlobals

saved_friend_game_state = None
saved_ai_game_state = None


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

def showPromotionUI(screen):
    overlay = p.Surface(screen.get_size(), p.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    p.display.flip()

    button_width, button_height = 100, 100
    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2
    piece_types = ["B", "N", "R", "Q"]
    spacing = 20
    start_x = center_x - (2 * button_width + spacing + button_width // 2)

    buttons = []
    for i, ptype in enumerate(piece_types):
        rect_x = start_x + i * (button_width + spacing)
        rect_y = center_y - button_height // 2
        rect = p.Rect(rect_x, rect_y, button_width, button_height)
        buttons.append((rect, ptype))

    def drawButtons():
        for rect, ptype in buttons:
            p.draw.rect(screen, (200, 200, 200), rect)
            font = p.font.SysFont("Arial", 40, True)
            text_surface = font.render(ptype, True, (0, 0, 0))
            tx = rect.centerx - text_surface.get_width() // 2
            ty = rect.centery - text_surface.get_height() // 2
            screen.blit(text_surface, (tx, ty))
        p.display.flip()

    drawButtons()

    chosen_type = None
    waiting = True
    while waiting:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                for rect, ptype in buttons:
                    if rect.collidepoint(mouse_pos):
                        chosen_type = ptype
                        waiting = False
        drawButtons()

    return chosen_type

def main(player_one=True, player_two=True):
    global saved_friend_game_state, saved_ai_game_state

    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.FULLSCREEN)
    clock = p.time.Clock()

    if ChessGlobals.is_sfx_on:
        start_sound.play()

    if ChessGlobals.is_sfx_on:
        p.mixer.music.load("sounds/chessgamesong.mp3")
        p.mixer.music.set_volume(0.2)
        p.mixer.music.play(-1)

    if player_two:
        if saved_friend_game_state:
            game_state = saved_friend_game_state
            saved_friend_game_state = None
        else:
            game_state = ChessEngine.GameState()
    else:
        if saved_ai_game_state:
            game_state = saved_ai_game_state
            saved_ai_game_state = None
        else:
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

    while running:
        human_turn = (game_state.white_to_move and player_one) or \
                     (not game_state.white_to_move and player_two)

        drawGameState(screen, game_state, valid_moves, square_selected)
        return_button = drawMoveLog(screen, game_state, move_log_font)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                if return_button.collidepoint(mouse_pos):
                    if e.button == 1:
                        if player_two:
                            saved_friend_game_state = game_state
                        else:
                            saved_ai_game_state = game_state
                        check_sound.stop()
                        mainMenu()
                        return

                if e.button == 1:
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if human_turn:
                        if 0 <= row < 8 and 0 <= col < 8:
                            piece = game_state.board[row][col]
                            if piece != "--":
                                if (game_state.white_to_move and piece[0] == 'w') or \
                                        (not game_state.white_to_move and piece[0] == 'b'):
                                    if piece_select_sound and ChessGlobals.is_sfx_on:
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
                if e.key == p.K_z:
                    if len(game_state.move_log) > 0:
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

        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                move_finder_thread = Thread(target=ChessAI.findBestMove, args=(game_state, valid_moves, return_queue))
                move_finder_thread.start()

            while ai_thinking:
                clock.tick(60)

                if not move_finder_thread.is_alive():
                    ai_move = return_queue.get()
                    if ai_move is None:
                        ai_move = ChessAI.findRandomMove(valid_moves)

                    animateMove(ai_move, screen, game_state.board, clock, IMAGES, SQUARE_SIZE, drawBoard, drawPieces)

                    game_state.makeMove(ai_move)
                    move_made = True
                    ai_thinking = False

            drawGameState(screen, game_state, valid_moves, square_selected)
            p.display.flip()

        if move_made:
            if len(game_state.move_log) > 0:
                last_move = game_state.move_log[-1]
                if last_move.is_pawn_promotion:
                    if human_turn:
                        promoted_piece_type = showPromotionUI(screen)
                        row, col = last_move.end_row, last_move.end_col
                        game_state.board[row][col] = last_move.piece_moved[0] + promoted_piece_type
                    else:
                        promoted_piece_type = random.choice(["Q", "R", "B", "N"])
                        row, col = last_move.end_row, last_move.end_col
                        game_state.board[row][col] = last_move.piece_moved[0] + promoted_piece_type

            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

            in_check_now = game_state.inCheck()
            if in_check_now and not in_check_prev:
                p.mixer.music.pause()
                if ChessGlobals.is_sfx_on:
                    check_sound.play()
            elif not in_check_now and in_check_prev:
                check_sound.stop()
                p.mixer.music.unpause()
            in_check_prev = in_check_now

        drawGameState(screen, game_state, valid_moves, square_selected)
        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate:
            game_over = True
            p.mixer.music.stop()
            check_sound.stop()
            in_check_prev = False
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
    drawBoard(screen)
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)

def drawBoard(screen):
    colors = [p.Color(255, 102, 242), p.Color(123, 6, 158)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            rect = p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            p.draw.rect(screen, color, rect)


def highlightSquares(screen, game_state, valid_moves, square_selected):
    outer_border_rect = None

    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_to_move else 'b'):
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))

            for move in valid_moves:
                if move.start_row == row and move.start_col == col and move.piece_captured != "--":
                    capture_highlight = True
                    break

            outer_border_rect = p.Rect(
                (col * SQUARE_SIZE) - 3,
                (row * SQUARE_SIZE) - 3,
                SQUARE_SIZE + 6,
                SQUARE_SIZE + 6
            )

            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    if move.piece_captured != "--":
                        s.fill((255, 186, 0))
                    else:
                        s.fill((110, 203, 245))
                    s.set_alpha(100)
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
    if outer_border_rect:
        p.draw.rect(screen, (255, 255, 255, 150), outer_border_rect, width=3)

def highlightAIMove(screen, move, color=(255, 186, 0)):
    s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
    s.set_alpha(100)
    s.fill(color)
    screen.blit(s, (move.start_col * SQUARE_SIZE, move.start_row * SQUARE_SIZE))
    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
    p.display.flip()
    p.time.wait(300)

def drawPieces(screen, board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "--":
                piece_rect = p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                screen.blit(IMAGES[piece], piece_rect)

def drawMoveLog(screen, game_state, font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_pair = f"{i //2 + 1}. {move_log[i]}"
        if i + 1 < len(move_log):
            move_pair += f"{move_log[i + 1]}"
        move_texts.append(move_pair)

    font = p.font.SysFont("Arial", 20, True, False)

    max_lines = (MOVE_LOG_PANEL_HEIGHT - 80) // (font.get_height() + 10)
    max_columns = 5
    column_width = (MOVE_LOG_PANEL_WIDTH - 40) // max_columns
    padding = 10
    line_spacing = font.get_height() + 10

    for i in range(len(move_texts)):
        row = i % max_lines
        col = i // max_lines

        if col >= max_columns:
            break

        text_object = font.render(move_texts[i], True, p.Color('yellow'))
        text_x = padding + col * column_width
        text_y = padding + row * line_spacing
        text_location = move_log_rect.move(text_x, text_y)
        screen.blit(text_object, text_location)

    button_width = MOVE_LOG_PANEL_WIDTH - 40
    button_height = 50
    button_x = BOARD_WIDTH + 20
    button_y = MOVE_LOG_PANEL_HEIGHT - 55

    return_button = p.Rect(button_x, button_y, button_width, button_height)
    mouse_pos = p.mouse.get_pos()

    button_color = (123, 6, 158)
    border_color = (255, 102, 242)
    text_color = (255, 255, 255)

    if return_button.collidepoint(mouse_pos):
        button_color = (153, 51, 204)
        if p.mouse.get_pressed()[0]:
            button_color = (90, 3, 120)
            if ChessGlobals.is_sfx_on:
                click_sound.play()
            generateStars(button_x + button_width // 2, button_y + button_height // 2)

    p.draw.rect(screen, button_color, return_button)
    p.draw.rect(screen, border_color, return_button, 3)

    button_font = p.font.SysFont("Arial", 28, True)
    button_text = button_font.render("Return to Menu", True, text_color)
    screen.blit(button_text, (button_x + (button_width // 2 - button_text.get_width() // 2),
                              button_y + (button_height // 2 - button_text.get_height() // 2)))

    return return_button


def drawEndGameText(screen, text):
    font = p.font.SysFont("Arial", 64, True, False)

    neon_color = (0, 0, 0)
    glow_color = (255, 20, 147)

    text_object = font.render(text, True, neon_color)
    glow_object = font.render(text, True, glow_color)

    for i in range (1, 5):
        screen.blit(glow_object, (BOARD_WIDTH // 2 - text_object.get_width() // 2 + i, BOARD_HEIGHT // 2 - text_object.get_height() // 2 + i))

    text_location = text_object.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
    screen.blit(text_object, text_location)

if __name__ == "__main__":
    mainMenu()