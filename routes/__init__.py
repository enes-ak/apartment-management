def register_blueprints(app):
    from routes.dashboard import bp as dashboard_bp
    from routes.payments import bp as payments_bp
    from routes.expenses import bp as expenses_bp
    from routes.cash_register import bp as cash_register_bp
    from routes.messages import bp as messages_bp
    from routes.reports import bp as reports_bp
    from routes.notes import bp as notes_bp
    from routes.directory import bp as directory_bp
    from routes.settings import bp as settings_bp
    from routes.logs import bp as logs_bp
    from routes.extra_collections import bp as extra_collections_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(extra_collections_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(cash_register_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(directory_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(logs_bp)
