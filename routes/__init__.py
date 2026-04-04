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
