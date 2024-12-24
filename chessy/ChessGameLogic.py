
import pygame as p
from ChessConstants import LIGHT_COLOR, DARK_COLOR, SQUARE_SIZE, DIMENSION, IMAGES


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
    """Oyunun mevcut durumunu çizer."""
    drawBoard(screen)
    highlightSquares(screen, game_state, game_state.getValidMoves(), square_selected)
    drawPieces(screen, game_state.board)



def drawBoard(screen):
    """
    Draw the squares on the board.
    The top left square is always light.
    """
    colors = [p.Color(255, 102, 242), p.Color(123, 6, 158)]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))




def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game_state.board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))




def highlightSquares(screen, game_state, valid_moves, square_selected):
    """
    Highlight square selected and moves for piece selected.
    """
    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_to_move else 'b'):  # square_selected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # transparency value 0 -> transparent, 255 -> opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
