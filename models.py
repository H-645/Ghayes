from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

# تعريف ثوابت الأدوار
ROLE_USER = 0
ROLE_ADMIN = 1

# إنشاء كائن قاعدة البيانات
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """نموذج المستخدم"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Integer, default=ROLE_USER)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    invited_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # العلاقات
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic')
    invited_users = db.relationship('User', backref=db.backref('inviter', remote_side=[id]), lazy='dynamic')
    
    def set_password(self, password):
        """تعيين كلمة المرور المشفرة"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """تحديث وقت آخر تسجيل دخول"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        """التحقق مما إذا كان المستخدم مسؤولاً"""
        return self.role == ROLE_ADMIN
    
    def __repr__(self):
        return f'<User {self.username}>'

class Analysis(db.Model):
    """نموذج تحليل الشارت"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    chart_type = db.Column(db.String(50), nullable=False)  # forex, stocks, crypto, etc.
    timeframe = db.Column(db.String(10), nullable=False)  # M1, M5, M15, H1, D1, etc.
    analysis_result = db.Column(db.Text)
    entry_point = db.Column(db.Float)
    take_profit = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    risk_reward_ratio = db.Column(db.Float)
    confidence = db.Column(db.Integer)  # 0-100%
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Analysis {self.id} by User {self.user_id}>'

class Invitation(db.Model):
    """نموذج دعوات المستخدمين"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Invitation {self.email}>'

class SystemSettings(db.Model):
    """نموذج إعدادات النظام"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.key}>'

class ActivityLog(db.Model):
    """نموذج سجل النشاطات"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ActivityLog {self.id} by User {self.user_id}>'
