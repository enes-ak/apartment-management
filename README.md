# Apartman Yonetim Sistemi

Apartman yoneticileri icin gelistirilmis, aidat takibi, gider yonetimi, raporlama ve iletisim gibi tum yonetim islerini tek bir yerden yurutmeyi saglayan web tabanli yonetim uygulamasi.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-DB-003B57?logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Ozellikler

### Ana Sayfa (Dashboard)
- Yillik gelir, gider, kasa bakiyesi ve aidat tutari ozet kartlari
- Yillik ve guncel tahsilat oranlari
- Odenmemis aidat uyari listesi (hangi daire, hangi ay)
- Hizli erisim linkleri

### Odeme Takibi
- 12 daire icin aylik aidat odeme durumu goruntuleme
- Tek tikla odendi/odenmedi degistirme (HTMX ile anlik guncelleme)
- Toplu odeme: bir daire icin birden fazla ayi tek seferde isaretle
- Daire detay sayfasi: yillik odeme gecmisi, toplam borc, gecikmis aylar
- Daire bazli PDF rapor indirme

### Gider Yonetimi
- Aylik gider kaydi (kategori, tutar, aciklama)
- On tanimli gider kalemleri: Elektrik, Su, Temizlik, Asansor Bakim
- Ozel gider kalemi ekleme/aktif-pasif yapma
- Gider silme ile otomatik kasa guncelleme

### Kasa
- Yillik gelir / gider / bakiye ozeti
- Aydan aya devir hesabi
- Gider dagilimi (kategori bazli yuzde)
- Tahsilat orani

### Mesaj Hazirlama
- Odemeyen dairelere otomatik hatirlatma mesaji olusturma
- Genel duyuru mesaji hazirlama
- Sablon destegi: `{apartman_adi}`, `{ay_yil}`, `{miktar}`, `{odemeyenler}`
- Mesaj onizleme ve panoya kopyalama

### Raporlar (Excel + PDF)
- **Aylik Ozet:** Gelir, gider, net, gider dagilimi
- **Odeme Durumu:** Tum daireler, odendi/odenmedi (renk kodlu)
- **Gider Detay:** Kalem bazli tutar ve oran
- **Yillik Ozet:** 12 ay gelir/gider/net tablosu
- Turkce karakter destegi, profesyonel tablolar

### Notlar
- Her ay icin ayri not alani
- Not ekleme, duzenleme, silme
- Hangi ayda not var gosterge noktasi
- Son guncelleme tarihi

### Rehber
- **Gorevliler:** Asansorcu, temizlikci vs. (ad, telefon, IBAN)
- **Abonelikler:** Elektrik, su, dogalgaz (abone/sayac numarasi)
- **Apartman Bilgileri:** Adres, genel bilgiler, telefon, IBAN

