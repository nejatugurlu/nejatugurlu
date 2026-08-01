import pygame

class Buton():
    def __init__(self, app, x=0, y=0, genislik=100, yukseklik=50, metin="", olay_tipi=""):
        self.app=app
        self.rect = pygame.Rect(x, y, genislik, yukseklik)
        self.metin = metin
        self.olay_tipi = olay_tipi
        self.font = self.app.font
        self.fontB= self.app.fontB
        self.RENK_BEY=self.app.RENK_BEYAZ 
        self.RENK_ARKA = self.app.RENK_ARKA_PLAN
        self.RENK_PAS = self.app.RENK_BUTON_PASIF
        self.RENK_AKT = self.app.RENK_BUTON_AKTIF
        self.RENK_KIR = self.app.RENK_KIRMIZI
        self.pasif_renk = self.RENK_PAS
        self.aktif_renk = self.RENK_AKT
    
    def ciz(self, ekran, AKTIF):
        renk = self.aktif_renk if AKTIF else self.pasif_renk
        if self.rect.width == self.rect.height:      
            pygame.draw.ellipse(ekran, self.RENK_KIR, self.rect)
        else:
            if self.metin=="HIZ" or self.metin=="ROTA":
                pygame.draw.rect(ekran, self.RENK_PAS, self.rect)
            else:
                pygame.draw.rect(ekran, renk, self.rect)
        if self.metin==self.metin=="+" or self.metin=="-" :
            yazi_yuzeyi = self.fontB.render(self.metin, True, self.RENK_BEY)
        else:
            yazi_yuzeyi = self.font.render(self.metin, True, self.RENK_BEY)
        yazi_rect = yazi_yuzeyi.get_rect()
        yazi_rect.center = self.rect.center
        ekran.blit(yazi_yuzeyi, yazi_rect)

    def tiklandi_mi(self, fare_konumu):
        if self.rect.collidepoint(fare_konumu):
            pygame.event.post(pygame.event.Event(self.olay_tipi))
            return True
        return False

            
