# Apartman Yonetim Uygulamasi - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tek blok, 12 daireli bir apartman icin aidat takibi, gider yonetimi, kasa kontrolu ve raporlama yapan local Flask web uygulamasi olusturmak.

**Architecture:** Flask + HTMX monolitik uygulama. SQLAlchemy ORM ile SQLite veritabani. Blueprint'ler ile route ayirimi, services katmani ile is mantigi. Jinja2 template'leri + Bootstrap 5 dark mode.

**Tech Stack:** Flask, Flask-SQLAlchemy, HTMX, Bootstrap 5, openpyxl, reportlab, smtplib, pytest

---

## File Map

```
apartman/
├── app.py                          # Flask app factory, blueprint registration, before_request mail check
├── config.py                       # Config class with SQLite path, secret key
├── database.py                     # db = SQLAlchemy(), init_db() seed function
├── models/
│   ├── __init__.py                 # Re-export all models
│   ├── daire.py                    # Daire model
│   ├── odeme.py                    # Odeme model
│   ├── gider.py                    # GiderKalemi + Gider models
│   ├── kasa.py                     # Kasa model
│   └── ayar.py                     # Ayar + Bildirim + AidatAyari models
├── routes/
│   ├── __init__.py                 # register_blueprints() helper
│   ├── ana_sayfa.py                # Dashboard route
│   ├── odemeler.py                 # Payment CRUD + HTMX toggle
│   ├── giderler.py                 # Expense CRUD + category management
│   ├── kasa.py                     # Treasury view + recalculate
│   ├── mesajlar.py                 # Message generator
│   ├── raporlar.py                 # Report generation endpoints
│   └── ayarlar.py                  # Settings CRUD
├── services/
│   ├── __init__.py
│   ├── rapor_servisi.py            # Excel + PDF generation
│   ├── mail_servisi.py             # SMTP mail sending
│   └── kasa_servisi.py             # Treasury calculation logic
├── templates/
│   ├── base.html                   # Dark theme layout, navbar, HTMX
│   ├── ana_sayfa.html
│   ├── odemeler.html
│   ├── giderler.html
│   ├── kasa.html
│   ├── mesajlar.html
│   ├── raporlar.html
│   ├── ayarlar.html
│   ├── daire_detay.html
│   └── parcalar/
│       ├── odeme_satir.html
│       ├── gider_tablo.html
│       └── mesaj_onizleme.html
├── static/
│   ├── css/stil.css
│   └── js/uygulama.js
├── raporlar/                       # Generated report files
├── tests/
│   ├── conftest.py                 # Flask test client fixture
│   ├── test_models.py
│   ├── test_odemeler.py
│   ├── test_giderler.py
│   ├── test_kasa.py
│   ├── test_mesajlar.py
│   ├── test_raporlar.py
│   └── test_mail.py
└── requirements.txt
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `database.py`
- Create: `models/__init__.py`
- Create: `models/daire.py`
- Create: `models/odeme.py`
- Create: `models/gider.py`
- Create: `models/kasa.py`
- Create: `models/ayar.py`
- Create: `app.py`
- Create: `tests/conftest.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Create requirements.txt**

```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
openpyxl==3.1.5
reportlab==4.4.0
pytest==8.3.4
```

- [ ] **Step 2: Install dependencies**

Run: `cd /home/enes/Desktop/apartman && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

- [ ] **Step 3: Create config.py**

```python
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'apartman-yonetim-local-key'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "apartman.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RAPORLAR_DIZINI = os.path.join(BASE_DIR, 'raporlar')
```

- [ ] **Step 4: Create database.py**

```python
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
```

- [ ] **Step 5: Create models/__init__.py**

```python
from models.daire import Daire
from models.odeme import Odeme
from models.gider import GiderKalemi, Gider
from models.kasa import Kasa
from models.ayar import Ayar, AidatAyari, Bildirim

__all__ = ['Daire', 'Odeme', 'GiderKalemi', 'Gider', 'Kasa', 'Ayar', 'AidatAyari', 'Bildirim']
```

- [ ] **Step 6: Create models/daire.py**

```python
from database import db


class Daire(db.Model):
    __tablename__ = 'daireler'

    id = db.Column(db.Integer, primary_key=True)
    daire_no = db.Column(db.Integer, nullable=False, unique=True)
    kat = db.Column(db.Integer, nullable=False)
    sakin_adi = db.Column(db.Text, default='')
    telefon = db.Column(db.Text, default='')

    odemeler = db.relationship('Odeme', backref='daire', lazy=True)

    def __repr__(self):
        return f'<Daire {self.daire_no}>'
```

- [ ] **Step 7: Create models/odeme.py**

```python
from database import db


class Odeme(db.Model):
    __tablename__ = 'odemeler'

    id = db.Column(db.Integer, primary_key=True)
    daire_id = db.Column(db.Integer, db.ForeignKey('daireler.id'), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    odendi = db.Column(db.Boolean, default=False)
    odeme_tarihi = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('daire_id', 'yil', 'ay', name='uq_daire_yil_ay'),)

    def __repr__(self):
        return f'<Odeme Daire:{self.daire_id} {self.yil}/{self.ay}>'
```

- [ ] **Step 8: Create models/gider.py**

```python
from database import db


class GiderKalemi(db.Model):
    __tablename__ = 'gider_kalemleri'

    id = db.Column(db.Integer, primary_key=True)
    kalem_adi = db.Column(db.Text, nullable=False)
    aktif = db.Column(db.Boolean, default=True)

    giderler = db.relationship('Gider', backref='kalem', lazy=True)

    def __repr__(self):
        return f'<GiderKalemi {self.kalem_adi}>'


class Gider(db.Model):
    __tablename__ = 'giderler'

    id = db.Column(db.Integer, primary_key=True)
    kalem_id = db.Column(db.Integer, db.ForeignKey('gider_kalemleri.id'), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    tutar = db.Column(db.Float, nullable=False)
    aciklama = db.Column(db.Text, default='')

    def __repr__(self):
        return f'<Gider {self.kalem.kalem_adi if self.kalem else "?"} {self.tutar} TL>'
```

- [ ] **Step 9: Create models/kasa.py**

```python
from database import db


class Kasa(db.Model):
    __tablename__ = 'kasa'

    id = db.Column(db.Integer, primary_key=True)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    toplam_gelir = db.Column(db.Float, default=0)
    toplam_gider = db.Column(db.Float, default=0)
    devir = db.Column(db.Float, default=0)
    bakiye = db.Column(db.Float, default=0)

    __table_args__ = (db.UniqueConstraint('yil', 'ay', name='uq_kasa_yil_ay'),)

    def __repr__(self):
        return f'<Kasa {self.yil}/{self.ay} Bakiye:{self.bakiye}>'
```

- [ ] **Step 10: Create models/ayar.py**

```python
from database import db


class Ayar(db.Model):
    __tablename__ = 'ayarlar'

    id = db.Column(db.Integer, primary_key=True)
    anahtar = db.Column(db.Text, unique=True, nullable=False)
    deger = db.Column(db.Text, default='')

    @staticmethod
    def getir(anahtar, varsayilan=''):
        ayar = Ayar.query.filter_by(anahtar=anahtar).first()
        return ayar.deger if ayar else varsayilan

    @staticmethod
    def kaydet(anahtar, deger):
        ayar = Ayar.query.filter_by(anahtar=anahtar).first()
        if ayar:
            ayar.deger = deger
        else:
            ayar = Ayar(anahtar=anahtar, deger=deger)
            db.session.add(ayar)
        db.session.commit()


class AidatAyari(db.Model):
    __tablename__ = 'aidat_ayarlari'

    id = db.Column(db.Integer, primary_key=True)
    miktar = db.Column(db.Float, nullable=False)
    gecerlilik_tarihi = db.Column(db.Date, nullable=False)

    @staticmethod
    def guncel_miktar():
        from datetime import date
        ayar = AidatAyari.query.filter(
            AidatAyari.gecerlilik_tarihi <= date.today()
        ).order_by(AidatAyari.gecerlilik_tarihi.desc()).first()
        return ayar.miktar if ayar else 0


class Bildirim(db.Model):
    __tablename__ = 'bildirimler'

    id = db.Column(db.Integer, primary_key=True)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    gonderildi = db.Column(db.Boolean, default=False)
    gonderim_tarihi = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('yil', 'ay', name='uq_bildirim_yil_ay'),)
