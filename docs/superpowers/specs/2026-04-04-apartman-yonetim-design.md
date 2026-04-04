# Apartman Yonetim Uygulamasi - Tasarim Dokumani

**Tarih:** 2026-04-04
**Durum:** Onaylandi

## Genel Bakis

Tek blok, 12 daireli bir apartman icin yerel (local) web tabanli yonetim uygulamasi. Uygulama sadece yonetici (tek kullanici) tarafindan kullanilacak. Canli ortama cikarilmayacak, localhost uzerinde calisacak. Temel amac: aidat takibi, gider yonetimi, kasa kontrolu ve apartman sakinlerine sunulacak seffaf raporlama.

## Teknoloji Kararlari

- **Framework:** Flask + HTMX (sayfa yenilemeden dinamik guncellemeler)
- **Veritabani:** SQLite (tek dosya, kurulum gerektirmez)
- **Arayuz:** Bootstrap 5 dark mode, Turkce
- **Raporlama:** openpyxl (Excel), reportlab (PDF)
- **Mail:** smtplib (Python built-in)
- **ORM:** Flask-SQLAlchemy

## Veritabani Yapisi

### Tablo: `daireler`
| Alan | Tip | Aciklama |
|------|-----|----------|
| id | INTEGER PK | Otomatik ID |
| daire_no | INTEGER | Daire numarasi (1-12) |
| kat | INTEGER | Kat numarasi |
| sakin_adi | TEXT | Daire sakininin adi |
| telefon | TEXT | Telefon numarasi |

### Tablo: `aidat_ayarlari`
| Alan | Tip | Aciklama |
|------|-----|----------|
| id | INTEGER PK | Otomatik ID |
| miktar | REAL | Aidat miktari (TL) |
| gecerlilik_tarihi | DATE | Bu miktarin gecerli oldugu tarih |

### Tablo: `odemeler`
| Alan | Tip | Aciklama |
|------|-----|----------|
| id | INTEGER PK | Otomatik ID |
| daire_id | INTEGER FK | Daire referansi |
| yil | INTEGER | Yil (2026) |
| ay | INTEGER | Ay (1-12) |
| odendi | BOOLEAN | Odeme durumu (True/False) |
| odeme_tarihi | DATETIME | Odeme yapildigi tarih |

### Tablo: `gider_kalemleri`
| Alan | Tip | Aciklama |
|------|-----|----------|
| id | INTEGER PK | Otomatik ID |
| kalem_adi | TEXT | Gider kalemi adi (Elektrik, Su vb.) |
| aktif | BOOLEAN | Aktif/Pasif (silmek yerine pasif yap) |

### Tablo: `giderler`
| Alan | Tip | Aciklama |
|------|-----|----------|
| id | INTEGER PK | Otomatik ID |
| kalem_id | INTEGER FK | Gider kalemi referansi |
| yil | INTEGER | Yil |
| ay | INTEGER | Ay |
| tutar | REAL | Gider tutari (TL) |
| aciklama | TEXT | Opsiyonel aciklama |

### Tablo: `kasa`
| Alan | Tip | Aciklama |
|------|-----|----------|
| id | INTEGER PK | Otomatik ID |
| yil | INTEGER | Yil |
| ay | INTEGER | Ay |
| toplam_gelir | REAL | O ay toplanan aidatlar |
| toplam_gider | REAL | O ay toplam giderler |
| devir | REAL | Onceki aydan devreden bakiye |
| bakiye | REAL | Ay sonu bakiye (devir + gelir - gider) |

### Tablo: `ayarlar`
| Alan | Tip | Aciklama |
|------|-----|----------|
| id | INTEGER PK | Otomatik ID |
| anahtar | TEXT UNIQUE | Ayar anahtari |
| deger | TEXT | Ayar degeri |

Kullanilacak ayarlar: `apartman_adi`, `mail_adresi`, `smtp_sunucu`, `smtp_port`, `smtp_sifre`, `mesaj_sablonu`

### Tablo: `bildirimler`
| Alan | Tip | Aciklama |
|------|-----|----------|
| id | INTEGER PK | Otomatik ID |
| yil | INTEGER | Yil |
| ay | INTEGER | Ay |
| gonderildi | BOOLEAN | Mail gonderildi mi |
| gonderim_tarihi | DATETIME | Gonderim tarihi |

## Sayfa Yapisi

### Ana Sayfa
- Bu ayin ozet bilgileri: kasa durumu, odeme orani, yaklasan/geciken odemeler
- Hizli erisim kartlari

### Odeme Takibi
- 12 dairenin ay bazli tablosu
- Ay/yil secici ile gecmis aylara bakma
- HTMX ile tikla = odendi/odenmedi (sayfa yenilemeden, yesil tik / kirmizi carpi)
- Toplam tahsilat ozeti

### Giderler
- Aylik gider girisi: kalem sec, tutar gir, aciklama ekle, kaydet
- HTMX ile aninda tablo guncelleme
- Gider kalemi yonetimi: yeni kalem ekle, mevcut kalemi pasif yap
- Aylik gider toplami goruntusu

### Kasa
- Aylik gelir-gider-bakiye tablosu
- Devir otomatik hesaplanir (onceki ay bakiyesi)
- Yillik kasa ozeti

