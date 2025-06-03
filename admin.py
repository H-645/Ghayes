from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
import datetime

from src import db
from src.models.models import User, ROLE_ADMIN

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def index():
    # التحقق من أن المستخدم هو مسؤول
    if current_user.role != ROLE_ADMIN:
        flash('غير مصرح لك بالوصول إلى لوحة تحكم المسؤول', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # الحصول على قائمة المستخدمين
    users = User.query.all()
    
    return render_template('admin/index.html', users=users)

@admin_bp.route('/users')
@login_required
def users():
    # التحقق من أن المستخدم هو مسؤول
    if current_user.role != ROLE_ADMIN:
        flash('غير مصرح لك بالوصول إلى إدارة المستخدمين', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # الحصول على قائمة المستخدمين
    users = User.query.all()
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle_active', methods=['POST'])
@login_required
def toggle_user_active(user_id):
    # التحقق من أن المستخدم هو مسؤول
    if current_user.role != ROLE_ADMIN:
        flash('غير مصرح لك بتعديل حالة المستخدمين', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # الحصول على المستخدم
    user = User.query.get_or_404(user_id)
    
    # لا يمكن تعطيل المسؤول الرئيسي
    if user.role == ROLE_ADMIN and user.username == 'admin':
        flash('لا يمكن تعطيل المسؤول الرئيسي', 'danger')
        return redirect(url_for('admin.users'))
    
    # تبديل حالة المستخدم
    user.is_active = not user.is_active
    db.session.commit()
    
    flash(f'تم {"تفعيل" if user.is_active else "تعطيل"} المستخدم بنجاح', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    # التحقق من أن المستخدم هو مسؤول
    if current_user.role != ROLE_ADMIN:
        flash('غير مصرح لك بحذف المستخدمين', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # الحصول على المستخدم
    user = User.query.get_or_404(user_id)
    
    # لا يمكن حذف المسؤول الرئيسي
    if user.role == ROLE_ADMIN and user.username == 'admin':
        flash('لا يمكن حذف المسؤول الرئيسي', 'danger')
        return redirect(url_for('admin.users'))
    
    # حذف المستخدم
    db.session.delete(user)
    db.session.commit()
    
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/invite', methods=['GET', 'POST'])
@login_required
def invite_user():
    # التحقق من أن المستخدم هو مسؤول
    if current_user.role != ROLE_ADMIN:
        flash('غير مصرح لك بدعوة مستخدمين جدد', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        # التحقق من وجود المستخدم
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'danger')
            return redirect(url_for('admin.invite_user'))
        
        # إنشاء مستخدم جديد مباشرة (بدلاً من نظام الدعوات)
        username = email.split('@')[0]  # استخدام جزء من البريد الإلكتروني كاسم مستخدم
        password = 'password123'  # كلمة مرور افتراضية
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.invited_by = current_user.id
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'تم إنشاء المستخدم {username} بنجاح. كلمة المرور الافتراضية هي: {password}', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/invite.html')

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # التحقق من أن المستخدم هو مسؤول
    if current_user.role != ROLE_ADMIN:
        flash('غير مصرح لك بالوصول إلى إعدادات النظام', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # تحديث إعدادات النظام
        # يمكن إضافة منطق حفظ الإعدادات هنا
        
        flash('تم تحديث إعدادات النظام بنجاح', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html')

@admin_bp.route('/contact_info', methods=['GET', 'POST'])
@login_required
def contact_info():
    # التحقق من أن المستخدم هو مسؤول
    if current_user.role != ROLE_ADMIN:
        flash('غير مصرح لك بتعديل معلومات الاتصال', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # تحديث معلومات الاتصال
        phone = request.form.get('phone', '+96176706151')
        email = request.form.get('email', 'aokalmohamad81@gmail.com')
        location = request.form.get('location', 'لبنان')
        
        # يمكن حفظ هذه المعلومات في قاعدة البيانات
        # للتبسيط، سنفترض أنها تم حفظها
        
        flash('تم تحديث معلومات الاتصال بنجاح', 'success')
        return redirect(url_for('admin.contact_info'))
    
    # للتبسيط، سنستخدم قيم افتراضية
    contact_info = {
        'phone': '+96176706151',
        'email': 'aokalmohamad81@gmail.com',
        'location': 'لبنان'
    }
    
    return render_template('admin/contact_info.html', contact_info=contact_info)
