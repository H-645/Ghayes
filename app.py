import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime
import json
import requests
import openai

# تكوين المفتاح الخاص بـ OpenAI
# يجب إضافة مفتاح OpenAI API كمتغير بيئة OPENAI_API_KEY في إعدادات الاستضافة
openai.api_key = os.environ.get('OPENAI_API_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chicha_ai_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///chicha_ai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')

# التأكد من وجود مجلد التحميلات
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# إعداد قاعدة البيانات
db = SQLAlchemy(app)

# إعداد نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# نموذج المستخدم
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# نموذج تحليل الشارت
class ChartAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    analysis_result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('analyses', lazy=True))

# نموذج المحادثة
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

# نموذج الصفقات
class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, nullable=False)
    take_profit = db.Column(db.Float, nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # "buy" or "sell"
    timeframe = db.Column(db.String(10), nullable=False)
    success_probability = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="open")  # "open", "closed", "cancelled"
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('trades', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render_template('login.html')

# صفحة التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # التحقق من عدم وجود مستخدم بنفس اسم المستخدم أو البريد الإلكتروني
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل')
            return redirect(url_for('register'))
        
        # إنشاء مستخدم جديد
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=(User.query.count() == 0)  # أول مستخدم يكون مسؤول
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# تسجيل الخروج
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# لوحة التحكم
@app.route('/dashboard')
@login_required
def dashboard():
    # الحصول على آخر 5 تحليلات للمستخدم
    recent_analyses = ChartAnalysis.query.filter_by(user_id=current_user.id).order_by(ChartAnalysis.created_at.desc()).limit(5).all()
    
    # الحصول على آخر 5 صفقات للمستخدم
    recent_trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.created_at.desc()).limit(5).all()
    
    # بيانات السوق الحية (محاكاة)
    market_data = {
        'EURUSD': 1.0923,
        'GBPUSD': 1.2745,
        'USDJPY': 107.82,
        'XAUUSD': 1912.45,
        'BTC/USD': 37245.67
    }
    
    return render_template('dashboard.html', 
                          recent_analyses=recent_analyses, 
                          recent_trades=recent_trades, 
                          market_data=market_data)

# صفحة تحليل الشارت
@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    if request.method == 'POST':
        # التحقق من وجود ملف
        if 'chart_image' not in request.files:
            flash('لم يتم تحديد ملف')
            return redirect(request.url)
        
        file = request.files['chart_image']
        
        # التحقق من أن الملف ليس فارغاً
        if file.filename == '':
            flash('لم يتم تحديد ملف')
            return redirect(request.url)
        
        # التحقق من أن الملف هو صورة
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # تحليل الشارت
            analysis_result = analyze_chart(file_path)
            
            # حفظ التحليل في قاعدة البيانات
            new_analysis = ChartAnalysis(
                user_id=current_user.id,
                image_path=os.path.join('uploads', filename),
                analysis_result=analysis_result
            )
            
            db.session.add(new_analysis)
            db.session.commit()
            
            return redirect(url_for('analysis_result', analysis_id=new_analysis.id))
    
    return render_template('analyze.html')

# صفحة نتيجة التحليل
@app.route('/analysis_result/<int:analysis_id>')
@login_required
def analysis_result(analysis_id):
    analysis = ChartAnalysis.query.get_or_404(analysis_id)
    
    # التحقق من أن التحليل ينتمي للمستخدم الحالي أو أن المستخدم مسؤول
    if analysis.user_id != current_user.id and not current_user.is_admin:
        flash('غير مصرح لك بعرض هذا التحليل')
        return redirect(url_for('dashboard'))
    
    return render_template('analysis_result.html', analysis=analysis)

# صفحة المحادثة
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        message = request.form.get('message')
        
        # الحصول على رد من OpenAI
        response = get_ai_response(message)
        
        # حفظ المحادثة في قاعدة البيانات
        new_message = ChatMessage(
            user_id=current_user.id,
            message=message,
            response=response
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            'message': message,
            'response': response,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # الحصول على آخر 10 محادثات للمستخدم
    chat_history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at.desc()).limit(10).all()
    chat_history.reverse()  # عكس الترتيب ليكون من الأقدم للأحدث
    
    return render_template('chat.html', chat_history=chat_history)

# صفحة السوق الحي
@app.route('/market/live')
@login_required
def market_live():
    # بيانات السوق الحية (محاكاة)
    market_data = {
        'forex': {
            'EURUSD': {'price': 1.0923, 'change': 0.0015},
            'GBPUSD': {'price': 1.2745, 'change': -0.0023},
            'USDJPY': {'price': 107.82, 'change': 0.45},
            'AUDUSD': {'price': 0.6832, 'change': 0.0012},
            'USDCAD': {'price': 1.3245, 'change': -0.0018}
        },
        'commodities': {
            'XAUUSD': {'price': 1912.45, 'change': 7.25},
            'XAGUSD': {'price': 24.32, 'change': 0.18},
            'OIL': {'price': 72.45, 'change': -1.23},
            'NATGAS': {'price': 2.845, 'change': 0.032}
        },
        'crypto': {
            'BTC/USD': {'price': 37245.67, 'change': 1243.25},
            'ETH/USD': {'price': 2187.34, 'change': 87.45},
            'XRP/USD': {'price': 0.5423, 'change': -0.0123}
        },
        'indices': {
            'US30': {'price': 34567.89, 'change': 234.56},
            'SPX500': {'price': 4567.89, 'change': 23.45},
            'NASDAQ': {'price': 15678.90, 'change': 123.45}
        }
    }
    
    return render_template('market/live.html', market_data=market_data)

