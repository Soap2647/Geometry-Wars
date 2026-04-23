"""Mermi sınıfı modülü."""
import math
import pygame
from settings import COLORS
from src.entities.game_object import GameObject


class Bullet(GameObject):
    """
    Oyuncu mermisi: elmas şeklinde, sarı renkli, kısa ömürlü.
    Hız: 500 px/s, Ömür: 1.5 saniye, 3 pozisyonluk iz.
    """

    SPEED = 500.0       # piksel/saniye
    LIFETIME = 1.5      # saniye
    RADIUS = 5.0        # çarpışma yarıçapı
    TRAIL_LEN = 3       # iz uzunluğu (pozisyon sayısı)

    def __init__(self, x: float, y: float, direction: pygame.Vector2, owner: str = 'player'):
        super().__init__(x, y)
        # Normalize et
        length = direction.length()
        if length > 0:
            self._vx = direction.x / length * self.SPEED
            self._vy = direction.y / length * self.SPEED
        else:
            self._vx = self.SPEED
            self._vy = 0.0
        self._lifetime = self.LIFETIME
        self._trail = []            # Geçmiş pozisyonlar
        self._trail_timer = 0.0
        self._trail_interval = 0.03 # Her 30ms'de bir trail noktası
        self._owner = owner         # 'player' veya 'enemy'

    @property
    def owner(self) -> str:
        """Mermiyi kimin attığını döndür."""
        return self._owner

    def update(self, dt: float) -> None:
        """Mermiyi ilerlet ve ömür sayacını azalt."""
        # Trail ekle
        self._trail_timer += dt
        if self._trail_timer >= self._trail_interval:
            self._trail_timer = 0.0
            self._trail.append((self._x, self._y))
            if len(self._trail) > self.TRAIL_LEN:
                self._trail.pop(0)

        # Hareketi uygula
        self._x += self._vx * dt
        self._y += self._vy * dt

        # Ömür sayacını azalt
        self._lifetime -= dt
        if self._lifetime <= 0:
            self._active = False

        # Ekran dışına çıkınca devre dışı bırak
        from settings import WINDOW_WIDTH, WINDOW_HEIGHT
        if (self._x < -20 or self._x > WINDOW_WIDTH + 20 or
                self._y < -20 or self._y > WINDOW_HEIGHT + 20):
            self._active = False

    def draw(self, surface: pygame.Surface) -> None:
        """Elmas şeklinde parlayan mermiyi çiz."""
        # Trail çiz
        for i, (tx, ty) in enumerate(self._trail):
            progress = (i + 1) / max(len(self._trail), 1)
            alpha = int(120 * progress)
            size = max(1, int(self.RADIUS * 0.5 * progress))
            trail_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            col = COLORS['bullet']
            pygame.draw.circle(trail_surf, (col[0], col[1], col[2], alpha),
                               (size + 1, size + 1), size)
            surface.blit(trail_surf, (int(tx) - size - 1, int(ty) - size - 1))

        # Glow efekti
        glow_sizes = [self.RADIUS + 6, self.RADIUS + 4, self.RADIUS + 2]
        alphas = [40, 60, 80]
        glow_col = COLORS['bullet_glow']
        for gs, ga in zip(glow_sizes, alphas):
            g_surf = pygame.Surface((int(gs * 2 + 2), int(gs * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(g_surf, (glow_col[0], glow_col[1], glow_col[2], ga),
                               (int(gs + 1), int(gs + 1)), int(gs))
            surface.blit(g_surf, (int(self._x - gs - 1), int(self._y - gs - 1)))

        # Elmas şekli (döndürülmüş kare)
        r = self.RADIUS
        diamond_points = [
            (self._x,     self._y - r),   # Üst
            (self._x + r, self._y),        # Sağ
            (self._x,     self._y + r),   # Alt
            (self._x - r, self._y),        # Sol
        ]
        col = COLORS['bullet']
        pygame.draw.polygon(surface, col, diamond_points, 0)
        pygame.draw.polygon(surface, (255, 255, 200), diamond_points, 1)

    def get_radius(self) -> float:
        """Çarpışma yarıçapını döndür."""
        return self.RADIUS


class EnemyBullet(GameObject):
    """
    Düşman mermisi: daha yavaş, farklı renkte.
    Shooter düşmanı tarafından fırlatılır.
    """

    SPEED = 200.0       # piksel/saniye
    LIFETIME = 3.0      # saniye
    RADIUS = 6.0        # çarpışma yarıçapı

    def __init__(self, x: float, y: float, direction: pygame.Vector2):
        super().__init__(x, y)
        length = direction.length()
        if length > 0:
            self._vx = direction.x / length * self.SPEED
            self._vy = direction.y / length * self.SPEED
        else:
            self._vx = self.SPEED
            self._vy = 0.0
        self._lifetime = self.LIFETIME

    def update(self, dt: float) -> None:
        """Mermiyi ilerlet ve ömür sayacını azalt."""
        self._x += self._vx * dt
        self._y += self._vy * dt
        self._lifetime -= dt
        if self._lifetime <= 0:
            self._active = False
        from settings import WINDOW_WIDTH, WINDOW_HEIGHT
        if (self._x < -20 or self._x > WINDOW_WIDTH + 20 or
                self._y < -20 or self._y > WINDOW_HEIGHT + 20):
            self._active = False

    def draw(self, surface: pygame.Surface) -> None:
        """Turuncu parlayan düşman mermi topunu çiz."""
        col = COLORS['shooter_bullet']
        # Glow
        for gs in [self.RADIUS + 5, self.RADIUS + 3]:
            g_surf = pygame.Surface((int(gs * 2 + 2), int(gs * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(g_surf, (col[0], col[1], col[2], 50),
                               (int(gs + 1), int(gs + 1)), int(gs))
            surface.blit(g_surf, (int(self._x - gs - 1), int(self._y - gs - 1)))
        pygame.draw.circle(surface, col, (int(self._x), int(self._y)), int(self.RADIUS))
        pygame.draw.circle(surface, (255, 220, 150),
                           (int(self._x), int(self._y)), int(self.RADIUS), 1)

    def get_radius(self) -> float:
        """Çarpışma yarıçapını döndür."""
        return self.RADIUS
