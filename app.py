import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask
from src.models.models import db
from src.routes.admin import admin_bp
from src.routes.market_api import market_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chicha_ai_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chicha_ai.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')

    # تهيئة قاعدة البيانات
    db.init_app(app)

    # تسجيل المسارات
    app.register_blueprint(admin_bp)
    app.register_blueprint(market_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
