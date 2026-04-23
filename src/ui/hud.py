"""HUD (Heads-Up Display) - Oyun içi arayüz modülü."""
import math
import pygame
from settings import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT


class HUD:
    """
    Oyun içi bilgi gösterimi.
    Puan, can, dalga numarası, katsal ve timer bar gösterir.
    """

    def __init__(self):
        pygame.font.init()
        # Font yükleme - sistem fontlarından yararlan
        try:
            self._font_large  = pygame.font.SysFont("consolas", 36, bold=True)
            self._font_medium = pygame.font.SysFont("consolas", 24, bold=True)
            self._font_small  = pygame.font.SysFont("consolas", 18)
            self._font_score_pop = pygame.font.SysFont("consolas", 22, bold=True)
        except Exception:
            self._font_large  = pygame.font.Font(None, 42)
            self._font_medium = pygame.font.Font(None, 30)
            self._font_small  = pygame.font.Font(None, 24)
            self._font_score_pop = pygame.font.Font(None, 28)

        self._time = 0.0    # Animasyon için zaman

    def update(self, dt: float) -> None:
        """HUD animasyonunu güncelle."""
        self._time += dt

    def draw(self, surface: pygame.Surface, score: int, lives: int,
             wave: int, multiplier: int, score_manager,
             high_score: int = 0) -> None:
        """
        Tüm HUD elementlerini çiz.
        """
        # --- Puan (sol üst) ---
        self._draw_score(surface, score, high_score)

        # --- Can göstergesi (sol alt) ---
        self._draw_lives(surface, lives)

        # --- Dalga numarası (sağ üst) ---
        self._draw_wave(surface, wave)

        # --- Katsal göstergesi (orta üst) ---
        self._draw_multiplier(surface, multiplier, score_manager)

        # --- Görsel puan metinleri ---
        score_manager.draw_floating_texts(surface, self._font_score_pop)

    def _draw_score(self, surface: pygame.Surface, score: int,
                    high_score: int) -> None:
        """Sol üst köşede puan göster."""
        # Glow efekti için birden fazla çiz
        for offset in [(2, 2), (0, 0)]:
            col = COLORS['ui_glow'] if offset == (2, 2) else COLORS['ui_text']
            alpha = 80 if offset == (2, 2) else 255
            text_surf = self._font_large.render(f"{score:,}", True, col)
            text_surf.set_alpha(alpha)
            surface.blit(text_surf, (20 + offset[0], 15 + offset[1]))

        # "SKOR" etiketi
        label = self._font_small.render("SKOR", True, COLORS['ui_glow'])
        surface.blit(label, (20, 12))

        # Yüksek skor
        if high_score > 0:
            hs_text = self._font_small.render(f"EN YÜKSEK: {high_score:,}", True,
                                              (150, 150, 200))
            surface.blit(hs_text, (20, 60))

    def _draw_lives(self, surface: pygame.Surface, lives: int) -> None:
        """Sol alt köşede can noktaları göster."""
        label = self._font_small.render("CAN", True, COLORS['ui_glow'])
        surface.blit(label, (20, WINDOW_HEIGHT - 55))

        dot_radius = 10
        dot_spacing = 28
        base_x = 20 + dot_radius
        base_y = WINDOW_HEIGHT - 28

        for i in range(3):  # Maksimum 3 can
            x = base_x + i * dot_spacing
            color = COLORS['player'] if i < lives else (40, 40, 60)
            glow_col = COLORS['player_glow']

            if i < lives:
                # Aktif can - parlayan daire
                glow_surf = pygame.Surface((dot_radius * 4, dot_radius * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*glow_col, 80),
                                   (dot_radius * 2, dot_radius * 2), dot_radius * 2)
                surface.blit(glow_surf, (x - dot_radius * 2, base_y - dot_radius * 2))
                pygame.draw.circle(surface, color, (x, base_y), dot_radius)
                pygame.draw.circle(surface, (200, 240, 255), (x, base_y), dot_radius, 2)
            else:
                # Boş can - sadece çizgi
                pygame.draw.circle(surface, color, (x, base_y), dot_radius, 1)

    def _draw_wave(self, surface: pygame.Surface, wave: int) -> None:
        """Sağ üst köşede dalga numarasını göster."""
        text = f"DALGA {wave}"
        text_surf = self._font_medium.render(text, True, COLORS['ui_text'])
        rect = text_surf.get_rect(topright=(WINDOW_WIDTH - 20, 15))
        surface.blit(text_surf, rect)

        # "WAVE" etiketi
        label = self._font_small.render("DALGA", True, COLORS['ui_glow'])
        label_rect = label.get_rect(topright=(WINDOW_WIDTH - 20, 12))
        surface.blit(label, label_rect)

    def _draw_multiplier(self, surface: pygame.Surface, multiplier: int,
                         score_manager) -> None:
        """Ekranın üst ortasında katsal göstergesi."""
        if multiplier <= 1:
            return

        # Nabız animasyonu
        pulse = math.sin(self._time * 4) * 0.15 + 0.85
        scale = int(24 * pulse) + 2

        try:
            font = pygame.font.SysFont("consolas", scale, bold=True)
        except Exception:
            font = pygame.font.Font(None, scale + 6)

        text = f"x{multiplier}"
        # Katsal 10'a yaklaştıkça renk değişir
        if multiplier >= 8:
            color = (255, 100, 50)    # Kırmızımsı
        elif multiplier >= 5:
            color = (255, 200, 0)     # Sarımsı
        else:
            color = COLORS['multiplier']

        text_surf = font.render(text, True, color)
        rect = text_surf.get_rect(midtop=(WINDOW_WIDTH // 2, 10))
        surface.blit(text_surf, rect)

        # Katsal sıfırlanma çubuğu
        self._draw_multiplier_bar(surface, score_manager, rect.bottom + 4)

    def _draw_multiplier_bar(self, surface: pygame.Surface,
                              score_manager, y: int) -> None:
        """
        Katsal sıfırlanma sayacını görsel çubuk olarak göster.
        Çubuk azaldıkça sıfırlanmaya yaklaşıyor.
        """
        reset_time = score_manager.multiplier_reset_time
        elapsed = score_manager.multiplier_timer
        ratio = max(0.0, 1.0 - elapsed / reset_time)

        bar_width = 120
        bar_height = 4
        bx = WINDOW_WIDTH // 2 - bar_width // 2
        by = y

        # Arka plan
        pygame.draw.rect(surface, (30, 30, 50), (bx, by, bar_width, bar_height))

        # Dolu kısım
        fill_w = int(bar_width * ratio)
        if fill_w > 0:
            col = COLORS['multiplier'] if ratio > 0.3 else (255, 100, 50)
            pygame.draw.rect(surface, col, (bx, by, fill_w, bar_height))

        # Kenar çizgisi
        pygame.draw.rect(surface, (60, 60, 100), (bx, by, bar_width, bar_height), 1)

    def draw_wave_transition(self, surface: pygame.Surface, wave: int,
                              timer: float) -> None:
        """
        Dalga geçiş ekranını çiz.
        Büyük "DALGA X" yazısı ve geri sayım gösterir.
        """
        # Yarı şeffaf arka plan overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        # Dalga yazısı - büyük ve parlayan
        try:
            font_title = pygame.font.SysFont("consolas", 72, bold=True)
            font_sub   = pygame.font.SysFont("consolas", 36)
        except Exception:
            font_title = pygame.font.Font(None, 80)
            font_sub   = pygame.font.Font(None, 42)

        cy = WINDOW_HEIGHT // 2

        # Glow yazısı
        for glow_offset in range(3, 0, -1):
            glow_text = font_title.render(f"DALGA {wave}", True, COLORS['ui_glow'])
            glow_text.set_alpha(50 * glow_offset)
            rect = glow_text.get_rect(center=(WINDOW_WIDTH // 2 + glow_offset,
                                               cy - 20 + glow_offset))
            surface.blit(glow_text, rect)

        main_text = font_title.render(f"DALGA {wave}", True, COLORS['ui_text'])
        rect = main_text.get_rect(center=(WINDOW_WIDTH // 2, cy - 20))
        surface.blit(main_text, rect)

        # Geri sayım
        countdown = max(0, int(math.ceil(timer)))
        sub_text = font_sub.render(f"Hazır mısın? {countdown}...", True,
                                   COLORS['multiplier'])
        rect2 = sub_text.get_rect(center=(WINDOW_WIDTH // 2, cy + 50))
        surface.blit(sub_text, rect2)

    def draw_game_over(self, surface: pygame.Surface, score: int,
                        high_score: int, wave: int) -> None:
        """Oyun bitti ekranını çiz."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        try:
            font_big  = pygame.font.SysFont("consolas", 72, bold=True)
            font_med  = pygame.font.SysFont("consolas", 36)
            font_sml  = pygame.font.SysFont("consolas", 24)
        except Exception:
            font_big  = pygame.font.Font(None, 80)
            font_med  = pygame.font.Font(None, 42)
            font_sml  = pygame.font.Font(None, 30)

        cy = WINDOW_HEIGHT // 2 - 60

        # "OYUN BİTTİ" başlığı
        for go in range(3, 0, -1):
            t = font_big.render("OYUN BİTTİ", True, (200, 0, 0))
            t.set_alpha(40 * go)
            r = t.get_rect(center=(WINDOW_WIDTH // 2 + go, cy + go))
            surface.blit(t, r)

        t = font_big.render("OYUN BİTTİ", True, (255, 60, 60))
        r = t.get_rect(center=(WINDOW_WIDTH // 2, cy))
        surface.blit(t, r)

        # Puan bilgileri
        score_t = font_med.render(f"Puan: {score:,}", True, COLORS['score_pop'])
        r2 = score_t.get_rect(center=(WINDOW_WIDTH // 2, cy + 80))
        surface.blit(score_t, r2)

        hs_t = font_med.render(f"En Yüksek: {high_score:,}", True, COLORS['ui_text'])
        r3 = hs_t.get_rect(center=(WINDOW_WIDTH // 2, cy + 120))
        surface.blit(hs_t, r3)

        wave_t = font_sml.render(f"Ulaşılan Dalga: {wave}", True, COLORS['ui_glow'])
        r4 = wave_t.get_rect(center=(WINDOW_WIDTH // 2, cy + 160))
        surface.blit(wave_t, r4)

        # Yeniden oyna butonu
        pulse = math.sin(self._time * 3) * 30
        btn_color = (int(100 + pulse), int(100 + pulse), int(200 + pulse * 0.5))
        btn_t = font_med.render("[ENTER] Yeniden Oyna  [ESC] Çıkış", True, btn_color)
        r5 = btn_t.get_rect(center=(WINDOW_WIDTH // 2, cy + 220))
        surface.blit(btn_t, r5)

    def draw_menu(self, surface: pygame.Surface) -> None:
        """Ana menü ekranını çiz."""
        try:
            font_title = pygame.font.SysFont("consolas", 80, bold=True)
            font_sub   = pygame.font.SysFont("consolas", 30)
            font_info  = pygame.font.SysFont("consolas", 22)
        except Exception:
            font_title = pygame.font.Font(None, 90)
            font_sub   = pygame.font.Font(None, 36)
            font_info  = pygame.font.Font(None, 28)

        cy = WINDOW_HEIGHT // 2 - 80

        # Başlık glow
        glow_colors = [COLORS['ui_glow'], COLORS['player_glow']]
        for i, gc in enumerate(glow_colors):
            t = font_title.render("GEOMETRY WARS", True, gc)
            t.set_alpha(40 + i * 30)
            r = t.get_rect(center=(WINDOW_WIDTH // 2 + (i + 1) * 2,
                                    cy + (i + 1) * 2))
            surface.blit(t, r)

        t = font_title.render("GEOMETRY WARS", True, COLORS['ui_text'])
        r = t.get_rect(center=(WINDOW_WIDTH // 2, cy))
        surface.blit(t, r)

        # Başlamak için tuş
        pulse = math.sin(self._time * 2.5) * 40
        start_col = (int(150 + pulse), int(150 + pulse), int(255))
        start_t = font_sub.render("BAŞLAMAK İÇİN [ENTER] BASIN", True, start_col)
        r2 = start_t.get_rect(center=(WINDOW_WIDTH // 2, cy + 100))
        surface.blit(start_t, r2)

        # Kontroller
        controls = [
            "WASD / Ok Tuşları : Hareket",
            "Fare              : Nişan Al",
            "Sol Tık / Boşluk  : Ateş Et",
            "ESC               : Duraklat",
        ]
        for i, ctrl in enumerate(controls):
            ct = font_info.render(ctrl, True, (120, 120, 180))
            r3 = ct.get_rect(center=(WINDOW_WIDTH // 2, cy + 180 + i * 30))
            surface.blit(ct, r3)

    def draw_paused(self, surface: pygame.Surface) -> None:
        """Duraklat ekranını çiz."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        try:
            font_big = pygame.font.SysFont("consolas", 60, bold=True)
            font_sml = pygame.font.SysFont("consolas", 28)
        except Exception:
            font_big = pygame.font.Font(None, 70)
            font_sml = pygame.font.Font(None, 34)

        t = font_big.render("DURAKLATILDI", True, COLORS['ui_text'])
        r = t.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        surface.blit(t, r)

        t2 = font_sml.render("[ESC] Devam Et  [Q] Ana Menü", True, COLORS['ui_glow'])
        r2 = t2.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
        surface.blit(t2, r2)

    @property
    def score_pop_font(self) -> pygame.font.Font:
        """Puan pop-up fontu."""
        return self._font_score_pop
