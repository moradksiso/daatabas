"""
سكريبت لإعادة إنشاء قاعدة البيانات بالكامل
"""

import os
import sqlite3
import time
from app import app, db, User

def reset_database():
    """إعادة إنشاء قاعدة البيانات بالكامل"""
    # حذف ملف قاعدة البيانات إذا كان موجودًا
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files.db')

    # التأكد من إغلاق جميع الاتصالات بقاعدة البيانات
    db.session.remove()

    # محاولة حذف الملف عدة مرات في حالة كان مفتوحًا
    for attempt in range(5):
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"تم حذف ملف قاعدة البيانات: {db_path}")
            break
        except Exception as e:
            print(f"محاولة {attempt+1}: فشل في حذف ملف قاعدة البيانات: {e}")
            time.sleep(1)  # انتظار ثانية قبل المحاولة مرة أخرى

    # إنشاء قاعدة البيانات من جديد
    with app.app_context():
        try:
            # إنشاء جميع الجداول من جديد
            db.create_all()
            print("تم إنشاء جميع الجداول")

            # إنشاء مستخدم مشرف افتراضي
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("تم إنشاء مستخدم مشرف افتراضي (admin/admin123)")

            # التحقق من وجود جميع الأعمدة المطلوبة
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(file)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"أعمدة جدول الملفات: {columns}")

            # التحقق من وجود عمود title
            if 'title' not in columns:
                print("تحذير: عمود 'title' غير موجود في جدول الملفات!")

            # التحقق من وجود عمود user_id
            if 'user_id' not in columns:
                print("تحذير: عمود 'user_id' غير موجود في جدول الملفات!")

            conn.close()

            print("تم إعادة إنشاء قاعدة البيانات بنجاح")
        except Exception as e:
            print(f"حدث خطأ أثناء إعادة إنشاء قاعدة البيانات: {e}")
            db.session.rollback()

if __name__ == "__main__":
    reset_database()