### Log Kayitlari
- Tum islemlerin otomatik kaydi
- Arama / filtreleme
- Sayfalama (50'ser kayit)

### Ayarlar
- Apartman adi duzenleme
- Aidat miktari degistirme (tarihce ile)
- Daire sakin bilgisi guncelleme (ad, telefon)
- Gider kalemi yonetimi
- Mesaj sablonu duzenleme
- Veritabani yedekleme (indir / listele)
- Tum verileri sifirlama (onay kodlu)

### E-posta Bildirimi
- SMTP ayarlari ile mail gonderme
- Her ayin ilk pazartesi otomatik aidat hatirlatmasi
- Bildirim durumu takibi

### Mobil Uyumlu (Responsive)
- Hamburger menu ile sidebar acilir/kapanir
- Kartlar, tablolar, formlar mobil uyumlu
- Telefon, tablet ve PC'de duzgun gorunum

---

## Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.10+, Flask 3.1, Flask-SQLAlchemy |
| Veritabani | SQLite |
| Frontend | Bootstrap 5.3, Bootstrap Icons, HTMX 2.0 |
| Raporlama | ReportLab (PDF), OpenPyXL (Excel) |
| Font | Plus Jakarta Sans, JetBrains Mono |
| Tema | Dark Theme |

---

## Kurulum

### Gereksinimler
- Python 3.10 veya uzeri
- pip

### Adimlar

```bash
# Repoyu klonla
git clone https://github.com/enes-ak/apartment-management.git
cd apartment-management

# Sanal ortam olustur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bagimlilikari yukle
pip install -r requirements.txt

# Uygulamayi baslat
python app.py
```

Tarayicida `http://localhost:5000` adresine git.

> **Not:** Ilk calistirmada veritabani ve 12 daire otomatik olarak olusturulur.

---

## Proje Yapisi

```
apartment-management/
├── app.py                  # Uygulama baslangic noktasi
├── config.py               # Yapilandirma
├── database.py             # Veritabani baslangic
├── requirements.txt        # Python bagimliliklar
│
├── models/                 # Veritabani modelleri
│   ├── daire.py            # Daire (apartman birimi)
│   ├── odeme.py            # Odeme takibi
│   ├── gider.py            # Gider & gider kalemleri
│   ├── kasa.py             # Kasa (gelir/gider ozeti)
│   ├── ayar.py             # Ayarlar, aidat, bildirim
│   ├── log.py              # Aktivite logları
│   ├── not_.py             # Aylik notlar
│   └── rehber.py           # Rehber (gorevli/abonelik/bilgi)
│
├── routes/                 # URL route'lari
│   ├── ana_sayfa.py        # Dashboard
│   ├── odemeler.py         # Odeme islemleri
│   ├── giderler.py         # Gider islemleri
│   ├── kasa.py             # Kasa goruntuleme
│   ├── mesajlar.py         # Mesaj hazirlama
│   ├── raporlar.py         # Rapor indirme
│   ├── notlar.py           # Not yonetimi
│   ├── rehber.py           # Rehber yonetimi
│   ├── loglar.py           # Log goruntuleme
│   └── ayarlar.py          # Ayarlar yonetimi
│
├── services/               # Is mantigi servisleri
│   ├── kasa_servisi.py     # Kasa hesaplama
│   ├── rapor_servisi.py    # Excel & PDF rapor uretimi
│   └── mail_servisi.py     # E-posta gonderimi
│
├── templates/              # HTML sablonlari (Jinja2)
│   ├── base.html           # Ana layout (sidebar, responsive)
│   ├── ana_sayfa.html      # Dashboard
│   ├── odemeler.html       # Odeme tablosu
│   ├── daire_detay.html    # Daire detay sayfasi
│   ├── giderler.html       # Gider kaydi
│   ├── kasa.html           # Kasa ozeti
│   ├── mesajlar.html       # Mesaj hazirlama
│   ├── raporlar.html       # Rapor secimi
│   ├── notlar.html         # Aylik notlar
│   ├── rehber.html         # Rehber
│   ├── loglar.html         # Log listesi
│   ├── ayarlar.html        # Ayarlar
│   └── parcalar/           # Yeniden kullanilabilir parcalar
│       ├── odeme_satir.html
│       └── mesaj_onizleme.html
│
├── static/
│   ├── css/stil.css        # Tum stiller (dark theme + responsive)
│   ├── js/uygulama.js      # JavaScript fonksiyonlari
│   └── favicon.svg         # Favicon
│
├── tests/                  # Test dosyalari
│   ├── test_modeller.py
│   ├── test_odemeler.py
│   ├── test_giderler.py
│   ├── test_kasa.py
│   ├── test_raporlar.py
│   ├── test_mesajlar.py
│   ├── test_mail.py
│   └── test_ayarlar.py
│
├── raporlar/               # Olusturulan raporlar (gitignore)
└── yedekler/               # Veritabani yedekleri (gitignore)
```

---

## Ekran Goruntuleri

| Dashboard | Odeme Takibi |
|-----------|-------------|
| Yillik ozet kartlari, odenmemis uyarilar | Aylik odeme durumu, tek tikla guncelle |

| Raporlar | Rehber |
|----------|--------|
| Excel & PDF rapor indirme | Gorevliler, abonelikler, bilgiler |

---

## Testler

```bash
pytest
```

---

## Lisans

MIT
