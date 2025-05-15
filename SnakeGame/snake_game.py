import pygame
import random
import sys
import math
import json
import os
from datetime import datetime

# Pygame başlatma
pygame.init()

# Renkler
SIYAH = (0, 0, 0)
BEYAZ = (255, 255, 255)
KIRMIZI = (255, 0, 0)
YESIL = (0, 255, 0)
MAVI = (0, 0, 255)
TURKUAZ = (0, 255, 255)
KOYU_YESIL = (0, 200, 0)
ACIK_KIRMIZI = (255, 100, 100)
MOR = (128, 0, 128)
ACIK_MAVI = (100, 200, 255)
KAHVERENGI = (139, 69, 19)
ACIK_KAHVERENGI = (205, 133, 63)
MODERN_YESIL = (46, 204, 113)
ACIK_MODERN_YESIL = (88, 214, 141)
KOYU_MODERN_YESIL = (39, 174, 96)

# Oyun ayarları
PENCERE_GENISLIK = 800
PENCERE_YUKSEKLIK = 600
BLOK_BOYUT = 20
BASLANGIC_HIZ = 8
MAKSIMUM_HIZ = 20
HIZ_ARTIS = 0.5

# Oyun penceresi
ekran = pygame.display.set_mode((PENCERE_GENISLIK, PENCERE_YUKSEKLIK))
pygame.display.set_caption('Yılan Oyunu')
saat = pygame.time.Clock()

