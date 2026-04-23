# Geometry Wars - Teknik Dokümantasyon

## İçindekiler
1. [Proje Genel Bakış](#genel-bakış)
2. [Proje Yapısı](#proje-yapısı)
3. [Mimari Tasarım](#mimari-tasarım)
4. [OOP Prensipleri](#oop-prensipleri)
5. [Görsel Efektler](#görsel-efektler)
6. [Oyun Mekaniği](#oyun-mekaniği)
7. [Sistem Bileşenleri](#sistem-bileşenleri)
8. [Kurulum Mekanizması](#kurulum-mekanizması)
9. [Performans Notları](#performans-notları)

---

## Genel Bakış

Geometry Wars, Python ve pygame kütüphanesiyle geliştirilmiş neon görselliğe sahip bir twin-stick shooter oyunudur. Orijinal Geometry Wars arcade oyunundan ilham alınmıştır.

**Teknik Özellikler:**
- Dil: Python 3.10+
- Grafik: pygame 2.x (yalnızca `pygame.draw` primitifleri)
- Çözünürlük: 1280x720 piksel, 60 FPS
- Platform: Windows 10/11

---

## Proje Yapısı

```
geometry_wars/
├── main.py                         # Giriş noktası
├── settings.py                     # Sabitler ve renk paleti
├── src/
│   ├── game.py                     # Ana oyun döngüsü, GameState enum
│   ├── entities/
│   │   ├── game_object.py          # Soyut temel sınıf (ABC)
│   │   ├── player.py               # Oyuncu: hareket, ateş, trail
│   │   ├── bullet.py               # Oyuncu ve düşman mermileri
│   │   └── enemies/
│   │       ├── enemy.py            # Soyut düşman temel sınıfı
│   │       ├── chaser.py           # Kovalayıcı (kırmızı üçgen)
│   │       ├── wanderer.py         # Gezgin (yeşil beşgen)
│   │       ├── shooter.py          # Atıcı (turuncu kare)
│   │       └── splitter.py         # Bölünen (mor sekizgen)
│   ├── effects/
│   │   ├── particle.py             # Tek parçacık sınıfı
│   │   ├── particle_system.py      # Parçacık yöneticisi
│   │   └── grid.py                 # Animasyonlu arka plan ızgarası
│   ├── managers/
│   │   ├── wave_manager.py         # Dalga sistemi
│   │   ├── collision_manager.py    # Çarpışma algılama
│   │   └── score_manager.py        # Puan ve katsal yönetimi
│   └── ui/
│       └── hud.py                  # HUD: puan, can, dalga, katsal
├── installer/
│   ├── registry_check.py           # Windows registry yöneticisi
│   ├── installer_script.iss        # Inno Setup kurulum betiği
│   └── build.bat                   # PyInstaller + Inno Setup derleme
└── docs/
    └── technical_documentation.md  # Bu dosya
```

---

## Mimari Tasarım

### Durum Makinesi (State Machine)

Oyun, `GameState` enum sınıfıyla tanımlanan 5 durumlu bir FSM (Finite State Machine) kullanır:

```
MENU → WAVE_TRANSITION → PLAYING ↔ PAUSED
                 ↑              ↓
                 └──── GAME_OVER ←┘
```

| Durum | Açıklama |
|-------|---------|
| `MENU` | Ana menü - grid animasyonu aktif |
| `WAVE_TRANSITION` | Dalga geçişi - geri sayım ekranı |
| `PLAYING` | Aktif oynanış |
| `PAUSED` | Duraklat - oyun arka planda görünür |
| `GAME_OVER` | Oyun bitti ekranı |

### Bileşim (Composition) Deseni

`Game` sınıfı tüm alt sistemleri sahiplenir (has-a ilişkisi):

```python
class Game:
    _player: Player
    _particle_system: ParticleSystem
    _grid: Grid
    _wave_manager: WaveManager
    _collision_manager: CollisionManager
    _score_manager: ScoreManager
    _hud: HUD
```

---

## OOP Prensipleri

### 1. Soyutlama (Abstraction)

`GameObject` soyut temel sınıfı (`ABC`), tüm oyun nesnelerinin ortak arayüzünü tanımlar:

```python
class GameObject(ABC):
    @abstractmethod
    def update(self, dt: float) -> None: ...
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...
    @abstractmethod
    def get_radius(self) -> float: ...
```

`Enemy` sınıfı da soyut bir ara katman oluşturur; sağlık sistemi, parlama efekti ve `on_death()` hook'u burada tanımlanır.

### 2. Kalıtım (Inheritance)

```
GameObject (ABC)
    ├── Player
    ├── Bullet
    ├── EnemyBullet
    └── Enemy (ABC)
            ├── Chaser
            ├── Wanderer
            ├── Shooter
            └── Splitter
```

### 3. Kapsülleme (Encapsulation)

Tüm öznitelikler `_` önekiyle **protected** olarak tanımlanmış, dış erişim için `@property` dekoratörleri kullanılmıştır:

```python
@property
def position(self) -> pygame.Vector2:
    return pygame.Vector2(self._x, self._y)

@property
def is_active(self) -> bool:
    return self._active
```

### 4. Çok Biçimlilik (Polymorphism)

`CollisionManager` tüm düşman türlerini `Enemy` referansıyla işler; `take_damage()`, `on_death()` ve `get_radius()` metotları türe göre farklı davranır:

```python
for enemy in enemies:
    died = enemy.take_damage(1)   # Her düşman için farklı can sistemi
    if died:
        spawn = enemy.on_death()  # Splitter: 2 Chaser döndürür; diğerleri: None
```

---

## Görsel Efektler

### Neon Parlama (Glow) Efekti

Her görsel element `pygame.SRCALPHA` destekli geçici yüzeyler üzerine çizilir. Katmanlı yaklaşım:

1. **Dış glow** (büyük radius, düşük alfa): `scale=1.9, alpha=27`
2. **Orta glow** (orta radius, orta alfa): `scale=1.6, alpha=53`
3. **İç glow** (küçük radius, yüksek alfa): `scale=1.3, alpha=80`
4. **Ana şekil** (tam boyut, yüksek alfa): `alpha=220`
5. **Kenar çizgisi** (beyaz, yarı şeffaf): `alpha=100`

### Parçacık Sistemi

`ParticleSystem.explode()` bir patlama noktasında `count` adet parçacık oluşturur:
- Rastgele yön (360°)
- Rastgele hız (`speed_min` - `speed_max` px/s)
- Rastgele ömür
- Sürtünme katsayısı ile yavaşlama
- Sıcak (sarı-turuncu) ve soğuk (pembe-kırmızı) renk karışımı

### Animasyonlu Izgara

- 40px hücre boyutu
- `sin(time * 1.5)` ile nabız efekti → renk interpole edilir
- Patlama noktalarına yakın kesişimler itmeli bozulma uygular
- Bozulma gücü `(1 - dist/radius)²` kuadratik azalma ile söner

### Oyuncu Trail Efekti

Her `20ms`'de bir geçmiş pozisyon kaydedilir (12 pozisyon saklanır). Eski pozisyonlar daha küçük ve şeffaf daireler olarak çizilir.

---

## Oyun Mekaniği

### Düşman Türleri

| Tür | Şekil | Renk | Can | Hız | Puan | Özel |
|-----|-------|------|-----|-----|------|------|
| Chaser | Üçgen | Kırmızı | 1 | 120 px/s | 25 | Oyuncuyu kovalar |
| Wanderer | Beşgen | Yeşil | 1 | 80 px/s | 15 | Sinüs dalgasıyla gezinir |
| Shooter | Kare | Turuncu | 2 | 60 px/s | 50 | Her 2s'de mermi atar |
| Splitter | Sekizgen | Mor | 3 | 50 px/s | 75 | Ölünce 2 Chaser üretir |

### Dalga Sistemi

| Dalga | İçerik |
|-------|--------|
| 1 | 5 Chaser |
| 2 | 5 Chaser + 3 Wanderer |
| 3 | 4 Chaser + 4 Wanderer + 2 Shooter |
| 4 | 5 Chaser + 3 Wanderer + 2 Shooter + 1 Splitter |
| 5 | 6 Chaser + 4 Wanderer + 3 Shooter + 2 Splitter |
| 6+ | Dalga × orantılı artış |

Tüm listeler `random.shuffle()` ile karıştırılır. Düşmanlar 0.5s aralıklarla spawn olur.

### Puan Katsalı Sistemi

- Her öldürme katsalı 1 artırır (maksimum x10)
- Son öldürmeden 4 saniye geçerse katsal x1'e sıfırlanır
- Görsel geri sayım çubuğu katsalın altında gösterilir
- Renk: x1-x4 yeşil, x5-x7 sarı, x8-x10 kırmızı

### Oyuncu Özellikleri

- **Hareket**: WASD veya Ok tuşları, normalize edilmiş (çapraz hareket aynı hız)
- **Nişan alma**: Fare konumuna bakan ship rotation
- **Ateş**: Sol fare tuşu veya Boşluk - 0.15s cooldown
- **Can sistemi**: 3 can, hasar sonrası 2s dokunulmazlık
- **Yanıp sönme**: Dokunulmazlık sırasında 80ms aralıklarla görünür/görünmez

---

## Sistem Bileşenleri

### CollisionManager

Daire-daire çarpışma testi: `dist² ≤ (r₁ + r₂)²` (karekök hesabından kaçınır).

İşlem sırası:
1. Oyuncu mermileri ↔ Düşmanlar
2. Düşman mermileri ↔ Oyuncu
3. Düşmanlar (temas) ↔ Oyuncu

### WaveManager

- `_spawn_queue`: Sınıf referanslarının listesi (instance değil)
- `update()` her çağrıda bir düşman instantiate edip döndürür
- `is_wave_complete()`: Tüm spawn tamamlandı **ve** aktif düşman yok

### ScoreManager

`FloatingText` nesneleri 1.2s boyunca yukarı kayarak solar. Her öldürme hem skor hemde katsal artışı tetikler.

---

## Kurulum Mekanizması

### PyInstaller Derlemesi

`build.bat` betiği:
1. Python ve bağımlılıkları kontrol eder
2. `--onedir` moduyla `GeometryWars/` klasörü oluşturur
3. Tüm `src/` paketi ve `settings.py` binary içine gömülür
4. Gizli importlar (`--hidden-import`) pygame alt modülleri için belirtilir

### Inno Setup Kurulum Paketi

`installer_script.iss` özellikleri:
- **Dil desteği**: Türkçe ve İngilizce
- **Registry kaydı**: `HKLM\SOFTWARE\GeometryWars` altında kurulum bilgileri
- **Programlar listesi**: Windows "Programlar ve Özellikler"de görünür
- **Masaüstü kısayolu**: Opsiyonel görev olarak sunulur

### Tekli Kurulum Kilidi (Single-Install Lock)

`InitializeSetup()` Pascal fonksiyonu kurulumdan önce çalışır:

```pascal
if IsAlreadyInstalled() then
begin
  // Kullanıcıya soru sor: Üzerine yükle veya iptal et
end;
```

`registry_check.py` aynı mantığı Python'da uygular ve şu modlarda kullanılabilir:
- `python registry_check.py check` - Kurulum durumunu kontrol et
- `python registry_check.py install --path "C:\..."` - Kaydı yaz
- `python registry_check.py remove` - Kaydı sil

---

## Performans Notları

1. **SRCALPHA yüzey havuzu**: Her frame yeni Surface oluşturmak GC baskısı yaratır. Üretimde `Surface` nesneleri önbelleğe alınabilir.

2. **Grid optimizasyonu**: Bozulma yokken `_draw_simple()` kullanılır (kesişim noktası hesabı atlanır). Bozulma varken `_draw_distorted()` tüm grid noktalarını hesaplar - bu O(cols × rows) karmaşıklığındadır.

3. **Parçacık limiti**: `ParticleSystem` her patlama için ~30 parçacık üretir. Yoğun savaşlarda `count` parametresi azaltılabilir.

4. **Düşman güncelleme**: Her düşmanın `update()` methodu `player_pos` alır. Bu, `pygame.Vector2` hesaplamasını bir kez yapıp dağıtmak yerine her düşmanda tekrarlar - optimize edilebilir.

5. **Font nesneleri**: `HUD.draw_wave_transition()` her frame yeni font nesnesi oluşturur. Üretimde font nesneleri önbelleğe alınmalıdır.
