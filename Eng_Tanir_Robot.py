import pygame
import pigpio
import sys
import time
import threading  # Threading modülü aktif
from pynput import keyboard
from pygame.locals import *

from gpiozero import DistanceSensor

from Kmd_Menu import kumandaMenusu, Buton # as menu, Buton as buton# Depomuzdan s?n?flar? çektik
from Kizil_Otesi_Kmd import KOAlici
from Robot_Kmd import robotSur,sinyalVer,rotadaGit

        
class Uygulama:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 18)
        self.fontB= pygame.font.SysFont("Arial", 40)
        self.RENK_BEYAZ = (255, 255, 255)
        self.RENK_ARKA_PLAN = (30, 30, 30)
        self.RENK_BUTON_PASIF = (52, 152, 219)
        self.RENK_BUTON_AKTIF = (0, 255, 0) # Yeşil
        self.RENK_KIRMIZI = (231, 76, 60)
        self.ekran_en=600
        self.ekran_boy=700
        self.ekran = pygame.display.set_mode((self.ekran_en, self.ekran_boy),pygame.RESIZABLE)
        self.saat = pygame.time.Clock()
        
        self.menu = kumandaMenusu(self)
        self.anlik_yon="DUR"
        self.anlik_hiz=0.6
        self.hedef_yon=self.anlik_yon
        self.hedef_hiz=self.anlik_hiz
        self.ENGEL_YAKIN=False
        self.ROTA_KURULMUYOR=True
        self.rota_liste=[]        
        self.durum_lock = threading.Lock()
        
        echopin, triggerpin = 14, 15
        self.sensor = DistanceSensor(echo=echopin, trigger=triggerpin, max_distance=2.0)
        
        # Olaylar ile fonksiyonlar?n e?le?mesi
        self.mouse_aksiyonlari = {
            self.menu.EVENT_DUR : self.dur,
            self.menu.EVENT_SOLA : self.solaGit ,
            self.menu.EVENT_SAGA : self.sagaGit,
            self.menu.EVENT_ILERI : self.ileriGit,
            self.menu.EVENT_GERI : self.geriGit,
            self.menu.EVENT_TAMSOLA : self.tamsolaGit,
            self.menu.EVENT_TAMSAGA : self.tamsagaGit,
            self.menu.EVENT_ARTIR : self.hizArtir,
            self.menu.EVENT_AZALT : self.hizAzalt,
            self.menu.EVENT_KUR : self.rotaKur,
            self.menu.EVENT_GIT : self.rotaGit
        }

        self.klavye_aksiyonlari = {
            K_w:                           self.ileriGit,
            K_s:                           self.geriGit,
            K_a:                           self.solaGit,
            K_d:                           self.sagaGit,
            K_z:                           self.tamsolaGit,
            K_x:                           self.tamsagaGit,
            K_c:                           self.dur,
            K_UP:                          self.ileriGit,  # Ok tu?u alternatifi
            K_DOWN:                        self.geriGit,   # Ok tu?u alternatifi
            K_LEFT:                        self.solaGit,   # Ok tu?u alternatifi
            K_RIGHT:                       self.sagaGit,   # Ok tu?u alternatifi
            K_SPACE:                       self.dur    # Bo?luk tu?u
            
        }
        
    def sensor_thread_func(self): # Argüman tamamen kaldırıldı, eski haline döndü
        MIN_UZAKLIK_cm=15.0
        # Sensörün ana programda tamamen kurulmas? için bekliyoruz
        #time.sleep(0.5) 
        print(f"[Sensör] Mesafe kontrolü aktif. Sınır: {MIN_UZAKLIK_cm} cm", end="\r")
        running=True
        while running:
            try:
                # Karmaşık if kontrolleri yerine doğrudan ana değişkenden okuyoruz
                uzaklik_cm = self.sensor.distance * 100
                # TEST SATIRI: Mesafe akışını canlı göreceğiz
                #print(f"Anlık Mesafe: {uzaklik_cm:.1f} cm  ", end="\r")
                with self.durum_lock:
                    if uzaklik_cm < MIN_UZAKLIK_cm:
                        self.ENGEL_YAKIN = True
                    else:
                        self.ENGEL_YAKIN = False
            except Exception as e:
                # Donan?msal bir hata (bağlantı vb.) varsa buraya düşecek
                print(f"\n[Sensör Donanım Hatası]: {e}")
                
            time.sleep(0.05)

    def dur(self):
        self.metin = self.font.render("Basılı: DUR", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Durdu.....\n")
        with self.durum_lock:self.anlik_yon = "DUR"  

    def solaGit(self):
        self.metin = self.font.render("Basılı: SOLA", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Sola gidiyor.....\n")
        with self.durum_lock:self.anlik_yon = "SOLA"
    def sagaGit(self):
        self.metin = self.font.render("Basılı: SAĞA", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Sağa gidiyor.....\n")
        with self.durum_lock:self.anlik_yon = "SAGA"
    def ileriGit(self):
        self.metin = self.font.render("Basılı: İLERİ", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("İleri gidiyor.....\n")
        with self.durum_lock:self.anlik_yon = "ILERI"
    def geriGit(self):
        self.metin = self.font.render("Basılı: GERİ", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Geri gidiyor.....\n" )
        with self.durum_lock:self.anlik_yon = "GERI"

    def tamsolaGit(self):
        self.metin = self.font.render("Basılı: TAMSOLA", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Tamsola gidiyor.....\n" )
        with self.durum_lock:self.anlik_yon = "TAMSOLA"
    def tamsagaGit(self):
        self.metin = self.font.render("Basılı: TAMSAĞA", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Tamsağa gidiyor.....\n" )
        with self.durum_lock:self.anlik_yon = "TAMSAGA"

    def hizArtir(self):
        #print("Hız artırılıyor..." )
        with self.durum_lock:
            self.anlik_hiz = min(1.0, round(self.anlik_hiz + 0.1, 1))
            self.anlik_yon = "ILERI"
        metin = self.font.render(f"Hız: %{int(self.anlik_hiz * 100)} | Durum: {self.hedef_yon}", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        
    def hizAzalt(self):
        print("Hız azaltılıyor..." ) 
        with self.durum_lock:
            self.anlik_hiz = max(0.0, round(self.anlik_hiz - 0.1, 1))
            self.anlik_yon = "ILERI"
        metin = self.font.render(f"Hız: %{int(self.anlik_hiz * 100)} | Durum: {self.hedef_yon}", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
            
    def rotaKur(self):
        print("Rota kuruluyor...\n" ) 
        metin = self.font.render("Basılı: ROTAKUR", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        self.ROTA_KURULMUYOR=False
        self.rota_liste=[]
        
    def rotaGit(self):
        print("Rota izleniyor...\n" ) 
        metin = self.font.render("Basılı: ROTAGIT", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        self.ROTA_KURULMUYOR=True
        rotadaGit(*self.rota_liste)  # burada * argümanları açıyor 

    def rotaEkle(self, yeni_yon, rota_listesi=None):
        if rota_listesi is None:
            rota_listesi = [] # E?er liste gönderilmediyse temiz bir liste aç
        
        rota_listesi.append(yeni_yon)
        return rota_listesi


    def calistir(self):
        # =======UZAKLIK SENSÖRÜ==========0====================================================
        # Sensör thread'ini başlatıyoruz
        sensor_thread = threading.Thread(target=self.sensor_thread_func, daemon=True)
        sensor_thread.start()

        print("Pi Hazır. OK TUŞLARI: Yön | 1-5 TUŞLARI: Hız Ayarı | ESC: Çıkış" , end="\r")

        # ======KIZIL ÖTESİ=================================================================
        pi = pigpio.pi()
        ALICI_PINI = 24
        alici = KOAlici(pi, ALICI_PINI)

        print("Sistem Başarıyla Kuruldu!")
        print("Şu anda GPIO 24 pininden kumanda sinyalleri ve bilgisayardan klavye tuşları dinleniyor.")
        print("Çıkış yapmak için CTRL+C tuşlarına basın.\n")
        self.son_yon= "DUR"
        self.metin_silme_zamani = 0
        
        ust_metin = self.font.render(f"Hız: %{int(self.anlik_hiz * 100)} | Durum: {self.hedef_yon}", True, self.RENK_BEYAZ)
        self.metin = self.font.render("Sistem Hazır", True, self.RENK_BEYAZ)
        metinrota=self.font.render("ROTA:  ", True, self.RENK_BEYAZ)
        
        calisiyor = True
        akt_but_ind = 0
        while calisiyor:
            # Kızıl Ötesi TV kontrol (NEXT)
            if alici.anlik_yon != "DUR":
                self.anlik_yon=alici.anlik_yon
                
            self.simdiki_zaman = pygame.time.get_ticks()

            # Belirli bir süre sonra alttaki bilgi metnini temizlemek için zaman kontrolü
            if self.metin_silme_zamani > 0 and self.simdiki_zaman > self.metin_silme_zamani:
                self.metin = self.font.render("", True, self.RENK_BEYAZ)
                self.metin_silme_zamani = 0
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    calisiyor = False
                
                if event.type == pygame.VIDEORESIZE:
                    # 1. Yeni ekran boyutlarını kaydet
                    self.ekran_en, self.ekran_boy = event.w, event.h
                    self.menu.konumGuncelle()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Depodaki buton listesini tarıyoruz (aktif butonun yeri için)
                    for i, buton in enumerate(self.menu.butonlar):
                        if buton.tiklandi_mi(event.pos):
                            akt_but_ind = i

                if event.type in self.mouse_aksiyonlari:
                    self.mouse_aksiyonlari[event.type]()
                    
                if event.type==KEYDOWN and event.key in self.klavye_aksiyonlari:
                    self.klavye_aksiyonlari[event.key]()
                    
                if event.type == KEYUP:
                # DÜZELTME: Raspberry Pi'de tuş bırakılınca robot durmalı, 
                # aksi halde haf?zada kalan yönü sonsuza kadar sürdürür.
                    if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT,  K_w, K_s, K_x, K_z, K_c, K_a, K_d]:
                        with self.durum_lock:
                            self.anlik_yon = "DUR"
                            self.anlik_hiz=0.60
                   
            
            # 2. VERİLERİN ANLIK DURUMUNU AL
            with self.durum_lock:
                self.hedef_yon = self.anlik_yon
                self.hedef_hiz = self.anlik_hiz
                YASAK_ALAN = self.ENGEL_YAKIN
                #self.son_yon="DUR"

            if self.ROTA_KURULMUYOR:

                if YASAK_ALAN and self.hedef_yon == "ILERI":
                    robotSur("DUR", 0.0) # ncr nesnesini fonksiyona gönderiyoruz
                    print("[?? ENGEL] Önü kapalı! ileri sürüş engellendi.      ", end="\r")
                else:
                    robotSur(self.hedef_yon, self.hedef_hiz) # ncr nesnesini fonksiyona gönderiyoruz
                    print(f"[Durum] Motor: {self.hedef_yon:<18} | Engel: {str(YASAK_ALAN):<8}", end="\r")    
            else:
                if self.hedef_yon != self.son_yon:
                    self.rota_liste=self.rotaEkle(self.hedef_yon, self.rota_liste)
                    rota_listestr=",".join(self.rota_liste)
                    metinrota = self.font.render(rota_listestr, True, self.RENK_BEYAZ)
                    self.metin_silme_zamani = self.simdiki_zaman + 2000
                    self.son_yon = self.hedef_yon
                
            # 3. YÖN DEĞİŞTİYSE LED SİNYALLERİNİ GÜNCELLE
            
            if self.hedef_yon != self.son_yon:
                sinyalVer(self.hedef_yon)
                self.son_yon = self.hedef_yon
                    
            self.ekran.fill((30, 30, 30))
            
            # Depodan gelen butonlar? ekrana çizdiriyoruz
            for i, buton in enumerate(self.menu.butonlar):
                    
                buton.ciz(self.ekran, AKTIF=(i == akt_but_ind))
                #print(self.butonYAKTIF.pasif_renk)

            ust_metin = self.font.render(f"Hız: %{int(self.hedef_hiz * 100)} | Durum: {self.hedef_yon}", True, self.RENK_BEYAZ)
            self.ekran.blit(ust_metin, (50, 20))
            self.ekran.blit(self.metin, (50, 50))
            self.ekran.blit(metinrota, (20, self.ekran_boy-75))


            pygame.display.flip() # Değişiklikleri ekrana yansıt
            self.saat.tick(60)
        pi.stop()
        pygame.quit()
        sys.exit()    
if __name__ == "__main__":
    Uygulama().calistir()