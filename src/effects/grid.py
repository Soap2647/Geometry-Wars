"""Arka plan grid (ızgara) efekti modülü."""
import math
import pygame
from settings import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT


class GridDistortion:
    """Izgara üzerindeki tek bir bozulma noktası."""

    def __init__(self, x: float, y: float, strength: float = 80.0):
        self.x = x
        self.y = y
        self.strength = strength
        self.max_strength = strength
        self.radius = 150.0     # Etki yarıçapı
        self.lifetime = 0.6     # Saniye
        self.max_lifetime = 0.6

    def update(self, dt: float) -> bool:
        """Güncelle. Ömrü bitince False döner."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        # Zaman geçtikçe güç azalır
        ratio = self.lifetime / self.max_lifetime
        self.strength = self.max_strength * ratio
        return True


class Grid:
    """
    Animasyonlu arka plan ızgarası.
    Patlama noktalarında bozulur, sinüs dalgasıyla nabız atar.
    Hücre boyutu: 40px
    """

    CELL_SIZE = 40  # piksel cinsinden hücre boyutu

    def __init__(self):
        self._time = 0.0              # Genel zaman (sinüs animasyonu için)
        self._distortions: list[GridDistortion] = []  # Aktif bozulma noktaları
        self._pulse_phase = 0.0       # Nabız fazı

        # Izgara çizgilerinin koordinatlarını önceden hesapla
        self._v_lines = list(range(0, WINDOW_WIDTH + self.CELL_SIZE, self.CELL_SIZE))
        self._h_lines = list(range(0, WINDOW_HEIGHT + self.CELL_SIZE, self.CELL_SIZE))

    def add_distortion(self, x: float, y: float, strength: float = 80.0) -> None:
        """Belirtilen noktaya patlama bozulması ekle."""
        self._distortions.append(GridDistortion(x, y, strength))

    def update(self, dt: float) -> None:
        """Izgarayı güncelle: zaman ilerlet, bozulmaları yönet."""
        self._time += dt
        self._pulse_phase = math.sin(self._time * 1.5) * 0.5 + 0.5  # 0 ile 1 arası

        # Bozulmaları güncelle, bitenleri kaldır
        self._distortions = [d for d in self._distortions if d.update(dt)]

    def _get_distortion_offset(self, gx: float, gy: float) -> tuple:
        """
        Belirtilen ızgara noktasının bozulma ofsetini hesapla.
        Tüm aktif bozulma noktalarının etkisi toplanır.
        """
        total_dx = 0.0
        total_dy = 0.0
        for d in self._distortions:
            dist = math.hypot(gx - d.x, gy - d.y)
            if dist < d.radius and dist > 1.0:
                # Mesafeye bağlı etki - yakın = güçlü
                factor = (1.0 - dist / d.radius) ** 2
                push_x = (gx - d.x) / dist * d.strength * factor
                push_y = (gy - d.y) / dist * d.strength * factor
                total_dx += push_x
                total_dy += push_y
        return (total_dx, total_dy)

    def draw(self, surface: pygame.Surface) -> None:
        """Izgarayı çiz."""
        # Temel ızgara rengi ve nabız rengi arasında interpolasyon
        base_col = COLORS['grid']
        bright_col = COLORS['grid_bright']
        pulse = self._pulse_phase * 0.3  # Nabız etkisini hafiflet

        line_color = (
            int(base_col[0] + (bright_col[0] - base_col[0]) * pulse),
            int(base_col[1] + (bright_col[1] - base_col[1]) * pulse),
            int(base_col[2] + (bright_col[2] - base_col[2]) * pulse),
        )

        # Bozulmalar varsa - her kesişim noktasını hesaplayarak eğimli çizgiler çiz
        if self._distortions:
            self._draw_distorted(surface, line_color)
        else:
            self._draw_simple(surface, line_color)

    def _draw_simple(self, surface: pygame.Surface, line_color: tuple) -> None:
        """Bozulma yokken basit düz çizgiler çiz (daha performanslı)."""
        # Dikey çizgiler
        for x in self._v_lines:
            # Sinüs dalgası ile hafif titreme
            offset = math.sin(self._time * 0.8 + x * 0.05) * 1.5
            pygame.draw.line(surface, line_color,
                             (x + int(offset), 0),
                             (x + int(offset), WINDOW_HEIGHT), 1)

        # Yatay çizgiler
        for y in self._h_lines:
            offset = math.sin(self._time * 0.8 + y * 0.05) * 1.5
            pygame.draw.line(surface, line_color,
                             (0, y + int(offset)),
                             (WINDOW_WIDTH, y + int(offset)), 1)

    def _draw_distorted(self, surface: pygame.Surface, line_color: tuple) -> None:
        """
        Bozulma noktaları varken segment segment çiz.
        Her hücre kesişimi ayrı hesaplanır - ızgarayı elastik gösterir.
        """
        cols = len(self._v_lines)
        rows = len(self._h_lines)

        # Tüm kesişim noktalarını önceden hesapla
        pts = {}
        for ci, gx in enumerate(self._v_lines):
            for ri, gy in enumerate(self._h_lines):
                dx, dy = self._get_distortion_offset(float(gx), float(gy))
                # Sinüs ofseti ekle
                sx = math.sin(self._time * 0.8 + gx * 0.05) * 1.5
                sy = math.sin(self._time * 0.8 + gy * 0.05) * 1.5
                pts[(ci, ri)] = (int(gx + dx + sx), int(gy + dy + sy))

        # Yatay segmentleri çiz
        for ri in range(rows):
            for ci in range(cols - 1):
                p1 = pts[(ci, ri)]
                p2 = pts[(ci + 1, ri)]
                pygame.draw.line(surface, line_color, p1, p2, 1)

        # Dikey segmentleri çiz
        for ci in range(cols):
            for ri in range(rows - 1):
                p1 = pts[(ci, ri)]
                p2 = pts[(ci, ri + 1)]
                pygame.draw.line(surface, line_color, p1, p2, 1)
