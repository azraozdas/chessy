import random
import ChessEngine

def evaluateBoard(game_state):
    """
    Çok basit bir değerlendirme fonksiyonu:
    - Beyaz taşlar için pozitif değer,
    - Siyah taşlar için negatif değer
    Temel taş puanları: p=1, N=3, B=3, R=5, Q=9, K=0

    Gelişmiş AI'lerde konum, piyon yapı düzeni, şah güvenliği, vb. faktörler de hesaba katılır.
    """
    # Taş puanları (örnek)
    piece_scores = {
        'K': 0,  # Şah için özel muamele gerekebilir, burada 0 diyoruz
        'Q': 9,
        'R': 5,
        'B': 3,
        'N': 3,
        'p': 1
    }

    score = 0
    for row in range(8):
        for col in range(8):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_type = piece[1]  # 'Q', 'R', 'B', ...
                if piece_type in piece_scores:
                    piece_value = piece_scores[piece_type]
                else:
                    piece_value = 0

                # Beyaz taşsa skora ekle, siyah taşsa çıkar
                if piece[0] == 'w':
                    score += piece_value
                else:
                    score -= piece_value
    return score


def findRandomMove(validMoves):
    """
    Elimizdeki geçerli hamleler listesinden rastgele bir hamle döndürür (basit AI).
    """
    if not validMoves:
        return None
    return random.choice(validMoves)


def minimax_alpha_beta(game_state, valid_moves, depth, alpha, beta, maximizing_player):
    """
    Alfa-beta budamalı Minimax fonksiyonu.
    - depth: arama derinliği (0'a ulaşınca veya oyun bittiğinde durur)
    - alpha, beta: budama için alt-üst sınırlar
    - maximizing_player = True → Beyaz'ın sırası (en yüksek skoru arar)
                         False → Siyah'ın sırası (skoru düşürmeye çalışır)

    Dönüş: (en_iyi_skor, en_iyi_hamle)
    """

    # Oyun bitti mi veya derinlik 0 mı?
    if depth == 0 or game_state.checkmate or game_state.stalemate:
        score = evaluateBoard(game_state)
        return (score, None)

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')

        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            evaluation = minimax_alpha_beta(game_state,
                                            next_moves,
                                            depth - 1,
                                            alpha,
                                            beta,
                                            False)[0]
            game_state.undoMove()

            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move

            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break  # Beta kesme
        return (max_eval, best_move)

    else:
        min_eval = float('inf')

        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            evaluation = minimax_alpha_beta(game_state,
                                            next_moves,
                                            depth - 1,
                                            alpha,
                                            beta,
                                            True)[0]
            game_state.undoMove()

            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move

            beta = min(beta, evaluation)
            if beta <= alpha:
                break  # Alfa kesme
        return (min_eval, best_move)


def findBestMoveMinimax(game_state, valid_moves, depth=3):
    """
    Minimax + Alfa-Beta ile en iyi hamleyi bulmaya çalışır.
    - depth=3 → 3 ply arar (beyaz hareketi, siyah hareketi, beyaz hareketi)
      Yüksek depth daha iyi ama daha yavaş.

    Dönüş: En iyi hamleyi (ChessEngine.Move nesnesi) döndürür,
    veya None (hiç hamle yoksa).
    """
    if not valid_moves:
        return None

    maximizing_player = game_state.white_to_move

    best_score, best_move = minimax_alpha_beta(
        game_state,
        valid_moves,
        depth,
        float('-inf'),
        float('inf'),
        maximizing_player
    )

    if best_move is None:
        # Yine de rastgele dönmek isteyebilirsiniz
        return findRandomMove(valid_moves)
    else:
        return best_move

###3