from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import requests
import json
import os

from src import db

market_bp = Blueprint('market', __name__, url_prefix='/market')

@market_bp.route('/live')
@login_required
def live_market():
    return render_template('market/live.html')

@market_bp.route('/api/symbols', methods=['GET'])
@login_required
def get_symbols():
    # في بيئة حقيقية، هذه البيانات ستأتي من API خارجي
    symbols = {
        'forex': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF'],
        'crypto': ['BTCUSD', 'ETHUSD', 'XRPUSD', 'LTCUSD', 'BCHUSD', 'ADAUSD', 'DOTUSD'],
        'stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA', 'NVDA'],
        'commodities': ['XAUUSD', 'XAGUSD', 'WTICOUSD', 'BRENTCOUSD', 'NATGASUSD']
    }
    
    return jsonify(symbols)

@market_bp.route('/api/price', methods=['GET'])
@login_required
def get_price():
    symbol = request.args.get('symbol', 'EURUSD')
    timeframe = request.args.get('timeframe', 'D1')
    
    # في بيئة حقيقية، هذه البيانات ستأتي من API خارجي
    # هنا نستخدم بيانات ثابتة للتوضيح
    
    # بيانات سعر افتراضية
    price_data = {
        'EURUSD': {
            'current': 1.1850,
            'open': 1.1830,
            'high': 1.1870,
            'low': 1.1810,
            'close': 1.1850,
            'change': 0.0020,
            'change_percent': 0.17
        },
        'BTCUSD': {
            'current': 45000.00,
            'open': 44500.00,
            'high': 45500.00,
            'low': 44000.00,
            'close': 45000.00,
            'change': 500.00,
            'change_percent': 1.12
        },
        'AAPL': {
            'current': 150.25,
            'open': 149.50,
            'high': 151.00,
            'low': 149.00,
            'close': 150.25,
            'change': 0.75,
            'change_percent': 0.50
        },
        'XAUUSD': {
            'current': 1850.50,
            'open': 1845.00,
            'high': 1855.00,
            'low': 1840.00,
            'close': 1850.50,
            'change': 5.50,
            'change_percent': 0.30
        }
    }
    
    # إذا كان الرمز غير موجود، استخدم EURUSD كافتراضي
    if symbol not in price_data:
        symbol = 'EURUSD'
    
    return jsonify({
        'symbol': symbol,
        'timeframe': timeframe,
        'data': price_data[symbol],
        'timestamp': datetime.datetime.now().isoformat()
    })

@market_bp.route('/api/chart_data', methods=['GET'])
@login_required
def get_chart_data():
    symbol = request.args.get('symbol', 'EURUSD')
    timeframe = request.args.get('timeframe', 'D1')
    limit = int(request.args.get('limit', 100))
    
    # في بيئة حقيقية، هذه البيانات ستأتي من API خارجي
    # هنا نستخدم بيانات ثابتة للتوضيح
    
    # إنشاء بيانات شارت افتراضية
    import numpy as np
    import datetime
    
    # تاريخ البداية (100 يوم قبل اليوم)
    start_date = datetime.datetime.now() - datetime.timedelta(days=limit)
    
    # إنشاء مصفوفة من التواريخ
    dates = [start_date + datetime.timedelta(days=i) for i in range(limit)]
    
    # إنشاء بيانات سعر افتراضية
    if symbol == 'EURUSD':
        base_price = 1.18
        volatility = 0.002
    elif symbol == 'BTCUSD':
        base_price = 45000
        volatility = 1000
    elif symbol == 'AAPL':
        base_price = 150
        volatility = 2
    elif symbol == 'XAUUSD':
        base_price = 1850
        volatility = 10
    else:
        base_price = 100
        volatility = 1
    
    # إنشاء بيانات OHLC افتراضية
    np.random.seed(42)  # للحصول على نفس البيانات في كل مرة
    
    data = []
    current_price = base_price
    
    for date in dates:
        # إنشاء تغير عشوائي
        change = np.random.normal(0, volatility)
        
        # حساب سعر الافتتاح والإغلاق
        open_price = current_price
        close_price = open_price + change
        
        # حساب السعر الأعلى والأدنى
        high_price = max(open_price, close_price) + abs(np.random.normal(0, volatility/2))
        low_price = min(open_price, close_price) - abs(np.random.normal(0, volatility/2))
        
        # إضافة البيانات
        data.append({
            'time': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 4),
            'high': round(high_price, 4),
            'low': round(low_price, 4),
            'close': round(close_price, 4),
            'volume': int(np.random.normal(1000, 200))
        })
        
        # تحديث السعر الحالي للفترة التالية
        current_price = close_price
    
    return jsonify({
        'symbol': symbol,
        'timeframe': timeframe,
        'data': data
    })

@market_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze_market():
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    timeframe = data.get('timeframe', 'D1')
    
    # في بيئة حقيقية، هنا سيتم تحليل البيانات باستخدام خوارزميات متقدمة
    # هنا نستخدم تحليل افتراضي للتوضيح
    
    # تحليل افتراضي
    analysis = {
        'trend': 'صاعد' if np.random.random() > 0.5 else 'هابط',
        'strength': np.random.choice(['ضعيف', 'متوسط', 'قوي']),
        'entry_point': round(base_price * (1 + np.random.normal(0, 0.01)), 4),
        'take_profit': round(base_price * (1 + np.random.normal(0.02, 0.01)), 4),
        'stop_loss': round(base_price * (1 - np.random.normal(0.01, 0.005)), 4),
        'risk_reward_ratio': round(np.random.normal(3, 0.5), 2),
        'confidence': int(np.random.normal(85, 5)),
        'recommendation': np.random.choice(['شراء', 'بيع', 'انتظار']),
        'support_levels': [round(base_price * (1 - np.random.normal(0.01 * i, 0.002)), 4) for i in range(1, 4)],
        'resistance_levels': [round(base_price * (1 + np.random.normal(0.01 * i, 0.002)), 4) for i in range(1, 4)],
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
    
    return jsonify({
        'symbol': symbol,
        'timeframe': timeframe,
        'analysis': analysis
    })

# استيراد render_template هنا لتجنب خطأ الاستيراد الدائري
from flask import render_template
import datetime
import numpy as np
