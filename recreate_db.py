"""
سكريبت لإعادة إنشاء قاعدة البيانات بالكامل بطريقة جذرية
"""

import os
import shutil
import time
from app import app, db, User

def recreate_database():
    """إعادة إنشاء قاعدة البيانات بالكامل بطريقة جذرية"""
    # مسار قاعدة البيانات
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files.db')
    
    # مسار مجلد النسخ الاحتياطي
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_backup')
    os.makedirs(backup_dir, exist_ok=True)
    
    # إنشاء نسخة احتياطية من قاعدة البيانات الحالية إذا كانت موجودة
    if os.path.exists(db_path):
        backup_path = os.path.join(backup_dir, f'files_backup_{int(time.time())}.db')
        try:
            shutil.copy2(db_path, backup_path)
            print(f"تم إنشاء نسخة احتياطية من قاعدة البيانات في: {backup_path}")
        except Exception as e:
            print(f"فشل في إنشاء نسخة احتياطية: {e}")
    
    # إغلاق جميع الاتصالات بقاعدة البيانات
    db.session.remove()
    
    # حذف ملف قاعدة البيانات
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"تم حذف ملف قاعدة البيانات: {db_path}")
        except Exception as e:
            print(f"فشل في حذف ملف قاعدة البيانات: {e}")
            
            # محاولة بديلة باستخدام shutil
            try:
                os.chmod(db_path, 0o777)  # تغيير صلاحيات الملف
                time.sleep(1)
                os.unlink(db_path)
                print("تم حذف ملف قاعدة البيانات باستخدام os.unlink")
            except Exception as e2:
                print(f"فشل في حذف ملف قاعدة البيانات باستخدام os.unlink: {e2}")
                return False
    
    # إنشاء قاعدة البيانات من جديد
    with app.app_context():
        try:
            db.create_all()
            print("تم إنشاء جميع الجداول")
            
            # إنشاء مستخدم مشرف افتراضي
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("تم إنشاء مستخدم مشرف افتراضي (admin/admin123)")
            
            print("تم إعادة إنشاء قاعدة البيانات بنجاح")
            return True
        except Exception as e:
            print(f"حدث خطأ أثناء إعادة إنشاء قاعدة البيانات: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    recreate_database()


