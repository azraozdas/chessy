import math
import random
import pygame as p

from chessy import ChessGlobals
from chessy.ChessConstants import move_sound, captured_sound

move_channel = p.mixer.Channel(1)

# Yıldızlar efektine dair global liste
stars = []

# Neon animasyonu için faz değişkeni (global)
import pygame as p
import math

neon_phase = 0.0

def lerp_color(color1, color2, t):
    """
    İki renk arasında t oranında lineer interpolasyon (LERP) yapar.
    - color1, color2: Başlangıç ve bitiş renkleri (r, g, b)
    - t: 0 ile 1 arasında bir değer (0 -> color1, 1 -> color2)
    """
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return (r, g, b)

def drawBreathingRectWithColorTransition(screen, colors, rect, transition_speed=0.02, border_width=3, border_radius=15):
    """
    Çerçeve rengi belirli renkler arasında yumuşak geçişlerle değişir.
    - colors: [(r, g, b), ...] Renklerin bir listesi
    - rect: Çerçeve tanımı (x, y, width, height)
    - transition_speed: Renk geçiş hızı
    - border_width: Çerçeve kalınlığı
    - border_radius: Köşe yuvarlatma
    """
    global neon_phase

    # Fazı artırıyoruz
    neon_phase += transition_speed

    # Geçerli renk endeksi ve bir sonraki renk
    current_index = int(neon_phase) % len(colors)
    next_index = (current_index + 1) % len(colors)

    # Fazın kesirli kısmını kullanarak geçiş oranını hesaplıyoruz
    t = neon_phase - int(neon_phase)

    # İki renk arasında geçiş yap
    current_color = lerp_color(colors[current_index], colors[next_index], t)

    # Çerçeveyi çiz
    p.draw.rect(screen, current_color, rect, width=border_width, border_radius=border_radius)


def animateMove(move, screen, board, clock, IMAGES, SQUARE_SIZE, drawBoard, drawPieces):
    if move_sound:
        if ChessGlobals.is_sfx_on:
            move_channel.play(move_sound)

    board[move.start_row][move.start_col] = "--"

    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square

    for frame in range(frame_count + 1):
        row = move.start_row + d_row * frame / frame_count
        col = move.start_col + d_col * frame / frame_count

        drawBoard(screen)
        drawPieces(screen, board)

        piece_rect = p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        screen.blit(IMAGES[move.piece_moved], piece_rect)

        p.display.flip()
        clock.tick(60)

    board[move.end_row][move.end_col] = move.piece_moved

    if move.piece_captured != "--":
        if captured_sound and ChessGlobals.is_sfx_on:
            captured_sound.set_volume(1.0)
            captured_sound.play()

        growAndShrinkEffect(screen, move.piece_moved, move.end_row, move.end_col, SQUARE_SIZE, IMAGES)


def drawSingleSquare(screen, board, row, col, SQUARE_SIZE, IMAGES):
    colors = [p.Color(255, 102, 242), p.Color(123, 6, 158)]
    color = colors[(row + col) % 2]

    square_rect = p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
    p.draw.rect(screen, color, square_rect)

    if board is not None:
        piece = board[row][col]
        if piece != "--":
            screen.blit(IMAGES[piece], square_rect)


def joyEffect(screen, row, col, SQUARE_SIZE):
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
    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

    start_size = SQUARE_SIZE
    min_size = 0
    steps = 15

    for step in range(steps):
        current_size = start_size - (step * (start_size - min_size) // steps)
        if current_size > 0:
            scaled_piece = p.transform.scale(IMAGES[captured_piece], (current_size, current_size))
            rect = scaled_piece.get_rect(center=(center_x, center_y))

            drawSingleSquare(screen, board, row, col, SQUARE_SIZE, IMAGES)
            screen.blit(scaled_piece, rect)

        p.display.flip()
        p.time.delay(20)

    board[row][col] = "--"
    drawSingleSquare(screen, board, row, col, SQUARE_SIZE, IMAGES)


def growAndShrinkEffect(screen, piece, row, col, SQUARE_SIZE, IMAGES):
    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

    start_size = SQUARE_SIZE
    max_size = int(SQUARE_SIZE * 1.5)  # %50 büyüme
    steps = 10

    for step in range(steps):
        if step < steps // 2:
            current_size = start_size + (step * (max_size - start_size) // (steps // 2))
        else:
            current_size = max_size - ((step - steps // 2) * (max_size - start_size) // (steps // 2))

        scaled_piece = p.transform.scale(IMAGES[piece], (current_size, current_size))
        rect = scaled_piece.get_rect(center=(center_x, center_y))

        drawSingleSquare(screen, None, row, col, SQUARE_SIZE, IMAGES)
        screen.blit(scaled_piece, rect)

        p.display.flip()
        p.time.delay(20)


def generateStars(x, y, count=40):
    global stars
    for _ in range(count):
        stars.append({
            'x': x,
            'y': y,
            'dx': random.uniform(-4, 4),
            'dy': random.uniform(-4, 4),
            'size': random.randint(2, 6),
            'color': (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255)
            ),
            'life': random.randint(20, 60)
        })


def drawStars(screen):
    global stars
    for star in stars:
        p.draw.circle(screen, star['color'], (int(star['x']), int(star['y'])), star['size'])
        star['x'] += star['dx']
        star['y'] += star['dy']
        star['life'] -= 1
    stars = [star for star in stars if star['life'] > 0]


if __name__ == "__main__":
    from ChessMain import main
    main()