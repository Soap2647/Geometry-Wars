"""Parçacık sistemi yöneticisi modülü."""
import math
import random
import pygame
from settings import COLORS
from src.effects.particle import Particle


class ParticleSystem:
    """
    Tüm parçacıkları yöneten sistem.
    Patlama efekti oluşturur, günceller ve çizer.
    """

    def __init__(self):
        self._particles: list[Particle] = []

    def explode(self, x: float, y: float, color: tuple,
                count: int = 20, speed_min: float = 50.0,
                speed_max: float = 200.0, lifetime_min: float = 0.4,
                lifetime_max: float = 0.9, size_min: float = 2.0,
                size_max: float = 5.0) -> None:
        """
        Belirtilen konumda patlama efekti oluştur.
        İki farklı renk (sıcak ve soğuk) karışımıyla neon patlama yaratır.
        """
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(speed_min, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            # Sıcak/soğuk renk karışımı
            if random.random() < 0.6:
                p_color = color
            elif random.random() < 0.5:
                p_color = COLORS['particle_hot']
            else:
                p_color = COLORS['particle_cool']

            lifetime = random.uniform(lifetime_min, lifetime_max)
            size = random.uniform(size_min, size_max)
            friction = random.uniform(0.88, 0.96)

            self._particles.append(
                Particle(x, y, vx, vy, p_color, lifetime, size, friction)
            )

        # Ek parlama parçacıkları - daha büyük, kısa ömürlü
        for _ in range(count // 4):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self._particles.append(
                Particle(x, y, vx, vy, (255, 255, 220),
                         random.uniform(0.1, 0.3),
                         random.uniform(4, 8), 0.85)
            )

    def spark(self, x: float, y: float, direction: pygame.Vector2,
              color: tuple, count: int = 5) -> None:
        """
        Mermi çarpmasında küçük kıvılcım efekti.
        Belirtilen yönde dağılım gösterir.
        """
        base_angle = math.atan2(direction.y, direction.x)
        for _ in range(count):
            spread = random.uniform(-math.pi / 4, math.pi / 4)
            angle = base_angle + spread + math.pi  # Geri çıkan kıvılcımlar
            speed = random.uniform(30, 120)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self._particles.append(
                Particle(x, y, vx, vy, color,
                         random.uniform(0.2, 0.5),
                         random.uniform(1.5, 3.5), 0.88)
            )

    def update(self, dt: float) -> None:
        """Tüm parçacıkları güncelle, ölü olanları temizle."""
        for p in self._particles:
            p.update(dt)
        # Aktif olmayan parçacıkları listeden çıkar
        self._particles = [p for p in self._particles if p.active]

    def draw(self, surface: pygame.Surface) -> None:
        """Tüm aktif parçacıkları çiz."""
        for p in self._particles:
            p.draw(surface)

    @property
    def count(self) -> int:
        """Aktif parçacık sayısı."""
        return len(self._particles)

    def clear(self) -> None:
        """Tüm parçacıkları temizle."""
        self._particles.clear()
