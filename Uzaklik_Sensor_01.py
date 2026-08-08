import threading
import time
from dataclasses import dataclass
from gpiozero import DistanceSensor
from Pin_Ayarlari import Pin 



# Sistem seviyesinde tek bir sensör referans? ve kilidi
_global_sensor = None
_global_sensor_lock = threading.Lock()

class Mesafe_Kontrol:
    # 2. Ad?m: init fonksiyonunda pinleri tek tek almak yerine dummy s?n?f? kabul ediyoruz
    def __init__(self):
        self.MIN_UZAKLIK_cm = 15.0
        global _global_sensor
        
        with _global_sensor_lock:
            if _global_sensor is None:
                try:
                    # Tüm projede SADECE B?R KEZ kurulur (Ayarlar s?n?f?ndan okunur)
                    _global_sensor = DistanceSensor(
                        echo=Pin.US_ECHO, 
                        trigger=Pin.US_TRIG, 
                        max_distance=2.0
                    )
                    print(f"[Sensör] İlk Kurulum Başarılı. Echo: {Pin.US_ECHO}, Trig: {Pin.US_TRIG}")
                except Exception as e:
                    print(f"[Sensör Kritik Hata]: İlk kurulum başarısız! {e}")
            else:
                print(f"[Sensör Bilgi]: Sistem çift tetiklendi. Mevcut sensör hattı korunuyor (Echo: {Pin.US_ECHO})")
        
        self.sensor = _global_sensor
        
        # Sadece sensör varsa arka plan dinlemesini başlatıyoruz
        if self.sensor:
            self.sensor_thread = threading.Thread(target=self.sensor_arka_plan_oku, daemon=True)
            self.sensor_thread.start()

    def sensor_arka_plan_oku(self):
        while True:
            try:
                if self.sensor:
                    uzaklik_cm = self.sensor.distance * 100
                    print(uzaklik_cm)
                    with self.app.durum_lock:
                        if uzaklik_cm < self.MIN_UZAKLIK_cm:
                            self.app.ENGEL_YAKIN = True
                        else:
                            self.app.ENGEL_YAKIN = False
            except Exception:
                pass
            time.sleep(0.05)
            
