from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """نموذج لتخزين معلومات المستخدمين في قاعدة البيانات"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """تعيين كلمة المرور المشفرة"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)

    @property
    def formatted_created_at(self):
        """إرجاع تاريخ الإنشاء بتنسيق مقروء"""
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def formatted_last_login(self):
        """إرجاع تاريخ آخر تسجيل دخول بتنسيق مقروء"""
        if self.last_login:
            return self.last_login.strftime('%Y-%m-%d %H:%M:%S')
        return "لم يسجل الدخول بعد"

class File(db.Model):
    """نموذج لتخزين معلومات الملفات في قاعدة البيانات"""

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # الحجم بالبايت
    file_type = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    description = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(255), nullable=True)  # عنوان الملف
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # العلاقة مع المستخدم
    user = db.relationship('User', backref=db.backref('files', lazy=True))

    def __repr__(self):
        return f'<File {self.original_filename}>'

    @property
    def size_in_kb(self):
        """إرجاع حجم الملف بالكيلوبايت"""
        return round(self.file_size / 1024, 2)

    @property
    def formatted_date(self):
        """إرجاع تاريخ الرفع بتنسيق مقروء"""
        return self.upload_date.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def is_image(self):
        """التحقق مما إذا كان الملف صورة"""
        return self.file_type.startswith('image/')

    @property
    def is_document(self):
        """التحقق مما إذا كان الملف مستند"""
        return (self.file_type == 'application/pdf' or
                self.file_type == 'application/msword' or
                self.file_type.startswith('application/vnd.openxmlformats-officedocument.wordprocessingml'))

    @property
    def is_spreadsheet(self):
        """التحقق مما إذا كان الملف جدول بيانات"""
        return (self.file_type == 'application/vnd.ms-excel' or
                self.file_type.startswith('application/vnd.openxmlformats-officedocument.spreadsheetml'))

    @property
    def is_text(self):
        """التحقق مما إذا كان الملف نصي"""
        return self.file_type == 'text/plain'

    @property
    def file_type_display(self):
        """إرجاع نوع الملف بصيغة مقروءة"""
        if self.is_image:
            return "صورة"
        elif self.file_type == 'application/pdf':
            return "PDF"
        elif self.file_type == 'application/msword' or self.file_type.startswith('application/vnd.openxmlformats-officedocument.wordprocessingml'):
            return "Word"
        elif self.file_type == 'application/vnd.ms-excel' or self.file_type.startswith('application/vnd.openxmlformats-officedocument.spreadsheetml'):
            return "Excel"
        elif self.is_text:
            return "نص"
        else:
            return "ملف آخر"


class ActivityLog(db.Model):
    """نموذج لتسجيل أنشطة المستخدمين في النظام"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # نوع الإجراء (تسجيل دخول، رفع ملف، حذف ملف، إلخ)
    details = db.Column(db.Text, nullable=True)  # تفاصيل إضافية عن الإجراء
    ip_address = db.Column(db.String(50), nullable=True)  # عنوان IP للمستخدم
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # وقت الإجراء

    # العلاقة مع المستخدم
    user = db.relationship('User', backref=db.backref('activities', lazy=True))

    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.user_id} at {self.timestamp}>'

    @property
    def formatted_timestamp(self):
        """إرجاع وقت الإجراء بتنسيق مقروء"""
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def user_display(self):
        """إرجاع اسم المستخدم أو 'زائر' إذا كان غير مسجل"""
        if self.user:
            return self.user.username
        return "زائر"
