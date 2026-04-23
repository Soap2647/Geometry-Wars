"""Oyuncu sınıfı modülü."""
import math
import pygame
from settings import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT
from src.entities.game_object import GameObject


class Player(GameObject):
    """
    Oyuncu sınıfı.
    WASD ile hareket, fare ile nişan alma ve ateş etme.
    Trail (iz) efekti, 3 can, hasar sonrası geçici dokunulmazlık.
    """

    SPEED = 250.0               # piksel/saniye
    SHOOT_INTERVAL = 0.15       # Saniye cinsinden ateş aralığı
    RADIUS = 14.0               # Çarpışma yarıçapı
    INVINCIBLE_DURATION = 2.0   # Hasar sonrası dokunulmazlık süresi (saniye)
    MAX_LIVES = 3               # Başlangıç can sayısı
    TRAIL_LENGTH = 12           # Trail pozisyon sayısı

    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self._lives = self.MAX_LIVES
        self._shoot_timer = 0.0
        self._invincible_timer = 0.0    # 0 ise dokunulmazlık yok
        self._angle = 0.0               # Fare'ye bakan açı (derece)
        self._trail = []                # Geçmiş pozisyonlar listesi
        self._trail_timer = 0.0
        self._trail_interval = 0.02     # Her 20ms'de bir trail noktası ekle
        self._flicker = True            # Dokunulmazlık sırasında yanıp sönme durumu
        self._flicker_timer = 0.0

    @property
    def lives(self) -> int:
        """Kalan can sayısı."""
        return self._lives

    @property
    def is_invincible(self) -> bool:
        """Oyuncu şu an dokunulmaz mı?"""
        return self._invincible_timer > 0

    @property
    def shoot_ready(self) -> bool:
        """Ateş etmeye hazır mı?"""
        return self._shoot_timer <= 0

    def reset_shoot_timer(self) -> None:
        """Ateş zamanlayıcısını sıfırla."""
        self._shoot_timer = self.SHOOT_INTERVAL

    def take_hit(self) -> bool:
        """
        Düşmandan hasar al.
        Dokunulmazsa False döner (hasar almaz).
        Ölürse (can = 0) True döner.
        """
        if self._invincible_timer > 0:
            return False
        self._lives -= 1
        self._invincible_timer = self.INVINCIBLE_DURATION
        return self._lives <= 0

    def respawn(self, x: float, y: float) -> None:
        """Belirtilen konumda yeniden doğ."""
        self._x = x
        self._y = y
        self._invincible_timer = self.INVINCIBLE_DURATION
        self._trail.clear()

    def update(self, dt: float) -> None:
        """Oyuncu güncellemesi: hareket, zamanlayıcılar, trail."""
        # Ateş zamanlayıcısı
        if self._shoot_timer > 0:
            self._shoot_timer -= dt

        # Dokunulmazlık zamanlayıcısı
        if self._invincible_timer > 0:
            self._invincible_timer -= dt
            self._flicker_timer += dt
            if self._flicker_timer >= 0.08:  # 80ms'de bir yanıp söner
                self._flicker = not self._flicker
                self._flicker_timer = 0.0
        else:
            self._flicker = True
            self._flicker_timer = 0.0

        # WASD hareket tuşları
        keys = pygame.key.get_pressed()
        vx, vy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy += 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx += 1.0

        # Normalize (çapraz harekette hız artmasın)
        length = math.hypot(vx, vy)
        if length > 0:
            vx /= length
            vy /= length

        self._x = max(20, min(WINDOW_WIDTH - 20,  self._x + vx * self.SPEED * dt))
        self._y = max(20, min(WINDOW_HEIGHT - 20, self._y + vy * self.SPEED * dt))

        # Fareye bakan açıyı hesapla
        mx, my = pygame.mouse.get_pos()
        dx = mx - self._x
        dy = my - self._y
        self._angle = math.degrees(math.atan2(dy, dx))

        # Trail güncelleme
        self._trail_timer += dt
        if self._trail_timer >= self._trail_interval:
            self._trail_timer = 0.0
            self._trail.append((self._x, self._y))
            if len(self._trail) > self.TRAIL_LENGTH:
                self._trail.pop(0)

    def get_aim_direction(self) -> pygame.Vector2:
        """Fare yönünde normalleştirilmiş birim vektör döndür."""
        rad = math.radians(self._angle)
        return pygame.Vector2(math.cos(rad), math.sin(rad))

    def draw(self, surface: pygame.Surface) -> None:
        """Oyuncuyu çiz: trail, glow, gemi şekli."""
        # Dokunulmazlık sırasında yanıp sönme
        if not self._flicker:
            return

        # Trail efekti - geçmiş pozisyonlar solarak çizilir
        for i, (tx, ty) in enumerate(self._trail):
            progress = (i + 1) / len(self._trail) if self._trail else 1
            alpha = int(60 * progress)
            size = max(2, int(self.RADIUS * 0.4 * progress))
            trail_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            color = COLORS['player_glow']
            pygame.draw.circle(trail_surf, (color[0], color[1], color[2], alpha),
                               (size + 1, size + 1), size)
            surface.blit(trail_surf, (int(tx) - size - 1, int(ty) - size - 1))

        # Glow katmanları
        for glow_r in [self.RADIUS + 10, self.RADIUS + 6, self.RADIUS + 3]:
            glow_surf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
            alpha = max(0, int(40 - (glow_r - self.RADIUS) * 4))
            color = COLORS['player_glow']
            pygame.draw.circle(glow_surf, (color[0], color[1], color[2], alpha),
                               (glow_r + 2, glow_r + 2), glow_r)
            surface.blit(glow_surf, (int(self._x) - glow_r - 2, int(self._y) - glow_r - 2))

        # Gemi şekli: ok/üçgen şeklinde
        angle_rad = math.radians(self._angle)
        # Merkez pozisyon
        cx, cy = self._x, self._y

        # Burun (önce)
        nose_x = cx + math.cos(angle_rad) * (self.RADIUS)
        nose_y = cy + math.sin(angle_rad) * (self.RADIUS)

        # Sol kanat
        left_angle = angle_rad + math.radians(145)
        left_x = cx + math.cos(left_angle) * (self.RADIUS * 0.85)
        left_y = cy + math.sin(left_angle) * (self.RADIUS * 0.85)

        # Sağ kanat
        right_angle = angle_rad - math.radians(145)
        right_x = cx + math.cos(right_angle) * (self.RADIUS * 0.85)
        right_y = cy + math.sin(right_angle) * (self.RADIUS * 0.85)

        # Arka orta
        back_x = cx + math.cos(angle_rad + math.pi) * (self.RADIUS * 0.5)
        back_y = cy + math.sin(angle_rad + math.pi) * (self.RADIUS * 0.5)

        ship_points = [
            (nose_x, nose_y),
            (left_x, left_y),
            (back_x, back_y),
            (right_x, right_y),
        ]

        # Gemi glow efekti (büyütülmüş şeffaf)
        glow_surf2 = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        glow_pts_scaled = []
        for px, py in ship_points:
            vx2 = px - cx
            vy2 = py - cy
            glow_pts_scaled.append((cx + vx2 * 1.5, cy + vy2 * 1.5))
        pygame.draw.polygon(glow_surf2, (0, 100, 200, 50), glow_pts_scaled, 0)
        surface.blit(glow_surf2, (0, 0))

        # Ana gemi
        color = COLORS['player']
        pygame.draw.polygon(surface, color, ship_points, 0)
        pygame.draw.polygon(surface, (200, 240, 255), ship_points, 2)

        # Merkez nokta parlaması
        pygame.draw.circle(surface, (200, 230, 255), (int(cx), int(cy)), 3)

    def get_radius(self) -> float:
        """Çarpışma yarıçapını döndür."""
        return self.RADIUS
