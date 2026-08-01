# 🤖 Pythonic Robot Control & Advanced Python Guide

Bu doküman, robot kontrol projeniz kapsamında konuştuğumuz tüm ileri seviye Python inceliklerini (Pythonic Tips), kod mimarisini (`main.py`) ve GitHub dokümantasyon düzenini tek bir çatı altında toplamaktadır.

---

## 📘 BÖLÜM 1: İLERİ SEVİYE PYTHON KAVRAMLARI (ADVANCED PYTHON CONCEPTS)

### 1. First-Class Functions & Event Mapping (Dictionary Instead of IF-ELSE)
#### 🇬🇧 English
Instead of using messy and hard-to-maintain `if-elif-else` blocks for robot movements, this project utilizes Python's **First-Class Functions** feature. In Python, functions are objects. We can store them inside a dictionary without parentheses `()` as references, and trigger them later using `.get()` with parentheses `()`.
* **Benefit:** High performance (O(1) time complexity), clean code, and easy scalability.

#### 🇹🇷 Türkçe
Robot hareketleri için karmaşık ve bakımı zor `if-elif-else` blokları kullanmak yerine, bu projede Python'ın **Birinci Sınıf Fonksiyonlar (First-Class Functions)** özelliği kullanılmıştır. Python'da fonksiyonlar birer nesnedir. Fonksiyonları parantez `()` koymadan birer referans olarak sözlük (dictionary) içinde saklayabilir ve daha sonra `.get()` yöntemiyle çağırıp sonuna parantez `()` ekleyerek tetikleyebiliriz.
* **Avantajı:** Yüksek performans (O(1) zaman karmaşıklığı), temiz kod ve kolay genişletilebilirlik.

```python
# Function Mapping Example / Fonksiyon Haritalama Örneği
self.actions = {
    'w': self.move_forward,
    's': self.move_backward
}
# Safe triggering / Güvenli tetikleme
action = self.actions.get(key)
if action: 
    action()
```

---

### 2. Iterating with `zip()` Function
#### 🇬🇧 English
When processing robot sensor data or matching motors with speeds, we avoid using index counters (like `i`). Instead, we use the built-in `zip()` function to iterate over multiple lists or tuples simultaneously in a parallel fashion.
* **Benefit:** Eliminates `IndexError` risks and makes the `for` loop highly readable.

#### 🇹🇷 Türkçe
Robot sensör verilerini işlerken veya motorları hızlarla eşleştirirken, indeks sayacı (yani `i` değişkeni) kullanmaktan kaçınırız. Bunun yerine, birden fazla listeyi veya demeti (tuple) aynı anda paralel olarak dönmek (iterate etmek) için gömülü `zip()` fonksiyonunu kullanıriz.
* **Avantajı:** `IndexError` (indeks hatası) riskini ortadan kaldırır ve `for` döngüsünü son derece okunabilir kılar.

```python
motors = ["front_left", "front_right", "rear_left", "rear_right"]
speeds = [80, 80, 75, 75]

# Pythonic way with zip() / zip() ile Pythonic yöntem
for motor, speed in zip(motors, speeds):
    print(f"Setting {motor} speed to {speed}%")
```

---

### 3. Dynamic Argument Passing with `*args` and `**kwargs`
#### 🇬🇧 English
In robot automation, different commands require different numbers of parameters. For example, `stop()` requires no parameters, while `move(speed, direction)` requires two. We use `*args` (positional arguments) and `**kwargs` (keyword arguments) to pass a dynamic number of arguments to our mapped functions.
* **Benefit:** Allows a single event handler to trigger any function, regardless of its parameters.

#### 🇹🇷 Türkçe
Robot otomasyonunda farklı komutlar farklı sayıda parametre gerektirir. Örneğin, `stop()` parametre gerektirmezken, `move(speed, direction)` iki parametre ister. Haritalanmış fonksiyonlarımıza dinamik sayıda argüman göndermek için `*args` (konumsal argümanlar) ve `**kwargs` (anahtar kelime argümanları) yapılarını kullanırız.
* **Avantajı:** Parametre sayısı ne olursa olsun, tek bir olay yöneticisinin (event handler) her fonksiyonu tetikleyebilmesini sağlar.

```python
# Triggering functions dynamically / Fonksiyonları dinamik tetikleme
def execute_action(action_func, *args, **kwargs):
    action_func(*args, **kwargs)
```

---

### 4. Dictionary Comprehensions
#### 🇬🇧 English
Instead of writing long loops to transform or filter keyboard configurations or telemetry data, we use **Dictionary Comprehensions** to create new dictionaries in a single, concise line.

