"""Gezgin düşman sınıfı modülü."""
import math
import random
import pygame
from settings import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT
from src.entities.enemies.enemy import Enemy


class Wanderer(Enemy):
    """
    Sinüs dalgası hareketiyle rastgele gezen yeşil beşgen düşman.
    Oyuncuyu aktif olarak kovalamaz, ama alanda dolaşır.
    Can: 1, Puan: 15, Hız: 80 px/s
    """

    SPEED = 80.0        # piksel/saniye
    RADIUS = 16.0       # çarpışma yarıçapı
    SCORE = 15          # öldürme puanı

    def __init__(self, x: float, y: float):
        super().__init__(x, y,
                         health=1,
                         color=COLORS['wanderer'],
                         score_value=self.SCORE)
        self._rotation_speed = 45.0
        # Hareket yönü (açı olarak)
        self._direction = random.uniform(0, 2 * math.pi)
        self._sine_timer = 0.0          # Sinüs dalgası zamanlayıcısı
        self._sine_amplitude = 60.0     # Dalga genliği
        self._sine_frequency = 1.5      # Dalga frekansı
        self._turn_timer = random.uniform(1.5, 3.5)  # Yön değiştirme süresi
        self._turn_interval = random.uniform(1.5, 3.5)

    def update(self, dt: float, player_pos: pygame.Vector2 = None) -> None:
        """Sinüs dalgası hareketiyle güncelle."""
        super().update(dt, player_pos)
        self._sine_timer += dt
        self._turn_timer -= dt

        # Belirli aralıklarla yönü değiştir
        if self._turn_timer <= 0:
            self._direction += random.uniform(-math.pi / 2, math.pi / 2)
            self._turn_timer = self._turn_interval
            self._turn_interval = random.uniform(1.5, 3.5)

        # Ana hareket vektörü
        base_vx = math.cos(self._direction) * self.SPEED
        base_vy = math.sin(self._direction) * self.SPEED

        # Sinüs dalgası - yan sapma
        perp_x = -math.sin(self._direction)
        perp_y = math.cos(self._direction)
        sine_offset = math.sin(self._sine_timer * self._sine_frequency * 2 * math.pi) * self._sine_amplitude

        vx = base_vx + perp_x * sine_offset * 0.5
        vy = base_vy + perp_y * sine_offset * 0.5

        self._x += vx * dt
        self._y += vy * dt

        # Ekran sınırlarında sekme (yansıtma)
        margin = 40
        if self._x < margin:
            self._x = margin
            self._direction = math.pi - self._direction
        elif self._x > WINDOW_WIDTH - margin:
            self._x = WINDOW_WIDTH - margin
            self._direction = math.pi - self._direction

        if self._y < margin:
            self._y = margin
            self._direction = -self._direction
        elif self._y > WINDOW_HEIGHT - margin:
            self._y = WINDOW_HEIGHT - margin
            self._direction = -self._direction

    def draw(self, surface: pygame.Surface) -> None:
        """Yeşil parlayan beşgen çiz."""
        points = self._get_rotated_polygon_points(5, self.RADIUS)
        self._draw_glow_polygon(surface, points,
                                COLORS['wanderer'],
                                COLORS['wanderer'],
                                layers=3)

    def get_radius(self) -> float:
        """Çarpışma yarıçapını döndür."""
        return self.RADIUS
