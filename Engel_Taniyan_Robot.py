import pygame
import pigpio
import sys
import time
import threading  # Threading modülü aktif
from pygame.locals import *
from gpiozero import DistanceSensor

from Kizil_Otesi_Alici import KO_Alici
import Robot_Mod

# ==========================================
# THREAD-SAFE GLOBAL DEĞİŞKENLER
# ==========================================
global anlik_yon, anlik_hiz, running
state_lock = threading.Lock()
anlik_yon = "DUR"  
anlik_hiz = 0.6         # Varsayılan başlangıç hızı %60
engel_yakin = False   
MIN_UZAKLIK_cm= 15.0 
running = True

echopin, triggerpin = 14, 15


# =============================UZAKLIK SENSÖRÜ=================================================0

sensor = DistanceSensor(echo=echopin, trigger=triggerpin, max_distance=2.0)


def sensor_thread_func(): # Argüman tamamen kaldırıldı, eski haline döndü
    global engel_yakin, running 
    
    # Sensörün ana programda tamamen kurulmas? için bekliyoruz
    #time.sleep(0.5) 
    print(f"[Sensör] Mesafe kontrolü aktif. Sınır: {MIN_UZAKLIK_cm} cm")
    
    while running:
        try:
            # Karmaşık if kontrolleri yerine doğrudan ana değişkenden okuyoruz
            uzaklik_cm = sensor.distance * 100
            
            # TEST SATIRI: Mesafe akışını canlı göreceğiz
            # print(f"Anlık Mesafe: {uzaklik_cm:.1f} cm  ", end="\r")
            
            with state_lock:
                if uzaklik_cm < MIN_UZAKLIK_cm:
                    engel_yakin = True
                else:
                    engel_yakin = False
        except Exception as e:
            # Donan?msal bir hata (bağlantı vb.) varsa buraya düşecek
            print(f"\n[Sensör Donanım Hatası]: {e}")
            
        time.sleep(0.05)



# Pygame Başlatma
pygame.init()
EN, BOY = 700, 600
ekran = pygame.display.set_mode((EN,BOY),RESIZABLE)
pygame.display.set_caption("ENGELDE DURAN ROBOT")
saat = pygame.time.Clock()

# Yazı Tipi ve Renk Tanımlamaları
font = pygame.font.SysFont("Arial", 18)
RENK_ARKA_PLAN = (40, 44, 52)
RENK_BEYAZ = (255, 255, 255)
RENK_KIRMIZI = (231, 76, 60)
RENK_BUTON = (52, 152, 219)
RENK_AKTIF = (46, 204, 113)

# Özel Event Tanımlamaları
EVENT_SOLA_TIKLANDI = pygame.event.custom_type()
EVENT_SAGA_TIKLANDI = pygame.event.custom_type()
EVENT_ILERI_TIKLANDI = pygame.event.custom_type()
EVENT_GERI_TIKLANDI = pygame.event.custom_type()
EVENT_DUR_TIKLANDI = pygame.event.custom_type()

EVENT_TAMSOLA_TIKLANDI = pygame.event.custom_type()
EVENT_TAMSAGA_TIKLANDI = pygame.event.custom_type()

EVENT_HIZARTIR_TIKLANDI = pygame.event.custom_type()
EVENT_HIZAZALT_TIKLANDI = pygame.event.custom_type()

# Buton Alanlarının Belirlenmesi
sola_buton_rect = pygame.Rect(200, 250, 50, 100)
saga_buton_rect = pygame.Rect(450, 250, 50, 100)
ileri_buton_rect = pygame.Rect(300, 100, 100, 50)
geri_buton_rect = pygame.Rect(300, 450, 100, 50)

dur_buton_rect = pygame.Rect(313, 300, 75 , 75)
tamsola_buton_rect = pygame.Rect(175, 375, 100, 50)
tamsaga_buton_rect = pygame.Rect(425, 375, 100, 50)
hizartir_buton_rect = pygame.Rect(175, 550, 100, 50)
hizazalt_buton_rect = pygame.Rect(425, 550, 100, 50)

