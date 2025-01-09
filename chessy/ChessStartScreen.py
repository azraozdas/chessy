
import pygame
from ChessConstants import SCREEN_WIDTH, SCREEN_HEIGHT, screen


def intro_screen():
    pygame.init()
    pygame.mixer.init()

    pygame.mixer.music.load("sounds/introchessysong.mp3")
    pygame.mixer.music.play(-1)


    pygame.display.set_caption("Intro Animation")

    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Times New Roman", 200)

    text = font.render("CHESSY", True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    uelogo = pygame.image.load("images/uelogo.png").convert_alpha()
    uelogo_rect = uelogo.get_rect(center=(SCREEN_WIDTH/ 2, SCREEN_HEIGHT / 2))

    kingsgambitlogo = pygame.image.load("images/teamlogo.png").convert_alpha()
    kingsgambitlogo_rect = kingsgambitlogo.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    alpha = 0
    text.set_alpha(alpha)
    uelogo.set_alpha(alpha)
    kingsgambitlogo.set_alpha(alpha)


    wait_time = 2000
    fade_in_time = 2000
    fade_out_time = 2000
    pause_between = 1000

    start_ticks = pygame.time.get_ticks()

    phase = "uelogo"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elapsed_ticks = pygame.time.get_ticks() - start_ticks

        if phase == "uelogo":
            if elapsed_ticks > wait_time:
                if elapsed_ticks <= wait_time + fade_in_time:
                    alpha = int((elapsed_ticks - wait_time) / fade_in_time * 255)
                elif elapsed_ticks <= wait_time + fade_in_time + 1000:
                    alpha = 255
                elif elapsed_ticks <= wait_time + fade_in_time + 1000 + fade_out_time:
                    alpha = 255 - int((elapsed_ticks - (wait_time + fade_in_time + 1000)) / fade_out_time * 255)
                else:
                    alpha = 0
                    phase = "teamlogo"
                    start_ticks = pygame.time.get_ticks()

            uelogo.set_alpha(alpha)
            screen.fill((0, 0, 0))
            screen.blit(uelogo, uelogo_rect)

        elif phase == "teamlogo":
            elapsed_ticks = pygame.time.get_ticks() - start_ticks

            if elapsed_ticks > pause_between:
                if elapsed_ticks <= pause_between + fade_in_time:
                    alpha = int((elapsed_ticks - pause_between) / fade_in_time * 255)
                elif elapsed_ticks <= pause_between + fade_in_time + 1000:
                    alpha = 255
                elif elapsed_ticks <= pause_between + fade_in_time + 1000 + fade_out_time:
                    alpha = 255 - int((elapsed_ticks - (pause_between + fade_in_time + 1000)) / fade_out_time * 255)
                else:
                    alpha = 0
                    phase = "CHESSY"
                    start_ticks = pygame.time.get_ticks()

            kingsgambitlogo.set_alpha(alpha)
            screen.fill((0, 0, 0))
            screen.blit(kingsgambitlogo, kingsgambitlogo_rect)

        elif phase == "CHESSY":
            elapsed_ticks = pygame.time.get_ticks() - start_ticks

            if elapsed_ticks > pause_between:
                if elapsed_ticks <= pause_between + fade_in_time:
                    alpha = int((elapsed_ticks - pause_between) / fade_in_time * 255)
                elif elapsed_ticks <= pause_between + fade_in_time + 1000:
                    alpha = 255
                elif elapsed_ticks <= pause_between + fade_in_time + 1000 + fade_out_time:
                    alpha = 255 - int((elapsed_ticks - (pause_between + fade_in_time + 1000)) / fade_out_time * 255)
                else:
                    running = False

            text.set_alpha(alpha)
            screen.fill((0, 0, 0))
            screen.blit(text, text_rect)

        pygame.display.flip()

        clock.tick(60)

    pygame.mixer.music.stop()

    return
#3###3#