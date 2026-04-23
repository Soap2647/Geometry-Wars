"""Puan ve çarpan yönetim sistemi modülü."""
import pygame
from settings import COLORS


class FloatingText:
    """
    Ekranda yukarı doğru kayan geçici puan metni.
    Öldürme anında düşmanın üzerinde belirir.
    """

    LIFETIME = 1.2          # Toplam görünür kalma süresi
    RISE_SPEED = 60.0       # Yukarı yükselme hızı (px/s)
    FONT_SIZE = 22

    def __init__(self, text: str, x: float, y: float, color: tuple):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = self.LIFETIME
        self.active = True
        self._font = None   # Font game loop'ta başlatılacak

    def update(self, dt: float) -> None:
        """Metni yukarı taşı ve ömür sayacını azalt."""
        self.y -= self.RISE_SPEED * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Metni solarak çiz."""
        if not self.active:
            return
        # Ömür oranına göre alfa hesapla
        alpha = int(255 * min(1.0, self.lifetime / self.LIFETIME))
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, rect)


class ScoreManager:
    """
    Oyun puanı ve katsal (multiplier) yöneticisi.
    Katsal 4 saniye öldürme olmadığında sıfırlanır.
    """

    MULTIPLIER_RESET_TIME = 4.0     # Saniye - bu sürede öldürme olmazsa sıfırlan
    MAX_MULTIPLIER = 10             # Maksimum katsal değeri

    def __init__(self):
        self._score = 0
        self._multiplier = 1
        self._multiplier_timer = 0.0    # Son öldürmeden bu yana geçen süre
        self._high_score = 0
        self._floating_texts: list[FloatingText] = []
        self._kills_this_wave = 0

    @property
    def score(self) -> int:
        """Mevcut puan."""
        return self._score

    @property
    def multiplier(self) -> int:
        """Mevcut katsal değeri."""
        return self._multiplier

    @property
    def high_score(self) -> int:
        """En yüksek puan."""
        return self._high_score

    @property
    def multiplier_timer(self) -> float:
        """Son öldürmeden bu yana geçen süre."""
        return self._multiplier_timer

    @property
    def multiplier_reset_time(self) -> float:
        """Katsal sıfırlanma süresi."""
        return self.MULTIPLIER_RESET_TIME

    def add_kill(self, base_points: int, position: pygame.Vector2) -> None:
        """
        Öldürme puanı ekle ve katsalı artır.
        Görsel puan metni oluştur.
        """
        actual_points = base_points * self._multiplier
        self._score += actual_points
        self._kills_this_wave += 1

        # Katsalı artır
        if self._multiplier < self.MAX_MULTIPLIER:
            self._multiplier += 1

        # Zamanlayıcıyı sıfırla
        self._multiplier_timer = 0.0

        # Yüksek puan güncelle
        if self._score > self._high_score:
            self._high_score = self._score

        # Görsel puan metni oluştur
        text = f"+{actual_points}"
        if self._multiplier > 1:
            color = COLORS['multiplier']
        else:
            color = COLORS['score_pop']
        self._floating_texts.append(
            FloatingText(text, position.x, position.y, color)
        )

    def update(self, dt: float) -> None:
        """Katsalı ve görsel metinleri güncelle."""
        # Katsal zamanlayıcısı
        self._multiplier_timer += dt
        if self._multiplier_timer >= self.MULTIPLIER_RESET_TIME and self._multiplier > 1:
            self._multiplier = 1
            # Sıfırlama bildirimi (opsiyonel görsel metin)

        # Görsel metinleri güncelle
        for ft in self._floating_texts:
            ft.update(dt)
        self._floating_texts = [ft for ft in self._floating_texts if ft.active]

    def draw_floating_texts(self, surface: pygame.Surface,
                            font: pygame.font.Font) -> None:
        """Tüm aktif görsel puan metinlerini çiz."""
        for ft in self._floating_texts:
            ft.draw(surface, font)

    def reset_wave(self) -> None:
        """Dalga başlangıcında öldürme sayacını sıfırla."""
        self._kills_this_wave = 0

    def reset_all(self) -> None:
        """Tüm oyun istatistiklerini sıfırla (yeni oyun başlangıcı)."""
        if self._score > self._high_score:
            self._high_score = self._score
        self._score = 0
        self._multiplier = 1
        self._multiplier_timer = 0.0
        self._kills_this_wave = 0
        self._floating_texts.clear()
