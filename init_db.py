from app import app, db, User
from datetime import datetime, timezone

# تشغيل التطبيق في سياق التطبيق
with app.app_context():
    # إعادة إنشاء قاعدة البيانات
    db.drop_all()
    db.create_all()
    print("تم إعادة إنشاء قاعدة البيانات")

    # إنشاء مستخدم مشرف افتراضي
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)
    
    # إنشاء مستخدم عادي للاختبار
    test_user = User(username='user', email='user@example.com', is_admin=False)
    test_user.set_password('user123')
    db.session.add(test_user)
    
    db.session.commit()
    print("تم إنشاء المستخدمين بنجاح")
    print("- مشرف: admin / admin123")
    print("- مستخدم: user / user123")