# API للحصول على بيانات السوق
@app.route('/api/market_data')
@login_required
def api_market_data():
    symbol = request.args.get('symbol', 'EURUSD')
    timeframe = request.args.get('timeframe', '1h')
    
    # محاكاة بيانات السوق
    data = generate_mock_market_data(symbol, timeframe)
    
    return jsonify(data)

# صفحة إدارة المستخدمين (للمسؤولين فقط)
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# إضافة/حذف مستخدم (للمسؤولين فقط)
@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # لا يمكن حذف المستخدم نفسه
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('تم حذف المستخدم بنجاح')
    return redirect(url_for('admin_users'))

# وظائف مساعدة

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_chart(image_path):
    # محاكاة تحليل الشارت
    analysis = {
        'trend': 'صاعد',
        'support_levels': [1.0850, 1.0800, 1.0750],
        'resistance_levels': [1.0950, 1.1000, 1.1050],
        'entry_point': 1.0923,
        'stop_loss': 1.0880,
        'take_profit': 1.0980,
        'risk_reward_ratio': '1:3',
        'success_probability': 85,
        'timeframe': '1 ساعة',
        'indicators': {
            'rsi': 62,
            'macd': 'إيجابي',
            'moving_averages': 'فوق المتوسط المتحرك 200'
        },
        'analysis_text': '''
        تحليل الشارت يظهر اتجاه صاعد قوي مع وجود نمط مثلث صاعد.
        المؤشرات الفنية تدعم الاتجاه الصاعد، مع RSI في منطقة قوة معتدلة (62) وإشارة إيجابية من MACD.
        السعر يتداول فوق المتوسط المتحرك 200، مما يؤكد الاتجاه الصاعد على المدى المتوسط.
        
        نقطة الدخول المقترحة هي 1.0923 مع وقف خسارة عند 1.0880 وهدف ربح عند 1.0980.
        نسبة المخاطرة إلى المكافأة هي 1:3، مما يجعلها صفقة جذابة.
        
        احتمالية نجاح الصفقة تقدر بـ 85% بناءً على تحليل 30 تأكيداً فنياً.
        
        ملاحظات إضافية:
        - مستويات الدعم الرئيسية: 1.0850، 1.0800، 1.0750
        - مستويات المقاومة الرئيسية: 1.0950، 1.1000، 1.1050
        - يفضل متابعة الأخبار الاقتصادية التي قد تؤثر على الزوج
        '''
    }
    
    return json.dumps(analysis)

def get_ai_response(message):
    try:
        # استخدام OpenAI للحصول على رد
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد تداول محترف يقدم تحليلات وإجابات دقيقة حول الأسواق المالية والتحليل الفني."},
                {"role": "user", "content": message}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        # في حالة حدوث خطأ، إرجاع رد افتراضي
        print(f"OpenAI API error: {e}")
        return "عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى لاحقاً."

def generate_mock_market_data(symbol, timeframe):
    # محاكاة بيانات السوق
    import random
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    
    if timeframe == '1m':
        start_date = end_date - timedelta(hours=1)
        interval = timedelta(minutes=1)
    elif timeframe == '5m':
        start_date = end_date - timedelta(hours=5)
        interval = timedelta(minutes=5)
    elif timeframe == '15m':
        start_date = end_date - timedelta(hours=15)
        interval = timedelta(minutes=15)
    elif timeframe == '1h':
        start_date = end_date - timedelta(days=2)
        interval = timedelta(hours=1)
    elif timeframe == '4h':
        start_date = end_date - timedelta(days=8)
        interval = timedelta(hours=4)
    elif timeframe == '1d':
        start_date = end_date - timedelta(days=30)
        interval = timedelta(days=1)
    else:
        start_date = end_date - timedelta(days=2)
        interval = timedelta(hours=1)
    
    # قيم أولية حسب الرمز
    if symbol == 'EURUSD':
        base_price = 1.09
        volatility = 0.0005
    elif symbol == 'GBPUSD':
        base_price = 1.27
        volatility = 0.0007
    elif symbol == 'USDJPY':
        base_price = 107.8
        volatility = 0.05
    elif symbol == 'XAUUSD':
        base_price = 1912.0
        volatility = 1.5
    elif symbol == 'BTC/USD':
        base_price = 37000.0
        volatility = 500.0
    else:
        base_price = 100.0
        volatility = 1.0
    
    data = []
    current_date = start_date
    current_price = base_price
    
    while current_date <= end_date:
        open_price = current_price
        high_price = open_price + random.uniform(0, volatility * 2)
        low_price = open_price - random.uniform(0, volatility * 2)
        close_price = random.uniform(low_price, high_price)
        volume = random.randint(1000, 10000)
        
        data.append({
            'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
            'open': round(open_price, 5),
            'high': round(high_price, 5),
            'low': round(low_price, 5),
            'close': round(close_price, 5),
            'volume': volume
        })
        
        current_date += interval
        current_price = close_price
    
    return data

# إنشاء قاعدة البيانات وإضافة مستخدم مسؤول افتراضي
@app.before_first_request
def create_tables_and_admin():
    db.create_all()
    
    # التحقق من وجود مستخدم مسؤول
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='aokalmohamad81@gmail.com',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
