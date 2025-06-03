from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import datetime
import os
from werkzeug.utils import secure_filename
import uuid

from src import db
from src.models.models import User, Analysis, ROLE_ADMIN

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            user.update_last_login()
            return redirect(url_for('main.dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # التحقق من وجود المستخدم
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل', 'danger')
            return render_template('register.html')
        
        # إنشاء مستخدم جديد
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # الحصول على تحليلات المستخدم
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).limit(5).all()
    
    # الحصول على عدد التحليلات
    analyses_count = Analysis.query.filter_by(user_id=current_user.id).count()
    
    # الحصول على عدد التحليلات الجديدة اليوم
    today = datetime.datetime.now().date()
    recent_analyses_count = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.created_at >= datetime.datetime.combine(today, datetime.time.min)
    ).count()
    
    # الحصول على قائمة المستخدمين للمسؤول
    users = []
    if current_user.role == ROLE_ADMIN:
        users = User.query.all()
    
    return render_template('dashboard.html', 
                          analyses=analyses, 
                          analyses_count=analyses_count,
                          recent_analyses_count=recent_analyses_count,
                          users=users,
                          current_date=datetime.datetime.now().strftime('%Y-%m-%d'))

@main_bp.route('/analyze_chart', methods=['GET', 'POST'])
@login_required
def analyze_chart():
    if request.method == 'POST':
        # التحقق من وجود ملف
        if 'chart_image' not in request.files:
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        file = request.files['chart_image']
        
        # التحقق من أن الملف ليس فارغاً
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        # التحقق من أن الملف هو صورة
        if file and allowed_file(file.filename):
            # إنشاء اسم ملف آمن
            filename = secure_filename(file.filename)
            # إضافة معرف فريد لتجنب تكرار أسماء الملفات
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # التأكد من وجود مجلد التحميل
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            # حفظ الملف
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # الحصول على معلومات التحليل
            chart_type = request.form.get('chart_type', 'forex')
            timeframe = request.form.get('timeframe', 'D1')
            
            # إنشاء تحليل جديد
            analysis = Analysis(
                user_id=current_user.id,
                image_path=f"uploads/{unique_filename}",
                chart_type=chart_type,
                timeframe=timeframe,
                analysis_result="تم تحليل الشارت بنجاح",
                entry_point=100.0,  # قيم افتراضية للتوضيح
                take_profit=110.0,
                stop_loss=95.0,
                risk_reward_ratio=1.5,
                confidence=85
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            # توجيه المستخدم إلى صفحة نتائج التحليل
            return redirect(url_for('main.analysis_result', analysis_id=analysis.id))
    
    return render_template('analyze.html')

@main_bp.route('/analysis_result/<int:analysis_id>')
@login_required
def analysis_result(analysis_id):
    # الحصول على التحليل
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # التحقق من أن التحليل ينتمي للمستخدم الحالي
    if analysis.user_id != current_user.id and current_user.role != ROLE_ADMIN:
        flash('غير مصرح لك بالوصول إلى هذا التحليل', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # بيانات التحليل (يمكن استبدالها بنتائج تحليل حقيقية)
    data = {
        'trend': 'صاعد',
        'strength': 'قوي',
        'entry_point': analysis.entry_point,
        'take_profit': analysis.take_profit,
        'stop_loss': analysis.stop_loss,
        'risk_reward_ratio': analysis.risk_reward_ratio,
        'confidence': analysis.confidence,
        'recommendation': 'شراء',
        'support_levels': [95.0, 92.5, 90.0],
        'resistance_levels': [105.0, 110.0, 115.0],
        'analysis_text': """
        تحليل الشارت يظهر اتجاهاً صاعداً قوياً مع تأكيدات متعددة من مؤشرات فنية مختلفة.
        السعر تجاوز المتوسط المتحرك 50 و 200 يوم، مما يشير إلى قوة الاتجاه الصاعد.
        تم تحديد مناطق العرض والطلب وفق استراتيجية SMC، مع وجود 30 تأكيداً لدخول الصفقة.
        نقطة الدخول المقترحة هي عند مستوى الدعم الأخير بعد الارتداد.
        يجب وضع وقف الخسارة تحت مستوى الدعم الرئيسي لتقليل المخاطر.
        هدف جني الأرباح تم تحديده عند مستوى المقاومة التاريخي.
        نسبة المخاطرة إلى المكافأة 1:3 تجعل هذه الصفقة جذابة من منظور إدارة المخاطر.
        """
    }
    
    return render_template('analysis_result.html', analysis=analysis, data=data)

@main_bp.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@main_bp.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    message = request.json.get('message', '')
    
    # هنا يمكن إضافة منطق معالجة الرسائل باستخدام OpenAI API
    # للتبسيط، سنستخدم ردوداً ثابتة
    
    responses = {
        'مرحبا': 'مرحباً بك! كيف يمكنني مساعدتك في تحليل السوق اليوم؟',
        'كيف حالك': 'أنا بخير، جاهز لمساعدتك في تحليل الشارت وتقديم توصيات التداول.',
        'ما هو أفضل سهم للشراء': 'لا يمكنني تقديم توصيات مالية محددة، ولكن يمكنني مساعدتك في تحليل أي شارت ترغب فيه.',
        'كيف أحلل الشارت': 'لتحليل الشارت، يمكنك تحميل صورة الشارت في صفحة "تحليل الشارت" وسأقوم بتحليلها وتحديد نقاط الدخول والخروج.',
        'ما هي استراتيجية SMC': 'استراتيجية SMC (Smart Money Concepts) هي استراتيجية تداول تركز على تحديد مناطق العرض والطلب التي يتفاعل معها المتداولون المؤسسيون (Smart Money).',
        'كيف أحدد نقطة الدخول': 'لتحديد نقطة الدخول المثالية، يجب البحث عن تأكيدات متعددة مثل: نمط انعكاس، تقاطع المتوسطات المتحركة، مستويات فيبوناتشي، ومناطق العرض والطلب.',
        'ما هي نسبة المخاطرة المثالية': 'نسبة المخاطرة إلى المكافأة المثالية هي 1:3 على الأقل، مما يعني أن المكافأة المحتملة يجب أن تكون 3 أضعاف المخاطرة المحتملة.',
        'كيف أضع وقف الخسارة': 'يجب وضع وقف الخسارة تحت مستوى الدعم الأخير في الاتجاه الصاعد، أو فوق مستوى المقاومة الأخير في الاتجاه الهابط.'
    }
    
    # البحث عن كلمات مفتاحية في الرسالة
    response = 'لم أفهم سؤالك. هل يمكنك إعادة صياغته؟'
    for key, value in responses.items():
        if key in message.lower():
            response = value
            break
    
    # إذا لم يتم العثور على كلمات مفتاحية، استخدم رداً عاماً
    if response == 'لم أفهم سؤالك. هل يمكنك إعادة صياغته؟':
        response = 'شكراً لسؤالك. يمكنني مساعدتك في تحليل الشارت وتحديد نقاط الدخول والخروج وفق استراتيجية SMC. هل ترغب في تحميل شارت للتحليل؟'
    
    return jsonify({'response': response})

@main_bp.route('/trading_plan')
@login_required
def trading_plan():
    return render_template('trading_plan.html')

def allowed_file(filename):
    """التحقق من أن امتداد الملف مسموح به"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
