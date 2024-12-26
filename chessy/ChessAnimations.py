import random
import pygame as p

stars = []


def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    colors = [p.Color(255, 102, 242), p.Color(123, 6, 158)]

    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)



def drawStars(screen):
    global stars  # stars listesini global olarak işaretliyoruz
    for star in stars:
        p.draw.circle(screen, (255, 255, 0), (int(star['x']), int(star['y'])), star['size'])
        star['x'] += star['dx']
        star['y'] += star['dy']
        star['life'] -= 1
    for star in stars[:]:
        if star['life'] <= 0:
            stars.remove(star)



def generateStars(x, y, count=30):
    """Yıldızları oluşturur"""
    global stars
    for _ in range(count):
        stars.append({
            'x': x,
            'y': y,
            'dx': random.uniform(-3, 3),
            'dy': random.uniform(-3, 3),
            'size': random.randint(2, 5),
            'life': random.randint(40, 100)
        })

if __name__ == "__main__":
    from ChessStarter import main
    main()