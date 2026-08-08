import pigpio

KUMANDA_HARITASI = {
    "0xFF1198A7": "SOLA",
    "0xFF1184BB": "SAGA",
    "0xFF11A897": "ILERI",
    "0xFF11A49B": "GERI",
    "0xFF11B887": "DUR",       # "OK"
    "0xFF11BCB3": "TAMSOLA",   # "INFO"
    "0xFF11AC93": "TAMSAGA",   # "SAT"
    "0xFF1194AB": "HIZARTIR",  # "MENU"
    "0xFF11B48B": "HIZAZALT"   # "EXIT"
}
class KOAlici:
    def __init__(self, pi, pin):
        self.pi = pi
        self.pin = pin
        self.anlik_yon = "DUR"  # İlk başta robot dursun
        self.kod = 0
        self.bit_sayisi = 0
        self.son_zaman = 0
       
        self.pi.set_mode(pin, pigpio.INPUT)
        self.cb = self.pi.callback(pin, pigpio.EITHER_EDGE, self._sinyal_coz)

    def _sinyal_coz(self, gpio, level, tick):
        if level == pigpio.TIMEOUT:
            if self.bit_sayisi >= 32:
                # Ba?ar?l? okunan 32 bitlik NEC kodunu HEX format?na çevir
                hex_kod = f"0xFF{self.kod & 0xFFFFFF:06X}"
                # Çözülen kod sözlüğümüzde varsa sınıfın içindeki anlik_yon'u güncelle
                if hex_kod in KUMANDA_HARITASI:
                    self.anlik_yon = KUMANDA_HARITASI[hex_kod]
                
                
            self.kod = 0
            self.bit_sayisi = 0
            self.pi.set_watchdog(self.pin, 0)
        else:
            sure = pigpio.tickDiff(self.son_zaman, tick)
            self.son_zaman = tick
           
            if level == 1:
                if 8000 < sure < 10000: # NEC Ba?lang?ç Sinyali
                    self.pi.set_watchdog(self.pin, 150)
            elif level == 0 and self.bit_sayisi < 32:
                if sure > 1000:
                    self.kod |= (1 << (31 - self.bit_sayisi))
                self.bit_sayisi += 1 
