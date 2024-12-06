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
        IMAGES[piece] = p.transfore.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
