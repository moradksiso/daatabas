# نظام إدارة الملفات

تطبيق ويب بسيط مبني بلغة Python وإطار Flask لإدارة وتخزين الملفات مع قاعدة بيانات SQLite.

## المميزات

- رفع الملفات وتخزينها في مجلد محلي
- عرض قائمة بالملفات المرفوعة
- تنزيل الملفات
- حذف الملفات
- عرض تفاصيل الملفات
- دعم معاينة الصور

## متطلبات التشغيل

- Python 3.7+
- Flask
- Flask-SQLAlchemy

## طريقة التثبيت

1. قم بتثبيت Python من [الموقع الرسمي](https://www.python.org/downloads/)

2. قم بنسخ المشروع:
   ```
   git clone https://github.com/yourusername/file-management-system.git
   cd file-management-system
   ```

3. قم بإنشاء بيئة افتراضية وتفعيلها:
   ```
   python -m venv venv
   
   # في نظام Windows
   venv\Scripts\activate
   
   # في نظام Linux/Mac
   source venv/bin/activate
   ```

4. قم بتثبيت المكتبات المطلوبة:
   ```
   pip install -r requirements.txt
   ```

5. قم بتشغيل التطبيق:
   ```
   python app.py
   ```

6. افتح المتصفح على العنوان:
   ```
   http://127.0.0.1:5000
   ```

## هيكل المشروع

```
file-management-system/
├── app.py                  # ملف التطبيق الرئيسي
├── config.py               # إعدادات التطبيق
├── models.py               # نماذج قاعدة البيانات
├── requirements.txt        # متطلبات المشروع
├── templates/              # قوالب HTML
│   ├── base.html           # القالب الأساسي
│   ├── index.html          # صفحة القائمة الرئيسية
│   ├── upload.html         # صفحة رفع الملفات
│   └── file.html           # صفحة تفاصيل الملف
└── uploads/                # مجلد تخزين الملفات المرفوعة
```

## الترخيص

هذا المشروع متاح تحت رخصة MIT.
