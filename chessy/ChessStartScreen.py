
import pygame
import sys

def intro_screen():
    # Pygame'i başlat
    pygame.init()
    pygame.mixer.init()

    # Müzik dosyasını yükle ve çal
    pygame.mixer.music.load("sounds/introchessysong.mp3")
    pygame.mixer.music.play(-1)  # -1 sonsuz döngüde çalar

    # Ekran boyutlarını al
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Intro Animation")

    # Saat nesnesi oluştur
    clock = pygame.time.Clock()

    # Yazı tipi ve metin ayarları
    font = pygame.font.Font(None, 200)
    text = font.render("CHESSY", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))

    # Resim ayarları
    uelogo = pygame.image.load("images/uelogo.png").convert_alpha()
    uelogo_rect = uelogo.get_rect(center=(screen_width / 2, screen_height / 2))

    kingsgambitlogo = pygame.image.load("images/kingsgambitteamlogo.png").convert_alpha()
    kingsgambitlogo_rect = kingsgambitlogo.get_rect(center=(screen_width / 2, screen_height / 2))

    # Alfa değeri (şeffaflık) ayarları
    alpha = 0
    text.set_alpha(alpha)
    uelogo.set_alpha(alpha)
    kingsgambitlogo.set_alpha(alpha)

    # Zaman ayarları
    wait_time = 2000  # Bekleme süresi (2 saniye)
    fade_in_time = 2000  # 2 saniyede belirginleşme
    fade_out_time = 2000  # 2 saniyede kaybolma
    pause_between = 1000  # Fazlar arasında bekleme süresi

    # Zamanlayıcıyı başlat
    start_ticks = pygame.time.get_ticks()

    # Geçiş durumu (uelogo -> kingsgambitlogo -> CHESSY)
    phase = "uelogo"  # İlk olarak "uelogo" gösterilecek

    # Ana döngü
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Geçen süreyi hesapla
        elapsed_ticks = pygame.time.get_ticks() - start_ticks

        # uelogo için geçiş
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
                    phase = "kingsgambitlogo"
                    start_ticks = pygame.time.get_ticks()  # Yeni faz için zamanlayıcıyı sıfırla

            uelogo.set_alpha(alpha)
            screen.fill((0, 0, 0))
            screen.blit(uelogo, uelogo_rect)

        # kingsgambitlogo için geçiş
        elif phase == "kingsgambitlogo":
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
                    start_ticks = pygame.time.get_ticks()  # Yeni faz için zamanlayıcıyı sıfırla

            kingsgambitlogo.set_alpha(alpha)
            screen.fill((0, 0, 0))
            screen.blit(kingsgambitlogo, kingsgambitlogo_rect)

        # CHESSY yazısı için geçiş
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
                    running = False  # Her şey bitti, programı sonlandır

            text.set_alpha(alpha)
            screen.fill((0, 0, 0))
            screen.blit(text, text_rect)

        # Ekranı güncelle
        pygame.display.flip()

        # Kare hızını sınırlama
        clock.tick(60)

    # Müzik durdur
    pygame.mixer.music.stop()

    return

#####