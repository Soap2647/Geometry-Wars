"""Tek parçacık (particle) sınıfı modülü."""
import pygame


class Particle:
    """
    Tek bir parçacığı temsil eder.
    Konum, hız, renk, ömür ve sürtünme özellikleri taşır.
    Patlama ve görsel efektlerde kullanılır.
    """

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: tuple, lifetime: float, size: float = 3.0,
                 friction: float = 0.92):
        """
        x, y       : Başlangıç konumu
        vx, vy     : Başlangıç hızı
        color      : RGB renk tuple'ı
        lifetime   : Toplam ömür (saniye)
        size       : Başlangıç boyutu
        friction   : Her frame'de hıza uygulanan sürtünme katsayısı (0-1)
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.size = size
        self.friction = friction
        self.active = True

    def update(self, dt: float) -> None:
        """Parçacığı bir adım güncelle."""
        if not self.active:
            return

        # Hareketi uygula
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Sürtünme - hızı azalt
        self.vx *= self.friction
        self.vy *= self.friction

        # Ömür sayacı
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            self.lifetime = 0

    def draw(self, surface: pygame.Surface) -> None:
        """Parçacığı çiz - ömür azaldıkça küçülür ve solar."""
        if not self.active:
            return

        # Ömür oranı (0.0 - 1.0)
        life_ratio = self.lifetime / self.max_lifetime

        # Boyut ve opaklık ömürle orantılı
        current_size = max(1, int(self.size * life_ratio))
        alpha = int(255 * life_ratio)

        # SRCALPHA ile şeffaf parçacık çiz
        surf_size = current_size * 2 + 2
        particle_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        draw_color = (
            min(255, self.color[0]),
            min(255, self.color[1]),
            min(255, self.color[2]),
            alpha
        )
        pygame.draw.circle(particle_surf, draw_color,
                           (current_size + 1, current_size + 1), current_size)
        surface.blit(particle_surf,
                     (int(self.x) - current_size - 1,
                      int(self.y) - current_size - 1))
