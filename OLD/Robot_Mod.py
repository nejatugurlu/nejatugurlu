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
    def __init__(self, left, right, radius):
        super().__init__(left, right)
        self.radius = radius

    def cal_circle_area(self):
        return round(math.pi * self.radius ** 2, 2)

class NCRobot():
    def __init__(self, lf, lb, rf, rb, radius):
        self.radius = radius
        self.ml = NCMotor(lf, lb, radius)
        self.mr = NCMotor(rf, rb, radius)
        
    def ileri(self, speed):
        self.ml.forward(speed)
        self.mr.forward(speed)

    def geri(self, speed):
        self.ml.backward(speed)
        self.mr.backward(speed)
     
    def saga(self, speed):
        self.ml.forward(speed)
        self.mr.stop()
    
    def sola(self, speed):
        self.ml.stop()
        self.mr.forward(speed)
   
    def tamsaga(self, speed):
        self.ml.forward(speed)
        self.mr.backward(speed)

    def tamsola(self, speed):
        self.ml.backward(speed)
        self.mr.forward(speed)
    
    def dur(self):
        self.ml.stop()
        self.mr.stop()

# Donanım Kurulumları
r = 40  
ncr = NCRobot(lf, lb, rf, rb, r)

ledPR = PWMLED(lpr)  # Sağ Sinyal
ledPW = PWMLED(lpw)  # Sol Sinyal


# ==========================================
# SİNYAL VE İKAZ FONKSİYONU
# ==========================================
def sinyal_ver(direction):
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

def robot_sur(direction, speed):
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

def robot_sinyal_sur(direction, speed):
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
    