#### 🇹🇷 Türkçe
Klavye konfigürasyonlarını veya telemetri verilerini dönüştürmek ya da filtrelemek için uzun döngüler yazmak yerine, tek bir satırda yeni sözlükler oluşturmak için **Sözlük Üreticilerini (Dictionary Comprehensions)** kullanırız.

```python
# Convert all key characters to uppercase / Tüm tuş karakterlerini büyük harfe çevir
raw_keys = {'w': 'forward', 's': 'backward'}
clean_keys = {key.upper(): value for key, value in raw_keys.items()}
# Result: {'W': 'forward', 'S': 'backward'}
```

---

### 5. Clean Data Encapsulation with `@property` (Getters & Setters)
#### 🇬🇧 English
In robotics, protecting critical states like battery level or motor speed is vital. Instead of traditional Java-style `get_speed()` and `set_speed()` methods, Python offers the `@property` decorator. It allows us to access methods as if they were simple attributes, while safely validating data behind the scenes.
* **Benefit:** Prevents dangerous values (e.g., setting speed to 500%) before sending commands to physical hardware.

#### 🇹🇷 Türkçe
Robotikte pil seviyesi veya motor hızı gibi kritik durumları korumak çok önemlidir. Geleneksel Java tarzı `get_speed()` ve `set_speed()` metotları yerine Python, `@property` dekoratörünü sunar. Bu yapı, metotlara düz bir değişkenmiş gibi erişmemizi sağlarken, arka planda veriyi güvenle doğrulamamıza (validation) imkan tanır.
* **Avantajı:** Fiziksel donanıma komut göndermeden önce tehlikeli değerlerin (örneğin hızın yanlışlıkla %500 yapılması) önüne geçer.

```python
class RobotHardware:
    def __init__(self):
        self._speed = 0  # Protected variable

    @property
    def speed(self):
        return self._speed

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if 0 <= value <= 100:  # Safety check
            self._speed = value
        else:
            raise ValueError("Speed must be between 0 and 100!")

# Usage / Kullanım:
robot = RobotHardware()
robot.speed = 80   # Works like a variable / Değişken gibi atanır
```

---

### 6. Memory-Efficient Streaming with Generators (`yield`)
#### 🇬🇧 English
Reading high-frequency sensor telemetry (like LiDAR distance vectors or IMU data) inside an infinite `while True` loop can cause memory spikes if stored in traditional lists. By using `yield` instead of `return`, we create **Generators** that stream data one item at a time, strictly on-demand.
* **Benefit:** O(1) memory usage. The robot processes the current telemetry frame without caching millions of past points in RAM.

#### 🇹🇷 Türkçe
Sonsuz bir `while True` döngüsü içinde yüksek frekanslı sensör telemetrisini (LiDAR mesafe vektörleri veya IMU verileri gibi) geleneksel listelerde saklamak hafıza (RAM) şişmelerine yol açar. `return` yerine `yield` kullanarak, verileri kesinlikle talep edildikçe tek tek akıtan **Üreteçler (Generators)** oluştururuz.
* **Avantajı:** O(1) hafıza kullanımı. Robot, geçmişe ait milyonlarca noktayı RAM'de önbelleğe almadan sadece o anki telemetri karesini işler.

```python
import random

def stream_sensor_data():
    while True:
        yield random.uniform(0.1, 5.0) 

# Usage / Kullanım:
telemetry = stream_sensor_data()
for distance in telemetry:
    if distance < 0.5:
        print("Obstacle detected!")
        break
```

---

### 7. Fast Telemetry Filtering with `lambda` & `filter()`
#### 🇬🇧 English
When managing multiple micro-tasks or filtering raw sensor arrays, writing full function definitions using `def` can overcomplicate the codebase. We employ anonymous **`lambda` functions** combined with **`filter()`** to isolate relevant hardware signals instantly.
* **Benefit:** Inline, expressive filtering that mirrors functional programming standards.

#### 🇹🇷 Türkçe
Birden fazla mikro görevi yönetirken veya ham sensör dizilerini filtrelerken, `def` kullanarak tam fonksiyon tanımlamaları yazmak kod tabanını aşırı karmaşıklaştırabilir. İlgili donanım sinyallerini anında izole etmek için gömülü **`filter()`** fonksiyonu ile birleştirilmiş anonim **`lambda` fonksiyonlarını** kullanırız.

```python
sonar_readings = [1.2, 0.3, 4.5, 0.2, 2.1, 0.4]
hazards = list(filter(lambda x: x < 0.5, sonar_readings))
# Result / Sonuç: [0.3, 0.2, 0.4]
```
8. Unified Event Loop Pattern (Tekil Olay Döngüsü)🇬🇧 EnglishInstead of separation with multiple async input listeners, this project routes both keyboard and mouse signals into a single Unified Event Loop. By storing event types and keys as dictionary keys, the main loop dispatches input handling dynamically in just a few lines of code.Benefit: Eliminates race conditions between mouse and keyboard, offering centralized control.

