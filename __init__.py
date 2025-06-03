from flask_sqlalchemy import SQLAlchemy

# إنشاء كائن قاعدة البيانات المركزي
db = SQLAlchemy()

def create_app():
    from flask import Flask
    from src.models.models import User, Analysis, Invitation, SystemSettings, ActivityLog
    from src.routes.admin import admin_bp
    from src.routes.market_api import market_bp
    import os
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chicha_ai_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chicha_ai.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')

    # تهيئة قاعدة البيانات مع التطبيق
    db.init_app(app)

    # تهيئة نظام تسجيل الدخول
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # تسجيل المسارات
    app.register_blueprint(admin_bp)
    app.register_blueprint(market_bp)

    # تسجيل المسارات الرئيسية
    from src.routes.main import main_bp
    app.register_blueprint(main_bp)

    # إنشاء الجداول وحساب المسؤول
    with app.app_context():
        db.create_all()
        
        # إنشاء مستخدم المسؤول إذا لم يكن موجوداً
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@chicha.ai',
                role=1,  # ROLE_ADMIN
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    return app
