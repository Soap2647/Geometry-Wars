"""Çarpışma algılama ve yönetim sistemi modülü."""
import math
import pygame


class CollisionManager:
    """
    Daire tabanlı çarpışma algılama sistemi.
    Mermi-düşman ve düşman-oyuncu çarpışmalarını işler.
    """

    @staticmethod
    def circles_overlap(ax: float, ay: float, ar: float,
                        bx: float, by: float, br: float) -> bool:
        """
        İki dairenin çakışıp çakışmadığını kontrol et.
        Mesafe tabanlı basit ve hızlı yöntem.
        """
        dist_sq = (ax - bx) ** 2 + (ay - by) ** 2
        radius_sum = ar + br
        return dist_sq <= radius_sum * radius_sum

    def process_all(self,
                    player,
                    bullets: list,
                    enemies: list,
                    enemy_bullets: list,
                    particle_system,
                    score_manager,
                    grid) -> tuple:
        """
        Tüm çarpışmaları işle.
        Döndürür: (player_hit: bool, new_enemies: list)
        new_enemies: Splitter'ların ölümünde üretilen yeni düşmanlar.
        """
        player_hit = False
        new_enemies = []
        killed_enemies = []

        px = player.position.x
        py = player.position.y
        pr = player.get_radius()

        # --- Oyuncu mermileri vs Düşmanlar ---
        for bullet in bullets:
            if not bullet.is_active:
                continue
            bx = bullet.position.x
            by = bullet.position.y
            br = bullet.get_radius()

            for enemy in enemies:
                if not enemy.is_active:
                    continue
                ex = enemy.position.x
                ey = enemy.position.y
                er = enemy.get_radius()

                if self.circles_overlap(bx, by, br, ex, ey, er):
                    # Mermi çarpışması
                    bullet.deactivate()
                    # Kıvılcım efekti
                    if particle_system:
                        from settings import COLORS
                        particle_system.spark(
                            ex, ey,
                            pygame.Vector2(bx - ex, by - ey),
                            COLORS['bullet']
                        )
                    # Düşmana hasar ver
                    died = enemy.take_damage(1)
                    if died:
                        killed_enemies.append(enemy)
                        # Patlama efekti
                        if particle_system:
                            particle_system.explode(
                                ex, ey, enemy._color,
                                count=25
                            )
                        # Grid bozulması
                        if grid:
                            grid.add_distortion(ex, ey, strength=100.0)
                        # Puan ver
                        if score_manager:
                            score_manager.add_kill(
                                enemy.score_value,
                                pygame.Vector2(ex, ey)
                            )
                        # Ölüm olayını işle (Splitter bölünmesi)
                        spawn_result = enemy.on_death()
                        if spawn_result:
                            new_enemies.extend(spawn_result)
                    break  # Mermi bir düşmana değdi, devam etme

        # --- Düşman mermileri vs Oyuncu ---
        if not player.is_invincible:
            for eb in enemy_bullets:
                if not eb.is_active:
                    continue
                ebx = eb.position.x
                eby = eb.position.y
                ebr = eb.get_radius()

                if self.circles_overlap(ebx, eby, ebr, px, py, pr):
                    eb.deactivate()
                    hit = player.take_hit()
                    player_hit = True
                    # Oyuncu hasar efekti
                    if particle_system:
                        from settings import COLORS
                        particle_system.explode(
                            px, py, COLORS['player'],
                            count=15, speed_max=150
                        )
                    break

        # --- Düşmanlar vs Oyuncu (temas) ---
        if not player.is_invincible:
            for enemy in enemies:
                if not enemy.is_active:
                    continue
                ex = enemy.position.x
                ey = enemy.position.y
                er = enemy.get_radius()

                if self.circles_overlap(px, py, pr, ex, ey, er):
                    hit = player.take_hit()
                    player_hit = True
                    # Her iki taraf da hasar alır
                    died = enemy.take_damage(1)
                    if died and enemy not in killed_enemies:
                        killed_enemies.append(enemy)
                        if particle_system:
                            particle_system.explode(ex, ey, enemy._color, count=20)
                        if grid:
                            grid.add_distortion(ex, ey, strength=80.0)
                        if score_manager:
                            score_manager.add_kill(
                                enemy.score_value,
                                pygame.Vector2(ex, ey)
                            )
                        spawn_result = enemy.on_death()
                        if spawn_result:
                            new_enemies.extend(spawn_result)
                    if particle_system:
                        from settings import COLORS
                        particle_system.explode(
                            px, py, COLORS['player'],
                            count=15, speed_max=150
                        )
                    break  # Tek seferde bir çarpışma

        return player_hit, new_enemies
