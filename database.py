from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Tablolari olustur ve varsayilan verileri ekle."""
    with app.app_context():
        from models import Daire, AidatAyari, GiderKalemi, Ayar
        db.create_all()

        # 12 daire yoksa olustur
        if Daire.query.count() == 0:
            for i in range(1, 13):
                daire = Daire(daire_no=i, kat=(i - 1) // 2 + 1, sakin_adi='', telefon='')
                db.session.add(daire)

        # Varsayilan aidat ayari
        if AidatAyari.query.count() == 0:
            from datetime import date
            ayar = AidatAyari(miktar=0, gecerlilik_tarihi=date.today())
            db.session.add(ayar)

        # Varsayilan gider kalemleri
        if GiderKalemi.query.count() == 0:
            for kalem in ['Elektrik', 'Su', 'Temizlik', 'Asansor Bakim']:
                db.session.add(GiderKalemi(kalem_adi=kalem, aktif=True))

        # Varsayilan ayarlar
        varsayilan_ayarlar = {
            'apartman_adi': 'Apartman',
            'mail_adresi': '',
            'smtp_sunucu': 'smtp.gmail.com',
            'smtp_port': '587',
            'smtp_sifre': '',
            'mesaj_sablonu': (
                '{apartman_adi} - {ay_yil} Aidat Bildirimi\n\n'
                'Sayin Komsularimiz,\n\n'
                '{ay_yil} aidatlari icin odeme zamani gelmistir.\n'
                'Aidat tutari: {miktar} TL\n\n'
                'Henuz odeme yapmayan daireler:\n{odemeyenler}\n\n'
                'Odemenizi en kisa surede yapmanizi rica ederiz.\n\n'
                'Tesekkurler,\nApartman Yonetimi'
            ),
        }
        for anahtar, deger in varsayilan_ayarlar.items():
            if not Ayar.query.filter_by(anahtar=anahtar).first():
                db.session.add(Ayar(anahtar=anahtar, deger=deger))

        db.session.commit()
