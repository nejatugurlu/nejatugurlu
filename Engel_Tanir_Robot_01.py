import pygame
import pigpio
import sys
import time
import threading  
from pynput import keyboard
from pygame.locals import *
from gpiozero import PWMLED
from dataclasses import dataclass

from Mouse_Menu_01 import Kumanda_Menu, Buton 
from Kizil_Otesi_Kumanda_01 import KO_Alici
from Uzaklik_Sensor_01 import Mesafe_Kontrol
from Robot_01 import Robot
from Pin_Ayarlari  import Pin

      
class Uygulama:
    def __init__(self):
        pygame.init()
        
        self.FONT = pygame.font.SysFont("Arial", 18)
        self.FONTB= pygame.font.SysFont("Arial", 40)
        self.RENK_BEYAZ = (255, 255, 255)
        self.RENK_ARKA_PLAN = (30, 30, 30)
        self.RENK_BUTON_PASIF = (52, 152, 219)
        self.RENK_BUTON_AKTIF = (0, 255, 0) # Yeşil
        self.RENK_KIRMIZI = (231, 76, 60)
        self.ekran_en=600
        self.ekran_boy=700
        self.ekran = pygame.display.set_mode((self.ekran_en, self.ekran_boy),pygame.RESIZABLE)
        pygame.display.set_caption("TUŞLU YARIŞ ARABASI")
        
        self.saat = pygame.time.Clock()
        
        self.menu = Kumanda_Menu(self)
        self.anlik_yon="DUR"
        self.anlik_hiz=0.6
        self.hedef_yon=self.anlik_yon
        self.hedef_hiz=self.anlik_hiz
        self.ENGEL_YAKIN=False
        self.ROTA_KURULMUYOR=True
        self.rota_liste=[]        
        self.durum_lock = threading.Lock()

        # Olaylar ile fonksiyonların eşleşmesi
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
        
    def dur(self):
        self.metin = self.FONT.render("Basılı: DUR", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Durdu.....\n")
        with self.durum_lock:self.anlik_yon = "DUR"  

    def solaGit(self):
        self.metin = self.FONT.render("Basılı: SOLA", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Sola gidiyor.....\n")
        with self.durum_lock:self.anlik_yon = "SOLA"
    def sagaGit(self):
        self.metin = self.FONT.render("Basılı: SAĞA", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Sağa gidiyor.....\n")
        with self.durum_lock:self.anlik_yon = "SAGA"
    def ileriGit(self):
        self.metin = self.FONT.render("Basılı: İLERİ", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("İleri gidiyor.....\n")
        with self.durum_lock:self.anlik_yon = "ILERI"
    def geriGit(self):
        self.metin = self.FONT.render("Basılı: GERİ", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Geri gidiyor.....\n" )
        with self.durum_lock:self.anlik_yon = "GERI"

    def tamsolaGit(self):
        self.metin = self.FONT.render("Basılı: TAMSOLA", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Tamsola gidiyor.....\n" )
        with self.durum_lock:self.anlik_yon = "TAMSOLA"
    def tamsagaGit(self):
        self.metin = self.FONT.render("Basılı: TAMSAĞA", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        print("Tamsağa gidiyor.....\n" )
        with self.durum_lock:self.anlik_yon = "TAMSAGA"

    def hizArtir(self):
        #print("Hız artırılıyor..." )
        with self.durum_lock:
            self.anlik_hiz = min(1.0, round(self.anlik_hiz + 0.1, 1))
            self.anlik_yon = "ILERI"
        metin = self.FONT.render(f"Hız: %{int(self.anlik_hiz * 100)} | Durum: {self.hedef_yon}", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        
    def hizAzalt(self):
        print("Hız azaltılıyor..." ) 
        with self.durum_lock:
            self.anlik_hiz = max(0.0, round(self.anlik_hiz - 0.1, 1))
            self.anlik_yon = "ILERI"
        metin = self.FONT.render(f"Hız: %{int(self.anlik_hiz * 100)} | Durum: {self.hedef_yon}", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
            
    def rotaKur(self):
        print("Rota kuruluyor...\n" ) 
        metin = self.FONT.render("Basılı: ROTAKUR", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        self.ROTA_KURULMUYOR=False
        self.rota_liste=[]
        
    def rotaGit(self):
        print("Rota izleniyor...\n" ) 
        metin = self.FONT.render("Basılı: ROTAGIT", True, self.RENK_BEYAZ)
        self.metin_silme_zamani = self.simdiki_zaman + 2000
        self.ROTA_KURULMUYOR=True
        self.rotadaGit(*self.rota_liste)  # burada * argümanları açıyor 

    def rotaEkle(self, yeni_yon, rota_listesi=None):
        if rota_listesi is None:
            rota_listesi = [] # E?er liste gönderilmediyse temiz bir liste aç
        
        rota_listesi.append(yeni_yon)
        return rota_listesi

    def rotadaGit(self, *komutlar):
        # 'komutlar' fonksiyon içinde bir Tuple (demet) gibi davran?r
        print(f"Toplam {len(komutlar)} adet komut alındı.")
        
        for komut in komutlar:
            print(f"Robotun sıradaki hareketi: {komut}")
            self.rbt.robotSur(komut)
            time.sleep(3)

    def calistir(self):
        print("Pi Hazır. OK TUŞLARI: Yön | 1-5 TUŞLARI: Hız Ayarı | ESC: Çıkış" , end="\r")

        # ======KIZIL ÖTESİ=================================================================
        pi = pigpio.pi()
        ALICI_PINI = Pin.KO_PIN
        alici = KO_Alici(pi, ALICI_PINI)

        print("Sistem Başarıyla Kuruldu!")
        print("Şu anda GPIO 24 pininden kumanda sinyalleri ve bilgisayardan klavye tuşları dinleniyor.")
        print("Çıkış yapmak için CTRL+C tuşlarına basın.\n")
        self.son_yon= ""
        self.metin_silme_zamani = 0
        
        ust_metin = self.FONT.render(f"Hız: %{int(self.anlik_hiz * 100)} | Durum: {self.hedef_yon}", True, self.RENK_BEYAZ)
        self.metin = self.FONT.render("Sistem Hazır", True, self.RENK_BEYAZ)
        metinrota=self.FONT.render("ROTA:  ", True, self.RENK_BEYAZ)
        
        app=Uygulama()
        self.rbt=Robot(app, Pin.SL_ILR, Pin.SL_GR,
                       Pin.SG_ILR, Pin.SG_GR )        

        calisiyor = True
        akt_but_ind = -1
        self.onceki_engel_durumu = None 
        metinrota = self.FONT.render("", True, self.RENK_BEYAZ) # ? Çökmeyi önlemek için varsay?lan de?er
 
        while calisiyor:
            # Kızıl Ötesi TV kontrol (NEXT)
            if alici.anlik_yon != "DUR":
                self.anlik_yon=alici.anlik_yon
            # uzaklık sensörü kontrol ediyor
           
            self.simdiki_zaman = pygame.time.get_ticks()

            # Belirli bir süre sonra alttaki bilgi metnini temizlemek için zaman kontrolü
            if self.metin_silme_zamani > 0 and self.simdiki_zaman > self.metin_silme_zamani:
                self.metin = self.FONT.render("", True, self.RENK_BEYAZ)
                self.metin_silme_zamani = 0
            
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                        
                    case pygame.VIDEORESIZE:
                        # 1. Yeni ekran boyutlarını kaydediyoruz
                        self.ekran_en, self.ekran_boy = event.w, event.h
                        self.menu.konum_guncelle()  # PEP 8 standardına göre snake_case yapıldı
                        
                    case pygame.MOUSEBUTTONDOWN if event.button == 1:
                        # 'if' koşulunu doğrudan case ifadesinin yanına (Guard) ekleyebiliyoruz
                        for i, buton in enumerate(self.menu.butonlar):
                            if buton.tiklandi_mi(event.pos):
                                akt_but_ind = i
                                
                    case pygame.KEYDOWN if event.key in self.klavye_aksiyonlari:
                        # Klavyeden bir tuşa basıldıysa ve bu tuş aksiyon haritamızda varsa tetikliyoruz
                        self.klavye_aksiyonlari[event.key]()
                        
                    case pygame.KEYUP:
                        # Ahududu Pi güvenlik düzeltmesi: Tuş bırakılınca robotu güvenle durduruyoruz
                        guvenli_tuslar = {K_UP, K_DOWN, K_LEFT, K_RIGHT, K_w, K_s, K_x, K_z, K_c, K_a, K_d}
                        if event.key in guvenli_tuslar:
                            with self.durum_lock:
                                self.anlik_yon = "DUR"
                                self.anlik_hiz = 0.60
                                
                    case e_type if e_type in self.mouse_aksiyonlari:
                        # Eğer yukarıdaki case'lere girmeyen bir mouse olayı ise (ve sözlükte varsa) tetikliyoruz
                        self.mouse_aksiyonlari[e_type]()
                        
            with self.durum_lock:
                su_anki_durum = self.ENGEL_YAKIN

            # KR?T?K NOKTA: Sadece durum DEĞİŞTİYSE ekrana yazd?r
            if su_anki_durum != self.onceki_engel_durumu:
                if su_anki_durum:
                    print("\n[ROBOT DURUMU] >>> ENGEL VAR! <<< (Yol Kilitlendi)")
                else:
                    print("\n[ROBOT DURUMU] >>> YOL TEM?Z <<< (Sürüş Serbest)")
                
                # Yeni durumu haf?zaya kaydediyoruz ki bir sonraki ad?mda tekrar yazmas?n
                self.onceki_engel_durumu = su_anki_durum


            # 2. VERİLERİN ANLIK DURUMUNU AL
            with self.durum_lock:
                self.hedef_yon = self.anlik_yon
                self.hedef_hiz = self.anlik_hiz
                YASAK_ALAN = self.ENGEL_YAKIN


            # ? S?NYAL TET?KLEME VE ROTA YÖNET?M?
            if self.hedef_yon != self.son_yon:
                # 1. Önce LED sinyalini tetikliyoruz (Böylece thread kesinlikle ba?lar)
                self.rbt.sinyalVer(self.hedef_yon)
                
                # 2. E?er rota modu aktifse rotaya ekleme yap?yoruz
                if not self.ROTA_KURULMUYOR:
                    self.rota_liste = self.rotaEkle(self.hedef_yon, self.rota_liste)
                    rota_listestr = ",".join(self.rota_liste)
                    metinrota = self.FONT.render(rota_listestr, True, self.RENK_BEYAZ)
                    self.metin_silme_zamani = self.simdiki_zaman + 2000
                
                # 3. Durumu güncelliyoruz (Sadece tek bir yerde e?itleme yap?l?yor)
                self.son_yon = self.hedef_yon

            # Sürü? mekanizmas? kontrolü

            if self.ROTA_KURULMUYOR:
 
                if YASAK_ALAN and self.hedef_yon == "ILERI":
                    self.rbt.rbtotSur("DUR", 0.0) # ncr nesnesini fonksiyona gönderiyoruz
                    print("[?? ENGEL] Önü kapalı! ileri sürüş engellendi.      ", end="\r")
                else:
                    self.rbt.robotSur(self.hedef_yon, self.hedef_hiz) # ncr nesnesini fonksiyona gönderiyoruz
                    print(f"[Durum] Motor: {self.hedef_yon:<18} | Engel: {str(YASAK_ALAN):<8}", end="\r")    
                    
            
            self.ekran.fill((30, 30, 30))
            
            # Depodan gelen butonlar? ekrana çizdiriyoruz
            for i, buton in enumerate(self.menu.butonlar):
                    
                buton.ciz(self.ekran, AKTIF=(i == akt_but_ind))
                #print(self.butonYAKTIF.pasif_renk)

            ust_metin = self.FONT.render(f"Hız: %{int(self.hedef_hiz * 100)} | Durum: {self.hedef_yon}", True, self.RENK_BEYAZ)
            self.ekran.blit(ust_metin, (50, 20))
            self.ekran.blit(self.metin, (50, 50))
            self.ekran.blit(metinrota, (20, self.ekran_boy-75))


            pygame.display.flip() # Değişiklikleri ekrana yansıt
            self.saat.tick(30)
        pi.stop()
        pygame.quit()
        sys.exit()    
if __name__ == "__main__":
    Uygulama().calistir()
