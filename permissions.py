import os
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

# تعريف مستويات الصلاحيات
ROLE_USER = 0
ROLE_ADMIN = 1

def admin_required(f):
    """
    مزخرف للتحقق من أن المستخدم الحالي هو المسؤول
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_api_key():
    """
    الحصول على مفتاح API من ملف البيئة
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        # قراءة المفتاح من ملف .env إذا كان موجوداً
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.strip().split('=', 1)[1].strip('"\'')
                        break
    return api_key

def set_api_key(api_key):
    """
    حفظ مفتاح API في ملف البيئة
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    # قراءة الملف الحالي إذا كان موجوداً
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # تحديث أو إضافة مفتاح API
    env_vars['OPENAI_API_KEY'] = f'"{api_key}"'
    
    # كتابة الملف
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    # تحديث المتغير البيئي للجلسة الحالية
    os.environ['OPENAI_API_KEY'] = api_key
    
    return True
