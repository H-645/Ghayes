# دليل نشر موقع Chicha AI على استضافة دائمة

هذا الدليل يشرح كيفية نشر موقع Chicha AI على استضافة دائمة لضمان توفر الموقع بشكل مستمر دون انقطاع.

## الخيارات المتاحة للاستضافة الدائمة

هناك عدة خيارات لاستضافة تطبيق Flask بشكل دائم:

### 1. استضافة على Heroku

Heroku هي منصة سحابية سهلة الاستخدام تدعم تطبيقات Python/Flask.

#### خطوات النشر على Heroku:

1. **إنشاء حساب على Heroku**:
   - قم بزيارة [heroku.com](https://www.heroku.com/) وإنشاء حساب جديد

2. **تثبيت Heroku CLI**:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

3. **تسجيل الدخول من خلال CLI**:
   ```bash
   heroku login
   ```

4. **إنشاء ملف Procfile**:
   - قم بإنشاء ملف باسم `Procfile` (بدون امتداد) في المجلد الرئيسي للمشروع
   - أضف السطر التالي:
     ```
     web: gunicorn src:create_app()
     ```

5. **إنشاء تطبيق جديد على Heroku**:
   ```bash
   heroku create chicha-ai
   ```

6. **إضافة قاعدة بيانات PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

7. **ضبط متغيرات البيئة**:
   ```bash
   heroku config:set OPENAI_API_KEY=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
   heroku config:set FLASK_ENV=production
   ```

8. **نشر التطبيق**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku master
   ```

9. **تهيئة قاعدة البيانات**:
   ```bash
   heroku run python -c "from src import create_app; app = create_app(); app.app_context().push(); from src.models.models import db; db.create_all()"
   ```

10. **فتح التطبيق**:
    ```bash
    heroku open
    ```

### 2. استضافة على AWS Elastic Beanstalk

AWS Elastic Beanstalk هي خدمة سهلة الاستخدام لنشر وتوسيع تطبيقات الويب.

#### خطوات النشر على AWS Elastic Beanstalk:

1. **إنشاء حساب AWS**:
   - قم بزيارة [aws.amazon.com](https://aws.amazon.com/) وإنشاء حساب جديد

2. **تثبيت AWS CLI و EB CLI**:
   ```bash
   pip install awscli awsebcli
   ```

3. **تهيئة AWS CLI**:
   ```bash
   aws configure
   ```

4. **إنشاء ملف التكوين**:
   - قم بإنشاء مجلد `.ebextensions` في المجلد الرئيسي للمشروع
   - أنشئ ملف `01_flask.config` داخل المجلد بالمحتوى التالي:
     ```yaml
     option_settings:
       aws:elasticbeanstalk:container:python:
         WSGIPath: application:application
       aws:elasticbeanstalk:application:environment:
         OPENAI_API_KEY: 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
         FLASK_ENV: production
     ```

5. **إنشاء ملف application.py**:
   - أنشئ ملف `application.py` في المجلد الرئيسي بالمحتوى التالي:
     ```python
     from src import create_app
     
     application = create_app()
     
     if __name__ == "__main__":
         application.run()
     ```

6. **تهيئة Elastic Beanstalk**:
   ```bash
   eb init -p python-3.8 chicha-ai --region us-east-1
   ```

7. **إنشاء بيئة وتنفيذ النشر**:
   ```bash
   eb create chicha-ai-env
   ```

8. **فتح التطبيق**:
   ```bash
   eb open
   ```

### 3. استضافة على PythonAnywhere

PythonAnywhere هي منصة استضافة مخصصة لتطبيقات Python وسهلة الاستخدام.

#### خطوات النشر على PythonAnywhere:

1. **إنشاء حساب على PythonAnywhere**:
   - قم بزيارة [pythonanywhere.com](https://www.pythonanywhere.com/) وإنشاء حساب جديد

2. **رفع الملفات**:
   - قم بضغط المشروع وتحميله إلى PythonAnywhere
   - استخدم الأمر التالي لفك الضغط:
     ```bash
     unzip chicha_ai_project.zip
     ```

3. **إنشاء بيئة افتراضية**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.8 chicha_ai_env
   cd chicha_ai_project
   pip install -r requirements.txt
   ```

4. **إعداد تطبيق الويب**:
   - انتقل إلى لوحة التحكم وانقر على "Web"
   - انقر على "Add a new web app"
   - اختر "Manual configuration" ثم "Python 3.8"
   - قم بتعيين مسار البيئة الافتراضية: `/home/yourusername/.virtualenvs/chicha_ai_env`
   - قم بتعديل ملف WSGI ليحتوي على:
     ```python
     import sys
     import os
     
     path = '/home/yourusername/chicha_ai_project'
     if path not in sys.path:
         sys.path.append(path)
     
     from src import create_app
     application = create_app()
     ```

5. **ضبط متغيرات البيئة**:
   - انتقل إلى علامة التبويب "WSGI configuration file"
   - أضف المتغيرات في بداية الملف:
     ```python
     os.environ['OPENAI_API_KEY'] = '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'
     os.environ['FLASK_ENV'] = 'production'
     ```

6. **إعادة تشغيل التطبيق**:
   - انقر على زر "Reload" في صفحة الويب

## متغيرات البيئة المطلوبة

يتطلب موقع Chicha AI ضبط المتغيرات البيئية التالية:

| المتغير | الوصف | القيمة الافتراضية |
|---------|-------|-------------------|
| `OPENAI_API_KEY` | مفتاح API الخاص بـ OpenAI | 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 |
| `FLASK_ENV` | بيئة التشغيل | production |
| `DATABASE_URL` | رابط قاعدة البيانات | يتم تعيينه تلقائياً في معظم خدمات الاستضافة |
| `SECRET_KEY` | مفتاح سري لتشفير الجلسات | يجب تعيين قيمة عشوائية آمنة |

## ربط بيانات السوق الحية

لضمان الحصول على بيانات حقيقية من السوق، يجب ربط الموقع بواجهات برمجية للبيانات المالية:

### 1. Yahoo Finance API

1. **الحصول على مفتاح API**:
   - قم بزيارة [RapidAPI](https://rapidapi.com/apidojo/api/yahoo-finance1)
   - سجل للحصول على مفتاح API

2. **ضبط متغير البيئة**:
   ```bash
   export YAHOO_FINANCE_API_KEY=your_api_key
   ```

3. **تعديل ملف `market_api.py`**:
   - قم بتحديث الدالة `get_price` و `get_chart_data` لاستخدام Yahoo Finance API

### 2. Alpha Vantage API

1. **الحصول على مفتاح API**:
   - قم بزيارة [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - سجل للحصول على مفتاح API مجاني

2. **ضبط متغير البيئة**:
   ```bash
   export ALPHA_VANTAGE_API_KEY=your_api_key
   ```

3. **تعديل ملف `market_api.py`**:
   - قم بتحديث الدوال المناسبة لاستخدام Alpha Vantage API

## تشغيل الموقع محلياً للاختبار

قبل النشر على استضافة دائمة، يمكنك تشغيل الموقع محلياً للاختبار:

1. **تنشيط البيئة الافتراضية**:
   ```bash
   cd chicha_ai_project
   source venv/bin/activate
   ```

2. **ضبط متغيرات البيئة**:
   ```bash
   export OPENAI_API_KEY=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
   export FLASK_ENV=development
   ```

3. **تشغيل التطبيق**:
   ```bash
   python -c "from src import create_app; app = create_app(); app.run(host='0.0.0.0', port=5000, debug=True)"
   ```

4. **الوصول إلى الموقع**:
   - افتح المتصفح وانتقل إلى `http://localhost:5000`

## الصيانة والتحديثات

بعد نشر الموقع، قد تحتاج إلى إجراء تحديثات أو صيانة:

### 1. تحديث الكود

1. **تعديل الكود المصدري**
2. **اختبار التغييرات محلياً**
3. **نشر التحديثات**:
   - على Heroku:
     ```bash
     git add .
     git commit -m "Update description"
     git push heroku master
     ```
   - على AWS Elastic Beanstalk:
     ```bash
     eb deploy
     ```
   - على PythonAnywhere:
     - قم بتحميل الملفات المحدثة
     - انقر على "Reload" في صفحة الويب

### 2. تحديث قاعدة البيانات

إذا قمت بتغيير نماذج قاعدة البيانات، ستحتاج إلى تحديث الجداول:

- على Heroku:
  ```bash
  heroku run python -c "from src import create_app; app = create_app(); app.app_context().push(); from src.models.models import db; db.create_all()"
  ```

- على AWS أو PythonAnywhere:
  - قم بتشغيل نفس الأمر من خلال واجهة سطر الأوامر

## استكشاف الأخطاء وإصلاحها

إذا واجهت مشاكل أثناء النشر، يمكنك التحقق من:

1. **سجلات التطبيق**:
   - على Heroku:
     ```bash
     heroku logs --tail
     ```
   - على AWS Elastic Beanstalk:
     ```bash
     eb logs
     ```
   - على PythonAnywhere:
     - انتقل إلى علامة التبويب "Logs"

2. **مشاكل قاعدة البيانات**:
   - تأكد من تهيئة قاعدة البيانات بشكل صحيح
   - تحقق من صحة متغير البيئة `DATABASE_URL`

3. **مشاكل متغيرات البيئة**:
   - تأكد من ضبط جميع متغيرات البيئة المطلوبة

4. **مشاكل الاعتمادات**:
   - تأكد من تثبيت جميع الحزم المطلوبة في ملف `requirements.txt`

## الخلاصة

باتباع هذا الدليل، يمكنك نشر موقع Chicha AI على استضافة دائمة وضمان توفره بشكل مستمر. اختر خدمة الاستضافة التي تناسب احتياجاتك وميزانيتك، وتأكد من ضبط جميع متغيرات البيئة المطلوبة.

إذا كنت بحاجة إلى مساعدة إضافية، لا تتردد في التواصل معنا.
