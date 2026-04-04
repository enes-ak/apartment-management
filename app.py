import os
from flask import Flask
from config import Config
from database import db, init_db


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or Config)

    db.init_app(app)

    # Rapor dizinini olustur
    os.makedirs(app.config['RAPORLAR_DIZINI'], exist_ok=True)

    init_db(app)

    from routes import register_blueprints
    register_blueprints(app)

    @app.before_request
    def mail_kontrol():
        try:
            from services.mail_servisi import aidat_hatirlatma_kontrol
            aidat_hatirlatma_kontrol()
        except Exception:
            pass  # Mail hatasi uygulamayi durdurmasin

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
