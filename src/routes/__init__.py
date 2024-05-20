from .main import main_bp
from .auth import auth_bp
from .docente import docente_bp
from .jefe import jefe_bp
from .admin import admin_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(docente_bp)
    app.register_blueprint(jefe_bp)
