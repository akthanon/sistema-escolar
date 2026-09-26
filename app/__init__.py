import os
from flask import Flask
from flask_login import LoginManager
from .models import db, User
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # ===== CONFIGURACIÓN DE SESIÓN PERMANENTE =====
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Sesión dura 30 días
    app.config['SESSION_PERMANENT'] = True  # Hace que la sesión sea permanente
    # =============================================
    
    # Ruta absoluta dentro del contenedor
    db_path = '/app/data/school.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Asegurar que el directorio /app/data existe y tiene permisos
    os.makedirs('/app/data', exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .attendance import attendance as attendance_blueprint
    app.register_blueprint(attendance_blueprint)

    from .tasks import tasks_bp
    app.register_blueprint(tasks_bp)

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin', first_name='Admin', last_name='System')
            admin.set_password('SuperPassword123')
            db.session.add(admin)
            db.session.commit()

    return app
