"""Geometry Wars - Giriş noktası (entry point)."""
import sys
import os

# geometry_wars/ dizinini Python path'e ekle
# Bu, `from settings import ...` gibi doğrudan importların çalışmasını sağlar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game import Game


def main():
    """Oyunu başlat."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