### Mesaj Hazirla
- Ay/yil sec (varsayilan: mevcut ay)
- Sistem odemeyenleri otomatik listeler
- Hazir sablon mesaj olusur:
  ```
  [Apartman Adi] - [Ay Yil] Aidat Bildirimi

  Sayin Komsularimiz,

  [Ay Yil] aidatlari icin odeme zamani gelmistir.
  Aidat tutari: [Miktar] TL

  Henuz odeme yapmayan daireler:
  - Daire [No] - [Sakin Adi]
  - ...

  Odemenizi en kisa surede yapmanizi rica ederiz.

  Tesekkurler,
  Apartman Yonetimi
  ```
- "Kopyala" butonu ile panoya kopyalama (WhatsApp'a yapistirmak icin)
- "Kopyalandi!" bildirimi
- Sablon ayarlardan ozellestirilebilir
- Tum sakinlere genel hatirlatma mesaji secenegi

### Raporlar
- Uc ayri rapor turu, bagimsiz secilir:

**1. Aylik Ozet Raporu:**
- Toplam gelir (toplanan aidatlar)
- Toplam gider (fatura + bakim + diger)
- Kasa bakiyesi ve gecen aydan devir

**2. Odeme Durumu Raporu:**
- 12 dairenin secilen ay veya ay araligi icin odeme tablosu
- Odeyenler yesil, odemeyenler kirmizi (PDF'de renkli)
- Toplam tahsilat orani (%)
- Borclu daireler ozeti

**3. Gider Detay Raporu:**
- Secilen donemde hangi kaleme ne kadar harcandi
- Kalem bazli toplam ve yuzdesel dagilim
- Aylik karsilastirma

**4. Yillik Ozet Raporu (ek ozellik):**
- Tum aylarin toplu gelir-gider-kasa durumu

**Rapor ortak ozellikleri:**
- Ay/yil veya tarih araligi secimi
- Format secimi: Excel (.xlsx) veya PDF
- Turkce basliklar, TL formatinda para birimi, gun.ay.yil tarih formati
- Apartman adi ve tarih raporun ustunde

### Ayarlar
- Aidat miktari guncelleme (zam)
- Mail adresi ve SMTP ayarlari
- Apartman adi
- Daire bilgileri duzenleme (sakin adi, telefon)
- Gider kalemleri yonetimi (ekle, pasif yap)
- Mesaj sablonu duzenleme

### Daire Detay Sayfasi (ek ozellik)
- Bir daireye tikla, o dairenin tum gecmisi gorunsun
- Odeme gecmisi (ay ay)
- Toplam borc durumu

## Mail Bildirim Sistemi

- Ayarlardan mail adresi ve SMTP bilgileri girilir (Gmail icin uygulama sifresi)
- Her ayin ilk pazartesi gunu, uygulama acikken otomatik kontrol
- "Bu ay bildirim gitti mi?" kontrolu yapilir
- Gitmediyse yoneticiye mail: "Aidat toplama zamani geldi! Bu ay henuz X daire odemedi."
- Ayarlardan test mail gonderme secenegi

## Proje Yapisi

```
apartman/
├── app.py                  # Flask ana uygulama, HTMX yapilandirma
├── config.py               # Uygulama ayarlari
├── database.py             # SQLite baglanti ve tablo olusturma
├── models/                 # Veritabani modelleri
│   ├── __init__.py
│   ├── daire.py
│   ├── odeme.py
│   ├── gider.py
│   ├── kasa.py
│   └── ayar.py
├── routes/                 # Sayfa route'lari (Flask blueprint)
│   ├── __init__.py
│   ├── ana_sayfa.py
│   ├── odemeler.py
│   ├── giderler.py
│   ├── kasa.py
│   ├── mesajlar.py
│   ├── raporlar.py
│   └── ayarlar.py
├── services/               # Is mantigi
│   ├── __init__.py
│   ├── rapor_servisi.py    # Excel ve PDF olusturma
│   ├── mail_servisi.py     # Mail gonderme
│   └── kasa_servisi.py     # Kasa hesaplama
├── templates/              # Jinja2 HTML sablonlari
│   ├── base.html           # Ana sablon (navbar, sidebar, dark theme)
│   ├── ana_sayfa.html
│   ├── odemeler.html
│   ├── giderler.html
│   ├── kasa.html
│   ├── mesajlar.html
│   ├── raporlar.html
│   ├── ayarlar.html
│   ├── daire_detay.html
│   └── parcalar/           # HTMX partial sablonlari
│       ├── odeme_satir.html
│       ├── gider_tablo.html
│       └── mesaj_onizleme.html
├── static/
│   ├── css/
│   │   └── stil.css        # Ozel stiller
│   └── js/
│       └── uygulama.js     # Kopyalama vb. yardimci JS
├── raporlar/               # Olusturulan rapor dosyalari
└── requirements.txt
```

## Kutuphaneler (requirements.txt)

```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
openpyxl==3.1.5
reportlab==4.4.0
```

## Gorunum

- Bootstrap 5 dark mode
- Turkce arayuz (tum etiketler, butonlar, mesajlar Turkce)
- Responsive degil (sadece masaustunden kullanilacak)
- Temiz, is odakli tasarim