class kumandaMenusu:
    def __init__(self,app):
        self.app=app

        # Özel olaylar (Custom Events)
        self.EVENT_DUR = pygame.event.custom_type()
        self.EVENT_SOLA = pygame.event.custom_type()
        self.EVENT_SAGA = pygame.event.custom_type()
        self.EVENT_ILERI = pygame.event.custom_type()
        self.EVENT_GERI = pygame.event.custom_type()
        self.EVENT_TAMSOLA = pygame.event.custom_type()
        self.EVENT_TAMSAGA = pygame.event.custom_type()
        self.EVENT_ARTIR = pygame.event.custom_type()
        self.EVENT_AZALT = pygame.event.custom_type()
        self.EVENT_KUR = pygame.event.custom_type()
        self.EVENT_GIT = pygame.event.custom_type()
        
        self.EVENT_HIZ = pygame.event.custom_type()
        self.EVENT_ROTA = pygame.event.custom_type()

        # Veri Deposu
        # Buton Alanlar?n?n Belirlenmesi
        self.dur_but_dkd = pygame.Rect(0, 0, 75, 75)
        self.sola_but_dkd = pygame.Rect(0, 0, 50, 100)
        self.saga_but_dkd = pygame.Rect(0, 0, 50, 100)
        self.ileri_but_dkd = pygame.Rect(0, 0, 100, 50)
        self.geri_but_dkd = pygame.Rect(0, 0, 100, 50)
        self.tamsola_but_dkd = pygame.Rect(0, 0, 100, 50)
        self.tamsaga_but_dkd = pygame.Rect(0, 0, 100, 50)
        self.hizart_but_dkd = pygame.Rect(0, 0, 50, 50)
        self.hizaz_but_dkd = pygame.Rect(0, 0, 50, 50)
        self.rotakur_but_dkd = pygame.Rect(0, 0, 50, 50)
        self.rotagit_but_dkd = pygame.Rect(0, 0, 50, 50)
        self.hiz_but_dkd = pygame.Rect(0, 0, 75, 50)
        self.rota_but_dkd = pygame.Rect(0, 0, 75, 50)

        metinler=["DUR","SOLA","SAĞA","İLERİ","GERİ","TAMSOLA","TAMSAĞA","+","-",
                 "KUR","GİT","HIZ","ROTA"]
        dkdrtgler=[self.dur_but_dkd, self.sola_but_dkd, self.saga_but_dkd, self.ileri_but_dkd, self.geri_but_dkd,
                  self.tamsola_but_dkd, self.tamsaga_but_dkd, self.hizart_but_dkd, self.hizaz_but_dkd,
                 self.rotakur_but_dkd, self.rotagit_but_dkd, self.hiz_but_dkd, self.rota_but_dkd  ]
        
      
        self.olaylar = [self.EVENT_DUR, self.EVENT_SOLA,self.EVENT_SAGA,self.EVENT_ILERI,self.EVENT_GERI,
                   self.EVENT_TAMSOLA,self.EVENT_TAMSAGA,self.EVENT_ARTIR,
                   self.EVENT_AZALT,self.EVENT_KUR,self.EVENT_GIT,self.EVENT_HIZ,self.EVENT_ROTA]

        # Butonlar? otomatik olu?turup listeye dolduruyoruz
        self.butonlar = []
        # zip ile tüm elemanlar? e?le?tirip buton nesnelerini üretiyoruz
        for dk, met, ol in zip(dkdrtgler, metinler, self.olaylar):
            yeni_buton = Buton(self.app, dk.x, dk.y, dk.width, dk.height, met, ol) # *dk ile x, y, g, y de?erlerini da??tt?k
            self.butonlar.append(yeni_buton)
        self.konumGuncelle()
 
 
    def konumGuncelle(self):
        self.merkez_x = self.app.ekran_en / 2
        self.merkez_y = self.app.ekran_boy / 2
        
        # ?lk butonu tam ortaya hizala (y ekseninde biraz yukar? al?yoruz ki di?erleri s??s?n)
        self.dur_but_dkd.centerx = self.merkez_x
        self.dur_but_dkd.centery = self.merkez_y-25
        
        self.sola_but_dkd.centerx = self.dur_but_dkd.centerx-150
        self.sola_but_dkd.centery = self.dur_but_dkd.centery
        
        self.saga_but_dkd.centerx = self.dur_but_dkd.centerx+150
        self.saga_but_dkd.centery = self.dur_but_dkd.centery
        
        self.ileri_but_dkd.centerx = self.dur_but_dkd.centerx
        self.ileri_but_dkd.bottom = self.dur_but_dkd.top - 150
        
        self.geri_but_dkd.centerx = self.dur_but_dkd.centerx
        self.geri_but_dkd.top = self.dur_but_dkd.bottom + 100
        
        self.tamsola_but_dkd.centerx = self.sola_but_dkd.centerx
        self.tamsola_but_dkd.centery = self.sola_but_dkd.centery+100
        
        self.tamsaga_but_dkd.centerx = self.saga_but_dkd.centerx
        self.tamsaga_but_dkd.centery = self.saga_but_dkd.centery+100
        
        self.hizart_but_dkd.centerx = self.sola_but_dkd.centerx
        self.hizart_but_dkd.centery = self.sola_but_dkd.centery+200
        self.hizaz_but_dkd.centerx = self.saga_but_dkd.centerx
        self.hizaz_but_dkd.centery = self.saga_but_dkd.centery+200
        self.rotakur_but_dkd.centerx = self.sola_but_dkd.centerx
        self.rotakur_but_dkd.centery = self.sola_but_dkd.centery+250
        self.rotagit_but_dkd.centerx = self.saga_but_dkd.centerx
        self.rotagit_but_dkd.centery = self.saga_but_dkd.centery+250
        self.hiz_but_dkd.centery=self.hizart_but_dkd.centery
        self.rota_but_dkd.centery=self.rotakur_but_dkd.centery
 
        # Buton nesnelerinin içindeki rect alanlar?n? kesin olarak güncelle
        dkdrtgler = [self.dur_but_dkd, self.sola_but_dkd, self.saga_but_dkd, self.ileri_but_dkd,
                     self.geri_but_dkd , self.tamsola_but_dkd, self.tamsaga_but_dkd, self.hizart_but_dkd,
                     self.hizaz_but_dkd, self.rotakur_but_dkd, self.rotagit_but_dkd, self.hiz_but_dkd,
                     self.rota_but_dkd ]
        for buton, yeni_rect in zip(self.butonlar, dkdrtgler):
            buton.rect = yeni_rect.copy()             
 

       
        