<div align="center">

# 💠 Geometry Wars (Python)

**A neon twin-stick arcade shooter built with nothing but `pygame.draw`: glowing shapes, particle
explosions and a warping grid**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.x-fbbf24?style=flat-square)
![Resolution](https://img.shields.io/badge/1280×720-60%20FPS-a78bfa?style=flat-square)
![Installer](https://img.shields.io/badge/installer-PyInstaller%20+%20Inno%20Setup-0ea5e9?style=flat-square)

[Gameplay](#-gameplay) · [Under the hood](#-under-the-hood) · [Play](#-play) · [Türkçe](#-türkçe)

</div>

---

A fan-made take on the classic neon arcade genre, written as an object-oriented programming project.
Every visual is drawn from geometric primitives at runtime, with no sprite assets.

## 🎮 Gameplay

| Control | Action |
|---|---|
| `W A S D` / arrow keys | Move (normalised diagonals) |
| Mouse | Aim |
| Left click / `Space` | Fire |

**Enemies**

| Enemy | Shape | Behaviour | Score |
|---|---|---|---:|
| 🔺 Chaser | triangle | Hunts the player | 25 |
| ⬠ Wanderer | pentagon | Drifts on a sine wave | 15 |
| 🟧 Shooter | square | Fires every 2 s | 50 |
| 🟣 Splitter | octagon | Splits into two Chasers on death | 75 |

- **Waves** grow and mix enemy types, with shuffled spawns every 0.5 s.
- **Combo multiplier** goes up to **×10** and resets after 4 s without a kill. A countdown bar changes colour as it rises.
- **3 lives** with 2 s of invulnerability after a hit.

## ⚙️ Under the hood

- **State machine** for menu, playing, paused, wave transitions and game over.
- **Composition** and an abstract `GameObject` base for the player, bullets and the enemy hierarchy.
- **Managers**: `CollisionManager`, `WaveManager`, `ScoreManager`.
- **Effects**: neon glow, a particle system, an animated grid and player trails.
- **Windows installer**: PyInstaller one-file build, an Inno Setup package and a **single-install lock** through the Windows registry.

Full write-up (in Turkish): [`docs/technical_documentation.md`](docs/technical_documentation.md).

## ▶️ Play

```bash
pip install pygame
python main.py
```

Build the installer on Windows with `installer\build.bat`.

## 📁 Project structure

```
src/
├── entities/   game_object, player, bullet, enemies/ (chaser, wanderer, shooter, splitter)
├── effects/    grid, particle, particle_system
├── managers/   collision, score, wave
├── ui/         hud
└── game.py
installer/      PyInstaller + Inno Setup scripts, registry check
settings.py     all tunables
```

## 🇹🇷 Türkçe

Python ve Pygame ile yalnızca geometrik çizimlerle yapılmış neon görünümlü bir arcade nişancı oyunu. WASD ile
hareket edilir, fareyle nişan alınır. Dört farklı düşman tipi, dalga sistemi, ×10'a kadar çıkan kombo çarpanı,
parçacık efektleri ve bükülen ızgara içerir. PyInstaller + Inno Setup ile Windows kurulum paketi ve kayıt
defteri üzerinden tek kurulum kilidi vardır. Nesneye Yönelik Programlama dersi projesidir.

---

<div align="center"><sub>Built by <a href="https://github.com/Soap2647">Mert Yasin Yılmaz</a> · inspired by classic neon arcade shooters</sub></div>
