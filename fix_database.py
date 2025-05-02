"""
سكريبت لإصلاح مشكلة عمود title في قاعدة البيانات
"""

import os
import sqlite3
import time
from app import app, db, User, File

def fix_database():
    """إصلاح قاعدة البيانات وإضافة عمود title"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files.db')
    
    print(f"جاري فحص قاعدة البيانات في: {db_path}")
    
    if not os.path.exists(db_path):
        print("قاعدة البيانات غير موجودة. سيتم إنشاؤها من جديد.")
        with app.app_context():
            db.create_all()
            
            # إنشاء مستخدم مشرف افتراضي
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@example.com', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("تم إنشاء مستخدم مشرف افتراضي (admin/admin123)")
        
        print("تم إنشاء قاعدة البيانات بنجاح")
        return
    
    # التحقق من وجود عمود title
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # التحقق من وجود جدول file
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file'")
        if not cursor.fetchone():
            print("جدول 'file' غير موجود. سيتم إنشاء الجداول من جديد.")
            conn.close()
            
            with app.app_context():
                db.create_all()
                print("تم إنشاء جميع الجداول")
            
            return
        
        # التحقق من وجود عمود title
        cursor.execute("PRAGMA table_info(file)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"أعمدة جدول الملفات الحالية: {columns}")
        
        # إضافة عمود title إذا لم يكن موجودًا
        if 'title' not in columns:
            print("جاري إضافة عمود 'title' إلى جدول الملفات...")
            cursor.execute("ALTER TABLE file ADD COLUMN title TEXT")
            conn.commit()
            print("تم إضافة عمود 'title' بنجاح")
        else:
            print("عمود 'title' موجود بالفعل")
        
        # إضافة عمود user_id إذا لم يكن موجودًا
        if 'user_id' not in columns:
            print("جاري إضافة عمود 'user_id' إلى جدول الملفات...")
            cursor.execute("ALTER TABLE file ADD COLUMN user_id INTEGER")
            conn.commit()
            print("تم إضافة عمود 'user_id' بنجاح")
            
            # تعيين المشرف كمالك لجميع الملفات الموجودة
            with app.app_context():
                admin = User.query.filter_by(username='admin').first()
                if admin:
                    cursor.execute("UPDATE file SET user_id = ? WHERE user_id IS NULL", (admin.id,))
                    conn.commit()
                    print(f"تم تعيين المشرف كمالك لجميع الملفات الموجودة")
        else:
            print("عمود 'user_id' موجود بالفعل")
        
        conn.close()
        print("تم إصلاح قاعدة البيانات بنجاح")
        
    except Exception as e:
        print(f"حدث خطأ أثناء إصلاح قاعدة البيانات: {e}")
        
        # في حالة فشل الإصلاح، نقوم بإعادة إنشاء قاعدة البيانات بالكامل
        print("جاري محاولة إعادة إنشاء قاعدة البيانات بالكامل...")
        
        try:
            # إغلاق الاتصال الحالي
            if 'conn' in locals() and conn:
                conn.close()
            
            # التأكد من إغلاق جميع الاتصالات بقاعدة البيانات
            db.session.remove()
            
            # حذف ملف قاعدة البيانات
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"تم حذف ملف قاعدة البيانات: {db_path}")
            
            # إنشاء قاعدة البيانات من جديد
            with app.app_context():
                db.create_all()
                print("تم إنشاء جميع الجداول")
                
                # إنشاء مستخدم مشرف افتراضي
                admin = User(username='admin', email='admin@example.com', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("تم إنشاء مستخدم مشرف افتراضي (admin/admin123)")
            
            print("تم إعادة إنشاء قاعدة البيانات بنجاح")
        except Exception as e2:
            print(f"فشل في إعادة إنشاء قاعدة البيانات: {e2}")

if __name__ == "__main__":
    fix_database()
