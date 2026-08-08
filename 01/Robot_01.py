import sys
import time
import threading
import pygame
from dataclasses import dataclass
from pygame.locals import *
from gpiozero import Motor, PWMLED
from Pin_Ayarlari import Pin

_global_led_lock = threading.Lock()

class N_Motor(Motor):
    def __init__(self, left, right, radius=None):
        super().__init__(left, right)
        self.radius = radius  # Yar?m kalan sat?r düzeltildi

class Robot():
    def __init__(self, ana_merkez, SL_ILR, SL_GR, SG_ILR, SG_GR ):
        self.app = ana_merkez
        
        self.LED_SL = PWMLED(Pin.US_ECHO)  
        self.LED_SG = PWMLED(Pin.US_TRIG) 
        self.SL_ILR = Pin.SL_ILR
        self.SL_GR = Pin.SL_GR
        self.SG_ILR = Pin.SG_ILR
        self.SG_GR = Pin.SG_GR
        
        self.msl = N_Motor(self.SL_ILR, self.SL_GR)
        self.msg = N_Motor(self.SG_ILR, self.SG_GR)
        

        self._hiz = 0.6  
        self._yon = "DUR"  
        self._sinyal = "DUR"
        
        self._sinyal_thread = None
        self._sinyal_durdur = threading.Event()
        
        self.robot_aksiyonlari = {
            "DUR": self.dur, "SOLA": self.sola, "SAGA": self.saga,
            "ILERI": self.ileri, "GERI": self.geri, "TAMSOLA": self.tamsola, "TAMSAGA": self.tamsaga
        }
        self.sinyal_aksiyonlari = {
            "DUR": self.siny_dur, "SOLA": self.siny_sola, "SAGA": self.siny_saga,
            "ILERI": self.siny_ileri, "GERI": self.siny_geri, "TAMSOLA": self.siny_tamsola, "TAMSAGA": self.siny_tamsaga
        }

    @property
    def hiz(self): return self._hiz
    @hiz.setter
    def hiz(self, value):
        if value is None: value = 0.6
        self._hiz = max(0.0, min(1.0, value))

    @property
    def yon(self): return self._yon
    @yon.setter
    def yon(self, yonRobot):
        if yonRobot in self.robot_aksiyonlari:
            self._yon = yonRobot
            self.robot_aksiyonlari[yonRobot]()

    @property
    def sinyal(self): return self._sinyal
    @sinyal.setter         
    def sinyal(self, yonSinyal):
        if yonSinyal in self.sinyal_aksiyonlari:
            self._sinyal = yonSinyal
            self.sinyal_aksiyonlari[yonSinyal]()

    def ileri(self): self.msl.forward(self._hiz); self.msg.forward(self._hiz)
    def geri(self): self.msl.backward(self._hiz); self.msg.backward(self._hiz)
    def saga(self): self.msl.forward(self._hiz); self.msg.stop()
    def sola(self): self.msl.stop(); self.msg.forward(self._hiz)
    def tamsaga(self): self.msl.forward(self._hiz); self.msg.backward(self._hiz)
    def tamsola(self): self.msl.backward(self._hiz); self.msg.forward(self._hiz)
    def dur(self): self.msl.stop(); self.msg.stop()
 
    def _temizle_ve_hazirlan(self):
        """Çal??an eski sinyal thread'ini TAMAMEN sonland?r?r."""
        self._sinyal_durdur.set()
        if self._sinyal_thread and self._sinyal_thread.is_alive():
            # ? DE????KL?K: 0.15'lik sleep sürelerinden dolay? timeout'u 0.4 yapt?k 
            # ve thread'in gerçekten bitmesini bekledik.
            self._sinyal_thread.join(timeout=0.4)
        
        self._sinyal_durdur.clear()
        
        with _global_led_lock:
            self.LED_SL.off()
            self.LED_SG.off()

    def _thread_baslat(self, hedef_fonksiyon):
        self._temizle_ve_hazirlan()
        self._sinyal_thread = threading.Thread(target=hedef_fonksiyon, daemon=True)
        self._sinyal_thread.start()

    def siny_dur(self): self._temizle_ve_hazirlan()
    def siny_ileri(self): pass
     
    def siny_sola(self): self._thread_baslat(lambda: self._blink_isleme(self.LED_SL, n=4))
    def siny_saga(self): self._thread_baslat(lambda: self._blink_isleme(self.LED_SG, n=4))
    def siny_geri(self): self._thread_baslat(lambda: self._blink_isleme(both=True, n=None))

    def _blink_isleme(self, hedef_led=None, both=False, n=None):
        sayac = 0
        while n is None or sayac < n:
            if self._sinyal_durdur.is_set(): break
            
            with _global_led_lock:
                if both:
                    self.LED_SL.on()
                    self.LED_SG.on()
                else:
                    hedef_led.on()
            
            # ? K?L?T DI?INDA UYUMA: Lock block'unun d???nda uyuyoruz ki di?er yap?lar kilitlenmesin
            time.sleep(0.15)
            if self._sinyal_durdur.is_set(): break

            with _global_led_lock:
                if both:
                    self.LED_SL.off()
                    self.LED_SG.off()
                else:
                    hedef_led.off()
            time.sleep(0.15)
            sayac += 1

    def siny_tamsola(self): self._thread_baslat(lambda: self._pulse_isleme(self.LED_SL, n=2))
    def siny_tamsaga(self): self._thread_baslat(lambda: self._pulse_isleme(self.LED_SG, n=2))

    def _pulse_isleme(self, hedef_led, n):
        adiz_sayisi = 10
        bekleme_suresi = 0.2 / adiz_sayisi
        for _ in range(n):
            if self._sinyal_durdur.is_set(): break
            for i in range(adiz_sayisi + 1):
                if self._sinyal_durdur.is_set(): break
                parlaklik = i / adiz_sayisi
                with _global_led_lock:
                    hedef_led.value = parlaklik
                time.sleep(bekleme_suresi)
            for i in range(adiz_sayisi, -1, -1):
                if self._sinyal_durdur.is_set(): break
                parlaklik = i / adiz_sayisi
                with _global_led_lock:
                    hedef_led.value = parlaklik
                time.sleep(bekleme_suresi)


    def sinyal_kapat(self):
        """Sinyalleri tamamen söndürür."""
        self._temizle_ve_hazirlan() 
 

    def robotSur(self, yonu, hiz=None ):
        if hiz == None:
            hiz=0.6
        else: hiz=hiz
        self.hiz=0.6
        self.yon=yonu
        time.sleep(0.2)

    def sinyalVer(self, yonu):
        self.sinyal=yonu


       
    def rotadaGit(self, *komutlar):
        # 'komutlar' fonksiyon içinde bir Tuple (demet) gibi davran?r
        print(f"Toplam {len(komutlar)} adet komut alındı.")
        
        for komut in komutlar:
            print(f"Robotun sıradaki hareketi: {komut}")
            self.robotSur(komut)
            time.sleep(3)

    def rotaEkle(self, yeni_yon, rota_listesi=None):
        if rota_listesi is None:
            rota_listesi = [] # Eger liste gönderilmediyse temiz bir liste aç
        rota_listesi.append(yeni_yon)
        return rota_listesi



