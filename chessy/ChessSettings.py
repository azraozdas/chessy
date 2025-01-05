import sys
import pygame as p
from ChessConstants import screen, click_sound, clock
from chessy import ChessGlobals

p.init()

SETTINGS_BACKGROUND = p.image.load("images/settingsphoto2.jpg")


def resize_background():
    global SETTINGS_BACKGROUND
    SETTINGS_BACKGROUND = p.transform.smoothscale(SETTINGS_BACKGROUND, screen.get_size())

def settingsScreen():
    running = True

    resize_background()

    while running:
        mouse_pos = p.mouse.get_pos()
        mouse_click = False

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_click = True
            elif event.type == p.VIDEORESIZE:
                p.display.set_mode((event.w, event.h), p.RESIZABLE)
                resize_background()

        screen.blit(SETTINGS_BACKGROUND, (0, 0))

        button_text = "Sound/SFX: ON" if ChessGlobals.is_sfx_on else "Sound/SFX: OFF"
        button_color = (0, 255, 0) if ChessGlobals.is_sfx_on else (128, 128, 128)

        sound_button = p.Rect(0, 0, 300, 100)
        sound_button.center = (screen.get_width() // 2, screen.get_height() // 2)

        p.draw.rect(screen, button_color, sound_button)

        font_size = 50
        while True:
            font = p.font.SysFont("comicsans", font_size, True)
            text_surface = font.render(button_text, True, (0, 0, 0))
            if text_surface.get_width() <= sound_button.width - 40:
                break
            font_size -= 1

        screen.blit(text_surface, (sound_button.centerx - text_surface.get_width() // 2,
                                   sound_button.centery - text_surface.get_height() // 2))

        if sound_button.collidepoint(mouse_pos) and mouse_click:
            ChessGlobals.is_sfx_on = not ChessGlobals.is_sfx_on
            if ChessGlobals.is_sfx_on:
                click_sound.play()
                p.mixer.music.load("sounds/menuchessysong.mp3")
                p.mixer.music.play(-1)
            else:
                p.mixer.music.stop()
                p.mixer.stop()

        return_font = p.font.SysFont("comicsans", 30, True)
        return_text_surface = return_font.render("Return to Menu", True, (255, 255, 0))
        return_button = p.Rect(0, 0, 250, 60)
        return_button.topleft = (20, 20)

        p.draw.rect(screen, (123, 6, 158), return_button)
        screen.blit(return_text_surface, (return_button.centerx - return_text_surface.get_width() // 2,
                                          return_button.centery - return_text_surface.get_height() // 2))

        if return_button.collidepoint(mouse_pos) and mouse_click:
            from ChessMenu import mainMenu
            mainMenu()
            return

        p.display.flip()
        clock.tick(60)