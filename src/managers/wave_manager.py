"""Dalga (wave) yönetim sistemi modülü."""
import random
import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


class WaveManager:
    """
    Düşman dalgalarını yöneten sınıf.
    Her dalga daha fazla ve farklı düşman içerir.
    Dalgalar arasında geçiş animasyonu gösterir.
    """

    TRANSITION_DURATION = 3.0   # Dalga geçişi süresi (saniye)
    SPAWN_MARGIN = 60           # Ekran kenarından spawn mesafesi

    def __init__(self):
        self._wave_number = 0           # Mevcut dalga numarası
        self._spawn_queue: list = []    # Spawn edilecek düşman listesi
        self._transition_timer = 0.0   # Geçiş animasyonu sayacı
        self._in_transition = True      # Dalga geçişinde mi?
        self._wave_active = False       # Dalga aktif mi?
        self._enemies_spawned = 0       # Bu dalgada spawn edilen düşman sayısı
        self._spawn_timer = 0.0         # Sonraki spawn'a kalan süre
        self._spawn_interval = 0.5      # Düşmanlar arası spawn süresi
        self._all_spawned = False       # Tüm düşmanlar spawn edildi mi?

    @property
    def wave_number(self) -> int:
        """Mevcut dalga numarası."""
        return self._wave_number

    @property
    def in_transition(self) -> bool:
        """Dalga geçişinde mi?"""
        return self._in_transition

    @property
    def transition_progress(self) -> float:
        """Geçiş animasyonunun ilerlemesi (0.0 - 1.0)."""
        if self._transition_timer <= 0:
            return 1.0
        return 1.0 - (self._transition_timer / self.TRANSITION_DURATION)

    @property
    def transition_timer(self) -> float:
        """Kalan geçiş süresi."""
        return self._transition_timer

    def start_next_wave(self) -> None:
        """Bir sonraki dalgayı hazırla ve geçiş başlat."""
        self._wave_number += 1
        self._spawn_queue = self._generate_spawn_list(self._wave_number)
        self._enemies_spawned = 0
        self._transition_timer = self.TRANSITION_DURATION
        self._in_transition = True
        self._wave_active = False
        self._all_spawned = False
        self._spawn_timer = 0.0

    def update(self, dt: float) -> list:
        """
        Dalga sistemini güncelle.
        Yeni spawn edilecek düşmanları döndür.
        """
        newly_spawned = []

        if self._in_transition:
            self._transition_timer -= dt
            if self._transition_timer <= 0:
                self._transition_timer = 0
                self._in_transition = False
                self._wave_active = True
            return newly_spawned

        if not self._wave_active or self._all_spawned:
            return newly_spawned

        # Sıradaki düşmanı spawn et
        self._spawn_timer -= dt
        if self._spawn_timer <= 0 and self._spawn_queue:
            self._spawn_timer = self._spawn_interval
            enemy_class = self._spawn_queue.pop(0)
            x, y = self._random_spawn_position()
            enemy = enemy_class(x, y)
            newly_spawned.append(enemy)
            self._enemies_spawned += 1

        if not self._spawn_queue:
            self._all_spawned = True

        return newly_spawned

    def is_wave_complete(self, active_enemy_count: int) -> bool:
        """
        Mevcut dalga tamamlandı mı?
        Tüm düşmanlar spawn edildi ve hayatta kalan düşman yok.
        """
        return self._all_spawned and active_enemy_count == 0 and self._wave_active

    def _random_spawn_position(self) -> tuple:
        """
        Ekranın kenarlarından rastgele bir spawn pozisyonu üret.
        Oyuncudan uzakta başlar.
        """
        side = random.randint(0, 3)
        margin = self.SPAWN_MARGIN

        if side == 0:    # Üst
            return (random.randint(margin, WINDOW_WIDTH - margin), margin)
        elif side == 1:  # Alt
            return (random.randint(margin, WINDOW_WIDTH - margin), WINDOW_HEIGHT - margin)
        elif side == 2:  # Sol
            return (margin, random.randint(margin, WINDOW_HEIGHT - margin))
        else:            # Sağ
            return (WINDOW_WIDTH - margin, random.randint(margin, WINDOW_HEIGHT - margin))

    def _generate_spawn_list(self, wave: int) -> list:
        """
        Dalga numarasına göre düşman listesi oluştur.
        Her dalga giderek zorlaşır.
        """
        # Yerel import - döngüsel bağımlılığı önler
        from src.entities.enemies.chaser import Chaser
        from src.entities.enemies.wanderer import Wanderer
        from src.entities.enemies.shooter import Shooter
        from src.entities.enemies.splitter import Splitter

        spawn_list = []

        if wave == 1:
            # Dalga 1: Sadece Chaser'lar - temel tanıtım
            spawn_list = [Chaser] * 5

        elif wave == 2:
            # Dalga 2: Chaser ve Wanderer karışımı
            spawn_list = [Chaser] * 5 + [Wanderer] * 3
            random.shuffle(spawn_list)

        elif wave == 3:
            # Dalga 3: İlk Shooter gelir
            spawn_list = [Chaser] * 4 + [Wanderer] * 4 + [Shooter] * 2
            random.shuffle(spawn_list)

        elif wave == 4:
            # Dalga 4: İlk Splitter
            spawn_list = ([Chaser] * 5 + [Wanderer] * 3 +
                          [Shooter] * 2 + [Splitter] * 1)
            random.shuffle(spawn_list)

        elif wave == 5:
            # Dalga 5: Zorlu karışım
            spawn_list = ([Chaser] * 6 + [Wanderer] * 4 +
                          [Shooter] * 3 + [Splitter] * 2)
            random.shuffle(spawn_list)

        else:
            # Dalga 6+: Dalga numarasıyla ölçeklenen zorluk
            base = wave - 5
            n_chasers  = 5 + base * 2
            n_wanderers = 3 + base
            n_shooters  = 2 + base
            n_splitters = 1 + base // 2

            spawn_list = ([Chaser]   * n_chasers  +
                          [Wanderer] * n_wanderers +
                          [Shooter]  * n_shooters  +
                          [Splitter] * n_splitters)
            random.shuffle(spawn_list)

        return spawn_list
