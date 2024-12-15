import pygame as p
import chessEngine
import sys

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    """Load images for chess pieces."""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def main():
    """Main driver for the chess game."""
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("purple"))
    game_state = chessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    loadImages()

    running = True
    square_selected = ()
    player_clicks = []
    game_over = False

    player_one = True  # White's turn
    player_two = False  # Black's turn
    move_log_font = p.font.SysFont("Arial", 14, False, False)

    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col):  # Same square clicked twice
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)

                    if len(player_clicks) == 2:  # After two clicks
                        move = chessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in valid_moves:
                            if move == i:
                                game_state.makeMove(i)
                                move_made = True
                                square_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo move
                    game_state.undoMove()
                    move_made = True
                if e.key == p.K_r:  # Reset game
                    game_state = chessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    game_over = False

        if move_made:
            valid_moves = game_state.getValidMoves()
            move_made = False

        drawGameState(screen, game_state, square_selected)

        # Draw the move log on the side panel
        drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate or game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Game Over")

        # Switch turns after each valid move
        if human_turn:
            if game_state.white_to_move:
                player_one = True
                player_two = False
            else:
                player_one = False
                player_two = True

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, game_state, square_selected):
    drawBoard(screen)
    drawPieces(screen, game_state.board)
    highlightSquares(screen, game_state, game_state.getValidMoves(), square_selected)


def highlightSquares(screen, game_state, valid_moves, square_selected):
    """
    Highlight selected square and possible moves for the piece selected.
    """
    if square_selected != ():  # If a square is selected
        row, col = square_selected
        piece = game_state.board[row][col]
        if piece != "--":  # There is a piece in the selected square
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # Transparency for the highlight
            s.fill(p.Color('yellow'))

            # Highlight valid moves for the selected piece
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    if piece[1] == 'p':  # Handle pawn moves specifically
                        if piece[0] == 'w':  # White pawn
                            if move.end_row == row - 1 and move.end_col == col:
                                screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
                            elif row == 6 and move.end_row == 4 and move.end_col == col:
                                screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
                            elif (move.end_row == row - 1 and abs(move.end_col - col) == 1 and
                                  game_state.board[move.end_row][move.end_col][0] == 'b'):  # Capture diagonally
                                screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
                        elif piece[0] == 'b':  # Black pawn
                            if move.end_row == row + 1 and move.end_col == col:
                                screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
                            elif row == 1 and move.end_row == 3 and move.end_col == col:
                                screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
                            elif (move.end_row == row + 1 and abs(move.end_col - col) == 1 and
                                  game_state.board[move.end_row][move.end_col][0] == 'w'):  # Capture diagonally
                                screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
                    else:  # Other pieces
                        screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))

    # Highlight the selected square in blue
    if square_selected != ():
        row, col = square_selected
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)  # transparency value 0 -> transparent, 255 -> opaque
        s.fill(p.Color('blue'))  # Blue for the selected square
        screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))


def drawBoard(screen):
    colors = [p.Color("purple"), p.Color("pink")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)


def drawMoveLog(screen, game_state, font):
    """Displays the move log on the screen"""
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)  # Draw the background for the move log

    move_log = game_state.move_log
    move_texts = []

    # Iterate over the move log and add formatted moves to move_texts
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 1  # We want one move per line
    padding = 5
    line_spacing = 2
    text_y = padding

    for i in range(0, len(move_texts)):
        text_object = font.render(move_texts[i], True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


if __name__ == "__main__":
    main()
