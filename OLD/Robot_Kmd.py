import sys
import time
import math
import pygame
from pygame.locals import *
from gpiozero import Motor, PWMLED
from gpiozero import PWMOutputDevice
# ==========================================
# DONANIM VE PİN TANIMLAMALARI
# ==========================================
lpr, lpw = 5, 10
lf, lb = 6, 13
rf, rb = 19, 26

irpin=24

class NCMotor(Motor):
    def __init__(self, left, right, radius=None):
        super().__init__(left, right)
        self.radius = radius

    def cal_circle_area(self):
        return round(math.pi * self.radius ** 2, 2)

class NCRobot():
    def __init__(self, lf, lb, rf, rb, radius=None):
        self.radius = radius
        self.ml = NCMotor(lf, lb)
        self.mr = NCMotor(rf, rb)
        
    def ileri(self, speed=None):
        if speed==None:speed=1
        self.ml.forward(speed)
        self.mr.forward(speed)

    def geri(self, speed=None):
        self.ml.backward()
        self.mr.backward()
     
    def saga(self, speed=None):
        self.ml.forward()
        self.mr.stop()
    
    def sola(self, speed=None):
        self.ml.stop()
        self.mr.forward()
   
    def tamsaga(self, speed=None):
        self.ml.forward()
        self.mr.backward()

    def tamsola(self, speed=None):
        self.ml.backward()
        self.mr.forward()
    
    def dur(self):
        self.ml.stop()
        self.mr.stop()

# Donanım Kurulumları
r = 40  
ncr = NCRobot(lf, lb, rf, rb)

ledPR = PWMLED(lpr)  # Sağ Sinyal
ledPW = PWMLED(lpw)  # Sol Sinyal


# ==========================================
# SİNYAL VE İKAZ FONKSİYONU
# ==========================================
def sinyalVer(direction):
    """Yön değişimine göre LED sinyallerini ve ikazları yönetir."""
    if direction == "SOLA":
        ledPR.off()
        ledPW.blink(on_time=0.1, off_time=0.1, n=4, background=True)
    elif direction == "SAGA":
        ledPW.off()
        ledPR.blink(on_time=0.1, off_time=0.1, n=4, background=True)
    elif direction == "TAMSOLA":
        ledPR.off()
        ledPW.pulse(fade_in_time=0.2, fade_out_time=0.2, n=2, background=True)
    elif direction == "TAMSAGA":
        ledPW.off()
        ledPR.pulse(fade_in_time=0.2, fade_out_time=0.2, n=2, background=True)
    elif direction == "GERI":
        # Geri viteste her iki LED de aynı anda hızlıca flaşör yapar (n parametresi yok, sürekli yanar)
        ledPR.blink(on_time=0.15, off_time=0.15, background=True)
        ledPW.blink(on_time=0.15, off_time=0.15, background=True)
    else:
        # Durma veya İleri hareketinde tüm ışıkları kapat
        ledPR.off()
        ledPW.off()

def robotSur(direction, speed=None ):
    """Robot pinlerini belirlenen hız değeri ile kontrol eder."""
    if direction == "ILERI":
        ncr.ileri(speed)
    elif direction == "GERI":
        ncr.geri(speed)
    elif direction == "SOLA":
        ncr.sola(speed)
    elif direction == "SAGA":
        ncr.saga(speed)
    elif direction == "TAMSOLA":
        ncr.tamsola(speed)
    elif direction == "TAMSAGA":
        ncr.tamsaga(speed)
    else:
        ncr.dur()

def robotSinyalSur(direction, speed=None):
    if direction == "ILERI":
        ncr.ileri(speed)
    elif direction == "GERI":
        ncr.geri(speed)
        # Geri viteste her iki LED de aynı anda hızlıca flaşör yapar (n parametresi yok, sürekli yanar)
        ledPR.blink(on_time=0.15, off_time=0.15, background=True)
        ledPW.blink(on_time=0.15, off_time=0.15, background=True)
    elif direction == "SOLA":
        ncr.sola(speed)
        ledPR.off()
        ledPW.blink(on_time=0.1, off_time=0.1, n=4, background=True)
    elif direction == "SAGA":
        ncr.saga(speed)
        ledPW.off()
        ledPR.blink(on_time=0.1, off_time=0.1, n=4, background=True)
    elif direction == "TSOLA":
        ncr.tamsola(speed)
        ledPR.off()
        ledPW.pulse(fade_in_time=0.2, fade_out_time=0.2, n=2, background=True)
    elif direction == "TSAGA":
        ncr.tamsaga(speed)
        ledPW.off()
        ledPR.pulse(fade_in_time=0.2, fade_out_time=0.2, n=2, background=True)
    else:
        # Durma veya İleri hareketinde tüm ışıkları kapat
        ncr.dur()
        ledPR.off()
        ledPW.off()
    
def rotadaGit(*komutlar):
    # 'komutlar' fonksiyon içinde bir Tuple (demet) gibi davranır
    print(f"Toplam {len(komutlar)} adet komut alındı.")
    
    for komut in komutlar:
        print(f"Robotun sıradaki hareketi: {komut}")
        robotSur(komut)
#         robot_sinyal_sur(komut)
        time.sleep(3)

def rotaEkle(yeni_yon, rota_listesi=None):
    if rota_listesi is None:
        rota_listesi = [] # E?er liste gönderilmediyse temiz bir liste aç
    rota_listesi.append(yeni_yon)
    return rota_listesi
