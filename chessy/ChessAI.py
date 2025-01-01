
import random

import ChessEngine

def evaluateBoard(game_state):
    piece_scores = {
        'K': 0,
        'Q': 9,
        'R': 5,
        'B': 3,
        'N': 3,
        'p': 1
    }

    score = 0
    center_squares = [ (3,3), (3,4), (4,3), (4,4) ]

    for row in range(8):
        for col in range(8):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_type = piece[1]
                if piece_type in piece_scores:
                    piece_value = piece_scores[piece_type]
                else:
                    piece_value = 0

                if piece[0] == 'w':
                    score += piece_value
                    if (row, col) in center_squares:
                        score += 0.5
                else:
                    score -= piece_value
                    if (row, col) in center_squares:
                        score -= 0.5

    return score

def findRandomMove(validMoves):
    if not validMoves:
        return None
    return random.choice(validMoves)

def minimax_alpha_beta(game_state, valid_moves, depth, alpha, beta, maximizing_player):
    if depth == 0 or game_state.checkmate or game_state.stalemate:
        return (evaluateBoard(game_state), None)

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')

        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            evaluation = minimax_alpha_beta(game_state, next_moves, depth - 1, alpha, beta, False)[0]
            game_state.undoMove()

            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move

            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return (max_eval, best_move)

    else:
        min_eval = float('inf')

        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            evaluation = minimax_alpha_beta(game_state, next_moves, depth - 1, alpha, beta, True)[0]
            game_state.undoMove()

            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move

            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return (min_eval, best_move)

def findBestMoveMinimax(game_state, valid_moves, depth=6):
    if not valid_moves:
        return None

    _, best_move = minimax_alpha_beta(
        game_state,
        valid_moves,
        depth,
        float('-inf'),
        float('inf'),
        game_state.white_to_move
    )

    if best_move is None:
        return findRandomMove(valid_moves)
    else:
        return best_move

###