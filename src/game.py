"""Ana oyun döngüsü ve durum yönetimi modülü."""
import sys
import enum
import pygame
from settings import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE

from src.entities.player import Player
from src.entities.bullet import Bullet, EnemyBullet
from src.effects.particle_system import ParticleSystem
from src.effects.grid import Grid
from src.managers.wave_manager import WaveManager
from src.managers.collision_manager import CollisionManager
from src.managers.score_manager import ScoreManager
from src.ui.hud import HUD


class GameState(enum.Enum):
    """Oyun durumları - Durum Makinesi (State Machine) deseni."""
    MENU            = "menu"
    PLAYING         = "playing"
    PAUSED          = "paused"
    WAVE_TRANSITION = "wave_transition"
    GAME_OVER       = "game_over"


class Game:
    """
    Ana oyun sınıfı. Tüm sistemi bir araya getirir.
    Oyun döngüsünü, event handling'i ve render'ı yönetir.

    Kullanılan OOP prensipleri:
    - Encapsulation (Kapsülleme): private/protected attributelar
    - Composition (Bileşim): Manager sınıfları
    - Polymorphism (Çok Biçimlilik): Enemy alt sınıfları
    - Abstraction (Soyutlama): GameObject ABC
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self._screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.DOUBLEBUF | pygame.HWSURFACE
        )
        self._clock = pygame.time.Clock()
        self._running = True
        self._state = GameState.MENU

        # Oyun nesneleri
        self._player: Player = None
        self._enemies: list = []
        self._bullets: list[Bullet] = []
        self._enemy_bullets: list[EnemyBullet] = []

        # Sistemler
        self._particle_system = ParticleSystem()
        self._grid = Grid()
        self._wave_manager = WaveManager()
        self._collision_manager = CollisionManager()
        self._score_manager = ScoreManager()
        self._hud = HUD()

        # Giriş durumları
        self._shooting = False      # Sürekli ateş tutuluyor mu?

    # -------------------------------------------------------------------------
    # Oyun başlatma ve sıfırlama
    # -------------------------------------------------------------------------

    def _new_game(self) -> None:
        """Yeni bir oyun başlat. Tüm durumları sıfırla."""
        self._player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self._enemies.clear()
        self._bullets.clear()
        self._enemy_bullets.clear()
        self._particle_system.clear()
        self._score_manager.reset_all()

        # Wave Manager'ı sıfırla
        self._wave_manager = WaveManager()
        self._wave_manager.start_next_wave()  # Dalga 1 başlat

        self._state = GameState.WAVE_TRANSITION

    # -------------------------------------------------------------------------
    # Ana oyun döngüsü
    # -------------------------------------------------------------------------

    def run(self) -> None:
        """Ana oyun döngüsü."""
        while self._running:
            dt = self._clock.tick(FPS) / 1000.0  # Saniye cinsinden delta time
            # Çok büyük dt değerlerini kırp (pencere taşındığında vb.)
            dt = min(dt, 0.05)

            self._handle_events()
            self._update(dt)
            self._draw()

        pygame.quit()
        sys.exit()

    # -------------------------------------------------------------------------
    # Olay işleme
    # -------------------------------------------------------------------------

    def _handle_events(self) -> None:
        """Pygame olaylarını işle."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            elif event.type == pygame.KEYDOWN:
                self._on_keydown(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    self._shooting = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self._shooting = False

        # Boşluk tuşu ile sürekli ateş
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self._shooting = True

    def _on_keydown(self, key: int) -> None:
        """Tuşa basılma olayını duruma göre işle."""
        if self._state == GameState.MENU:
            if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                self._new_game()

        elif self._state == GameState.PLAYING:
            if key == pygame.K_ESCAPE:
                self._state = GameState.PAUSED

        elif self._state == GameState.PAUSED:
            if key == pygame.K_ESCAPE:
                self._state = GameState.PLAYING
            elif key == pygame.K_q:
                self._state = GameState.MENU

        elif self._state == GameState.GAME_OVER:
            if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                self._new_game()
            elif key == pygame.K_ESCAPE:
                self._state = GameState.MENU

        elif self._state == GameState.WAVE_TRANSITION:
            pass  # Geçiş sırasında girişi engelle

    # -------------------------------------------------------------------------
    # Güncelleme
    # -------------------------------------------------------------------------

    def _update(self, dt: float) -> None:
        """Oyun durumuna göre güncelle."""
        self._hud.update(dt)

        if self._state == GameState.MENU:
            self._grid.update(dt)

        elif self._state == GameState.PLAYING:
            self._update_playing(dt)

        elif self._state == GameState.WAVE_TRANSITION:
            self._update_transition(dt)

        elif self._state == GameState.PAUSED:
            pass  # Duraklat: sadece HUD animasyonu

        elif self._state == GameState.GAME_OVER:
            self._particle_system.update(dt)
            self._grid.update(dt)

    def _update_transition(self, dt: float) -> None:
        """Dalga geçiş durumunu güncelle."""
        self._grid.update(dt)
        self._particle_system.update(dt)

        # Wave manager'ı güncelle - geçiş bitince PLAYING'e geç
        newly_spawned = self._wave_manager.update(dt)
        for enemy in newly_spawned:
            self._enemies.append(enemy)

        if not self._wave_manager.in_transition:
            self._state = GameState.PLAYING
            self._score_manager.reset_wave()

    def _update_playing(self, dt: float) -> None:
        """Oynanış durumunu güncelle."""
        player_pos = self._player.position

        # --- Oyuncuyu güncelle ---
        self._player.update(dt)

        # --- Ateş etme ---
        if self._shooting and self._player.shoot_ready:
            self._player.reset_shoot_timer()
            direction = self._player.get_aim_direction()
            bullet = Bullet(
                self._player.position.x,
                self._player.position.y,
                direction
            )
            self._bullets.append(bullet)

        # --- Düşmanları güncelle ---
        for enemy in self._enemies:
            if enemy.is_active:
                enemy.update(dt, player_pos)

                # Shooter'ın atış mantığı
                from src.entities.enemies.shooter import Shooter
                if isinstance(enemy, Shooter) and enemy.pending_shot:
                    direction = enemy.get_shoot_direction(player_pos)
                    eb = EnemyBullet(
                        enemy.position.x,
                        enemy.position.y,
                        direction
                    )
                    self._enemy_bullets.append(eb)
                    enemy.reset_shot()

        # --- Mermileri güncelle ---
        for bullet in self._bullets:
            if bullet.is_active:
                bullet.update(dt)

        for eb in self._enemy_bullets:
            if eb.is_active:
                eb.update(dt)

        # --- Çarpışmaları işle ---
        player_hit, new_enemies = self._collision_manager.process_all(
            self._player,
            self._bullets,
            self._enemies,
            self._enemy_bullets,
            self._particle_system,
            self._score_manager,
            self._grid
        )

        # Yeni düşmanları (Splitter bölünmesi) ekle
        for ne in new_enemies:
            self._enemies.append(ne)

        # Oyuncu öldü mü?
        if player_hit and self._player.lives <= 0:
            self._state = GameState.GAME_OVER
            self._particle_system.explode(
                self._player.position.x,
                self._player.position.y,
                COLORS['player'],
                count=40, speed_max=300
            )
            return

        # --- Dalga yönetimi ---
        # Yeni spawn'ları ekle
        newly_spawned = self._wave_manager.update(dt)
        for enemy in newly_spawned:
            self._enemies.append(enemy)

        # Aktif düşman sayısını hesapla
        active_count = sum(1 for e in self._enemies if e.is_active)

        # Dalga tamamlandı mı?
        if self._wave_manager.is_wave_complete(active_count):
            self._wave_manager.start_next_wave()
            self._state = GameState.WAVE_TRANSITION

        # --- Ölü nesneleri temizle ---
        self._enemies = [e for e in self._enemies if e.is_active]
        self._bullets = [b for b in self._bullets if b.is_active]
        self._enemy_bullets = [eb for eb in self._enemy_bullets if eb.is_active]

        # --- Efektleri güncelle ---
        self._particle_system.update(dt)
        self._grid.update(dt)
        self._score_manager.update(dt)

    # -------------------------------------------------------------------------
    # Çizim
    # -------------------------------------------------------------------------

    def _draw(self) -> None:
        """Oyun durumuna göre ekrana çiz."""
        # Arka planı temizle
        self._screen.fill(COLORS['background'])

        if self._state == GameState.MENU:
            self._draw_menu()

        elif self._state == GameState.PLAYING:
            self._draw_playing()

        elif self._state == GameState.PAUSED:
            self._draw_playing()           # Oyunu arka planda göster
            self._hud.draw_paused(self._screen)

        elif self._state == GameState.WAVE_TRANSITION:
            self._draw_playing()           # Grid ve parçacıkları göster
            self._hud.draw_wave_transition(
                self._screen,
                self._wave_manager.wave_number,
                self._wave_manager.transition_timer
            )

        elif self._state == GameState.GAME_OVER:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_menu(self) -> None:
        """Ana menüyü çiz."""
        self._grid.draw(self._screen)
        self._hud.draw_menu(self._screen)

    def _draw_playing(self) -> None:
        """Oynanış durumunu çiz (grid, parçacıklar, düşmanlar, oyuncu, HUD)."""
        # Arka plan ızgarası
        self._grid.draw(self._screen)

        # Parçacıklar (düşmanların arkasında)
        self._particle_system.draw(self._screen)

        # Düşman mermileri
        for eb in self._enemy_bullets:
            if eb.is_active:
                eb.draw(self._screen)

        # Oyuncu mermileri
        for bullet in self._bullets:
            if bullet.is_active:
                bullet.draw(self._screen)

        # Düşmanlar
        for enemy in self._enemies:
            if enemy.is_active:
                enemy.draw(self._screen)

        # Oyuncu (en üstte)
        if self._player and self._player.is_active:
            self._player.draw(self._screen)

        # HUD
        if self._player:
            self._hud.draw(
                self._screen,
                self._score_manager.score,
                self._player.lives,
                self._wave_manager.wave_number,
                self._score_manager.multiplier,
                self._score_manager,
                self._score_manager.high_score
            )

    def _draw_game_over(self) -> None:
        """Oyun bitti ekranını çiz."""
        self._grid.draw(self._screen)
        self._particle_system.draw(self._screen)
        self._hud.draw_game_over(
            self._screen,
            self._score_manager.score,
            self._score_manager.high_score,
            self._wave_manager.wave_number
        )
