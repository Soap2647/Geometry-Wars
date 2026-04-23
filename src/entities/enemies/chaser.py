"""Kovalayıcı düşman sınıfı modülü."""
import math
import pygame
from settings import COLORS
from src.entities.enemies.enemy import Enemy


class Chaser(Enemy):
    """
    Oyuncuyu doğrudan kovalayan kırmızı üçgen düşman.
    Basit ama hızlı - oyuncuya düz çizgide yaklaşır.
    Can: 1, Puan: 25, Hız: 120 px/s
    """

    SPEED = 120.0       # piksel/saniye
    RADIUS = 14.0       # çarpışma yarıçapı
    SCORE = 25          # öldürme puanı

    def __init__(self, x: float, y: float):
        super().__init__(x, y,
                         health=1,
                         color=COLORS['chaser'],
                         score_value=self.SCORE)
        self._rotation_speed = 90.0   # Hızlı dönüş

    def update(self, dt: float, player_pos: pygame.Vector2 = None) -> None:
        """Oyuncuya doğru hareket et."""
        super().update(dt, player_pos)
        if player_pos is not None:
            # Oyuncuya yönelik vektörü hesapla
            dx = player_pos.x - self._x
            dy = player_pos.y - self._y
            dist = math.hypot(dx, dy)
            if dist > 1.0:
                # Normalize et ve hızla çarp
                self._x += (dx / dist) * self.SPEED * dt
                self._y += (dy / dist) * self.SPEED * dt

    def draw(self, surface: pygame.Surface) -> None:
        """Kırmızı parlayan üçgen çiz."""
        points = self._get_rotated_polygon_points(3, self.RADIUS)
        self._draw_glow_polygon(surface, points,
                                COLORS['chaser'],
                                COLORS['chaser'],
                                layers=3)

    def get_radius(self) -> float:
        """Çarpışma yarıçapını döndür."""
        return self.RADIUS
