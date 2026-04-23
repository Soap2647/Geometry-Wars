"""Atıcı düşman sınıfı modülü."""
import math
import pygame
from settings import COLORS
from src.entities.enemies.enemy import Enemy


class Shooter(Enemy):
    """
    Oyuncuya mermi atan turuncu kare düşman.
    Oyuncudan ~200px mesafe tutar ve her 2 saniyede bir ateş eder.
    Can: 2, Puan: 50, Hız: 60 px/s
    """

    SPEED = 60.0            # piksel/saniye
    RADIUS = 18.0           # çarpışma yarıçapı
    SCORE = 50              # öldürme puanı
    PREFERRED_DIST = 200.0  # Oyuncuyla tutulan tercih mesafesi
    SHOOT_INTERVAL = 2.0    # Atış aralığı (saniye)

    def __init__(self, x: float, y: float):
        super().__init__(x, y,
                         health=2,
                         color=COLORS['shooter'],
                         score_value=self.SCORE)
        self._rotation_speed = 45.0
        self._shoot_timer = self.SHOOT_INTERVAL  # İlk atışa kalan süre
        self._pending_shot = False               # Bu frame'de ateş edilecek mi?

    @property
    def pending_shot(self) -> bool:
        """Bu frame'de ateş edilmesi gerekiyor mu?"""
        return self._pending_shot

    def reset_shot(self) -> None:
        """Atış bayrağını sıfırla."""
        self._pending_shot = False

    def update(self, dt: float, player_pos: pygame.Vector2 = None) -> None:
        """Oyuncuyla mesafe koru ve atış zamanlayıcısını yönet."""
        super().update(dt, player_pos)
        self._pending_shot = False

        if player_pos is not None:
            dx = player_pos.x - self._x
            dy = player_pos.y - self._y
            dist = math.hypot(dx, dy)

            if dist > 1.0:
                # Oyuncuya çok yakınsa geri çekil, çok uzaksa yaklaş
                if dist < self.PREFERRED_DIST - 30:
                    # Oyuncudan uzaklaş
                    self._x -= (dx / dist) * self.SPEED * dt
                    self._y -= (dy / dist) * self.SPEED * dt
                elif dist > self.PREFERRED_DIST + 30:
                    # Oyuncuya yaklaş
                    self._x += (dx / dist) * self.SPEED * dt
                    self._y += (dy / dist) * self.SPEED * dt
                # Tercih mesafesindeyse dur (küçük titreme yok)

        # Atış zamanlayıcısı
        self._shoot_timer -= dt
        if self._shoot_timer <= 0:
            self._shoot_timer = self.SHOOT_INTERVAL
            self._pending_shot = True

    def get_shoot_direction(self, player_pos: pygame.Vector2) -> pygame.Vector2:
        """Oyuncuya doğru atış yönünü hesapla."""
        dx = player_pos.x - self._x
        dy = player_pos.y - self._y
        dist = math.hypot(dx, dy)
        if dist > 0:
            return pygame.Vector2(dx / dist, dy / dist)
        return pygame.Vector2(1, 0)

    def draw(self, surface: pygame.Surface) -> None:
        """Turuncu parlayan kare çiz."""
        points = self._get_rotated_polygon_points(4, self.RADIUS)
        self._draw_glow_polygon(surface, points,
                                COLORS['shooter'],
                                COLORS['shooter'],
                                layers=3)

    def get_radius(self) -> float:
        """Çarpışma yarıçapını döndür."""
        return self.RADIUS
