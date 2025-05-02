# تعليمات إعداد التطبيق على PythonAnywhere

## 1. إنشاء حساب على PythonAnywhere

1. قم بزيارة [PythonAnywhere](https://www.pythonanywhere.com/) وإنشاء حساب جديد.
2. بعد تسجيل الدخول، انتقل إلى لوحة التحكم.

## 2. رفع المشروع

### الطريقة 1: استخدام Git

1. انتقل إلى علامة التبويب "Consoles" وافتح وحدة تحكم Bash جديدة.
2. قم بنسخ المشروع من مستودع Git:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   ```

### الطريقة 2: رفع الملفات مباشرة

1. انتقل إلى علامة التبويب "Files".
2. قم بإنشاء مجلد جديد للمشروع.
3. استخدم خيار "Upload a file" لرفع ملفات المشروع.

## 3. إعداد البيئة الافتراضية

1. انتقل إلى علامة التبويب "Consoles" وافتح وحدة تحكم Bash جديدة.
2. قم بإنشاء بيئة افتراضية جديدة:
   ```bash
   cd ~/YOUR_PROJECT_PATH
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 4. إعداد تطبيق الويب

1. انتقل إلى علامة التبويب "Web".
2. انقر على "Add a new web app".
3. اختر "Manual configuration".
4. اختر إصدار Python المناسب (Python 3.9).
5. أدخل مسار المشروع: `/home/YOUR_PYTHONANYWHERE_USERNAME/YOUR_PROJECT_PATH`.
6. قم بتعديل ملف WSGI:
   - انقر على رابط ملف WSGI.
   - احذف كل المحتوى واستبدله بمحتوى ملف `pythonanywhere_wsgi.py` (مع تعديل المسارات).
   - قم بحفظ الملف.

## 5. إعداد المتغيرات البيئية

1. انتقل إلى علامة التبويب "Web".
2. انتقل إلى قسم "WSGI configuration file".
3. أضف المتغيرات البيئية التالية في بداية الملف:
   ```python
   import os
   os.environ['SECRET_KEY'] = 'your_secret_key_here'
   os.environ['FLASK_ENV'] = 'production'
   ```

## 6. تهيئة قاعدة البيانات

1. انتقل إلى علامة التبويب "Consoles" وافتح وحدة تحكم Bash جديدة.
2. قم بتنشيط البيئة الافتراضية:
   ```bash
   cd ~/YOUR_PROJECT_PATH
   source venv/bin/activate
   ```
3. قم بتشغيل سكريبت تهيئة قاعدة البيانات:
   ```bash
   python init_db.py
   ```

## 7. إعداد المجلدات الثابتة

1. انتقل إلى علامة التبويب "Web".
2. انتقل إلى قسم "Static files".
3. أضف المسارات التالية:
   - URL: `/static/` - Directory: `/home/YOUR_PYTHONANYWHERE_USERNAME/YOUR_PROJECT_PATH/static`
   - URL: `/uploads/` - Directory: `/home/YOUR_PYTHONANYWHERE_USERNAME/YOUR_PROJECT_PATH/uploads`

## 8. إعادة تشغيل التطبيق

1. انتقل إلى علامة التبويب "Web".
2. انقر على زر "Reload" لإعادة تشغيل التطبيق.

## 9. اختبار التطبيق

1. انقر على الرابط المقدم في علامة التبويب "Web" (مثل `http://YOUR_USERNAME.pythonanywhere.com`).
2. قم بتسجيل الدخول باستخدام:
   - اسم المستخدم: `admin`
   - كلمة المرور: `admin123`

## 10. استكشاف الأخطاء وإصلاحها

1. انتقل إلى علامة التبويب "Web".
2. انقر على رابط "Error log" لعرض سجل الأخطاء.
3. إذا واجهت مشاكل في تسجيل الدخول:
   - تأكد من تهيئة قاعدة البيانات بشكل صحيح.
   - تأكد من إعداد مجلد الجلسات بشكل صحيح.
   - تأكد من تعيين مفتاح سري قوي.

## ملاحظات هامة

1. تأكد من تغيير كلمات المرور الافتراضية بعد تسجيل الدخول الأول.
2. قم بإنشاء نسخة احتياطية من قاعدة البيانات بانتظام.
3. تأكد من تعيين الأذونات المناسبة لمجلدات التحميل والجلسات.
