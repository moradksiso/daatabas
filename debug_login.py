from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

# تشغيل التطبيق في سياق التطبيق
with app.app_context():
    # طباعة معلومات عن المستخدمين الموجودين
    users = User.query.all()
    print(f"عدد المستخدمين في قاعدة البيانات: {len(users)}")
    
    for user in users:
        print(f"المستخدم: {user.username}, البريد الإلكتروني: {user.email}, مشرف: {user.is_admin}, نشط: {user.is_active}")
    
    # التحقق من وجود مستخدم مشرف
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"تم العثور على مستخدم مشرف: {admin.username}")
        
        # اختبار كلمة المرور
        test_password = 'admin123'
        is_valid = check_password_hash(admin.password_hash, test_password)
        print(f"كلمة المرور '{test_password}' صالحة: {is_valid}")
        
        if not is_valid:
            # إعادة تعيين كلمة المرور
            print("إعادة تعيين كلمة المرور للمستخدم المشرف")
            admin.password_hash = generate_password_hash('admin123')
            db.session.commit()
            print("تم إعادة تعيين كلمة المرور بنجاح")
    else:
        print("لم يتم العثور على مستخدم مشرف")
        
        # إنشاء مستخدم مشرف جديد
        print("إنشاء مستخدم مشرف جديد")
        new_admin = User(username='admin', email='admin@example.com', is_admin=True, is_active=True)
        new_admin.password_hash = generate_password_hash('admin123')
        db.session.add(new_admin)
        db.session.commit()
        print("تم إنشاء مستخدم مشرف جديد بنجاح")
    
    # التحقق من وجود مستخدم عادي
    user = User.query.filter_by(username='user').first()
    if user:
        print(f"تم العثور على مستخدم عادي: {user.username}")
        
        # اختبار كلمة المرور
        test_password = 'user123'
        is_valid = check_password_hash(user.password_hash, test_password)
        print(f"كلمة المرور '{test_password}' صالحة: {is_valid}")
        
        if not is_valid:
            # إعادة تعيين كلمة المرور
            print("إعادة تعيين كلمة المرور للمستخدم العادي")
            user.password_hash = generate_password_hash('user123')
            db.session.commit()
            print("تم إعادة تعيين كلمة المرور بنجاح")
    else:
        print("لم يتم العثور على مستخدم عادي")
        
        # إنشاء مستخدم عادي جديد
        print("إنشاء مستخدم عادي جديد")
        new_user = User(username='user', email='user@example.com', is_admin=False, is_active=True)
        new_user.password_hash = generate_password_hash('user123')
        db.session.add(new_user)
        db.session.commit()
        print("تم إنشاء مستخدم عادي جديد بنجاح")
    
    print("\nتم الانتهاء من تشخيص وإصلاح مشاكل تسجيل الدخول")