met_rect = pygame.Rect(50, BOY-25, 600, 30)


# Buton metinlerini hazırlama
sola_metin = font.render("SOLA", True, RENK_BEYAZ)
saga_metin = font.render("SAĞA", True, RENK_BEYAZ)
ileri_metin = font.render("İLERİ", True, RENK_BEYAZ)
geri_metin = font.render("GERİ", True, RENK_BEYAZ)

dur_metin = font.render("DUR", True, RENK_BEYAZ)
tamsola_metin = font.render("TAMSOLA", True, RENK_BEYAZ)
tamsaga_metin = font.render("TAMSAĞA", True, RENK_BEYAZ)
hizartir_metin = font.render("HIZARTIR", True, RENK_BEYAZ)
hizazalt_metin = font.render("HIZAZALT", True, RENK_BEYAZ)

metin = font.render("Sistem Hazır", True, RENK_BEYAZ)

def ortala_yaz(metin, tus):
    ekran.blit(metin, (tus.x + (tus.width - metin.get_width()) // 2,
                     tus.y + (tus.height - metin.get_height()) // 2))

# =======UZAKLIK SENSÖRÜ==========0====================================================
# Sensör thread'ini başlatıyoruz
sensor_thread = threading.Thread(target=sensor_thread_func, daemon=True)
sensor_thread.start()

print("Pi Hazır. OK TUŞLARI: Yön | 1-5 TUŞLARI: Hız Ayarı | ESC: Çıkış")

# ======KIZIL ÖTESİ=================================================================
pi = pigpio.pi()
ALICI_PINI = 24
alici = KO_Alici(pi, ALICI_PINI)

print("Sistem Başarıyla Kuruldu!")
print("Şu anda GPIO 24 pininden kumanda sinyalleri ve bilgisayardan klavye tuşları dinleniyor.")
print("Çıkış yapmak için CTRL+C tuşlarına basın.\n")

# ANA DÖNGÜ ======================================================0
son_yon = "DUR" 
metin_silme_zamani = 0

while running:
    fare_konumu = pygame.mouse.get_pos()
    simdiki_zaman = pygame.time.get_ticks()
    if alici.anlik_yon != "DUR":
        anlik_yon=alici.anlik_yon

    # Belirli bir süre sonra alttaki bilgi metnini temizlemek için zaman kontrolü
    if metin_silme_zamani > 0 and simdiki_zaman > metin_silme_zamani:
        metin = font.render("", True, RENK_BEYAZ)
        metin_silme_zamani = 0

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        elif event.type == KEYDOWN:
            metin_silme_zamani = simdiki_zaman + 2000 # Yazı ekranda 2 saniye kalsın
            if (event.key == K_UP) or (event.key == K_w):
                metin = font.render("İLERİ butonu basıldı", True, RENK_BEYAZ)
                with state_lock: anlik_yon = "ILERI"
            elif (event.key == K_DOWN) or (event.key == K_z):
                metin = font.render("GERİ butonu basıldı", True, RENK_BEYAZ)
                with state_lock: anlik_yon = "GERI"
            elif (event.key == K_LEFT) or (event.key == K_a):
                metin = font.render("SOLA butonu basıldı", True, RENK_BEYAZ)
                with state_lock: anlik_yon = "SOLA"
            elif (event.key == K_RIGHT) or (event.key == K_s):
                metin = font.render("SAĞA butonu basıldı", True, RENK_BEYAZ)
                with state_lock: anlik_yon = "SAGA"
            elif event.key == K_1:
                with state_lock: anlik_hiz = 0.2
            elif event.key == K_2:
                with state_lock: anlik_hiz = 0.4
            elif event.key == K_3:
                with state_lock: anlik_hiz = 0.6
            elif event.key == K_4:
                with state_lock: anlik_hiz = 0.8
            elif event.key == K_5:
                with state_lock: anlik_hiz = 1.0
            elif event.key == K_b or event.key == K_ESCAPE:
                with state_lock:
                    anlik_yon = "DUR"
                    anlik_hiz=0.0
                running = False

        elif event.type == KEYUP:
            # DÜZELTME: Raspberry Pi'de tuş bırakılınca robot durmalı, 
            # aksi halde hafızada kalan yönü sonsuza kadar sürdürür.
            if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT, K_1, K_2, K_3, K_4, K_5, K_7, K_s, K_x, K_z, K_c, K_a, K_d]:
                with state_lock:
                    anlik_yon = "DUR"
                    anlik_hiz=0.0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Sol tık
                if sola_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_SOLA_TIKLANDI))
                if saga_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_SAGA_TIKLANDI))
                if ileri_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_ILERI_TIKLANDI))
                if geri_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_GERI_TIKLANDI))
                if dur_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_DUR_TIKLANDI))
                    
                if tamsola_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_TAMSOLA_TIKLANDI))
                if tamsaga_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_TAMSAGA_TIKLANDI))
                
                if hizartir_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_HIZARTIR_TIKLANDI))
                if hizazalt_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_HIZAZALT_TIKLANDI))            

            elif event.button == 3:  # Sağ tık
                if sola_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_TAMSOLA_TIKLANDI))
                if saga_buton_rect.collidepoint(fare_konumu):
                    pygame.event.post(pygame.event.Event(EVENT_TAMSAGA_TIKLANDI))

        # Özel Eventlerin Yakalanması
        elif event.type == EVENT_SOLA_TIKLANDI:
            metin = font.render("Event: SOLA", True, RENK_BEYAZ)
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock: anlik_yon = "SOLA" 
        elif event.type == EVENT_SAGA_TIKLANDI:
            metin = font.render("Event: SAĞA", True, RENK_BEYAZ)
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock: anlik_yon = "SAGA"
        elif event.type == EVENT_ILERI_TIKLANDI:
            metin = font.render("Event: İLERİ", True, RENK_BEYAZ)
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock: anlik_yon = "ILERI"
        elif event.type == EVENT_GERI_TIKLANDI:
            metin = font.render("Event: GERİ", True, RENK_BEYAZ)
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock: anlik_yon = "GERI"
        elif event.type == EVENT_TAMSOLA_TIKLANDI:
            metin = font.render("Event: TAMSOLA", True, RENK_BEYAZ)
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock: anlik_yon = "TAMSOLA"
        elif event.type == EVENT_TAMSAGA_TIKLANDI:
            metin = font.render("Event: TAMSAĞA", True, RENK_BEYAZ)
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock: anlik_yon = "TAMSAGA"
        elif event.type == EVENT_DUR_TIKLANDI:
            metin = font.render("Event: DUR", True, RENK_KIRMIZI)
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock: anlik_yon = "DUR"
            
           
        elif event.type == EVENT_HIZARTIR_TIKLANDI:
            metin = font.render("Event: HIZARTIR", True, RENK_BEYAZ)
            if (anlik_hiz<1.0) and (anlik_hiz>0.0):
                yeni_hiz=anlik_hiz+0.1
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock:
                anlik_yon = "ILERI"
                anlik_hiz=yeni_hiz
        elif event.type == EVENT_HIZAZALT_TIKLANDI:
            metin = font.render("Event: HIZAZALT", True, RENK_BEYAZ)
            if (anlik_hiz<1.0) and (anlik_hiz>0.0):
                yeni_hiz=anlik_hiz-0.1
            metin_silme_zamani = simdiki_zaman + 2000
            with state_lock:
                anlik_yon = "ILERI"
                anlik_hiz=yeni_hiz

    # ==========================================
    # KODUNUZUN DEVAMI VE GÜVENLİK PROTOKOLÜ
    # ==========================================
    
    # 2. VERİLERİN ANLIK DURUMUNU AL
    with state_lock:
        hedef_yon = anlik_yon
        hedef_hiz = anlik_hiz
        yasak_alan = engel_yakin

    
    if yasak_alan and hedef_yon == "ILERI":
        Robot_Mod.robot_sur("DUR", 0.0) # ncr nesnesini fonksiyona gönderiyoruz
        print("[?? ENGEL] Önü kapalı! ileri sürüş engellendi.      ", end="\r")
    else:
        Robot_Mod.robot_sur(hedef_yon, hedef_hiz) # ncr nesnesini fonksiyona gönderiyoruz
        print(f"[Durum] Motor: {hedef_yon:<8} | Engel: {str(yasak_alan):<8}", end="\r")    
    
    # 3. YÖN DEĞİŞTİYSE LED SİNYALLERİNİ GÜNCELLE
    
    if hedef_yon != son_yon:
        Robot_Mod.sinyal_ver(hedef_yon)
        son_yon = hedef_yon
    
    # ==========================================
    # GÖRSEL ÇİZİM İŞLEMLERİ (RENDER)
    # ==========================================
    ekran.fill(RENK_ARKA_PLAN)

    # Engel durumuna göre İleri buton rengini değiştir (Görsel Geri Bildirim)
    ileri_renk = RENK_KIRMIZI if yasak_alan else (RENK_AKTIF if hedef_yon == "ILERI" else RENK_BUTON)
    sola_renk = RENK_AKTIF if hedef_yon == "SOLA" else RENK_BUTON
    saga_renk = RENK_AKTIF if hedef_yon == "SAGA" else RENK_BUTON
    geri_renk = RENK_AKTIF if hedef_yon == "GERI" else RENK_BUTON
    dur_renk = RENK_KIRMIZI
    tamsola_renk = RENK_AKTIF if hedef_yon == "TAMSOLA" else RENK_BUTON
    tamsaga_renk = RENK_AKTIF if hedef_yon == "TAMSAGA" else RENK_BUTON

    # Butonları Ekrana Çiz
    pygame.draw.rect(ekran, ileri_renk, ileri_buton_rect)
    pygame.draw.rect(ekran, sola_renk, sola_buton_rect)
    pygame.draw.rect(ekran, saga_renk, saga_buton_rect)
    pygame.draw.rect(ekran, geri_renk, geri_buton_rect)
    
    pygame.draw.ellipse(ekran, RENK_KIRMIZI, dur_buton_rect)
    pygame.draw.rect(ekran, tamsola_renk, tamsola_buton_rect)
    pygame.draw.rect(ekran, tamsaga_renk, tamsaga_buton_rect)
    pygame.draw.ellipse(ekran, RENK_KIRMIZI, hizartir_buton_rect)
    pygame.draw.ellipse(ekran, RENK_KIRMIZI, hizazalt_buton_rect)

    # Buton Metinlerini Ortala ve Yaz
    ortala_yaz(ileri_metin, ileri_buton_rect)
    ortala_yaz(sola_metin, sola_buton_rect)
    ortala_yaz(saga_metin, saga_buton_rect)
    ortala_yaz(geri_metin, geri_buton_rect)
    
    ortala_yaz(dur_metin, dur_buton_rect)
    ortala_yaz(tamsola_metin, tamsola_buton_rect)
    ortala_yaz(tamsaga_metin, tamsaga_buton_rect)
    ortala_yaz(hizartir_metin, hizartir_buton_rect)
    ortala_yaz(hizazalt_metin, hizazalt_buton_rect)
    
    # Alt Bilgi Durum Metinleri ve Üst Hız Bilgisi Grafiği
    ekran.blit(metin, (met_rect.x, met_rect.y))
    
    ust_metin = font.render(f"Hız: %{int(hedef_hiz * 100)} | Mod: {hedef_yon}", True, RENK_BEYAZ)
    ekran.blit(ust_metin, (50, 20))
    
    pygame.display.flip()
    saat.tick(60)
    
pygame.quit()
sys.exit()    
    
    
    
    
    
    
    
    
    
    
    