class Buton:
    def __init__(self, x, y, genislik, yukseklik, text, renk):
        self.rect = pygame.Rect(x, y, genislik, yukseklik)
        self.text = text
        self.renk = renk
        self.hover = False

    def ciz(self, surface):
        renk = (min(self.renk[0] + 30, 255), min(self.renk[1] + 30, 255), min(self.renk[2] + 30, 255)) if self.hover else self.renk
        pygame.draw.rect(surface, renk, self.rect, border_radius=12)
        pygame.draw.rect(surface, BEYAZ, self.rect, 2, border_radius=12)
        
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, BEYAZ)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def fare_uzerinde(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover

class Yilan:
    def __init__(self):
        self.pozisyon = [100, 50]
        self.govde = [[100, 50], [90, 50], [80, 50]]
        self.yon = "SAG"
        self.skor = 0
        self.yeni_blok = False
        self.hiz = BASLANGIC_HIZ

    def hareket_et(self):
        if self.yon == "SAG":
            self.pozisyon[0] += BLOK_BOYUT
        elif self.yon == "SOL":
            self.pozisyon[0] -= BLOK_BOYUT
        elif self.yon == "YUKARI":
            self.pozisyon[1] -= BLOK_BOYUT
        elif self.yon == "ASAGI":
            self.pozisyon[1] += BLOK_BOYUT

        self.govde.insert(0, list(self.pozisyon))
        if not self.yeni_blok:
            self.govde.pop()
        else:
            self.yeni_blok = False

    def yem_ye(self, yem_pozisyon):
        mesafe = math.sqrt((self.pozisyon[0] - yem_pozisyon[0])**2 + 
                          (self.pozisyon[1] - yem_pozisyon[1])**2)
        if mesafe < BLOK_BOYUT:
            self.skor += 1
            self.yeni_blok = True
            # Hızı artır
            self.hiz = min(BASLANGIC_HIZ + (self.skor * HIZ_ARTIS), MAKSIMUM_HIZ)
            return True
        return False

    def carpma_kontrol(self):
        if (self.pozisyon[0] >= PENCERE_GENISLIK or self.pozisyon[0] < 0 or
            self.pozisyon[1] >= PENCERE_YUKSEKLIK or self.pozisyon[1] < 0 or
            list(self.pozisyon) in self.govde[1:]):
            return True
        return False

class SkorKayit:
    def __init__(self):
        self.skorlar = {}
        self.skor_dosyasi = "skorlar.json"
        self.skorlari_yukle()

    def skorlari_yukle(self):
        if os.path.exists(self.skor_dosyasi):
            with open(self.skor_dosyasi, 'r') as f:
                self.skorlar = json.load(f)
        else:
            self.skorlar = {}

    def skor_kaydet(self, kullanici_adi, skor, hiz):
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if kullanici_adi not in self.skorlar:
            self.skorlar[kullanici_adi] = []
        self.skorlar[kullanici_adi].append({
            "skor": skor,
            "hiz": hiz,
            "tarih": tarih
        })
        # En son 10 skoru tut
        self.skorlar[kullanici_adi] = sorted(self.skorlar[kullanici_adi], 
                                            key=lambda x: x["skor"], 
                                            reverse=True)[:10]
        self.skorlari_kaydet()

    def skorlari_kaydet(self):
        with open(self.skor_dosyasi, 'w') as f:
            json.dump(self.skorlar, f)

    def skorlari_temizle(self):
        self.skorlar = {}
        if os.path.exists(self.skor_dosyasi):
            os.remove(self.skor_dosyasi)

    def en_yuksek_skorlar(self, kullanici_adi):
        if kullanici_adi in self.skorlar:
            return self.skorlar[kullanici_adi]
        return []

class GirdiKutusu:
    def __init__(self, x, y, genislik, yukseklik, text=''):
        self.rect = pygame.Rect(x, y, genislik, yukseklik)
        self.text = text
        self.aktif = False
        self.font = pygame.font.Font(None, 36)
        self.placeholder = "Kullanıcı adınızı girin"
        self.placeholder_renk = (128, 128, 128)

    def olay_isle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.aktif = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN:
            if self.aktif:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 15:  # Maksimum 15 karakter
                        self.text += event.unicode

    def ciz(self, surface):
        # Baloncuk arka planı
        pygame.draw.rect(surface, ACIK_MAVI if self.aktif else SIYAH, self.rect, border_radius=10)
        pygame.draw.rect(surface, BEYAZ, self.rect, 2, border_radius=10)
        
        # Metin veya placeholder
        if self.text:
            text_surface = self.font.render(self.text, True, BEYAZ)
        else:
            text_surface = self.font.render(self.placeholder, True, self.placeholder_renk)
        
        # Metni ortala
        text_rect = text_surface.get_rect()
        text_rect.center = self.rect.center
        surface.blit(text_surface, text_rect)

def yem_olustur(yilan):
    # Duvarlardan en az 2 blok uzakta olacak şekilde sınırları belirle
    min_x = BLOK_BOYUT * 2
    max_x = PENCERE_GENISLIK - (BLOK_BOYUT * 3)
    min_y = BLOK_BOYUT * 2
    max_y = PENCERE_YUKSEKLIK - (BLOK_BOYUT * 3)
    
    while True:
        # Belirlenen sınırlar içinde rastgele x ve y koordinatları oluştur
        x = random.randrange(min_x, max_x, BLOK_BOYUT)
        y = random.randrange(min_y, max_y, BLOK_BOYUT)
        if [x, y] not in yilan.govde:
            return [x, y]

def arkaplan_ciz():
    # Izgara çizimi
    for x in range(0, PENCERE_GENISLIK, BLOK_BOYUT):
        pygame.draw.line(ekran, (40, 40, 40), (x, 0), (x, PENCERE_YUKSEKLIK))
    for y in range(0, PENCERE_YUKSEKLIK, BLOK_BOYUT):
        pygame.draw.line(ekran, (40, 40, 40), (0, y), (PENCERE_GENISLIK, y))

def yilan_ciz(yilan):
    # Yılanın gövdesi
    for i, pos in enumerate(yilan.govde):
        if i == 0:  # Yılanın başı
            # Yılan başı için modern yuvarlak çiz
            pygame.draw.circle(ekran, MODERN_YESIL, 
                             (pos[0] + BLOK_BOYUT//2, pos[1] + BLOK_BOYUT//2), 
                             BLOK_BOYUT//2)
            
            # Gözler
            goz_renk = SIYAH
            goz_beyaz = BEYAZ
            if yilan.yon == "SAG":
                # Göz beyazları
                pygame.draw.circle(ekran, goz_beyaz, (pos[0] + BLOK_BOYUT*3//4, pos[1] + BLOK_BOYUT//4), 4)
                pygame.draw.circle(ekran, goz_beyaz, (pos[0] + BLOK_BOYUT*3//4, pos[1] + BLOK_BOYUT*3//4), 4)
                # Göz bebekleri
                pygame.draw.circle(ekran, goz_renk, (pos[0] + BLOK_BOYUT*3//4, pos[1] + BLOK_BOYUT//4), 2)
                pygame.draw.circle(ekran, goz_renk, (pos[0] + BLOK_BOYUT*3//4, pos[1] + BLOK_BOYUT*3//4), 2)
                # Dil
                pygame.draw.line(ekran, KIRMIZI, (pos[0] + BLOK_BOYUT, pos[1] + BLOK_BOYUT//2),
                               (pos[0] + BLOK_BOYUT + 10, pos[1] + BLOK_BOYUT//2), 2)
            elif yilan.yon == "SOL":
                pygame.draw.circle(ekran, goz_beyaz, (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT//4), 4)
                pygame.draw.circle(ekran, goz_beyaz, (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT*3//4), 4)
                pygame.draw.circle(ekran, goz_renk, (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT//4), 2)
                pygame.draw.circle(ekran, goz_renk, (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT*3//4), 2)
                pygame.draw.line(ekran, KIRMIZI, (pos[0], pos[1] + BLOK_BOYUT//2),
                               (pos[0] - 10, pos[1] + BLOK_BOYUT//2), 2)
            elif yilan.yon == "YUKARI":
                pygame.draw.circle(ekran, goz_beyaz, (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT//4), 4)
                pygame.draw.circle(ekran, goz_beyaz, (pos[0] + BLOK_BOYUT*3//4, pos[1] + BLOK_BOYUT//4), 4)
                pygame.draw.circle(ekran, goz_renk, (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT//4), 2)
                pygame.draw.circle(ekran, goz_renk, (pos[0] + BLOK_BOYUT*3//4, pos[1] + BLOK_BOYUT//4), 2)
                pygame.draw.line(ekran, KIRMIZI, (pos[0] + BLOK_BOYUT//2, pos[1]),
                               (pos[0] + BLOK_BOYUT//2, pos[1] - 10), 2)
            elif yilan.yon == "ASAGI":
                pygame.draw.circle(ekran, goz_beyaz, (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT*3//4), 4)
                pygame.draw.circle(ekran, goz_beyaz, (pos[0] + BLOK_BOYUT*3//4, pos[1] + BLOK_BOYUT*3//4), 4)
                pygame.draw.circle(ekran, goz_renk, (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT*3//4), 2)
                pygame.draw.circle(ekran, goz_renk, (pos[0] + BLOK_BOYUT*3//4, pos[1] + BLOK_BOYUT*3//4), 2)
                pygame.draw.line(ekran, KIRMIZI, (pos[0] + BLOK_BOYUT//2, pos[1] + BLOK_BOYUT),
                               (pos[0] + BLOK_BOYUT//2, pos[1] + BLOK_BOYUT + 10), 2)
        else:
            # Gövde parçaları için modern görünüm
            # Ana gövde rengi
            pygame.draw.circle(ekran, MODERN_YESIL, 
                             (pos[0] + BLOK_BOYUT//2, pos[1] + BLOK_BOYUT//2), 
                             BLOK_BOYUT//2 - 1)
            
            # Parlak efekt
            pygame.draw.circle(ekran, ACIK_MODERN_YESIL,
                             (pos[0] + BLOK_BOYUT//4, pos[1] + BLOK_BOYUT//4),
                             BLOK_BOYUT//6)
            
            # Gövde parçaları arası bağlantı
            if i > 1:
                onceki_pos = yilan.govde[i-1]
                pygame.draw.line(ekran, KOYU_MODERN_YESIL,
                               (pos[0] + BLOK_BOYUT//2, pos[1] + BLOK_BOYUT//2),
                               (onceki_pos[0] + BLOK_BOYUT//2, onceki_pos[1] + BLOK_BOYUT//2),
                               BLOK_BOYUT - 2)

def yem_ciz(yem_pos):
    # Elma şeklinde yem
    # Elma gövdesi
    pygame.draw.circle(ekran, KIRMIZI, (yem_pos[0] + BLOK_BOYUT//2, yem_pos[1] + BLOK_BOYUT//2), BLOK_BOYUT//2)
    # Elma sapı
    pygame.draw.line(ekran, KOYU_YESIL, 
                    (yem_pos[0] + BLOK_BOYUT//2, yem_pos[1]),
                    (yem_pos[0] + BLOK_BOYUT//2, yem_pos[1] - 5), 2)
    # Yaprak
    pygame.draw.ellipse(ekran, YESIL, 
                       pygame.Rect(yem_pos[0] + BLOK_BOYUT//2 - 3, yem_pos[1] - 8, 6, 4))

def oyun_dongusu():
    yilan = Yilan()
    yem = yem_olustur(yilan)
    oyun_devam = True

    while oyun_devam:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and yilan.yon != "SOL":
                    yilan.yon = "SAG"
                elif event.key == pygame.K_LEFT and yilan.yon != "SAG":
                    yilan.yon = "SOL"
                elif event.key == pygame.K_UP and yilan.yon != "ASAGI":
                    yilan.yon = "YUKARI"
                elif event.key == pygame.K_DOWN and yilan.yon != "YUKARI":
                    yilan.yon = "ASAGI"

        yilan.hareket_et()
        if yilan.yem_ye(yem):
            yem = yem_olustur(yilan)

        if yilan.carpma_kontrol():
            return yilan.skor, yilan.hiz

        # Arkaplan
        ekran.fill(SIYAH)
        arkaplan_ciz()
        
        # Yılan ve yem çizimi
        yilan_ciz(yilan)
        yem_ciz(yem)

        pygame.display.flip()
        saat.tick(yilan.hiz)

def oyun_bitti_ekrani(skor, hiz):
    tekrar_oyna_buton = Buton(PENCERE_GENISLIK//2 - 100, PENCERE_YUKSEKLIK//2 + 80, 200, 50, "Tekrar Oyna", MAVI)
    cikis_buton = Buton(PENCERE_GENISLIK//2 - 100, PENCERE_YUKSEKLIK//2 + 150, 200, 50, "Çıkış", KIRMIZI)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    if tekrar_oyna_buton.fare_uzerinde(event.pos):
                        return True
                    elif cikis_buton.fare_uzerinde(event.pos):
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                tekrar_oyna_buton.fare_uzerinde(event.pos)
                cikis_buton.fare_uzerinde(event.pos)

        ekran.fill(SIYAH)
        
        # Oyun bitti yazısı
        font = pygame.font.Font(None, 74)
        text = font.render('Oyun Bitti!', True, BEYAZ)
        text_rect = text.get_rect(center=(PENCERE_GENISLIK/2, PENCERE_YUKSEKLIK/2 - 100))
        ekran.blit(text, text_rect)
        
        # Skor ve hız bilgileri
        font = pygame.font.Font(None, 36)
        skor_text = font.render(f'Final Skor: {skor}', True, BEYAZ)
        hiz_text = font.render(f'Final Hız: {int(hiz)}', True, BEYAZ)
        skor_rect = skor_text.get_rect(center=(PENCERE_GENISLIK/2, PENCERE_YUKSEKLIK/2 - 20))
        hiz_rect = hiz_text.get_rect(center=(PENCERE_GENISLIK/2, PENCERE_YUKSEKLIK/2 + 20))
        ekran.blit(skor_text, skor_rect)
        ekran.blit(hiz_text, hiz_rect)
        
        # Butonları çiz
        tekrar_oyna_buton.ciz(ekran)
        cikis_buton.ciz(ekran)
        
        pygame.display.flip()
        saat.tick(60)

def kullanici_adi_ekrani():
    girdi = GirdiKutusu(PENCERE_GENISLIK//2 - 100, PENCERE_YUKSEKLIK//2 - 25, 200, 50)
    basla_buton = Buton(PENCERE_GENISLIK//2 - 100, PENCERE_YUKSEKLIK//2 + 50, 200, 50, "Başla", MAVI)
    skorlar_buton = Buton(PENCERE_GENISLIK//2 - 100, PENCERE_YUKSEKLIK//2 + 120, 200, 50, "Skorlar", TURKUAZ)
    cikis_buton = Buton(PENCERE_GENISLIK//2 - 100, PENCERE_YUKSEKLIK//2 + 190, 200, 50, "Çıkış", KIRMIZI)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    if basla_buton.fare_uzerinde(event.pos) and girdi.text.strip():
                        return girdi.text.strip()
                    elif skorlar_buton.fare_uzerinde(event.pos):
                        if skorlar_ekrani():  # Skor tablosundan dönüş değeri True ise
                            continue  # Ana menüye dön
                    elif cikis_buton.fare_uzerinde(event.pos):
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                basla_buton.fare_uzerinde(event.pos)
                skorlar_buton.fare_uzerinde(event.pos)
                cikis_buton.fare_uzerinde(event.pos)
            
            girdi.olay_isle(event)

        ekran.fill(SIYAH)
        
        # Başlık
        font = pygame.font.Font(None, 74)
        text = font.render('Yılan Oyunu', True, BEYAZ)
        text_rect = text.get_rect(center=(PENCERE_GENISLIK/2, PENCERE_YUKSEKLIK/2 - 100))
        ekran.blit(text, text_rect)
        
        # Girdi kutusu ve butonları çiz
        girdi.ciz(ekran)
        basla_buton.ciz(ekran)
        skorlar_buton.ciz(ekran)
        cikis_buton.ciz(ekran)
        
        pygame.display.flip()
        saat.tick(60)

def skorlar_ekrani():
    skor_kayit = SkorKayit()
    geri_buton = Buton(50, 50, 100, 40, "Geri", MAVI)
    
    # Skor tablosu başlıkları
    font = pygame.font.Font(None, 36)
    basliklar = ["Sıra", "Kullanıcı Adı", "En Yüksek Skor", "Son Oyun Tarihi"]
    baslik_x = [50, 200, 400, 600]
    
    # Tüm kullanıcıların en yüksek skorlarını al ve sırala
    siralama = []
    for kullanici, skorlar in skor_kayit.skorlar.items():
        if skorlar:
            siralama.append({
                "kullanici": kullanici,
                "skor": skorlar[0]["skor"],
                "tarih": skorlar[0]["tarih"]
            })
    
    # Skorlara göre sırala (büyükten küçüğe)
    siralama.sort(key=lambda x: x["skor"], reverse=True)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    if geri_buton.fare_uzerinde(event.pos):
                        return True  # Ana menüye dön
            elif event.type == pygame.MOUSEMOTION:
                geri_buton.fare_uzerinde(event.pos)

        ekran.fill(SIYAH)
        
        # Başlık
        font_buyuk = pygame.font.Font(None, 74)
        text = font_buyuk.render('Skor Tablosu', True, BEYAZ)
        text_rect = text.get_rect(center=(PENCERE_GENISLIK/2, 100))
        ekran.blit(text, text_rect)
        
        # Tablo başlıkları
        for i, baslik in enumerate(basliklar):
            text = font.render(baslik, True, ACIK_MAVI)
            text_rect = text.get_rect(center=(baslik_x[i], 150))
            ekran.blit(text, text_rect)
        
        # Yatay çizgi
        pygame.draw.line(ekran, ACIK_MAVI, (50, 170), (PENCERE_GENISLIK-50, 170), 2)
        
        # Skorları listele
        y_pozisyon = 200
        for i, veri in enumerate(siralama):
            # İlk 3 için özel renkler
            if i < 3:
                if i == 0:  # 1. sıra
                    renk = (255, 215, 0)  # Altın
                elif i == 1:  # 2. sıra
                    renk = (192, 192, 192)  # Gümüş
                else:  # 3. sıra
                    renk = (205, 127, 50)  # Bronz
            else:
                renk = BEYAZ
            
            # Sıra numarası
            text = font.render(f"{i+1}.", True, renk)
            ekran.blit(text, (baslik_x[0] - 20, y_pozisyon))
            
            # Kullanıcı adı
            text = font.render(veri["kullanici"], True, renk)
            ekran.blit(text, (baslik_x[1] - 100, y_pozisyon))
            
            # En yüksek skor
            text = font.render(str(veri["skor"]), True, renk)
            ekran.blit(text, (baslik_x[2] - 20, y_pozisyon))
            
            # Son tarih
            text = font.render(veri["tarih"], True, renk)
            ekran.blit(text, (baslik_x[3] - 100, y_pozisyon))
            
            y_pozisyon += 40
        
        # Geri butonu
        geri_buton.ciz(ekran)
        
        pygame.display.flip()
        saat.tick(60)

def oyunu_baslat():
    skor_kayit = SkorKayit()
    
    while True:
        kullanici_adi = kullanici_adi_ekrani()
        skor, hiz = oyun_dongusu()
        skor_kayit.skor_kaydet(kullanici_adi, skor, hiz)
        if not oyun_bitti_ekrani(skor, hiz):
            skor_kayit.skorlari_temizle()  # Oyun kapatılırken skorları temizle
            break

if __name__ == "__main__":
    oyunu_baslat() 