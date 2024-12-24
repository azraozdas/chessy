"""
Main driver file.
Handling user input.
Displaying current GameStatus object.
"""
import sys
import pygame as p
import ChessEngine
from ChessStarter import loadImages, loadSounds
import ChessConstants  # Genel sabitleri içeren modül
from chessy import ChessAnimations
from chessy.ChessAnimations import generateStars, drawStars
from ChessMenu import mainMenu  # mainMenu doğrudan import ediliyor

import ChessGameLogic

p.init()

def main():
    """Satranç oyununun ana döngüsü."""
    global screen, BOARD_WIDTH, BOARD_HEIGHT, SQUARE_SIZE  # Global değişkenler

    # Pygame ve sesleri yükle
    p.init()
    loadImages()
    loadSounds()  # 🎉 Sesleri yükle

    # Başlangıç ekran ayarları
    screen_width = p.display.Info().current_w
    screen_height = p.display.Info().current_h
    screen = p.display.set_mode((screen_width, screen_height), p.FULLSCREEN)  # Ekranı tam ekran yap
    p.display.set_caption('CHESSY')  # Pencere başlığı

    running = True
    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    square_selected = ()
    player_clicks = []
    game_over = False
    return_button = None  # Return to Menu butonunu başlat
    is_check = False  # Şah durumunu takip etmek için başlangıç değeri
    settings_button = None  # Yeni Settings butonu
    clicked_settings = False

    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.VIDEORESIZE:  # Pencere boyutu değiştirildiğinde
                new_width = event.w - ChessConstants.MOVE_LOG_PANEL_WIDTH
                new_height = event.h
                BOARD_WIDTH = BOARD_HEIGHT = min(new_width, new_height)
                SQUARE_SIZE = BOARD_WIDTH // ChessConstants.DIMENSION
                screen = p.display.set_mode(
                    (BOARD_WIDTH + ChessConstants.MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.FULLSCREEN
                )
                loadImages()
            elif event.type == p.MOUSEBUTTONDOWN:  # Taş hareketlerini işleme
                mouse_pos = p.mouse.get_pos()

                # Return to Menu butonu
                if return_button and return_button.collidepoint(mouse_pos):
                    ChessConstants.click_sound.play()  # 🔊 Click sesi ekleniyor
                    generateStars(
                        return_button.centerx, return_button.centery
                    )  # Yıldız animasyonu butonun ortasında başlat
                    start_time = p.time.get_ticks()
                    while p.time.get_ticks() - start_time < 1000:  # Yıldız animasyonu 1 saniye sürsün
                        screen.fill((0, 0, 0))  # Ekranı temizle (ana menüden bağımsız yıldızlar)
                        drawMoveLog(screen, [])  # Sadece return to menu kısmını çiz
                        drawStars()  # Yıldızları ekrana çiz
                        p.display.flip()
                        ChessConstants.clock.tick(60)
                    mainMenu()  # Yıldız animasyonu tamamlandıktan sonra ana menüye dön
                    return  # Ana menüye dönmek için döngüyü sonlandır

                col = mouse_pos[0] // SQUARE_SIZE
                row = mouse_pos[1] // SQUARE_SIZE

                if 0 <= row < ChessConstants.DIMENSION and 0 <= col < ChessConstants.DIMENSION:
                    if square_selected == (row, col):
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)

                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                ChessConstants.move_sound.play()  # 🔊 Hareket sesi çalıyor
                                ChessAnimations.animateMove(move, game_state, screen, ChessConstants.clock)
                                game_state.board[move.start_row][move.start_col] = "--"

                                if move.piece_captured != "--":
                                    ChessAnimations.celebratePiece(
                                        move.piece_moved, move.end_row, move.end_col, screen, ChessConstants.clock, game_state
                                    )

                                game_state.makeMove(valid_moves[i])

                                if move.getMoveSummary() not in game_state.move_log:
                                    game_state.move_log.append(move.getMoveSummary())

                                move_made = True
                                square_selected = ()
                                player_clicks = []
                                break
                        if not move_made:
                            player_clicks = [square_selected]

            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    game_state.undoMove()
                    move_made = True
                elif event.key == p.K_r:
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    game_over = False

        if move_made:
            valid_moves = game_state.getValidMoves()
            move_made = False

            # Şah durumunu kontrol et
            if game_state.inCheck():
                if not is_check:  # Şah durumu yeni başladıysa
                    ChessConstants.check_sound.play()  # Şah sesini çal
                    is_check = True
            else:
                if is_check:  # Şah durumu sona erdiğinde
                    ChessConstants.check_sound.stop()  # Şah sesini durdur
                    is_check = False

        square_selected = ()  # Varsayılan olarak boş bir tuple
        drawGameState(screen, game_state, square_selected)
        return_button = drawMoveLog(screen, game_state.move_log)  # Hamle logunu ve butonu çiz
        p.display.flip()
        ChessConstants.clock.tick(ChessConstants.MAX_FPS)

        if not game_over:
            drawMoveLog(screen, game_state, ChessConstants.move_log_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        ChessConstants.clock.tick(ChessConstants.MAX_FPS)
        p.display.flip()


def drawMoveLog(screen, game_state, font):
    """
    Draws the move log.

    """
    move_log_rect = p.Rect(BOARD_WIDTH, 0, ChessConstants.MOVE_LOG_PANEL_WIDTH, ChessConstants.MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    main()
