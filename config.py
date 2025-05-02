import os

class Config:
    # إعدادات التطبيق
    SECRET_KEY = 'a7c4d8e2f1b3a9c6d5e8f2b1a7c4d8e2f1b3a9c6'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 ميجابايت كحد أقصى لحجم الملف

    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = 'sqlite:///files.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # إعدادات أخرى يمكن إضافتها هنا

    @staticmethod
    def init_app(app):
        # إنشاء مجلد التحميلات إذا لم يكن موجودًا
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
