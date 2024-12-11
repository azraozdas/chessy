import pygame
import pygame as p

from chessy import chessEngine

p.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadimages():
    pieces = ["Pawn_W", "Rook_W", "Knight_W", "Bishop_W", "King_W", "Queen_W", "Pawn_B", "Rook_B", "Knight_B", "Bishop_B", "King_B", "Queen_B"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

        def main():
            p.init()
            screen = p.display.set_mode((WIDTH, HEIGHT))
            clock = p.time.Clock()
            screen.fill(p.Color("white"))
            gs = chessEngine.GameState()
            print(gs.board)
            loadimages()
            running = True

            while running:
                for e in p.event.get():
                    if e.type == p.QUIT:
                        running = False

                drawGameState(screen, gs)
                clock.tick(MAX_FPS)
                p.display.flip()

        def drawPieces(screen, board):
            pass

        def drawGameState(screen, gs):
            drawBoard(screen)
            drawPieces(screen, gs.board)

        def drawBoard(screen):
            colors = [p.Color("white"), p.Color("gray")]
            for r in range(DIMENSION):
                for c in range(DIMENSION):
                    color = colors[((r + c) % 2)]
                    p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, c * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        main()