from app import app
import os

# طباعة معلومات عن إعدادات الجلسة
print("إعدادات الجلسة:")
print(f"SECRET_KEY: {'*' * 10}")  # لا تطبع المفتاح السري كاملاً
print(f"SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
print(f"SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
print(f"PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME')}")
print(f"SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
print(f"SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
print(f"SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE')}")
print(f"SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
print(f"SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}")

# التحقق من وجود مجلد الجلسات
session_dir = app.config.get('SESSION_FILE_DIR')
if session_dir:
    if os.path.exists(session_dir):
        print(f"\nمجلد الجلسات موجود: {session_dir}")
        
        # عرض محتويات مجلد الجلسات
        session_files = os.listdir(session_dir)
        print(f"عدد ملفات الجلسات: {len(session_files)}")
        
        if len(session_files) > 0:
            print("أول 5 ملفات جلسات:")
            for file in session_files[:5]:
                file_path = os.path.join(session_dir, file)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                print(f"- {file} (الحجم: {file_size} بايت، آخر تعديل: {file_mtime})")
    else:
        print(f"\nمجلد الجلسات غير موجود: {session_dir}")
        
        # إنشاء مجلد الجلسات
        try:
            os.makedirs(session_dir, exist_ok=True)
            print(f"تم إنشاء مجلد الجلسات: {session_dir}")
        except Exception as e:
            print(f"خطأ في إنشاء مجلد الجلسات: {str(e)}")
else:
    print("\nلم يتم تعيين مجلد الجلسات")

# التحقق من أذونات مجلد الجلسات
if session_dir and os.path.exists(session_dir):
    try:
        # إنشاء ملف اختبار
        test_file_path = os.path.join(session_dir, 'test_session_file')
        with open(test_file_path, 'w') as f:
            f.write('test')
        
        print("\nتم إنشاء ملف اختبار في مجلد الجلسات بنجاح")
        
        # قراءة ملف الاختبار
        with open(test_file_path, 'r') as f:
            content = f.read()
        
        print(f"تم قراءة ملف الاختبار بنجاح: {content}")
        
        # حذف ملف الاختبار
        os.remove(test_file_path)
        print("تم حذف ملف الاختبار بنجاح")
    except Exception as e:
        print(f"\nخطأ في اختبار أذونات مجلد الجلسات: {str(e)}")
        print("قد تكون هناك مشكلة في أذونات مجلد الجلسات")

print("\nتم الانتهاء من التحقق من إعدادات الجلسة")