```

- [ ] **Step 11: Create minimal app.py**

```python
import os
from flask import Flask
from config import Config
from database import db, init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Rapor dizinini olustur
    os.makedirs(app.config['RAPORLAR_DIZINI'], exist_ok=True)

    init_db(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
```

- [ ] **Step 12: Create tests/conftest.py**

```python
import pytest
from app import create_app
from database import db as _db


@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    with app.app_context():
        _db.create_all()

        # Seed 12 daire
        from models import Daire, AidatAyari, GiderKalemi, Ayar
        from datetime import date

        for i in range(1, 13):
            _db.session.add(Daire(daire_no=i, kat=(i - 1) // 2 + 1, sakin_adi=f'Sakin {i}', telefon=''))

        _db.session.add(AidatAyari(miktar=500, gecerlilik_tarihi=date(2026, 1, 1)))

        for kalem in ['Elektrik', 'Su', 'Temizlik', 'Asansor Bakim']:
            _db.session.add(GiderKalemi(kalem_adi=kalem, aktif=True))

        _db.session.add(Ayar(anahtar='apartman_adi', deger='Test Apartmani'))
        _db.session.add(Ayar(anahtar='mesaj_sablonu', deger='{apartman_adi} - {ay_yil}\n{odemeyenler}'))
        _db.session.commit()

        yield app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield _db.session
```

- [ ] **Step 13: Write model tests in tests/test_models.py**

```python
from models import Daire, AidatAyari, GiderKalemi, Ayar
from datetime import date


def test_daire_sayisi(db_session):
    assert Daire.query.count() == 12


def test_daire_no_sirali(db_session):
    daireler = Daire.query.order_by(Daire.daire_no).all()
    assert [d.daire_no for d in daireler] == list(range(1, 13))


def test_aidat_guncel_miktar(db_session):
    assert AidatAyari.guncel_miktar() == 500


def test_aidat_zam(db_session):
    from database import db
    db.session.add(AidatAyari(miktar=750, gecerlilik_tarihi=date(2026, 4, 1)))
    db.session.commit()
    assert AidatAyari.guncel_miktar() == 750


def test_gider_kalemleri(db_session):
    aktif = GiderKalemi.query.filter_by(aktif=True).all()
    assert len(aktif) == 4
    isimler = {k.kalem_adi for k in aktif}
    assert 'Elektrik' in isimler
    assert 'Su' in isimler


def test_ayar_getir_kaydet(db_session):
    assert Ayar.getir('apartman_adi') == 'Test Apartmani'
    Ayar.kaydet('apartman_adi', 'Yeni Apartman')
    assert Ayar.getir('apartman_adi') == 'Yeni Apartman'


def test_ayar_getir_varsayilan(db_session):
    assert Ayar.getir('yok_boyle_bir_sey', 'fallback') == 'fallback'
```

- [ ] **Step 14: Run tests to verify models work**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_models.py -v`
Expected: All 7 tests PASS

- [ ] **Step 15: Commit**

```bash
git add requirements.txt config.py database.py app.py models/ tests/
git commit -m "feat: proje iskeleti, veritabani modelleri ve testler"
```

---

### Task 2: Base Template and Navigation

**Files:**
- Create: `templates/base.html`
- Create: `static/css/stil.css`
- Create: `static/js/uygulama.js`
- Create: `routes/__init__.py`
- Create: `routes/ana_sayfa.py`
- Create: `templates/ana_sayfa.html`
- Modify: `app.py`

- [ ] **Step 1: Create static/css/stil.css**

```css
/* Genel stil ayarlari */
body {
    min-height: 100vh;
}

.sidebar {
    min-height: 100vh;
    background-color: #1a1d21;
    border-right: 1px solid #2d3238;
}

.sidebar .nav-link {
    color: #9da5b1;
    padding: 0.75rem 1.25rem;
    border-radius: 0.5rem;
    margin: 0.15rem 0.5rem;
}

.sidebar .nav-link:hover {
    color: #fff;
    background-color: #2d3238;
}

.sidebar .nav-link.active {
    color: #fff;
    background-color: #0d6efd;
}

.sidebar .nav-link i {
    width: 24px;
    text-align: center;
    margin-right: 8px;
}

.content-area {
    min-height: 100vh;
    background-color: #212529;
}

/* Odeme durumu ikonlari */
.odeme-btn {
    cursor: pointer;
    font-size: 1.4rem;
    border: none;
    background: none;
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
    transition: transform 0.15s;
}

.odeme-btn:hover {
    transform: scale(1.2);
}

.odeme-btn.odendi {
    color: #198754;
}

.odeme-btn.odenmedi {
    color: #dc3545;
}

/* Kart stilleri */
.ozet-kart {
    border: 1px solid #2d3238;
    border-radius: 0.75rem;
    transition: transform 0.15s;
}

.ozet-kart:hover {
    transform: translateY(-2px);
}

/* Toast bildirimi */
.toast-container {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    z-index: 9999;
}

/* Tablo stili */
.table-dark th {
    background-color: #1a1d21;
    border-color: #2d3238;
}

/* HTMX gostergeleri */
.htmx-indicator {
    display: none;
}

.htmx-request .htmx-indicator {
    display: inline-block;
}

.htmx-request.htmx-indicator {
    display: inline-block;
}
```

- [ ] **Step 2: Create static/js/uygulama.js**

```javascript
// Panoya kopyalama fonksiyonu
function panoyaKopyala(elementId) {
    const metin = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(metin).then(function () {
        bildirimGoster('Kopyalandi!');
    });
}

// Toast bildirimi goster
function bildirimGoster(mesaj, tip = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${tip} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${mesaj}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// HTMX sonrasi bildirim
document.addEventListener('htmx:afterRequest', function (event) {
    const mesaj = event.detail.xhr.getResponseHeader('X-Bildirim');
    if (mesaj) {
        bildirimGoster(decodeURIComponent(mesaj));
    }
});
```

- [ ] **Step 3: Create templates/base.html**

```html
<!DOCTYPE html>
<html lang="tr" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Apartman Yonetimi{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/stil.css') }}" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-2 sidebar d-flex flex-column py-3">
                <h5 class="text-white px-3 mb-4">
                    <i class="bi bi-building"></i> Apartman
                </h5>
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint == 'ana_sayfa.index' %}active{% endif %}"
                           href="{{ url_for('ana_sayfa.index') }}">
                            <i class="bi bi-house-door"></i> Ana Sayfa
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint and 'odemeler' in request.endpoint %}active{% endif %}"
                           href="{{ url_for('odemeler.index') }}">
                            <i class="bi bi-cash-stack"></i> Odeme Takibi
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint and 'giderler' in request.endpoint %}active{% endif %}"
                           href="{{ url_for('giderler.index') }}">
                            <i class="bi bi-receipt"></i> Giderler
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint and 'kasa' in request.endpoint %}active{% endif %}"
                           href="{{ url_for('kasa.index') }}">
                            <i class="bi bi-safe"></i> Kasa
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint and 'mesajlar' in request.endpoint %}active{% endif %}"
                           href="{{ url_for('mesajlar.index') }}">
                            <i class="bi bi-chat-dots"></i> Mesaj Hazirla
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint and 'raporlar' in request.endpoint %}active{% endif %}"
                           href="{{ url_for('raporlar.index') }}">
                            <i class="bi bi-file-earmark-bar-graph"></i> Raporlar
                        </a>
                    </li>
                    <li class="nav-item mt-auto">
                        <a class="nav-link {% if request.endpoint and 'ayarlar' in request.endpoint %}active{% endif %}"
                           href="{{ url_for('ayarlar.index') }}">
                            <i class="bi bi-gear"></i> Ayarlar
                        </a>
                    </li>
                </ul>
            </nav>

            <!-- Ana icerik -->
            <main class="col-md-10 content-area py-4 px-4">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                {% block content %}{% endblock %}
            </main>
        </div>
    </div>

    <!-- Toast container -->
    <div id="toast-container" class="toast-container"></div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/uygulama.js') }}"></script>
</body>
</html>
```

- [ ] **Step 4: Create routes/__init__.py**

```python
def register_blueprints(app):
    from routes.ana_sayfa import bp as ana_sayfa_bp
    from routes.odemeler import bp as odemeler_bp
    from routes.giderler import bp as giderler_bp
    from routes.kasa import bp as kasa_bp
    from routes.mesajlar import bp as mesajlar_bp
    from routes.raporlar import bp as raporlar_bp
    from routes.ayarlar import bp as ayarlar_bp

    app.register_blueprint(ana_sayfa_bp)
    app.register_blueprint(odemeler_bp)
    app.register_blueprint(giderler_bp)
    app.register_blueprint(kasa_bp)
    app.register_blueprint(mesajlar_bp)
    app.register_blueprint(raporlar_bp)
    app.register_blueprint(ayarlar_bp)
```

- [ ] **Step 5: Create routes/ana_sayfa.py (placeholder)**

```python
from flask import Blueprint, render_template

bp = Blueprint('ana_sayfa', __name__)


@bp.route('/')
def index():
    return render_template('ana_sayfa.html')
```

- [ ] **Step 6: Create placeholder blueprints for all other routes**

Create each of these files with a minimal blueprint so the app can start:

`routes/odemeler.py`:
```python
from flask import Blueprint, render_template

bp = Blueprint('odemeler', __name__, url_prefix='/odemeler')


@bp.route('/')
def index():
    return render_template('odemeler.html')
```

`routes/giderler.py`:
```python
from flask import Blueprint, render_template

bp = Blueprint('giderler', __name__, url_prefix='/giderler')


@bp.route('/')
def index():
    return render_template('giderler.html')
```

`routes/kasa.py`:
```python
from flask import Blueprint, render_template

bp = Blueprint('kasa', __name__, url_prefix='/kasa')


@bp.route('/')
def index():
    return render_template('kasa.html')
```

`routes/mesajlar.py`:
```python
from flask import Blueprint, render_template

bp = Blueprint('mesajlar', __name__, url_prefix='/mesajlar')


@bp.route('/')
def index():
    return render_template('mesajlar.html')
```

`routes/raporlar.py`:
```python
from flask import Blueprint, render_template

bp = Blueprint('raporlar', __name__, url_prefix='/raporlar')


@bp.route('/')
def index():
    return render_template('raporlar.html')
```

`routes/ayarlar.py`:
```python
from flask import Blueprint, render_template

bp = Blueprint('ayarlar', __name__, url_prefix='/ayarlar')


@bp.route('/')
def index():
    return render_template('ayarlar.html')
```

- [ ] **Step 7: Create placeholder templates**

Create each file extending base.html with a simple heading:

`templates/ana_sayfa.html`:
```html
{% extends "base.html" %}
{% block title %}Ana Sayfa - Apartman Yonetimi{% endblock %}
{% block content %}
<h2>Ana Sayfa</h2>
<p class="text-muted">Yakin zamanda burada ozet bilgiler olacak.</p>
{% endblock %}
```

`templates/odemeler.html`:
```html
{% extends "base.html" %}
{% block title %}Odeme Takibi - Apartman Yonetimi{% endblock %}
{% block content %}
<h2>Odeme Takibi</h2>
{% endblock %}
```

`templates/giderler.html`:
```html
{% extends "base.html" %}
{% block title %}Giderler - Apartman Yonetimi{% endblock %}
{% block content %}
<h2>Giderler</h2>
{% endblock %}
```

`templates/kasa.html`:
```html
{% extends "base.html" %}
{% block title %}Kasa - Apartman Yonetimi{% endblock %}
{% block content %}
<h2>Kasa</h2>
{% endblock %}
```

`templates/mesajlar.html`:
```html
{% extends "base.html" %}
{% block title %}Mesaj Hazirla - Apartman Yonetimi{% endblock %}
{% block content %}
<h2>Mesaj Hazirla</h2>
{% endblock %}
```

`templates/raporlar.html`:
```html
{% extends "base.html" %}
{% block title %}Raporlar - Apartman Yonetimi{% endblock %}
{% block content %}
<h2>Raporlar</h2>
{% endblock %}
```

`templates/ayarlar.html`:
```html
{% extends "base.html" %}
{% block title %}Ayarlar - Apartman Yonetimi{% endblock %}
{% block content %}
<h2>Ayarlar</h2>
{% endblock %}
```

- [ ] **Step 8: Update app.py to register blueprints**

```python
import os
from flask import Flask
from config import Config
from database import db, init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Rapor dizinini olustur
    os.makedirs(app.config['RAPORLAR_DIZINI'], exist_ok=True)

    # Blueprint'leri kaydet
    from routes import register_blueprints
    register_blueprints(app)

    init_db(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
```

- [ ] **Step 9: Run the app and verify it starts**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && timeout 3 python app.py || true`
Expected: `Running on http://127.0.0.1:5000` (times out after 3s, that's OK)

- [ ] **Step 10: Run all tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 11: Commit**

```bash
git add templates/ static/ routes/ app.py
git commit -m "feat: base template (dark theme), sidebar navigasyon, placeholder sayfalar"
```

---

### Task 3: Ayarlar Sayfasi

**Files:**
- Modify: `routes/ayarlar.py`
- Modify: `templates/ayarlar.html`

- [ ] **Step 1: Write test for ayarlar routes in tests/test_models.py (append)**

Append to `tests/test_models.py`:

```python
def test_ayarlar_sayfasi_yukle(client):
    response = client.get('/ayarlar/')
    assert response.status_code == 200
    assert 'Ayarlar'.encode() in response.data


def test_ayarlar_apartman_adi_guncelle(client):
    response = client.post('/ayarlar/genel', data={
        'apartman_adi': 'Gul Apartmani',
        'mail_adresi': 'test@test.com',
        'smtp_sunucu': 'smtp.gmail.com',
        'smtp_port': '587',
        'smtp_sifre': '',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import Ayar
    assert Ayar.getir('apartman_adi') == 'Gul Apartmani'


def test_aidat_guncelle(client):
    response = client.post('/ayarlar/aidat', data={
        'miktar': '750',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import AidatAyari
    assert AidatAyari.guncel_miktar() == 750


def test_daire_guncelle(client):
    from models import Daire
    response = client.post('/ayarlar/daire/1', data={
        'sakin_adi': 'Ahmet Yilmaz',
        'telefon': '5551234567',
    }, follow_redirects=True)
    assert response.status_code == 200


def test_gider_kalemi_ekle(client):
    response = client.post('/ayarlar/gider-kalemi', data={
        'kalem_adi': 'Dogalgaz',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import GiderKalemi
    assert GiderKalemi.query.filter_by(kalem_adi='Dogalgaz').first() is not None


def test_gider_kalemi_pasif_yap(client):
    from models import GiderKalemi
    kalem = GiderKalemi.query.first()
    response = client.post(f'/ayarlar/gider-kalemi/{kalem.id}/toggle', follow_redirects=True)
    assert response.status_code == 200
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_models.py::test_ayarlar_sayfasi_yukle -v`
Expected: FAIL (template not implemented)

- [ ] **Step 3: Implement routes/ayarlar.py**

```python
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Ayar, AidatAyari, Daire, GiderKalemi

bp = Blueprint('ayarlar', __name__, url_prefix='/ayarlar')


@bp.route('/')
def index():
    apartman_adi = Ayar.getir('apartman_adi', '')
    mail_adresi = Ayar.getir('mail_adresi', '')
    smtp_sunucu = Ayar.getir('smtp_sunucu', 'smtp.gmail.com')
    smtp_port = Ayar.getir('smtp_port', '587')
    smtp_sifre = Ayar.getir('smtp_sifre', '')
    mesaj_sablonu = Ayar.getir('mesaj_sablonu', '')

    aidat = AidatAyari.guncel_miktar()
    daireler = Daire.query.order_by(Daire.daire_no).all()
    gider_kalemleri = GiderKalemi.query.all()

    return render_template('ayarlar.html',
                           apartman_adi=apartman_adi,
                           mail_adresi=mail_adresi,
                           smtp_sunucu=smtp_sunucu,
                           smtp_port=smtp_port,
                           smtp_sifre=smtp_sifre,
                           mesaj_sablonu=mesaj_sablonu,
                           aidat=aidat,
                           daireler=daireler,
                           gider_kalemleri=gider_kalemleri)


@bp.route('/genel', methods=['POST'])
def genel_kaydet():
    Ayar.kaydet('apartman_adi', request.form.get('apartman_adi', ''))
    Ayar.kaydet('mail_adresi', request.form.get('mail_adresi', ''))
    Ayar.kaydet('smtp_sunucu', request.form.get('smtp_sunucu', ''))
    Ayar.kaydet('smtp_port', request.form.get('smtp_port', ''))
    Ayar.kaydet('smtp_sifre', request.form.get('smtp_sifre', ''))
    flash('Genel ayarlar kaydedildi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/aidat', methods=['POST'])
def aidat_kaydet():
    miktar = float(request.form.get('miktar', 0))
    yeni = AidatAyari(miktar=miktar, gecerlilik_tarihi=date.today())
    db.session.add(yeni)
    db.session.commit()
    flash(f'Aidat miktari {miktar:.2f} TL olarak guncellendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/daire/<int:daire_id>', methods=['POST'])
def daire_kaydet(daire_id):
    daire = Daire.query.get_or_404(daire_id)
    daire.sakin_adi = request.form.get('sakin_adi', '')
    daire.telefon = request.form.get('telefon', '')
    db.session.commit()
    flash(f'Daire {daire.daire_no} bilgileri guncellendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/gider-kalemi', methods=['POST'])
def gider_kalemi_ekle():
    kalem_adi = request.form.get('kalem_adi', '').strip()
    if kalem_adi:
        db.session.add(GiderKalemi(kalem_adi=kalem_adi, aktif=True))
        db.session.commit()
        flash(f'"{kalem_adi}" gider kalemi eklendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/gider-kalemi/<int:kalem_id>/toggle', methods=['POST'])
def gider_kalemi_toggle(kalem_id):
    kalem = GiderKalemi.query.get_or_404(kalem_id)
    kalem.aktif = not kalem.aktif
    db.session.commit()
    durum = 'aktif' if kalem.aktif else 'pasif'
    flash(f'"{kalem.kalem_adi}" {durum} yapildi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/mesaj-sablonu', methods=['POST'])
def mesaj_sablonu_kaydet():
    sablon = request.form.get('mesaj_sablonu', '')
    Ayar.kaydet('mesaj_sablonu', sablon)
    flash('Mesaj sablonu kaydedildi.', 'success')
    return redirect(url_for('ayarlar.index'))
```

- [ ] **Step 4: Implement templates/ayarlar.html**

```html
{% extends "base.html" %}
{% block title %}Ayarlar - Apartman Yonetimi{% endblock %}
{% block content %}
<h2 class="mb-4"><i class="bi bi-gear"></i> Ayarlar</h2>

<!-- Genel Ayarlar -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-header"><h5 class="mb-0">Genel Ayarlar</h5></div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('ayarlar.genel_kaydet') }}">
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">Apartman Adi</label>
                    <input type="text" class="form-control" name="apartman_adi" value="{{ apartman_adi }}">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Mail Adresi</label>
                    <input type="email" class="form-control" name="mail_adresi" value="{{ mail_adresi }}">
                </div>
                <div class="col-md-4">
                    <label class="form-label">SMTP Sunucu</label>
                    <input type="text" class="form-control" name="smtp_sunucu" value="{{ smtp_sunucu }}">
                </div>
                <div class="col-md-2">
                    <label class="form-label">SMTP Port</label>
                    <input type="text" class="form-control" name="smtp_port" value="{{ smtp_port }}">
                </div>
                <div class="col-md-6">
                    <label class="form-label">SMTP Sifre (Uygulama Sifresi)</label>
                    <input type="password" class="form-control" name="smtp_sifre" value="{{ smtp_sifre }}">
                </div>
            </div>
            <button type="submit" class="btn btn-primary mt-3">Kaydet</button>
        </form>
    </div>
</div>

<!-- Aidat Ayari -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-header"><h5 class="mb-0">Aidat Miktari</h5></div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('ayarlar.aidat_kaydet') }}" class="row g-3 align-items-end">
            <div class="col-auto">
                <label class="form-label">Mevcut Aidat: <strong>{{ "%.2f"|format(aidat) }} TL</strong></label>
                <div class="input-group">
                    <input type="number" step="0.01" class="form-control" name="miktar" placeholder="Yeni miktar">
                    <span class="input-group-text">TL</span>
                </div>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-primary">Guncelle</button>
            </div>
        </form>
    </div>
</div>

<!-- Daire Bilgileri -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-header"><h5 class="mb-0">Daire Bilgileri</h5></div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-dark table-hover">
                <thead>
                    <tr>
                        <th>Daire No</th>
                        <th>Kat</th>
                        <th>Sakin Adi</th>
                        <th>Telefon</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {% for daire in daireler %}
                    <tr>
                        <form method="POST" action="{{ url_for('ayarlar.daire_kaydet', daire_id=daire.id) }}">
                            <td>{{ daire.daire_no }}</td>
                            <td>{{ daire.kat }}</td>
                            <td><input type="text" class="form-control form-control-sm" name="sakin_adi" value="{{ daire.sakin_adi }}"></td>
                            <td><input type="text" class="form-control form-control-sm" name="telefon" value="{{ daire.telefon }}"></td>
                            <td><button type="submit" class="btn btn-sm btn-outline-primary">Kaydet</button></td>
                        </form>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Gider Kalemleri -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-header"><h5 class="mb-0">Gider Kalemleri</h5></div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('ayarlar.gider_kalemi_ekle') }}" class="row g-3 mb-3 align-items-end">
            <div class="col-auto">
                <input type="text" class="form-control" name="kalem_adi" placeholder="Yeni gider kalemi">
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-success">Ekle</button>
            </div>
        </form>
        <table class="table table-dark table-hover">
            <thead>
                <tr><th>Kalem Adi</th><th>Durum</th><th></th></tr>
            </thead>
            <tbody>
                {% for kalem in gider_kalemleri %}
                <tr>
                    <td>{{ kalem.kalem_adi }}</td>
                    <td>
                        {% if kalem.aktif %}
                            <span class="badge bg-success">Aktif</span>
                        {% else %}
                            <span class="badge bg-secondary">Pasif</span>
                        {% endif %}
                    </td>
                    <td>
                        <form method="POST" action="{{ url_for('ayarlar.gider_kalemi_toggle', kalem_id=kalem.id) }}" style="display:inline">
                            <button type="submit" class="btn btn-sm btn-outline-warning">
                                {% if kalem.aktif %}Pasif Yap{% else %}Aktif Yap{% endif %}
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Mesaj Sablonu -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-header"><h5 class="mb-0">Mesaj Sablonu</h5></div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('ayarlar.mesaj_sablonu_kaydet') }}">
            <p class="text-muted small">
                Kullanilabilir degiskenler: <code>{apartman_adi}</code>, <code>{ay_yil}</code>,
                <code>{miktar}</code>, <code>{odemeyenler}</code>
            </p>
            <textarea class="form-control mb-3" name="mesaj_sablonu" rows="8">{{ mesaj_sablonu }}</textarea>
            <button type="submit" class="btn btn-primary">Kaydet</button>
        </form>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_models.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add routes/ayarlar.py templates/ayarlar.html tests/test_models.py
git commit -m "feat: ayarlar sayfasi - genel, aidat, daire, gider kalemi, mesaj sablonu"
```

---

### Task 4: Odeme Takibi

**Files:**
- Modify: `routes/odemeler.py`
- Modify: `templates/odemeler.html`
- Create: `templates/parcalar/odeme_satir.html`
- Create: `templates/daire_detay.html`
- Create: `tests/test_odemeler.py`

- [ ] **Step 1: Write tests in tests/test_odemeler.py**

```python
from models import Odeme, Daire


def test_odemeler_sayfasi_yukle(client):
    response = client.get('/odemeler/')
    assert response.status_code == 200
    assert 'Odeme Takibi'.encode() in response.data


def test_odemeler_ay_secimi(client):
    response = client.get('/odemeler/?yil=2026&ay=4')
    assert response.status_code == 200


def test_odeme_toggle_odendi(client, db_session):
    daire = Daire.query.filter_by(daire_no=1).first()
    response = client.post(f'/odemeler/toggle/{daire.id}/2026/4')
    assert response.status_code == 200
    odeme = Odeme.query.filter_by(daire_id=daire.id, yil=2026, ay=4).first()
    assert odeme is not None
    assert odeme.odendi is True


def test_odeme_toggle_geri_al(client, db_session):
    daire = Daire.query.filter_by(daire_no=1).first()
    # Ilk tikla: odendi
    client.post(f'/odemeler/toggle/{daire.id}/2026/4')
    # Ikinci tikla: geri al
    client.post(f'/odemeler/toggle/{daire.id}/2026/4')
    odeme = Odeme.query.filter_by(daire_id=daire.id, yil=2026, ay=4).first()
    assert odeme.odendi is False


def test_daire_detay(client, db_session):
    daire = Daire.query.filter_by(daire_no=1).first()
    response = client.get(f'/odemeler/daire/{daire.id}')
    assert response.status_code == 200
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_odemeler.py -v`
Expected: FAIL

- [ ] **Step 3: Implement routes/odemeler.py**

```python
from datetime import datetime
from flask import Blueprint, render_template, request
from database import db
from models import Daire, Odeme, AidatAyari

bp = Blueprint('odemeler', __name__, url_prefix='/odemeler')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)
    ay = request.args.get('ay', now.month, type=int)

    daireler = Daire.query.order_by(Daire.daire_no).all()
    aidat = AidatAyari.guncel_miktar()

    # Her daire icin odeme durumunu getir
    odeme_durumlari = {}
    for daire in daireler:
        odeme = Odeme.query.filter_by(daire_id=daire.id, yil=yil, ay=ay).first()
        odeme_durumlari[daire.id] = odeme

    # Ozet bilgiler
    toplam_daire = len(daireler)
    odenen = sum(1 for o in odeme_durumlari.values() if o and o.odendi)
    odenmeyen = toplam_daire - odenen

    return render_template('odemeler.html',
                           daireler=daireler,
                           odeme_durumlari=odeme_durumlari,
                           yil=yil, ay=ay,
                           aidat=aidat,
                           ay_isimleri=AY_ISIMLERI,
                           toplam_daire=toplam_daire,
                           odenen=odenen,
                           odenmeyen=odenmeyen)


@bp.route('/toggle/<int:daire_id>/<int:yil>/<int:ay>', methods=['POST'])
def toggle(daire_id, yil, ay):
    odeme = Odeme.query.filter_by(daire_id=daire_id, yil=yil, ay=ay).first()
    if odeme is None:
        odeme = Odeme(daire_id=daire_id, yil=yil, ay=ay, odendi=True, odeme_tarihi=datetime.now())
        db.session.add(odeme)
    else:
        odeme.odendi = not odeme.odendi
        odeme.odeme_tarihi = datetime.now() if odeme.odendi else None
    db.session.commit()

    daire = Daire.query.get(daire_id)
    return render_template('parcalar/odeme_satir.html', daire=daire, odeme=odeme, yil=yil, ay=ay)


@bp.route('/daire/<int:daire_id>')
def daire_detay(daire_id):
    daire = Daire.query.get_or_404(daire_id)
    odemeler = Odeme.query.filter_by(daire_id=daire_id).order_by(Odeme.yil.desc(), Odeme.ay.desc()).all()
    aidat = AidatAyari.guncel_miktar()

    # Borc hesapla: odenmeyen aylar * aidat
    odenmeyen_sayisi = sum(1 for o in odemeler if not o.odendi)

    return render_template('daire_detay.html',
                           daire=daire,
                           odemeler=odemeler,
                           aidat=aidat,
                           odenmeyen_sayisi=odenmeyen_sayisi,
                           ay_isimleri=AY_ISIMLERI)
```

- [ ] **Step 4: Create templates/parcalar/odeme_satir.html**

```html
<tr id="odeme-satir-{{ daire.id }}">
    <td>{{ daire.daire_no }}</td>
    <td>{{ daire.sakin_adi or '-' }}</td>
    <td class="text-center">
        <button class="odeme-btn {{ 'odendi' if odeme and odeme.odendi else 'odenmedi' }}"
                hx-post="{{ url_for('odemeler.toggle', daire_id=daire.id, yil=yil, ay=ay) }}"
                hx-target="#odeme-satir-{{ daire.id }}"
                hx-swap="outerHTML">
            {% if odeme and odeme.odendi %}
                <i class="bi bi-check-circle-fill"></i>
            {% else %}
                <i class="bi bi-x-circle-fill"></i>
            {% endif %}
        </button>
    </td>
    <td>
        {% if odeme and odeme.odendi and odeme.odeme_tarihi %}
            {{ odeme.odeme_tarihi.strftime('%d.%m.%Y') }}
        {% else %}
            -
        {% endif %}
    </td>
    <td>
        <a href="{{ url_for('odemeler.daire_detay', daire_id=daire.id) }}" class="btn btn-sm btn-outline-info">
            <i class="bi bi-eye"></i>
        </a>
    </td>
</tr>
```

- [ ] **Step 5: Implement templates/odemeler.html**

```html
{% extends "base.html" %}
{% block title %}Odeme Takibi - Apartman Yonetimi{% endblock %}
{% block content %}
<h2 class="mb-4"><i class="bi bi-cash-stack"></i> Odeme Takibi</h2>

<!-- Ay/Yil secici -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-end">
            <div class="col-auto">
                <label class="form-label">Ay</label>
                <select name="ay" class="form-select">
                    {% for a in range(1, 13) %}
                    <option value="{{ a }}" {% if a == ay %}selected{% endif %}>{{ ay_isimleri[a] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-auto">
                <label class="form-label">Yil</label>
                <select name="yil" class="form-select">
                    {% for y in range(2024, 2031) %}
                    <option value="{{ y }}" {% if y == yil %}selected{% endif %}>{{ y }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-primary">Goster</button>
            </div>
        </form>
    </div>
</div>

<!-- Ozet kartlar -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card ozet-kart bg-dark border-secondary text-center p-3">
            <div class="text-muted small">Aidat Miktari</div>
            <div class="fs-4 fw-bold">{{ "%.2f"|format(aidat) }} TL</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card ozet-kart bg-dark border-secondary text-center p-3">
            <div class="text-muted small">Odenen</div>
            <div class="fs-4 fw-bold text-success">{{ odenen }} / {{ toplam_daire }}</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card ozet-kart bg-dark border-secondary text-center p-3">
            <div class="text-muted small">Odenmeyen</div>
            <div class="fs-4 fw-bold text-danger">{{ odenmeyen }}</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card ozet-kart bg-dark border-secondary text-center p-3">
            <div class="text-muted small">Tahsilat</div>
            <div class="fs-4 fw-bold">{{ "%.2f"|format(odenen * aidat) }} TL</div>
        </div>
    </div>
</div>

<!-- Odeme tablosu -->
<div class="card bg-dark border-secondary">
    <div class="card-header">
        <h5 class="mb-0">{{ ay_isimleri[ay] }} {{ yil }} - Odeme Durumu</h5>
    </div>
    <div class="card-body">
        <table class="table table-dark table-hover">
            <thead>
                <tr>
                    <th>Daire No</th>
                    <th>Sakin</th>
                    <th class="text-center">Durum</th>
                    <th>Odeme Tarihi</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {% for daire in daireler %}
                    {% set odeme = odeme_durumlari[daire.id] %}
                    {% include "parcalar/odeme_satir.html" %}
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Implement templates/daire_detay.html**

```html
{% extends "base.html" %}
{% block title %}Daire {{ daire.daire_no }} - Apartman Yonetimi{% endblock %}
{% block content %}
<h2 class="mb-4">
    <a href="{{ url_for('odemeler.index') }}" class="text-decoration-none text-muted">
        <i class="bi bi-arrow-left"></i>
    </a>
    Daire {{ daire.daire_no }} - {{ daire.sakin_adi or 'Bilinmiyor' }}
</h2>

<div class="row mb-4">
    <div class="col-md-4">
        <div class="card ozet-kart bg-dark border-secondary p-3">
            <div class="text-muted small">Kat</div>
            <div class="fs-4 fw-bold">{{ daire.kat }}</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card ozet-kart bg-dark border-secondary p-3">
            <div class="text-muted small">Telefon</div>
            <div class="fs-4 fw-bold">{{ daire.telefon or '-' }}</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card ozet-kart bg-dark border-secondary p-3">
            <div class="text-muted small">Odenmemis Aidat</div>
            <div class="fs-4 fw-bold text-danger">{{ odenmeyen_sayisi }} ay ({{ "%.2f"|format(odenmeyen_sayisi * aidat) }} TL)</div>
        </div>
    </div>
</div>

<div class="card bg-dark border-secondary">
    <div class="card-header"><h5 class="mb-0">Odeme Gecmisi</h5></div>
    <div class="card-body">
        {% if odemeler %}
        <table class="table table-dark table-hover">
            <thead>
                <tr><th>Donem</th><th>Durum</th><th>Odeme Tarihi</th></tr>
            </thead>
            <tbody>
                {% for odeme in odemeler %}
                <tr>
                    <td>{{ ay_isimleri.get(odeme.ay, '?') }} {{ odeme.yil }}</td>
                    <td>
                        {% if odeme.odendi %}
                            <span class="badge bg-success">Odendi</span>
                        {% else %}
                            <span class="badge bg-danger">Odenmedi</span>
                        {% endif %}
                    </td>
                    <td>{{ odeme.odeme_tarihi.strftime('%d.%m.%Y') if odeme.odeme_tarihi else '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-muted">Henuz odeme kaydi bulunmuyor.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 7: Run tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_odemeler.py -v`
Expected: All 5 tests PASS

- [ ] **Step 8: Commit**

```bash
git add routes/odemeler.py templates/odemeler.html templates/parcalar/odeme_satir.html templates/daire_detay.html tests/test_odemeler.py
git commit -m "feat: odeme takibi - HTMX toggle, ay secimi, daire detay sayfasi"
```

---

### Task 5: Giderler

**Files:**
- Modify: `routes/giderler.py`
- Modify: `templates/giderler.html`
- Create: `templates/parcalar/gider_tablo.html`
- Create: `tests/test_giderler.py`

- [ ] **Step 1: Write tests in tests/test_giderler.py**

```python
from models import Gider, GiderKalemi


def test_giderler_sayfasi_yukle(client):
    response = client.get('/giderler/')
    assert response.status_code == 200
    assert 'Giderler'.encode() in response.data


def test_gider_ekle(client, db_session):
    kalem = GiderKalemi.query.filter_by(kalem_adi='Elektrik').first()
    response = client.post('/giderler/ekle', data={
        'kalem_id': kalem.id,
        'yil': 2026,
        'ay': 4,
        'tutar': '1500.50',
        'aciklama': 'Nisan elektrik faturasi',
    }, follow_redirects=True)
    assert response.status_code == 200
    gider = Gider.query.filter_by(kalem_id=kalem.id, yil=2026, ay=4).first()
    assert gider is not None
    assert gider.tutar == 1500.50


def test_gider_sil(client, db_session):
    kalem = GiderKalemi.query.filter_by(kalem_adi='Su').first()
    from database import db
    gider = Gider(kalem_id=kalem.id, yil=2026, ay=4, tutar=300, aciklama='')
    db.session.add(gider)
    db.session.commit()
    gider_id = gider.id

    response = client.post(f'/giderler/sil/{gider_id}', follow_redirects=True)
    assert response.status_code == 200
    assert Gider.query.get(gider_id) is None
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_giderler.py -v`
Expected: FAIL

- [ ] **Step 3: Implement routes/giderler.py**

```python
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import GiderKalemi, Gider

bp = Blueprint('giderler', __name__, url_prefix='/giderler')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)
    ay = request.args.get('ay', now.month, type=int)

    kalemleri = GiderKalemi.query.filter_by(aktif=True).all()
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam = sum(g.tutar for g in giderler)

    return render_template('giderler.html',
                           kalemleri=kalemleri,
                           giderler=giderler,
                           yil=yil, ay=ay,
                           toplam=toplam,
                           ay_isimleri=AY_ISIMLERI)


@bp.route('/ekle', methods=['POST'])
def ekle():
    kalem_id = request.form.get('kalem_id', type=int)
    yil = request.form.get('yil', type=int)
    ay = request.form.get('ay', type=int)
    tutar = request.form.get('tutar', type=float)
    aciklama = request.form.get('aciklama', '')

    gider = Gider(kalem_id=kalem_id, yil=yil, ay=ay, tutar=tutar, aciklama=aciklama)
    db.session.add(gider)
    db.session.commit()
    flash('Gider eklendi.', 'success')
    return redirect(url_for('giderler.index', yil=yil, ay=ay))


@bp.route('/sil/<int:gider_id>', methods=['POST'])
def sil(gider_id):
    gider = Gider.query.get_or_404(gider_id)
    yil, ay = gider.yil, gider.ay
    db.session.delete(gider)
    db.session.commit()
    flash('Gider silindi.', 'success')
    return redirect(url_for('giderler.index', yil=yil, ay=ay))
```

- [ ] **Step 4: Implement templates/giderler.html**

```html
{% extends "base.html" %}
{% block title %}Giderler - Apartman Yonetimi{% endblock %}
{% block content %}
<h2 class="mb-4"><i class="bi bi-receipt"></i> Giderler</h2>

<!-- Ay/Yil secici -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-end">
            <div class="col-auto">
                <label class="form-label">Ay</label>
                <select name="ay" class="form-select">
                    {% for a in range(1, 13) %}
                    <option value="{{ a }}" {% if a == ay %}selected{% endif %}>{{ ay_isimleri[a] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-auto">
                <label class="form-label">Yil</label>
                <select name="yil" class="form-select">
                    {% for y in range(2024, 2031) %}
                    <option value="{{ y }}" {% if y == yil %}selected{% endif %}>{{ y }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-primary">Goster</button>
            </div>
        </form>
    </div>
</div>

<!-- Gider ekleme formu -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-header"><h5 class="mb-0">Yeni Gider Ekle</h5></div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('giderler.ekle') }}" class="row g-3 align-items-end">
            <input type="hidden" name="yil" value="{{ yil }}">
            <input type="hidden" name="ay" value="{{ ay }}">
            <div class="col-md-3">
                <label class="form-label">Gider Kalemi</label>
                <select name="kalem_id" class="form-select" required>
                    {% for kalem in kalemleri %}
                    <option value="{{ kalem.id }}">{{ kalem.kalem_adi }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Tutar (TL)</label>
                <input type="number" step="0.01" class="form-control" name="tutar" required>
            </div>
            <div class="col-md-4">
                <label class="form-label">Aciklama</label>
                <input type="text" class="form-control" name="aciklama">
            </div>
            <div class="col-md-2">
                <button type="submit" class="btn btn-success w-100">Ekle</button>
            </div>
        </form>
    </div>
</div>

<!-- Gider listesi -->
<div class="card bg-dark border-secondary">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">{{ ay_isimleri[ay] }} {{ yil }} Giderleri</h5>
        <span class="badge bg-info fs-6">Toplam: {{ "%.2f"|format(toplam) }} TL</span>
    </div>
    <div class="card-body">
        {% if giderler %}
        <table class="table table-dark table-hover">
            <thead>
                <tr>
                    <th>Kalem</th>
                    <th>Tutar</th>
                    <th>Aciklama</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {% for gider in giderler %}
                <tr>
                    <td>{{ gider.kalem.kalem_adi }}</td>
                    <td>{{ "%.2f"|format(gider.tutar) }} TL</td>
                    <td>{{ gider.aciklama or '-' }}</td>
                    <td>
                        <form method="POST" action="{{ url_for('giderler.sil', gider_id=gider.id) }}" style="display:inline">
                            <button type="submit" class="btn btn-sm btn-outline-danger" onclick="return confirm('Bu gideri silmek istediginize emin misiniz?')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-muted">Bu ay icin gider kaydi bulunmuyor.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_giderler.py -v`
Expected: All 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add routes/giderler.py templates/giderler.html tests/test_giderler.py
git commit -m "feat: giderler sayfasi - gider ekleme, silme, ay bazli listeleme"
```

---

### Task 6: Kasa Servisi ve Sayfasi

**Files:**
- Create: `services/__init__.py`
- Create: `services/kasa_servisi.py`
- Modify: `routes/kasa.py`
- Modify: `templates/kasa.html`
- Create: `tests/test_kasa.py`

- [ ] **Step 1: Write tests in tests/test_kasa.py**

```python
from models import Odeme, Gider, GiderKalemi, Kasa, Daire, AidatAyari
from database import db as _db


def _odeme_olustur(db_session, daire_no, yil, ay, odendi=True):
    daire = Daire.query.filter_by(daire_no=daire_no).first()
    odeme = Odeme(daire_id=daire.id, yil=yil, ay=ay, odendi=odendi)
    _db.session.add(odeme)
    _db.session.commit()


def _gider_olustur(db_session, kalem_adi, yil, ay, tutar):
    kalem = GiderKalemi.query.filter_by(kalem_adi=kalem_adi).first()
    gider = Gider(kalem_id=kalem.id, yil=yil, ay=ay, tutar=tutar, aciklama='')
    _db.session.add(gider)
    _db.session.commit()


def test_kasa_hesapla(db_session):
    # 3 daire odedi, 1 gider var
    for i in range(1, 4):
        _odeme_olustur(db_session, i, 2026, 4, True)
    _gider_olustur(db_session, 'Elektrik', 2026, 4, 800)

    from services.kasa_servisi import kasa_hesapla
    kasa = kasa_hesapla(2026, 4)
    assert kasa.toplam_gelir == 1500  # 3 * 500
    assert kasa.toplam_gider == 800
    assert kasa.bakiye == 700  # 1500 - 800


def test_kasa_devir(db_session):
    # Onceki ay kasa
    onceki = Kasa(yil=2026, ay=3, toplam_gelir=6000, toplam_gider=3000, devir=0, bakiye=3000)
    _db.session.add(onceki)
    _db.session.commit()

    for i in range(1, 4):
        _odeme_olustur(db_session, i, 2026, 4, True)
    _gider_olustur(db_session, 'Su', 2026, 4, 500)

    from services.kasa_servisi import kasa_hesapla
    kasa = kasa_hesapla(2026, 4)
    assert kasa.devir == 3000
    assert kasa.bakiye == 3000 + 1500 - 500  # 4000


def test_kasa_sayfasi(client):
    response = client.get('/kasa/')
    assert response.status_code == 200
    assert 'Kasa'.encode() in response.data
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_kasa.py -v`
Expected: FAIL

- [ ] **Step 3: Create services/__init__.py (empty)**

```python
```

- [ ] **Step 4: Implement services/kasa_servisi.py**

```python
from database import db
from models import Kasa, Odeme, Gider, AidatAyari


def kasa_hesapla(yil, ay):
    """Belirli ay icin kasa hesapla ve kaydet."""
    aidat = AidatAyari.guncel_miktar()

    # Odenen aidatlar
    odenen_sayisi = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    toplam_gelir = odenen_sayisi * aidat

    # Toplam gider
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam_gider = sum(g.tutar for g in giderler)

    # Onceki ay devir
    devir = 0
    if ay == 1:
        onceki = Kasa.query.filter_by(yil=yil - 1, ay=12).first()
    else:
        onceki = Kasa.query.filter_by(yil=yil, ay=ay - 1).first()
    if onceki:
        devir = onceki.bakiye

    bakiye = devir + toplam_gelir - toplam_gider

    # Kaydet veya guncelle
    kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
    if kasa is None:
        kasa = Kasa(yil=yil, ay=ay)
        db.session.add(kasa)
    kasa.toplam_gelir = toplam_gelir
    kasa.toplam_gider = toplam_gider
    kasa.devir = devir
    kasa.bakiye = bakiye
    db.session.commit()

    return kasa


def yillik_kasa(yil):
    """Bir yilin tum aylarinin kasa durumunu dondur."""
    kayitlar = []
    for ay in range(1, 13):
        kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
        kayitlar.append(kasa)
    return kayitlar
```

- [ ] **Step 5: Implement routes/kasa.py**

```python
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Kasa
from services.kasa_servisi import kasa_hesapla, yillik_kasa

bp = Blueprint('kasa', __name__, url_prefix='/kasa')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)
    kayitlar = yillik_kasa(yil)

    # Yillik toplamlar
    toplam_gelir = sum(k.toplam_gelir for k in kayitlar if k)
    toplam_gider = sum(k.toplam_gider for k in kayitlar if k)
    son_bakiye = 0
    for k in reversed(kayitlar):
        if k:
            son_bakiye = k.bakiye
            break

    return render_template('kasa.html',
                           kayitlar=kayitlar,
                           yil=yil,
                           toplam_gelir=toplam_gelir,
                           toplam_gider=toplam_gider,
                           son_bakiye=son_bakiye,
                           ay_isimleri=AY_ISIMLERI)


@bp.route('/hesapla', methods=['POST'])
def hesapla():
    yil = request.form.get('yil', type=int)
    ay = request.form.get('ay', type=int)
    kasa_hesapla(yil, ay)
    flash(f'{AY_ISIMLERI[ay]} {yil} kasa durumu hesaplandi.', 'success')
    return redirect(url_for('kasa.index', yil=yil))
```

- [ ] **Step 6: Implement templates/kasa.html**

```html
{% extends "base.html" %}
{% block title %}Kasa - Apartman Yonetimi{% endblock %}
{% block content %}
<h2 class="mb-4"><i class="bi bi-safe"></i> Kasa</h2>

<!-- Yil secici ve hesapla -->
<div class="card bg-dark border-secondary mb-4">
    <div class="card-body">
        <div class="row g-3 align-items-end">
            <div class="col-auto">
                <form method="GET" class="d-flex gap-2 align-items-end">
                    <div>
                        <label class="form-label">Yil</label>
                        <select name="yil" class="form-select">
                            {% for y in range(2024, 2031) %}
                            <option value="{{ y }}" {% if y == yil %}selected{% endif %}>{{ y }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Goster</button>
                </form>
            </div>
            <div class="col-auto ms-auto">
                <form method="POST" action="{{ url_for('kasa.hesapla') }}" class="d-flex gap-2 align-items-end">
                    <input type="hidden" name="yil" value="{{ yil }}">
                    <div>
                        <label class="form-label">Ay Hesapla</label>
                        <select name="ay" class="form-select">
                            {% for a in range(1, 13) %}
                            <option value="{{ a }}">{{ ay_isimleri[a] }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <button type="submit" class="btn btn-success">Hesapla</button>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Yillik ozet -->
<div class="row mb-4">
    <div class="col-md-4">
        <div class="card ozet-kart bg-dark border-secondary text-center p-3">
            <div class="text-muted small">Yillik Toplam Gelir</div>
            <div class="fs-4 fw-bold text-success">{{ "%.2f"|format(toplam_gelir) }} TL</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card ozet-kart bg-dark border-secondary text-center p-3">
            <div class="text-muted small">Yillik Toplam Gider</div>
            <div class="fs-4 fw-bold text-danger">{{ "%.2f"|format(toplam_gider) }} TL</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card ozet-kart bg-dark border-secondary text-center p-3">
            <div class="text-muted small">Guncel Bakiye</div>
            <div class="fs-4 fw-bold">{{ "%.2f"|format(son_bakiye) }} TL</div>
        </div>
    </div>
</div>

<!-- Aylik kasa tablosu -->
<div class="card bg-dark border-secondary">
    <div class="card-header"><h5 class="mb-0">{{ yil }} Aylik Kasa Durumu</h5></div>
    <div class="card-body">
        <table class="table table-dark table-hover">
            <thead>
                <tr>
                    <th>Ay</th>
                    <th>Devir</th>
                    <th>Gelir</th>
                    <th>Gider</th>
                    <th>Bakiye</th>
                </tr>
            </thead>
            <tbody>
                {% for i in range(12) %}
                    {% set kasa = kayitlar[i] %}
                    <tr>
                        <td>{{ ay_isimleri[i + 1] }}</td>
                        {% if kasa %}
                            <td>{{ "%.2f"|format(kasa.devir) }} TL</td>
                            <td class="text-success">{{ "%.2f"|format(kasa.toplam_gelir) }} TL</td>
                            <td class="text-danger">{{ "%.2f"|format(kasa.toplam_gider) }} TL</td>
                            <td class="fw-bold">{{ "%.2f"|format(kasa.bakiye) }} TL</td>
                        {% else %}
                            <td colspan="4" class="text-muted">Henuz hesaplanmadi</td>
                        {% endif %}
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 7: Run tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_kasa.py -v`
Expected: All 3 tests PASS

- [ ] **Step 8: Commit**

```bash
git add services/ routes/kasa.py templates/kasa.html tests/test_kasa.py
git commit -m "feat: kasa servisi ve sayfasi - gelir/gider/devir/bakiye hesaplama"
```

---

### Task 7: Ana Sayfa (Dashboard)

**Files:**
- Modify: `routes/ana_sayfa.py`
- Modify: `templates/ana_sayfa.html`

- [ ] **Step 1: Implement routes/ana_sayfa.py**

```python
from datetime import datetime
from flask import Blueprint, render_template
from models import Daire, Odeme, Gider, Kasa, AidatAyari

bp = Blueprint('ana_sayfa', __name__)

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    yil, ay = now.year, now.month
    aidat = AidatAyari.guncel_miktar()
    toplam_daire = Daire.query.count()

    # Bu ay odeme durumu
    odenen = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    odenmeyen = toplam_daire - odenen

    # Bu ay giderler
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam_gider = sum(g.tutar for g in giderler)

    # Kasa durumu
    kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()

    # Odemeyenler listesi
    odenen_daire_idler = {o.daire_id for o in Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).all()}
    odemeyenler = Daire.query.filter(~Daire.id.in_(odenen_daire_idler)).order_by(Daire.daire_no).all() if odenen_daire_idler else Daire.query.order_by(Daire.daire_no).all()

    return render_template('ana_sayfa.html',
                           yil=yil, ay=ay,
                           ay_adi=AY_ISIMLERI[ay],
                           aidat=aidat,
                           toplam_daire=toplam_daire,
                           odenen=odenen,
                           odenmeyen=odenmeyen,
                           toplam_gider=toplam_gider,
                           kasa=kasa,
                           odemeyenler=odemeyenler)
```

- [ ] **Step 2: Implement templates/ana_sayfa.html**

```html
{% extends "base.html" %}
{% block title %}Ana Sayfa - Apartman Yonetimi{% endblock %}
{% block content %}
<h2 class="mb-4"><i class="bi bi-house-door"></i> {{ ay_adi }} {{ yil }} Ozeti</h2>

<!-- Ozet kartlar -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card ozet-kart bg-dark border-secondary p-3">
            <div class="text-muted small">Aidat Miktari</div>
            <div class="fs-4 fw-bold">{{ "%.2f"|format(aidat) }} TL</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card ozet-kart bg-dark border-secondary p-3">
            <div class="text-muted small">Tahsilat</div>
            <div class="fs-4 fw-bold text-success">{{ odenen }}/{{ toplam_daire }}</div>
            <div class="text-muted small">{{ "%.2f"|format(odenen * aidat) }} TL</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card ozet-kart bg-dark border-secondary p-3">
            <div class="text-muted small">Toplam Gider</div>
            <div class="fs-4 fw-bold text-danger">{{ "%.2f"|format(toplam_gider) }} TL</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card ozet-kart bg-dark border-secondary p-3">
            <div class="text-muted small">Kasa Bakiye</div>
            <div class="fs-4 fw-bold">{{ "%.2f"|format(kasa.bakiye) if kasa else 'Hesaplanmadi' }}</div>
        </div>
    </div>
</div>

<!-- Odemeyenler -->
{% if odemeyenler %}
<div class="card bg-dark border-warning mb-4">
    <div class="card-header text-warning">
        <h5 class="mb-0"><i class="bi bi-exclamation-triangle"></i> Odeme Yapmayan Daireler ({{ odenmeyen }})</h5>
    </div>
    <div class="card-body">
        <div class="row">
            {% for daire in odemeyenler %}
            <div class="col-md-3 mb-2">
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-danger">Daire {{ daire.daire_no }}</span>
                    <span class="text-muted small">{{ daire.sakin_adi or '-' }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endif %}

<!-- Hizli erisim -->
<div class="row">
    <div class="col-md-4 mb-3">
        <a href="{{ url_for('odemeler.index') }}" class="card bg-dark border-secondary p-3 text-decoration-none ozet-kart">
            <div class="d-flex align-items-center gap-3">
                <i class="bi bi-cash-stack fs-2 text-primary"></i>
                <div>
                    <div class="fw-bold text-white">Odeme Takibi</div>
                    <div class="text-muted small">Aidat odemelerini yonet</div>
                </div>
            </div>
        </a>
    </div>
    <div class="col-md-4 mb-3">
        <a href="{{ url_for('mesajlar.index') }}" class="card bg-dark border-secondary p-3 text-decoration-none ozet-kart">
            <div class="d-flex align-items-center gap-3">
                <i class="bi bi-chat-dots fs-2 text-success"></i>
                <div>
                    <div class="fw-bold text-white">Mesaj Hazirla</div>
                    <div class="text-muted small">Odemeyenlere mesaj olustur</div>
                </div>
            </div>
        </a>
    </div>
    <div class="col-md-4 mb-3">
        <a href="{{ url_for('raporlar.index') }}" class="card bg-dark border-secondary p-3 text-decoration-none ozet-kart">
            <div class="d-flex align-items-center gap-3">
                <i class="bi bi-file-earmark-bar-graph fs-2 text-info"></i>
                <div>
                    <div class="fw-bold text-white">Raporlar</div>
                    <div class="text-muted small">Excel ve PDF raporlar olustur</div>
                </div>
            </div>
        </a>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Run all tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add routes/ana_sayfa.py templates/ana_sayfa.html
git commit -m "feat: ana sayfa dashboard - ozet kartlar, odemeyenler, hizli erisim"
```

---

### Task 8: Mesaj Hazirlama

**Files:**
- Modify: `routes/mesajlar.py`
- Modify: `templates/mesajlar.html`
- Create: `templates/parcalar/mesaj_onizleme.html`
- Create: `tests/test_mesajlar.py`

- [ ] **Step 1: Write tests in tests/test_mesajlar.py**

```python
from models import Daire, Odeme
from database import db as _db


def test_mesajlar_sayfasi_yukle(client):
    response = client.get('/mesajlar/')
    assert response.status_code == 200
    assert 'Mesaj Hazirla'.encode() in response.data


def test_mesaj_olustur_tum_odemeyenler(client, db_session):
    response = client.get('/mesajlar/olustur?yil=2026&ay=4')
    assert response.status_code == 200
    # Hicbir odeme yoksa 12 daire de odememiştir
    assert 'Daire 1'.encode() in response.data


def test_mesaj_olustur_kismi_odeme(client, db_session):
    # Daire 1 odedi
    daire = Daire.query.filter_by(daire_no=1).first()
    _db.session.add(Odeme(daire_id=daire.id, yil=2026, ay=4, odendi=True))
    _db.session.commit()

    response = client.get('/mesajlar/olustur?yil=2026&ay=4')
    assert response.status_code == 200
    assert 'Daire 1'.encode() not in response.data
    assert 'Daire 2'.encode() in response.data
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_mesajlar.py -v`
Expected: FAIL

- [ ] **Step 3: Implement routes/mesajlar.py**

```python
from datetime import datetime
from flask import Blueprint, render_template, request
from models import Daire, Odeme, Ayar, AidatAyari

bp = Blueprint('mesajlar', __name__, url_prefix='/mesajlar')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    return render_template('mesajlar.html',
                           yil=now.year, ay=now.month,
                           ay_isimleri=AY_ISIMLERI)


@bp.route('/olustur')
def olustur():
    yil = request.args.get('yil', type=int)
    ay = request.args.get('ay', type=int)
    tur = request.args.get('tur', 'odemeyenler')  # 'odemeyenler' veya 'genel'

    aidat = AidatAyari.guncel_miktar()
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    sablon = Ayar.getir('mesaj_sablonu', '')
    ay_yil = f'{AY_ISIMLERI[ay]} {yil}'

    if tur == 'genel':
        # Tum dairelere genel mesaj
        daireler = Daire.query.order_by(Daire.daire_no).all()
        odemeyenler_metni = '(Genel hatirlatma - tum daireler)'
    else:
        # Sadece odemeyenler
        odenen_idler = {o.daire_id for o in Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).all()}
        if odenen_idler:
            daireler = Daire.query.filter(~Daire.id.in_(odenen_idler)).order_by(Daire.daire_no).all()
        else:
            daireler = Daire.query.order_by(Daire.daire_no).all()

        satirlar = []
        for d in daireler:
            satirlar.append(f'- Daire {d.daire_no} - {d.sakin_adi or "Bilinmiyor"}')
        odemeyenler_metni = '\n'.join(satirlar)

    mesaj = sablon.format(
        apartman_adi=apartman_adi,
        ay_yil=ay_yil,
        miktar=f'{aidat:.2f}',
        odemeyenler=odemeyenler_metni,
    )

    return render_template('parcalar/mesaj_onizleme.html',
                           mesaj=mesaj,
                           daireler=daireler,
                           yil=yil, ay=ay,
                           ay_adi=AY_ISIMLERI[ay])
```

- [ ] **Step 4: Implement templates/mesajlar.html**

```html
{% extends "base.html" %}
{% block title %}Mesaj Hazirla - Apartman Yonetimi{% endblock %}
{% block content %}
<h2 class="mb-4"><i class="bi bi-chat-dots"></i> Mesaj Hazirla</h2>

<div class="card bg-dark border-secondary mb-4">
    <div class="card-body">
        <div class="row g-3 align-items-end">
            <div class="col-auto">
                <label class="form-label">Ay</label>
                <select id="mesaj-ay" class="form-select">
                    {% for a in range(1, 13) %}
                    <option value="{{ a }}" {% if a == ay %}selected{% endif %}>{{ ay_isimleri[a] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-auto">
                <label class="form-label">Yil</label>
                <select id="mesaj-yil" class="form-select">
                    {% for y in range(2024, 2031) %}
                    <option value="{{ y }}" {% if y == yil %}selected{% endif %}>{{ y }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-auto">
                <button class="btn btn-warning"
                        hx-get="{{ url_for('mesajlar.olustur') }}"
                        hx-include="#mesaj-ay, #mesaj-yil"
                        hx-vals='{"tur": "odemeyenler"}'
                        hx-target="#mesaj-sonuc"
                        hx-params="yil,ay,tur"
                        onclick="this.setAttribute('hx-get', '{{ url_for('mesajlar.olustur') }}?yil=' + document.getElementById('mesaj-yil').value + '&ay=' + document.getElementById('mesaj-ay').value + '&tur=odemeyenler')"
                >
                    <i class="bi bi-exclamation-circle"></i> Odemeyenlere Mesaj
                </button>
            </div>
            <div class="col-auto">
                <button class="btn btn-info"
                        hx-get="{{ url_for('mesajlar.olustur') }}"
                        hx-target="#mesaj-sonuc"
                        onclick="this.setAttribute('hx-get', '{{ url_for('mesajlar.olustur') }}?yil=' + document.getElementById('mesaj-yil').value + '&ay=' + document.getElementById('mesaj-ay').value + '&tur=genel')"
                >
                    <i class="bi bi-megaphone"></i> Genel Hatirlatma
                </button>
            </div>
        </div>
    </div>
</div>

<div id="mesaj-sonuc">
    <div class="card bg-dark border-secondary">
        <div class="card-body text-center text-muted py-5">
            <i class="bi bi-chat-left-text fs-1"></i>
            <p class="mt-3">Mesaj olusturmak icin yukaridaki butonlardan birini tiklayin.</p>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Implement templates/parcalar/mesaj_onizleme.html**

```html
<div class="card bg-dark border-secondary">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">{{ ay_adi }} {{ yil }} - Mesaj Onizleme</h5>
        <button class="btn btn-success" onclick="panoyaKopyala('mesaj-icerik')">
            <i class="bi bi-clipboard"></i> Kopyala
        </button>
    </div>
    <div class="card-body">
        <div id="mesaj-icerik" class="bg-black p-3 rounded" style="white-space: pre-wrap; font-family: inherit;">{{ mesaj }}</div>
    </div>
    {% if daireler %}
    <div class="card-footer">
        <small class="text-muted">{{ daireler|length }} daire listelendi</small>
    </div>
    {% endif %}
</div>
```

- [ ] **Step 6: Run tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_mesajlar.py -v`
Expected: All 3 tests PASS

- [ ] **Step 7: Commit**

```bash
git add routes/mesajlar.py templates/mesajlar.html templates/parcalar/mesaj_onizleme.html tests/test_mesajlar.py
git commit -m "feat: mesaj hazirlama - odemeyenler listesi, sablon mesaj, kopyala"
```

---

### Task 9: Rapor Servisi (Excel + PDF)

**Files:**
- Create: `services/rapor_servisi.py`
- Modify: `routes/raporlar.py`
- Modify: `templates/raporlar.html`
- Create: `tests/test_raporlar.py`

- [ ] **Step 1: Write tests in tests/test_raporlar.py**

```python
import os
from models import Daire, Odeme, Gider, GiderKalemi, Kasa
from database import db as _db


def _hazirlik(db_session):
    """Test icin ornek veri olustur."""
    # Birkaç odeme
    for i in range(1, 7):
        daire = Daire.query.filter_by(daire_no=i).first()
        _db.session.add(Odeme(daire_id=daire.id, yil=2026, ay=4, odendi=True))
    # Birkaç gider
    kalem = GiderKalemi.query.filter_by(kalem_adi='Elektrik').first()
    _db.session.add(Gider(kalem_id=kalem.id, yil=2026, ay=4, tutar=1200, aciklama=''))
    kalem_su = GiderKalemi.query.filter_by(kalem_adi='Su').first()
    _db.session.add(Gider(kalem_id=kalem_su.id, yil=2026, ay=4, tutar=400, aciklama=''))
    # Kasa
    _db.session.add(Kasa(yil=2026, ay=4, toplam_gelir=3000, toplam_gider=1600, devir=500, bakiye=1900))
    _db.session.commit()


def test_raporlar_sayfasi(client):
    response = client.get('/raporlar/')
    assert response.status_code == 200


def test_rapor_excel_aylik_ozet(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=aylik_ozet&yil=2026&ay=4&format=excel')
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def test_rapor_pdf_aylik_ozet(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=aylik_ozet&yil=2026&ay=4&format=pdf')
    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_rapor_excel_odeme_durumu(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=odeme_durumu&yil=2026&ay=4&format=excel')
    assert response.status_code == 200


def test_rapor_excel_gider_detay(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=gider_detay&yil=2026&ay=4&format=excel')
    assert response.status_code == 200


def test_rapor_excel_yillik_ozet(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=yillik_ozet&yil=2026&format=excel')
    assert response.status_code == 200
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_raporlar.py -v`
Expected: FAIL

- [ ] **Step 3: Implement services/rapor_servisi.py**

```python
import io
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from models import Daire, Odeme, Gider, GiderKalemi, Kasa, Ayar, AidatAyari

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

# Excel stilleri
BASLIK_FONT = Font(bold=True, size=14)
ALT_BASLIK_FONT = Font(bold=True, size=11)
BASLIK_FILL = PatternFill(start_color='1a1d21', end_color='1a1d21', fill_type='solid')
BASLIK_FONT_WHITE = Font(bold=True, size=11, color='FFFFFF')
YESIL_FILL = PatternFill(start_color='d4edda', end_color='d4edda', fill_type='solid')
KIRMIZI_FILL = PatternFill(start_color='f8d7da', end_color='f8d7da', fill_type='solid')
INCE_BORDER = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)


def _excel_baslik(ws, apartman_adi, rapor_adi, tarih_str):
    """Excel dosyasina baslik satirlari ekle."""
    ws.append([apartman_adi])
    ws['A1'].font = BASLIK_FONT
    ws.append([rapor_adi])
    ws['A2'].font = ALT_BASLIK_FONT
    ws.append([f'Olusturma Tarihi: {tarih_str}'])
    ws.append([])


def _excel_tablo_basligi(ws, basliklar, satir_no):
    """Tablo baslik satirini formatla."""
    for col, baslik in enumerate(basliklar, 1):
        hucre = ws.cell(row=satir_no, column=col, value=baslik)
        hucre.fill = BASLIK_FILL
        hucre.font = BASLIK_FONT_WHITE
        hucre.border = INCE_BORDER
        hucre.alignment = Alignment(horizontal='center')


def aylik_ozet_excel(yil, ay):
    """Aylik ozet raporu - Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Aylik Ozet'
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    tarih_str = datetime.now().strftime('%d.%m.%Y')
    ay_adi = AY_ISIMLERI[ay]

    _excel_baslik(ws, apartman_adi, f'{ay_adi} {yil} - Aylik Ozet Raporu', tarih_str)

    aidat = AidatAyari.guncel_miktar()
    odenen = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    toplam_daire = Daire.query.count()
    toplam_gelir = odenen * aidat

    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam_gider = sum(g.tutar for g in giderler)

    kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
    devir = kasa.devir if kasa else 0
    bakiye = kasa.bakiye if kasa else (devir + toplam_gelir - toplam_gider)

    satir = ws.max_row + 1
    basliklar = ['Kalem', 'Tutar (TL)']
    _excel_tablo_basligi(ws, basliklar, satir)

    veriler = [
        ('Aidat Miktari', f'{aidat:.2f}'),
        ('Odenen Daire Sayisi', f'{odenen}/{toplam_daire}'),
        ('Toplam Gelir (Aidat)', f'{toplam_gelir:.2f}'),
        ('Toplam Gider', f'{toplam_gider:.2f}'),
        ('Onceki Aydan Devir', f'{devir:.2f}'),
        ('Ay Sonu Bakiye', f'{bakiye:.2f}'),
    ]
    for kalem, tutar in veriler:
        satir += 1
        ws.cell(row=satir, column=1, value=kalem).border = INCE_BORDER
        ws.cell(row=satir, column=2, value=tutar).border = INCE_BORDER

    # Gider detay
    satir += 2
    ws.cell(row=satir, column=1, value='Gider Detaylari').font = ALT_BASLIK_FONT
    satir += 1
    _excel_tablo_basligi(ws, ['Gider Kalemi', 'Tutar (TL)', 'Aciklama'], satir)
    for g in giderler:
        satir += 1
        ws.cell(row=satir, column=1, value=g.kalem.kalem_adi).border = INCE_BORDER
        ws.cell(row=satir, column=2, value=f'{g.tutar:.2f}').border = INCE_BORDER
        ws.cell(row=satir, column=3, value=g.aciklama or '').border = INCE_BORDER

    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 30

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def odeme_durumu_excel(yil, ay):
    """Odeme durumu raporu - Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Odeme Durumu'
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    tarih_str = datetime.now().strftime('%d.%m.%Y')
    ay_adi = AY_ISIMLERI[ay]

    _excel_baslik(ws, apartman_adi, f'{ay_adi} {yil} - Odeme Durumu Raporu', tarih_str)

    satir = ws.max_row + 1
    basliklar = ['Daire No', 'Sakin Adi', 'Durum', 'Odeme Tarihi']
    _excel_tablo_basligi(ws, basliklar, satir)

    daireler = Daire.query.order_by(Daire.daire_no).all()
    aidat = AidatAyari.guncel_miktar()
    odenen_sayisi = 0

    for daire in daireler:
        satir += 1
        odeme = Odeme.query.filter_by(daire_id=daire.id, yil=yil, ay=ay).first()
        odendi = odeme and odeme.odendi

        ws.cell(row=satir, column=1, value=daire.daire_no).border = INCE_BORDER
        ws.cell(row=satir, column=2, value=daire.sakin_adi or '-').border = INCE_BORDER

        durum_hucre = ws.cell(row=satir, column=3, value='Odendi' if odendi else 'Odenmedi')
        durum_hucre.border = INCE_BORDER
        durum_hucre.fill = YESIL_FILL if odendi else KIRMIZI_FILL

        tarih = odeme.odeme_tarihi.strftime('%d.%m.%Y') if odeme and odeme.odeme_tarihi else '-'
        ws.cell(row=satir, column=4, value=tarih).border = INCE_BORDER

        if odendi:
            odenen_sayisi += 1

    # Ozet
    satir += 2
    ws.cell(row=satir, column=1, value='Toplam Tahsilat').font = ALT_BASLIK_FONT
    ws.cell(row=satir, column=2, value=f'{odenen_sayisi}/{len(daireler)} (%{odenen_sayisi * 100 // len(daireler)})')
    satir += 1
    ws.cell(row=satir, column=1, value='Tahsilat Tutari')
    ws.cell(row=satir, column=2, value=f'{odenen_sayisi * aidat:.2f} TL')

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 18

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def gider_detay_excel(yil, ay):
    """Gider detay raporu - Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Gider Detay'
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    tarih_str = datetime.now().strftime('%d.%m.%Y')
    ay_adi = AY_ISIMLERI[ay]

    _excel_baslik(ws, apartman_adi, f'{ay_adi} {yil} - Gider Detay Raporu', tarih_str)

    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam = sum(g.tutar for g in giderler)

    satir = ws.max_row + 1
    _excel_tablo_basligi(ws, ['Gider Kalemi', 'Tutar (TL)', 'Oran (%)', 'Aciklama'], satir)

    for g in giderler:
        satir += 1
        oran = (g.tutar / toplam * 100) if toplam > 0 else 0
        ws.cell(row=satir, column=1, value=g.kalem.kalem_adi).border = INCE_BORDER
        ws.cell(row=satir, column=2, value=f'{g.tutar:.2f}').border = INCE_BORDER
        ws.cell(row=satir, column=3, value=f'{oran:.1f}').border = INCE_BORDER
        ws.cell(row=satir, column=4, value=g.aciklama or '').border = INCE_BORDER

    satir += 1
    ws.cell(row=satir, column=1, value='TOPLAM').font = ALT_BASLIK_FONT
    ws.cell(row=satir, column=1).border = INCE_BORDER
    ws.cell(row=satir, column=2, value=f'{toplam:.2f}').font = ALT_BASLIK_FONT
    ws.cell(row=satir, column=2).border = INCE_BORDER

    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 30

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def yillik_ozet_excel(yil):
    """Yillik ozet raporu - Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Yillik Ozet'
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    tarih_str = datetime.now().strftime('%d.%m.%Y')

    _excel_baslik(ws, apartman_adi, f'{yil} - Yillik Ozet Raporu', tarih_str)

    satir = ws.max_row + 1
    _excel_tablo_basligi(ws, ['Ay', 'Gelir (TL)', 'Gider (TL)', 'Devir (TL)', 'Bakiye (TL)'], satir)

    toplam_gelir = 0
    toplam_gider = 0

    for ay in range(1, 13):
        satir += 1
        kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
        ws.cell(row=satir, column=1, value=AY_ISIMLERI[ay]).border = INCE_BORDER
        if kasa:
            ws.cell(row=satir, column=2, value=f'{kasa.toplam_gelir:.2f}').border = INCE_BORDER
            ws.cell(row=satir, column=3, value=f'{kasa.toplam_gider:.2f}').border = INCE_BORDER
            ws.cell(row=satir, column=4, value=f'{kasa.devir:.2f}').border = INCE_BORDER
            ws.cell(row=satir, column=5, value=f'{kasa.bakiye:.2f}').border = INCE_BORDER
            toplam_gelir += kasa.toplam_gelir
            toplam_gider += kasa.toplam_gider
        else:
            for c in range(2, 6):
                ws.cell(row=satir, column=c, value='-').border = INCE_BORDER

    satir += 1
    ws.cell(row=satir, column=1, value='TOPLAM').font = ALT_BASLIK_FONT
    ws.cell(row=satir, column=2, value=f'{toplam_gelir:.2f}').font = ALT_BASLIK_FONT
    ws.cell(row=satir, column=3, value=f'{toplam_gider:.2f}').font = ALT_BASLIK_FONT

    for col in ['A', 'B', 'C', 'D', 'E']:
        ws.column_dimensions[col].width = 18

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# --- PDF fonksiyonlari ---

def _pdf_baslik_tablosu(apartman_adi, rapor_adi, tarih_str):
    """PDF baslik satirlari icin tablo dondur."""
    styles = getSampleStyleSheet()
    elemanlar = []
    elemanlar.append(Paragraph(apartman_adi, styles['Title']))
    elemanlar.append(Paragraph(rapor_adi, styles['Heading2']))
    elemanlar.append(Paragraph(f'Olusturma Tarihi: {tarih_str}', styles['Normal']))
    elemanlar.append(Spacer(1, 0.5 * cm))
    return elemanlar


def _pdf_tablo(basliklar, veriler, col_widths=None):
    """Formatli PDF tablosu olustur."""
    tablo_veri = [basliklar] + veriler
    tablo = Table(tablo_veri, colWidths=col_widths)
    stil = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d21')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
    ])
    tablo.setStyle(stil)
    return tablo


def aylik_ozet_pdf(yil, ay):
    """Aylik ozet raporu - PDF."""
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    tarih_str = datetime.now().strftime('%d.%m.%Y')
    ay_adi = AY_ISIMLERI[ay]

    elemanlar = _pdf_baslik_tablosu(apartman_adi, f'{ay_adi} {yil} - Aylik Ozet Raporu', tarih_str)

    aidat = AidatAyari.guncel_miktar()
    odenen = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    toplam_daire = Daire.query.count()
    toplam_gelir = odenen * aidat
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam_gider = sum(g.tutar for g in giderler)
    kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
    devir = kasa.devir if kasa else 0
    bakiye = kasa.bakiye if kasa else (devir + toplam_gelir - toplam_gider)

    veriler = [
        ['Aidat Miktari', f'{aidat:.2f} TL'],
        ['Odenen Daire', f'{odenen}/{toplam_daire}'],
        ['Toplam Gelir', f'{toplam_gelir:.2f} TL'],
        ['Toplam Gider', f'{toplam_gider:.2f} TL'],
        ['Devir', f'{devir:.2f} TL'],
        ['Bakiye', f'{bakiye:.2f} TL'],
    ]
    elemanlar.append(_pdf_tablo(['Kalem', 'Deger'], veriler, col_widths=[8 * cm, 6 * cm]))

    if giderler:
        elemanlar.append(Spacer(1, 1 * cm))
        styles = getSampleStyleSheet()
        elemanlar.append(Paragraph('Gider Detaylari', styles['Heading3']))
        gider_veriler = [[g.kalem.kalem_adi, f'{g.tutar:.2f} TL', g.aciklama or ''] for g in giderler]
        elemanlar.append(_pdf_tablo(['Kalem', 'Tutar', 'Aciklama'], gider_veriler, col_widths=[5 * cm, 4 * cm, 7 * cm]))

    doc.build(elemanlar)
    output.seek(0)
    return output


def odeme_durumu_pdf(yil, ay):
    """Odeme durumu raporu - PDF."""
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    tarih_str = datetime.now().strftime('%d.%m.%Y')
    ay_adi = AY_ISIMLERI[ay]

    elemanlar = _pdf_baslik_tablosu(apartman_adi, f'{ay_adi} {yil} - Odeme Durumu Raporu', tarih_str)

    daireler = Daire.query.order_by(Daire.daire_no).all()
    veriler = []
    for daire in daireler:
        odeme = Odeme.query.filter_by(daire_id=daire.id, yil=yil, ay=ay).first()
        odendi = odeme and odeme.odendi
        tarih = odeme.odeme_tarihi.strftime('%d.%m.%Y') if odeme and odeme.odeme_tarihi else '-'
        veriler.append([str(daire.daire_no), daire.sakin_adi or '-', 'Odendi' if odendi else 'Odenmedi', tarih])

    tablo = _pdf_tablo(['Daire No', 'Sakin', 'Durum', 'Tarih'], veriler,
                       col_widths=[2.5 * cm, 5 * cm, 3.5 * cm, 4 * cm])

    # Renklendir: odendi yesil, odenmedi kirmizi
    for i, veri in enumerate(veriler):
        satir = i + 1  # +1 for header
        if veri[2] == 'Odendi':
            tablo.setStyle(TableStyle([('BACKGROUND', (2, satir), (2, satir), colors.HexColor('#d4edda'))]))
        else:
            tablo.setStyle(TableStyle([('BACKGROUND', (2, satir), (2, satir), colors.HexColor('#f8d7da'))]))

    elemanlar.append(tablo)
    doc.build(elemanlar)
    output.seek(0)
    return output


def gider_detay_pdf(yil, ay):
    """Gider detay raporu - PDF."""
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    tarih_str = datetime.now().strftime('%d.%m.%Y')
    ay_adi = AY_ISIMLERI[ay]

    elemanlar = _pdf_baslik_tablosu(apartman_adi, f'{ay_adi} {yil} - Gider Detay Raporu', tarih_str)

    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam = sum(g.tutar for g in giderler)

    veriler = []
    for g in giderler:
        oran = (g.tutar / toplam * 100) if toplam > 0 else 0
        veriler.append([g.kalem.kalem_adi, f'{g.tutar:.2f} TL', f'%{oran:.1f}', g.aciklama or ''])
    veriler.append(['TOPLAM', f'{toplam:.2f} TL', '%100', ''])

    elemanlar.append(_pdf_tablo(['Kalem', 'Tutar', 'Oran', 'Aciklama'], veriler,
                                col_widths=[4.5 * cm, 3.5 * cm, 2.5 * cm, 5.5 * cm]))

    doc.build(elemanlar)
    output.seek(0)
    return output


def yillik_ozet_pdf(yil):
    """Yillik ozet raporu - PDF."""
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    tarih_str = datetime.now().strftime('%d.%m.%Y')

    elemanlar = _pdf_baslik_tablosu(apartman_adi, f'{yil} - Yillik Ozet Raporu', tarih_str)

    veriler = []
    toplam_gelir = 0
    toplam_gider = 0
    for ay in range(1, 13):
        kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
        if kasa:
            veriler.append([AY_ISIMLERI[ay], f'{kasa.toplam_gelir:.2f}', f'{kasa.toplam_gider:.2f}',
                            f'{kasa.devir:.2f}', f'{kasa.bakiye:.2f}'])
            toplam_gelir += kasa.toplam_gelir
            toplam_gider += kasa.toplam_gider
        else:
            veriler.append([AY_ISIMLERI[ay], '-', '-', '-', '-'])
    veriler.append(['TOPLAM', f'{toplam_gelir:.2f}', f'{toplam_gider:.2f}', '', ''])

    elemanlar.append(_pdf_tablo(['Ay', 'Gelir (TL)', 'Gider (TL)', 'Devir (TL)', 'Bakiye (TL)'], veriler,
                                col_widths=[3 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm]))

    doc.build(elemanlar)
    output.seek(0)
    return output
```

- [ ] **Step 4: Implement routes/raporlar.py**

```python
from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from services import rapor_servisi

bp = Blueprint('raporlar', __name__, url_prefix='/raporlar')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

RAPOR_TURLERI = {
    'aylik_ozet': 'Aylik Ozet Raporu',
    'odeme_durumu': 'Odeme Durumu Raporu',
    'gider_detay': 'Gider Detay Raporu',
    'yillik_ozet': 'Yillik Ozet Raporu',
}


@bp.route('/')
def index():
    now = datetime.now()
    return render_template('raporlar.html',
                           yil=now.year, ay=now.month,
                           ay_isimleri=AY_ISIMLERI,
                           rapor_turleri=RAPOR_TURLERI)


@bp.route('/olustur')
def olustur():
    tur = request.args.get('tur')
    fmt = request.args.get('format', 'excel')
    yil = request.args.get('yil', type=int)
    ay = request.args.get('ay', type=int)

    # Fonksiyon haritasi
    fonksiyonlar = {
        ('aylik_ozet', 'excel'): lambda: rapor_servisi.aylik_ozet_excel(yil, ay),
        ('aylik_ozet', 'pdf'): lambda: rapor_servisi.aylik_ozet_pdf(yil, ay),
        ('odeme_durumu', 'excel'): lambda: rapor_servisi.odeme_durumu_excel(yil, ay),
        ('odeme_durumu', 'pdf'): lambda: rapor_servisi.odeme_durumu_pdf(yil, ay),
        ('gider_detay', 'excel'): lambda: rapor_servisi.gider_detay_excel(yil, ay),
        ('gider_detay', 'pdf'): lambda: rapor_servisi.gider_detay_pdf(yil, ay),
        ('yillik_ozet', 'excel'): lambda: rapor_servisi.yillik_ozet_excel(yil),
        ('yillik_ozet', 'pdf'): lambda: rapor_servisi.yillik_ozet_pdf(yil),
    }

    fonksiyon = fonksiyonlar.get((tur, fmt))
    if not fonksiyon:
        return 'Gecersiz rapor turu veya format', 400

    output = fonksiyon()
    ay_adi = AY_ISIMLERI.get(ay, '')

    if fmt == 'excel':
        dosya_adi = f'{tur}_{ay_adi}_{yil}.xlsx' if ay else f'{tur}_{yil}.xlsx'
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=dosya_adi)
    else:
        dosya_adi = f'{tur}_{ay_adi}_{yil}.pdf' if ay else f'{tur}_{yil}.pdf'
        return send_file(output, mimetype='application/pdf',
                         as_attachment=True, download_name=dosya_adi)
```

- [ ] **Step 5: Implement templates/raporlar.html**

```html
{% extends "base.html" %}
{% block title %}Raporlar - Apartman Yonetimi{% endblock %}
{% block content %}
<h2 class="mb-4"><i class="bi bi-file-earmark-bar-graph"></i> Raporlar</h2>

<div class="row">
    <!-- Aylik Ozet -->
    <div class="col-md-6 mb-4">
        <div class="card bg-dark border-secondary h-100">
            <div class="card-header"><h5 class="mb-0"><i class="bi bi-graph-up"></i> Aylik Ozet Raporu</h5></div>
            <div class="card-body">
                <p class="text-muted">Gelir, gider, kasa durumu ve genel ozet.</p>
                <form class="row g-2 align-items-end">
                    <input type="hidden" name="tur" value="aylik_ozet">
                    <div class="col-auto">
                        <select name="ay" class="form-select form-select-sm">
                            {% for a in range(1, 13) %}
                            <option value="{{ a }}" {% if a == ay %}selected{% endif %}>{{ ay_isimleri[a] }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-auto">
                        <select name="yil" class="form-select form-select-sm">
                            {% for y in range(2024, 2031) %}
                            <option value="{{ y }}" {% if y == yil %}selected{% endif %}>{{ y }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-auto">
                        <a class="btn btn-sm btn-success" onclick="window.location.href='{{ url_for('raporlar.olustur') }}?tur=aylik_ozet&format=excel&yil=' + this.closest('form').yil.value + '&ay=' + this.closest('form').ay.value">
                            <i class="bi bi-file-earmark-excel"></i> Excel
                        </a>
                    </div>
                    <div class="col-auto">
                        <a class="btn btn-sm btn-danger" onclick="window.location.href='{{ url_for('raporlar.olustur') }}?tur=aylik_ozet&format=pdf&yil=' + this.closest('form').yil.value + '&ay=' + this.closest('form').ay.value">
                            <i class="bi bi-file-earmark-pdf"></i> PDF
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Odeme Durumu -->
    <div class="col-md-6 mb-4">
        <div class="card bg-dark border-secondary h-100">
            <div class="card-header"><h5 class="mb-0"><i class="bi bi-people"></i> Odeme Durumu Raporu</h5></div>
            <div class="card-body">
                <p class="text-muted">Daire bazli odeme durumu ve tahsilat orani.</p>
                <form class="row g-2 align-items-end">
                    <input type="hidden" name="tur" value="odeme_durumu">
                    <div class="col-auto">
                        <select name="ay" class="form-select form-select-sm">
                            {% for a in range(1, 13) %}
                            <option value="{{ a }}" {% if a == ay %}selected{% endif %}>{{ ay_isimleri[a] }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-auto">
                        <select name="yil" class="form-select form-select-sm">
                            {% for y in range(2024, 2031) %}
                            <option value="{{ y }}" {% if y == yil %}selected{% endif %}>{{ y }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-auto">
                        <a class="btn btn-sm btn-success" onclick="window.location.href='{{ url_for('raporlar.olustur') }}?tur=odeme_durumu&format=excel&yil=' + this.closest('form').yil.value + '&ay=' + this.closest('form').ay.value">
                            <i class="bi bi-file-earmark-excel"></i> Excel
                        </a>
                    </div>
                    <div class="col-auto">
                        <a class="btn btn-sm btn-danger" onclick="window.location.href='{{ url_for('raporlar.olustur') }}?tur=odeme_durumu&format=pdf&yil=' + this.closest('form').yil.value + '&ay=' + this.closest('form').ay.value">
                            <i class="bi bi-file-earmark-pdf"></i> PDF
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Gider Detay -->
    <div class="col-md-6 mb-4">
        <div class="card bg-dark border-secondary h-100">
            <div class="card-header"><h5 class="mb-0"><i class="bi bi-receipt"></i> Gider Detay Raporu</h5></div>
            <div class="card-body">
                <p class="text-muted">Kalem bazli gider dagilimi ve oranlar.</p>
                <form class="row g-2 align-items-end">
                    <input type="hidden" name="tur" value="gider_detay">
                    <div class="col-auto">
                        <select name="ay" class="form-select form-select-sm">
                            {% for a in range(1, 13) %}
                            <option value="{{ a }}" {% if a == ay %}selected{% endif %}>{{ ay_isimleri[a] }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-auto">
                        <select name="yil" class="form-select form-select-sm">
                            {% for y in range(2024, 2031) %}
                            <option value="{{ y }}" {% if y == yil %}selected{% endif %}>{{ y }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-auto">
                        <a class="btn btn-sm btn-success" onclick="window.location.href='{{ url_for('raporlar.olustur') }}?tur=gider_detay&format=excel&yil=' + this.closest('form').yil.value + '&ay=' + this.closest('form').ay.value">
                            <i class="bi bi-file-earmark-excel"></i> Excel
                        </a>
                    </div>
                    <div class="col-auto">
                        <a class="btn btn-sm btn-danger" onclick="window.location.href='{{ url_for('raporlar.olustur') }}?tur=gider_detay&format=pdf&yil=' + this.closest('form').yil.value + '&ay=' + this.closest('form').ay.value">
                            <i class="bi bi-file-earmark-pdf"></i> PDF
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Yillik Ozet -->
    <div class="col-md-6 mb-4">
        <div class="card bg-dark border-secondary h-100">
            <div class="card-header"><h5 class="mb-0"><i class="bi bi-calendar-range"></i> Yillik Ozet Raporu</h5></div>
            <div class="card-body">
                <p class="text-muted">Tum yilin aylik gelir-gider-kasa ozeti.</p>
                <form class="row g-2 align-items-end">
                    <input type="hidden" name="tur" value="yillik_ozet">
                    <div class="col-auto">
                        <select name="yil" class="form-select form-select-sm">
                            {% for y in range(2024, 2031) %}
                            <option value="{{ y }}" {% if y == yil %}selected{% endif %}>{{ y }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-auto">
                        <a class="btn btn-sm btn-success" onclick="window.location.href='{{ url_for('raporlar.olustur') }}?tur=yillik_ozet&format=excel&yil=' + this.closest('form').yil.value">
                            <i class="bi bi-file-earmark-excel"></i> Excel
                        </a>
                    </div>
                    <div class="col-auto">
                        <a class="btn btn-sm btn-danger" onclick="window.location.href='{{ url_for('raporlar.olustur') }}?tur=yillik_ozet&format=pdf&yil=' + this.closest('form').yil.value">
                            <i class="bi bi-file-earmark-pdf"></i> PDF
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Run tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_raporlar.py -v`
Expected: All 6 tests PASS

- [ ] **Step 7: Commit**

```bash
git add services/rapor_servisi.py routes/raporlar.py templates/raporlar.html tests/test_raporlar.py
git commit -m "feat: raporlama sistemi - 4 rapor turu, Excel ve PDF format secimi"
```

---

### Task 10: Mail Bildirim Sistemi

**Files:**
- Create: `services/mail_servisi.py`
- Modify: `app.py` (before_request hook)
- Modify: `routes/ayarlar.py` (test mail endpoint)
- Create: `tests/test_mail.py`

- [ ] **Step 1: Write tests in tests/test_mail.py**

```python
from unittest.mock import patch, MagicMock
from models import Bildirim, Ayar
from database import db as _db


def test_bildirim_kaydi_olustur(db_session):
    b = Bildirim(yil=2026, ay=4, gonderildi=True)
    _db.session.add(b)
    _db.session.commit()
    assert Bildirim.query.filter_by(yil=2026, ay=4).first().gonderildi is True


def test_mail_kontrol_ilk_pazartesi(app):
    """Mail kontrolu sadece ayin ilk pazartesi calisir."""
    from services.mail_servisi import ilk_pazartesi_mi
    from datetime import date
    # 2026-04-06 Pazartesi (ilk hafta)
    assert ilk_pazartesi_mi(date(2026, 4, 6)) is True
    # 2026-04-13 Pazartesi (ikinci hafta)
    assert ilk_pazartesi_mi(date(2026, 4, 13)) is False
    # 2026-04-07 Sali
    assert ilk_pazartesi_mi(date(2026, 4, 7)) is False


@patch('services.mail_servisi.smtplib')
def test_mail_gonder(mock_smtp, db_session):
    Ayar.kaydet('mail_adresi', 'test@test.com')
    Ayar.kaydet('smtp_sunucu', 'smtp.test.com')
    Ayar.kaydet('smtp_port', '587')
    Ayar.kaydet('smtp_sifre', 'sifre123')

    from services.mail_servisi import mail_gonder
    mock_server = MagicMock()
    mock_smtp.SMTP.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.SMTP.return_value.__exit__ = MagicMock(return_value=False)

    sonuc = mail_gonder('Test Konu', 'Test icerik')
    assert sonuc is True


def test_test_mail_endpoint(client, db_session):
    Ayar.kaydet('mail_adresi', 'test@test.com')
    Ayar.kaydet('smtp_sifre', 'test')
    with patch('services.mail_servisi.mail_gonder', return_value=True):
        response = client.post('/ayarlar/test-mail', follow_redirects=True)
        assert response.status_code == 200
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_mail.py -v`
Expected: FAIL

- [ ] **Step 3: Implement services/mail_servisi.py**

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime
from models import Ayar, Bildirim, Odeme, Daire
from database import db


def ilk_pazartesi_mi(tarih=None):
    """Verilen tarih ayin ilk pazartesi gunu mu?"""
    if tarih is None:
        tarih = date.today()
    # Pazartesi = 0 (weekday), ve gun <= 7 (ilk hafta)
    return tarih.weekday() == 0 and tarih.day <= 7


def mail_gonder(konu, icerik):
    """SMTP ile mail gonder."""
    mail_adresi = Ayar.getir('mail_adresi')
    smtp_sunucu = Ayar.getir('smtp_sunucu', 'smtp.gmail.com')
    smtp_port = int(Ayar.getir('smtp_port', '587'))
    smtp_sifre = Ayar.getir('smtp_sifre')

    if not mail_adresi or not smtp_sifre:
        return False

    mesaj = MIMEMultipart()
    mesaj['From'] = mail_adresi
    mesaj['To'] = mail_adresi
    mesaj['Subject'] = konu
    mesaj.attach(MIMEText(icerik, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP(smtp_sunucu, smtp_port) as server:
            server.starttls()
            server.login(mail_adresi, smtp_sifre)
            server.send_message(mesaj)
        return True
    except Exception:
        return False


def aidat_hatirlatma_kontrol():
    """Her ayin ilk pazartesi, bildirim gonderilmediyse mail at."""
    bugun = date.today()
    if not ilk_pazartesi_mi(bugun):
        return

    yil, ay = bugun.year, bugun.month

    # Bu ay zaten gonderildi mi?
    bildirim = Bildirim.query.filter_by(yil=yil, ay=ay).first()
    if bildirim and bildirim.gonderildi:
        return

    # Odemeyenleri say
    toplam_daire = Daire.query.count()
    odenen = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    odenmeyen = toplam_daire - odenen

    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    konu = f'{apartman_adi} - Aidat Hatirlatmasi'
    icerik = (
        f'Aidat toplama zamani geldi!\n\n'
        f'Toplam daire: {toplam_daire}\n'
        f'Odenen: {odenen}\n'
        f'Odenmeyen: {odenmeyen}\n\n'
        f'Uygulamayi acarak detaylari gorebilirsiniz.'
    )

    sonuc = mail_gonder(konu, icerik)

    if bildirim is None:
        bildirim = Bildirim(yil=yil, ay=ay)
        db.session.add(bildirim)
    bildirim.gonderildi = sonuc
    if sonuc:
        bildirim.gonderim_tarihi = datetime.now()
    db.session.commit()
```

- [ ] **Step 4: Add test-mail endpoint to routes/ayarlar.py**

Append to `routes/ayarlar.py`:

```python
@bp.route('/test-mail', methods=['POST'])
def test_mail():
    from services.mail_servisi import mail_gonder
    sonuc = mail_gonder('Test Mail - Apartman Yonetimi', 'Bu bir test mailidir. Mail ayarlariniz dogru calisiyor.')
    if sonuc:
        flash('Test maili basariyla gonderildi!', 'success')
    else:
        flash('Mail gonderilemedi. SMTP ayarlarinizi kontrol edin.', 'danger')
    return redirect(url_for('ayarlar.index'))
```

Also add a test mail button to `templates/ayarlar.html` inside the Genel Ayarlar card, after the Kaydet button:

```html
            <button type="submit" class="btn btn-primary mt-3">Kaydet</button>
        </form>
        <form method="POST" action="{{ url_for('ayarlar.test_mail') }}" class="mt-2">
            <button type="submit" class="btn btn-outline-info btn-sm">
                <i class="bi bi-envelope"></i> Test Mail Gonder
            </button>
        </form>
```

- [ ] **Step 5: Add before_request hook to app.py**

Update `create_app()` in `app.py` — add after `init_db(app)`:

```python
    @app.before_request
    def mail_kontrol():
        try:
            from services.mail_servisi import aidat_hatirlatma_kontrol
            aidat_hatirlatma_kontrol()
        except Exception:
            pass  # Mail hatasi uygulamayi durdurmasin
```

- [ ] **Step 6: Run tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/test_mail.py -v`
Expected: All 4 tests PASS

- [ ] **Step 7: Run ALL tests**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add services/mail_servisi.py routes/ayarlar.py templates/ayarlar.html app.py tests/test_mail.py
git commit -m "feat: mail bildirim sistemi - aidat hatirlatma, test mail, SMTP ayarlari"
```

---

### Task 11: Final Integration and Cleanup

**Files:**
- Create: `templates/parcalar/gider_tablo.html` (remove placeholder if needed)
- Verify: all routes, templates, static files work together

- [ ] **Step 1: Create .gitignore**

```
venv/
__pycache__/
*.pyc
*.db
raporlar/*.xlsx
raporlar/*.pdf
.pytest_cache/
```

- [ ] **Step 2: Create raporlar/.gitkeep**

```
```

- [ ] **Step 3: Run the full application manually**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && timeout 5 python app.py 2>&1 || true`
Expected: `Running on http://127.0.0.1:5000` — no import errors, no crashes.

- [ ] **Step 4: Run all tests one final time**

Run: `cd /home/enes/Desktop/apartman && source venv/bin/activate && python -m pytest tests/ -v --tb=short`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .gitignore raporlar/.gitkeep
git commit -m "chore: gitignore ve proje yapilandirmasi tamamlandi"
```
