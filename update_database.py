"""
سكريبت لتحديث قاعدة البيانات بعد إضافة حقل user_id إلى نموذج File
"""

import os
import sqlite3
from app import app, db, User, File

def add_user_id_column():
    """إضافة عمود user_id إلى جدول file إذا لم يكن موجودًا"""
    # الحصول على مسار قاعدة البيانات
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files.db')

    if not os.path.exists(db_path):
        print(f"قاعدة البيانات غير موجودة في المسار: {db_path}")
        return False

    try:
        # الاتصال بقاعدة البيانات مباشرة
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # التحقق من وجود عمود user_id
        cursor.execute("PRAGMA table_info(file)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if 'user_id' not in column_names:
            print("إضافة عمود user_id إلى جدول file")
            cursor.execute("ALTER TABLE file ADD COLUMN user_id INTEGER")
            conn.commit()
            print("تم إضافة العمود بنجاح")
        else:
            print("عمود user_id موجود بالفعل")

        conn.close()
        return True
    except Exception as e:
        print(f"حدث خطأ: {e}")
        return False

def update_files_user_id():
    """تحديث حقل user_id للملفات الموجودة"""
    # إضافة العمود أولاً إذا لم يكن موجودًا
    if not add_user_id_column():
        print("فشل في إضافة عمود user_id")
        return

    with app.app_context():
        # إعادة إنشاء قاعدة البيانات إذا لزم الأمر
        try:
            # الحصول على المشرف الافتراضي
            admin = User.query.filter_by(username='admin').first()

            if not admin:
                print("المشرف الافتراضي غير موجود، جاري إنشاؤه...")
                admin = User(username='admin', email='admin@example.com', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("تم إنشاء مستخدم مشرف افتراضي (admin/admin123)")

            # تحديث جميع الملفات التي ليس لها user_id
            try:
                files_without_user = File.query.filter(File.user_id.is_(None)).all()

                if not files_without_user:
                    print("لا توجد ملفات بدون user_id")
                    return

                print(f"تم العثور على {len(files_without_user)} ملف بدون user_id")

                # تعيين المشرف كمالك لجميع الملفات الموجودة
                for file in files_without_user:
                    file.user_id = admin.id
                    print(f"تحديث الملف: {file.original_filename}")

                # حفظ التغييرات
                db.session.commit()

                print("تم تحديث قاعدة البيانات بنجاح")
            except Exception as e:
                print(f"حدث خطأ أثناء تحديث الملفات: {e}")
        except Exception as e:
            print(f"حدث خطأ: {e}")
            print("جاري إعادة إنشاء قاعدة البيانات...")
            db.drop_all()
            db.create_all()

            # إنشاء مستخدم مشرف افتراضي
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

            print("تم إعادة إنشاء قاعدة البيانات بنجاح")

if __name__ == "__main__":
    update_files_user_id()
