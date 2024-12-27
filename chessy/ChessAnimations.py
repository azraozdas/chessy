import random
import pygame as p
import ChessMenu
from chessy.ChessConstants import move_sound, captured_sound

stars = []


def animateMove(move, screen, board, clock, IMAGES, SQUARE_SIZE, drawBoard, drawPieces):
    """
    Perform the move animation and trigger effects after the animation completes.
    """
    from ChessAnimations import growAndShrinkEffect

    # Hareket başlangıcında ses efekti çal (eğer başka bir ses çalmıyorsa)
    if move_sound and not p.mixer.get_busy():
        move_sound.play()

    # Başlangıç karesini tahtada hemen temizle
    board[move.start_row][move.start_col] = "--"

    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square

    for frame in range(frame_count + 1):
        row = move.start_row + d_row * frame / frame_count
        col = move.start_col + d_col * frame / frame_count

        # Tahtayı ve taşları yeniden çiz
        drawBoard(screen)
        drawPieces(screen, board)

        # Hareket eden taşı geçici pozisyonda çiz
        piece_rect = p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        screen.blit(IMAGES[move.piece_moved], piece_rect)

        # Ekranı güncelle
        p.display.flip()
        clock.tick(60)

    # Tahtanın yeni durumunu güncelle
    board[move.end_row][move.end_col] = move.piece_moved

    # Eğer taş yakalanıyorsa, capture yapan taş için büyüyüp küçülme efekti uygula
    if move.piece_captured != "--":
        if captured_sound:
            captured_sound.play()
        growAndShrinkEffect(screen, move.piece_moved, move.end_row, move.end_col, SQUARE_SIZE, IMAGES)


def drawSingleSquare(screen, board, row, col, SQUARE_SIZE, IMAGES):
    """
    Redraw a single square on the board.
    """
    # Renkleri doğru ayarla
    colors = [p.Color(255, 102, 242), p.Color(123, 6, 158)]
    color = colors[(row + col) % 2]

    # Kareyi temizle
    square_rect = p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
    p.draw.rect(screen, color, square_rect)

    # Eğer `board` geçerliyse ve karede taş varsa, taşı yeniden çiz
    if board is not None:
        piece = board[row][col]
        if piece != "--":
            screen.blit(IMAGES[piece], square_rect)


def joyEffect(screen, row, col, SQUARE_SIZE):
    """
    Display a yellow ring (transparent inside) that grows in size and fades away.
    """
    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

    start_radius = SQUARE_SIZE // 10
    max_radius = SQUARE_SIZE // 2
    steps = 20

    for step in range(steps):
        radius = start_radius + (step * (max_radius - start_radius) // steps)
        alpha = 255 - (step * (255 // steps))

        surface = p.Surface((SQUARE_SIZE * 2, SQUARE_SIZE * 2), p.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        p.draw.circle(surface, (255, 255, 0, alpha), (SQUARE_SIZE, SQUARE_SIZE), radius, 3)

        screen.blit(surface, (center_x - SQUARE_SIZE, center_y - SQUARE_SIZE))
        p.display.flip()
        p.time.delay(20)

def popEffect(screen, captured_piece, row, col, SQUARE_SIZE, IMAGES, board):
    """
    Make the captured piece shrink and disappear smoothly.
    """
    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

    start_size = SQUARE_SIZE
    min_size = 0  # Taş tamamen kaybolana kadar küçülecek
    steps = 15  # Küçülme adımları

    for step in range(steps):
        # Mevcut boyutu hesapla
        current_size = start_size - (step * (start_size - min_size) // steps)

        # Taşı yeniden boyutlandır ve konumlandır
        if current_size > 0:  # Boyut sıfır olduğunda artık çizme
            scaled_piece = p.transform.scale(IMAGES[captured_piece], (current_size, current_size))
            rect = scaled_piece.get_rect(center=(center_x, center_y))

            # Kareyi temizle
            drawSingleSquare(screen, board, row, col, SQUARE_SIZE, IMAGES)

            # Yeniden boyutlandırılmış taşı çiz
            screen.blit(scaled_piece, rect)

        # Ekranı güncelle
        p.display.flip()
        p.time.delay(20)

    # Tahtada kareyi temizle (taş tamamen kayboldu)
    board[row][col] = "--"
    drawSingleSquare(screen, board, row, col, SQUARE_SIZE, IMAGES)

def growAndShrinkEffect(screen, piece, row, col, SQUARE_SIZE, IMAGES):
    """
    Make the piece grow and shrink upon reaching the target square.
    """
    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

    start_size = SQUARE_SIZE
    max_size = int(SQUARE_SIZE * 1.5)  # %50 büyüme
    steps = 10  # Daha hızlı animasyon için adım sayısı

    for step in range(steps):
        # Boyutu hesapla (ilk yarıda büyüme, ikinci yarıda küçülme)
        if step < steps // 2:
            current_size = start_size + (step * (max_size - start_size) // (steps // 2))
        else:
            current_size = max_size - ((step - steps // 2) * (max_size - start_size) // (steps // 2))

        # Taşı yeniden boyutlandır
        scaled_piece = p.transform.scale(IMAGES[piece], (current_size, current_size))
        rect = scaled_piece.get_rect(center=(center_x, center_y))

        # Kareyi temizlemeden taşı çiz
        drawSingleSquare(screen, None, row, col, SQUARE_SIZE, IMAGES)
        screen.blit(scaled_piece, rect)

        # Ekranı güncelle
        p.display.flip()
        p.time.delay(20)

def generateStars(x, y, count=40):
    """Generate stars at the specified location."""
    global stars
    for _ in range(count):
        stars.append({
            'x': x,
            'y': y,
            'dx': random.uniform(-4, 4),  # Stars move in random directions
            'dy': random.uniform(-4, 4),
            'size': random.randint(2, 6),  # Random star sizes
            'color': (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)),  # Random colors
            'life': random.randint(20, 60)
        })


def drawStars(screen):
    """Draw stars and update their position."""
    global stars
    for star in stars:
        p.draw.circle(screen, star['color'], (int(star['x']), int(star['y'])), star['size'])
        star['x'] += star['dx']
        star['y'] += star['dy']
        star['life'] -= 1
    stars = [star for star in stars if star['life'] > 0]  # Remove stars that have "died"

if __name__ == "__main__":
    from ChessMain import main
    main()

##