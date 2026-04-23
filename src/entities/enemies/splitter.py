"""Bölünen düşman sınıfı modülü."""
import math
import pygame
from settings import COLORS
from src.entities.enemies.enemy import Enemy


class Splitter(Enemy):
    """
    Ölünce 2 Chaser'a bölünen mor sekizgen düşman.
    Yavaş hareket eder ama yüksek can ve puana sahiptir.
    Can: 3, Puan: 75, Hız: 50 px/s
    """

    SPEED = 50.0    # piksel/saniye
    RADIUS = 22.0   # çarpışma yarıçapı
    SCORE = 75      # öldürme puanı

    def __init__(self, x: float, y: float):
        super().__init__(x, y,
                         health=3,
                         color=COLORS['splitter'],
                         score_value=self.SCORE)
        self._rotation_speed = 30.0   # Yavaş dönüş

    def update(self, dt: float, player_pos: pygame.Vector2 = None) -> None:
        """Oyuncuya doğru yavaşça hareket et."""
        super().update(dt, player_pos)
        if player_pos is not None:
            dx = player_pos.x - self._x
            dy = player_pos.y - self._y
            dist = math.hypot(dx, dy)
            if dist > 1.0:
                self._x += (dx / dist) * self.SPEED * dt
                self._y += (dy / dist) * self.SPEED * dt

    def on_death(self):
        """
        Ölünce 2 Chaser düşmanı oluştur.
        Biri soldan biri sağdan çıkar.
        """
        # Döngüsel import'u önlemek için yerel import kullanılır
        from src.entities.enemies.chaser import Chaser
        return [
            Chaser(self._x - 15, self._y),
            Chaser(self._x + 15, self._y),
        ]

    def draw(self, surface: pygame.Surface) -> None:
        """Mor parlayan sekizgen çiz."""
        points = self._get_rotated_polygon_points(8, self.RADIUS)
        self._draw_glow_polygon(surface, points,
                                COLORS['splitter'],
                                COLORS['splitter'],
                                layers=3)

    def get_radius(self) -> float:
        """Çarpışma yarıçapını döndür."""
        return self.RADIUS
