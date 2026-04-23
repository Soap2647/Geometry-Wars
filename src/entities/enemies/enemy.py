"""Soyut düşman temel sınıfı modülü."""
import math
import pygame
from src.entities.game_object import GameObject


class Enemy(GameObject):
    """
    Tüm düşman türlerinin soyut temel sınıfı.
    GameObject'ten kalıtım alır (Inheritance).
    Sağlık sistemi, parlama efekti ve hasar alma mantığını içerir.
    """

    def __init__(self, x: float, y: float, health: int, color: tuple, score_value: int):
        super().__init__(x, y)
        self._health = health           # Düşman can puanı
        self._max_health = health
        self._color = color             # Ana renk
        self._score_value = score_value # Öldürünce verilen puan
        self._rotation = 0.0            # Dönüş açısı (derece)
        self._rotation_speed = 60.0     # Derece/saniye
        self._flash_timer = 0.0         # Hasar aldığında beyaz flash süresi
        self._flash_duration = 0.1      # Saniye cinsinden flash süresi

    @property
    def score_value(self) -> int:
        """Öldürülünce verilen puan değeri."""
        return self._score_value

    @property
    def health(self) -> int:
        """Mevcut can değeri."""
        return self._health

    def take_damage(self, amount: int = 1) -> bool:
        """
        Düşmana hasar ver.
        Ölürse True döner, aksi halde False.
        """
        self._health -= amount
        self._flash_timer = self._flash_duration
        if self._health <= 0:
            self._active = False
            return True
        return False

    def on_death(self):
        """
        Ölüm olayı - alt sınıflarda override edilebilir.
        Splitter gibi düşmanlar bu metodu kullanarak yavru düşman üretir.
        Varsayılan olarak None döner.
        """
        return None

    def _draw_glow_polygon(self, surface: pygame.Surface, points: list,
                           color: tuple, glow_color: tuple, layers: int = 3) -> None:
        """
        Parlama efektiyle çokgen çiz.
        SRCALPHA yüzeyleri kullanarak katmanlı glow efekti oluşturur.
        """
        if len(points) < 3:
            return

        # Çokgenin sınır kutusunu hesapla
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        max_y = max(ys)
        w = max(int(max_x - min_x) + 40, 4)
        h = max(int(max_y - min_y) + 40, 4)
        pad = 20

        # Glow katmanlarını çiz (dıştan içe, azalan opaklıkla)
        for i in range(layers, 0, -1):
            glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            alpha = int(80 // layers * i)
            scale = 1.0 + (i * 0.3)
            cx = (min_x + max_x) / 2
            cy = (min_y + max_y) / 2
            scaled_points = [
                (pad + (p[0] - cx) * scale + (cx - min_x),
                 pad + (p[1] - cy) * scale + (cy - min_y))
                for p in points
            ]
            glow_col = (glow_color[0], glow_color[1], glow_color[2], alpha)
            pygame.draw.polygon(glow_surf, glow_col, scaled_points, 0)
            surface.blit(glow_surf, (int(min_x) - pad, int(min_y) - pad))

        # Flash efekti - hasar alındığında beyaz yanma
        if self._flash_timer > 0:
            flash_alpha = int(255 * (self._flash_timer / self._flash_duration))
            flash_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            local_points = [(p[0] - min_x + pad, p[1] - min_y + pad) for p in points]
            pygame.draw.polygon(flash_surf, (255, 255, 255, flash_alpha), local_points, 0)
            surface.blit(flash_surf, (int(min_x) - pad, int(min_y) - pad))

        # Ana şekli çiz
        temp_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        local_points = [(p[0] - min_x + pad, p[1] - min_y + pad) for p in points]
        pygame.draw.polygon(temp_surf, (color[0], color[1], color[2], 220), local_points, 0)
        pygame.draw.polygon(temp_surf, (255, 255, 255, 100), local_points, 2)
        surface.blit(temp_surf, (int(min_x) - pad, int(min_y) - pad))

    def _get_rotated_polygon_points(self, num_sides: int, radius: float) -> list:
        """
        Döndürülmüş düzenli çokgenin köşe noktalarını hesapla.
        """
        points = []
        angle_offset = math.radians(self._rotation)
        for i in range(num_sides):
            angle = angle_offset + (2 * math.pi * i / num_sides)
            px = self._x + radius * math.cos(angle)
            py = self._y + radius * math.sin(angle)
            points.append((px, py))
        return points

    def update(self, dt: float, player_pos: pygame.Vector2 = None) -> None:
        """Temel güncelleme - flash timer yönetimi. Alt sınıflar bu metodu genişletir."""
        if self._flash_timer > 0:
            self._flash_timer -= dt
            if self._flash_timer < 0:
                self._flash_timer = 0
        # Sürekli dönüş
        self._rotation = (self._rotation + self._rotation_speed * dt) % 360

    def draw(self, surface: pygame.Surface) -> None:
        """Alt sınıflarda override edilmelidir."""
        pass

    def get_radius(self) -> float:
        """Alt sınıflarda override edilmelidir."""
        return 15.0
