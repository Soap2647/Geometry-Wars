"""Soyut temel oyun nesnesi modülü."""
from abc import ABC, abstractmethod
import pygame


class GameObject(ABC):
    """
    Tüm oyun nesnelerinin soyut temel sınıfı.
    OOP'ta Soyutlama (Abstraction) prensibini uygular:
    update(), draw(), get_radius() metodları alt sınıflarda somutlaştırılmalıdır.
    """

    def __init__(self, x: float, y: float):
        self._x = x          # Kapsülleme: protected attribute
        self._y = y
        self._active = True

    @abstractmethod
    def update(self, dt: float) -> None:
        """Her frame güncelleme mantığı."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Nesneyi ekrana çiz."""
        pass

    @abstractmethod
    def get_radius(self) -> float:
        """Çarpışma yarıçapını döndür."""
        pass

    @property
    def position(self) -> pygame.Vector2:
        """Nesnenin pozisyonunu Vector2 olarak döndür."""
        return pygame.Vector2(self._x, self._y)

    @property
    def is_active(self) -> bool:
        """Nesne aktif mi?"""
        return self._active

    def deactivate(self) -> None:
        """Nesneyi devre dışı bırak."""
        self._active = False