🇹🇷 Türkçe
Fare ve klavye için ayrı ayrı asenkron dinleyiciler kullanmak yerine, bu projede tüm sinyaller tek bir Tekil Olay Döngüsü (Unified Event Loop) üzerinde toplanmıştır. Olay türlerini (event type) ve tuşları sözlük anahtarı olarak saklayarak, ana döngü içindeki tüm girdi yönetimini sadece birkaç satır kodla dinamik olarak dağıtıyoruz.Avantajı: Fare ve klavye arasında yaşanabilecek senkronizasyon hatalarını (race condition) yok eder ve tek bir noktadan kontrol sağlar.
---


1. Unified Architecture Template (main.py)

🇬🇧 EnglishThis script combines Event Mapping, Generators, @property, and Lambda Filtering into a single, clean, production-ready class architecture.

🇹🇷 TürkçeBu betik; Olay Haritalama, Üreteçler, @property ve Lambda Filtreleme özelliklerini tek bir temiz, üretime hazır sınıf mimarisinde birleştirir.

## 🛠️ BÖLÜM 2: BİRLEŞİK KOD MİMARİSİ ŞABLONU (`main.py`)

```python
import time
import random
from typing import Dict, Callable, Iterator, List

class AdvancedRobot:
    def __init__(self) -> None:
        self._battery_level: int = 100  # Encapsulated state
        
        # 1. Event Mapping (No more IF-ELSE)
        self.keyboard_actions: Dict[str, Callable[[], None]] = {
            'w': self.move_forward,
            's': self.move_backward,
            'space': self.stop_robot
        }

    # 2. Encapsulation with @property
    @property
    def battery(self) -> int:
        return self._battery_level

    @battery.setter
    def battery(self, value: int) -> None:
        if 0 <= value <= 100:
            self._battery_level = value
        else:
            print("⚠️ Invalid battery value skipped!")

    def move_forward(self) -> None: print("🤖 Moving Forward...")
    def move_backward(self) -> None: print("🤖 Moving Backward...")
    def stop_robot(self) -> None: print("🛑 Emergency Stop!")

    # 3. Memory-Efficient Telemetry Stream (Generator)
    def stream_lidar(self) -> Iterator[List[float]]:
        while True:
            yield [random.uniform(0.1, 3.0) for _ in range(4)]
            time.sleep(0.5)

    # 4. Fast Telemetry Processing (Lambda & Filter)
    def process_hazards(self, sensor_data: List[float]) -> List[float]:
        return list(filter(lambda distance: distance < 0.6, sensor_data))

# --- Execution Example ---
if __name__ == "__main__":
    bot = AdvancedRobot()
    
    action = bot.keyboard_actions.get('w')
    if action: action()

    lidar_stream = bot.stream_lidar()
    for _ in range(3):
        frame = next(lidar_stream)
        hazards = bot.process_hazards(frame)
        print(f"Raw Lidar: {[round(x,2) for x in frame]} -> Hazards (<0.6m): {[round(x,2) for x in hazards]}")
```

---

## 🎯 BÖLÜM 3: TIP İPUÇLARI VE GITHUB DOSYA DÜZENİ

### Code Safety with Type Hinting (Tip İpuçları)
#### 🇬🇧 English
Python is dynamically typed. **Type Hinting** explicitly declares expected types. It acts as self-documenting code and helps tools like `mypy` catch bugs before the code runs on a physical robot.
#### 🇹🇷 Türkçe
Python dinamik tipli bir dildir. **Tip İpuçları (Type Hinting)**, beklenen veri tiplerini açıkça beyan ederek kod güvenliğini artırır.

```python
def calculate_speed(distance: float, time: float) -> float:
    return distance / time
```

### GitHub README.md Presentation Layout / Tanıtım Düzeni
```markdown
# 🤖 Pythonic Autonomous Robot Controller

An educational, high-performance robot controller built with advanced "Pythonic" design patterns.

## 🌟 Key Features / Öne Çıkan Özellikler
- 🚀 **O(1) Event Mapping:** Zero `if-else` blocks for ultra-clean movement handling.
- ⚡ **Memory-Efficient Telemetry:** Built with Python Generators for low-RAM streaming.
- 🎯 **Type Safe:** Fully typed architecture using Python Type Hinting.

## 📘 Educational Guide / Eğitim Kılavuzu
Want to learn the advanced Python secrets behind this code? 
Check out our detailed guide: [👉 PYTHONIC_DETAILS.md](./PYTHONIC_DETAILS.md)
```
