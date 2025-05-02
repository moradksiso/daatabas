import sys
import os

# إضافة مسار المشروع إلى مسارات Python
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/YOUR_PROJECT_PATH'
if path not in sys.path:
    sys.path.append(path)

# تعيين المجلد الحالي
os.chdir(path)

# استيراد التطبيق
from app import app as application

# تهيئة قاعدة البيانات (اختياري - قم بإزالة هذا الجزء بعد التهيئة الأولى)
"""
from app import app, db, User
with app.app_context():
    db.create_all()
    
    # التحقق من وجود مستخدم مشرف
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("تم إنشاء مستخدم مشرف افتراضي")
"""
