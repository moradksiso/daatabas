import os
import uuid
import secrets
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, g
from werkzeug.utils import secure_filename
from config import Config
from models import db, File, User, ActivityLog

app = Flask(__name__)
app.config.from_object(Config)

# تعيين مفتاح سري قوي للجلسة
app.secret_key = secrets.token_hex(32)

# تهيئة قاعدة البيانات
db.init_app(app)

# تهيئة الجلسة
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # جلسة تستمر لمدة أسبوع
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
app.config['SESSION_COOKIE_SECURE'] = False  # تعيين إلى True في بيئة الإنتاج مع HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# إنشاء مجلد الجلسات إذا لم يكن موجودًا
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# طباعة معلومات تصحيح الأخطاء
print(f"مجلد الجلسات: {app.config['SESSION_FILE_DIR']}")
print(f"مفتاح الجلسة السري: {app.secret_key[:10]}...")

# تهيئة التطبيق
Config.init_app(app)

# File type constants
IMAGE_FILE_TYPE = 'image/'
PDF_FILE_TYPE = 'application/pdf'
MSWORD_FILE_TYPE = 'application/msword'
DOCX_FILE_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml'
EXCEL_FILE_TYPE = 'application/vnd.ms-excel'
XLSX_FILE_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml'
TEXT_FILE_TYPE = 'text/plain'

# وظيفة مساعدة لتسجيل الأنشطة
def log_activity(action, details=None, user_id=None):
    """تسجيل نشاط في قاعدة البيانات"""
    try:
        # إذا لم يتم تحديد معرف المستخدم، استخدم المستخدم الحالي إذا كان متاحًا
        if user_id is None and hasattr(g, 'user') and g.user is not None:
            user_id = g.user.id

        # الحصول على عنوان IP للمستخدم
        ip_address = request.remote_addr

        # إنشاء سجل جديد
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address
        )

        # حفظ السجل في قاعدة البيانات
        db.session.add(log_entry)
        db.session.commit()

        return True
    except Exception as e:
        # طباعة الخطأ للتصحيح ولكن لا تتوقف عن تنفيذ العملية الأساسية
        print(f"خطأ في تسجيل النشاط: {str(e)}")
        return False

# Constants for file type labels
LABEL_ALL_FILES = 'جميع أنواع الملفات'
LABEL_IMAGES = 'صور'
# Constants for document label
LABEL_DOCUMENTS = 'مستندات'
LABEL_SPREADSHEETS = 'جداول بيانات'
LABEL_TEXT_FILES = 'ملفات نصية'
LABEL_OTHER = 'أخرى'

# تعريف أنواع الملفات المتاحة للفلترة - تم نقلها إلى مستوى عالي لتجنب التكرار
FILE_TYPES = [
    {'value': '', 'label': LABEL_ALL_FILES},
    {'value': 'image', 'label': LABEL_IMAGES},
    {'value': 'document', 'label': LABEL_DOCUMENTS},
    {'value': 'spreadsheet', 'label': LABEL_SPREADSHEETS},
    {'value': 'text', 'label': LABEL_TEXT_FILES},
    {'value': 'other', 'label': LABEL_OTHER}
]

# Constants for sort options labels
LABEL_DATE_DESC = 'الأحدث أولاً'
LABEL_DATE_ASC = 'الأقدم أولاً'
LABEL_NAME_ASC = 'الاسم (أ-ي)'
LABEL_NAME_DESC = 'الاسم (ي-أ)'
LABEL_SIZE_ASC = 'الحجم (الأصغر أولاً)'
LABEL_SIZE_DESC = 'الحجم (الأكبر أولاً)'

# تعريف خيارات الترتيب - تم نقلها إلى مستوى عالي لتجنب التكرار
SORT_OPTIONS = [
    {'value': 'date_desc', 'label': LABEL_DATE_DESC},
    {'value': 'date_asc', 'label': LABEL_DATE_ASC},
    {'value': 'name_asc', 'label': LABEL_NAME_ASC},
    {'value': 'name_desc', 'label': LABEL_NAME_DESC},
    {'value': 'size_asc', 'label': LABEL_SIZE_ASC},
    {'value': 'size_desc', 'label': LABEL_SIZE_DESC}
]

def allowed_file(filename):
    """التحقق من أن امتداد الملف مسموح به"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.context_processor
def inject_now():
    """إضافة متغير now إلى سياق القالب"""
    return {'now': datetime.now(timezone.utc)}

# وظائف التحقق من الصلاحيات
def login_required(f):
    """وظيفة للتحقق من تسجيل دخول المستخدم"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """وظيفة للتحقق من صلاحيات المشرف"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('login', next=request.url))

        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    """تحميل معلومات المستخدم قبل كل طلب"""
    user_id = session.get('user_id')

    # طباعة معلومات تصحيح الأخطاء
    print(f"محاولة تحميل المستخدم من الجلسة. معرف المستخدم: {user_id}")
    print(f"محتوى الجلسة: {session}")

    if user_id is None:
        g.user = None
        print("لا يوجد معرف مستخدم في الجلسة")
    else:
        try:
            g.user = User.query.get(user_id)
            if g.user:
                print(f"تم تحميل المستخدم بنجاح: {g.user.username} (ID: {g.user.id})")
            else:
                print(f"لم يتم العثور على المستخدم بالمعرف: {user_id}")
                # إذا لم يتم العثور على المستخدم، مسح الجلسة
                session.clear()
                print("تم مسح الجلسة")
        except Exception as e:
            print(f"خطأ في تحميل المستخدم: {str(e)}")
            g.user = None
            session.clear()
            print("تم مسح الجلسة بسبب خطأ")

@app.route('/')
def index():
    """الصفحة الرئيسية - صفحة ترحيبية للزوار وعرض الملفات للمستخدمين المسجلين"""
    # إذا كان المستخدم مسجل الدخول، توجيهه إلى صفحة استكشاف الملفات
    if g.user:
        return redirect(url_for('explore_files'))

    # للزوار، عرض صفحة ترحيبية فقط
    return render_template('index.html')

@app.route('/explore')
@login_required
def explore_files():
    """صفحة استكشاف الملفات - عرض قائمة الملفات مع إمكانية البحث والفلترة"""
    # استخراج معايير البحث والفلترة من الطلب
    search_query = request.args.get('search', '')
    file_type = request.args.get('file_type', '')
    sort_by = request.args.get('sort_by', 'date_desc')

    # بناء استعلام قاعدة البيانات
    query = File.query

    # تطبيق البحث إذا تم تحديده
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                File.original_filename.like(search_term),
                File.description.like(search_term)
            )
        )

    # تطبيق فلترة نوع الملف إذا تم تحديدها
    if file_type:
        if file_type == 'image':
            query = query.filter(File.file_type.startswith(IMAGE_FILE_TYPE))
        elif file_type == 'document':
            query = query.filter(
                db.or_(
                    File.file_type == PDF_FILE_TYPE,
                    File.file_type == MSWORD_FILE_TYPE,
                    File.file_type.startswith(DOCX_FILE_TYPE)
                )
            )
        elif file_type == 'spreadsheet':
            query = query.filter(
                db.or_(
                    File.file_type == EXCEL_FILE_TYPE,
                    File.file_type.startswith(XLSX_FILE_TYPE)
                )
            )
        elif file_type == 'text':
            query = query.filter(File.file_type == TEXT_FILE_TYPE)
        elif file_type == 'other':
            query = query.filter(
                db.and_(
                    ~File.file_type.startswith(IMAGE_FILE_TYPE),
                    ~File.file_type.startswith(PDF_FILE_TYPE),
                    ~File.file_type.startswith(MSWORD_FILE_TYPE),
                    ~File.file_type.startswith(DOCX_FILE_TYPE),
                    ~File.file_type.startswith(EXCEL_FILE_TYPE),
                    ~File.file_type.startswith(XLSX_FILE_TYPE),
                    ~File.file_type.startswith(TEXT_FILE_TYPE)
                )
            )

    # تطبيق الترتيب
    if sort_by == 'date_asc':
        query = query.order_by(File.upload_date.asc())
    elif sort_by == 'date_desc':
        query = query.order_by(File.upload_date.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(File.original_filename.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(File.original_filename.desc())
    elif sort_by == 'size_asc':
        query = query.order_by(File.file_size.asc())
    elif sort_by == 'size_desc':
        query = query.order_by(File.file_size.desc())
    else:
        query = query.order_by(File.upload_date.desc())

    # تنفيذ الاستعلام
    files = query.all()

    # إعداد قائمة بأنواع الملفات للفلترة
    file_types = [
        {'value': '', 'label': 'جميع الملفات'},
        {'value': 'image', 'label': 'صور'},
        {'value': 'document', 'label': 'مستندات'},
        {'value': 'spreadsheet', 'label': 'جداول بيانات'},
        {'value': 'text', 'label': 'ملفات نصية'},
        {'value': 'other', 'label': 'أنواع أخرى'}
    ]

    # إعداد قائمة بخيارات الترتيب
    sort_options = [
        {'value': 'date_desc', 'label': 'الأحدث أولاً'},
        {'value': 'date_asc', 'label': 'الأقدم أولاً'},
        {'value': 'name_asc', 'label': 'الاسم (أ-ي)'},
        {'value': 'name_desc', 'label': 'الاسم (ي-أ)'},
        {'value': 'size_asc', 'label': 'الحجم (الأصغر أولاً)'},
        {'value': 'size_desc', 'label': 'الحجم (الأكبر أولاً)'}
    ]

    return render_template(
        'explore.html',
        files=files,
        search_query=search_query,
        file_type=file_type,
        sort_by=sort_by,
        file_types=file_types,
        sort_options=sort_options
    )

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """صفحة رفع الملفات"""
    if request.method == 'POST':
        return handle_file_upload()

    return render_template('upload.html')

def handle_file_upload():
    """معالجة عملية رفع الملف"""
    # التحقق من وجود ملف في الطلب
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف', 'error')
        return redirect(request.url)

    file = request.files['file']
    title = request.form.get('title', '')
    description = request.form.get('description', '')

    # التحقق من صحة البيانات المدخلة
    if not is_valid_upload_data(file, title):
        return redirect(request.url)

    # التحقق من أن الملف له امتداد مسموح به
    if file and allowed_file(file.filename):
        return process_valid_file(file, title, description)
    else:
        flash('نوع الملف غير مسموح به', 'error')
        return redirect(request.url)

def is_valid_upload_data(file, title):
    """التحقق من صحة بيانات الرفع"""
    # التحقق من أن العنوان غير فارغ
    if not title:
        flash('يرجى إدخال عنوان للملف', 'error')
        return False

    # التحقق من أن المستخدم اختار ملفًا
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'error')
        return False

    return True

def process_valid_file(file, title, description):
    """معالجة الملف الصالح وحفظه"""
    # تأمين اسم الملف وإنشاء اسم فريد للتخزين
    original_filename = secure_filename(file.filename)

    # التحقق من عدم وجود ملف بنفس الاسم
    if check_duplicate_filename(original_filename):
        return redirect(request.url)

    # إنشاء اسم فريد للملف
    unique_filename = create_unique_filename(original_filename)

    # حفظ الملف وإنشاء سجل في قاعدة البيانات
    return save_file_and_create_record(file, unique_filename, original_filename, title, description)

def check_duplicate_filename(original_filename):
    """التحقق من عدم وجود ملف بنفس الاسم"""
    existing_file = File.query.filter_by(original_filename=original_filename).first()
    if existing_file:
        flash(f'يوجد ملف بنفس الاسم "{original_filename}" مرفوع بالفعل. يرجى اختيار اسم آخر أو تغيير اسم الملف.', 'error')
        return True
    return False

def create_unique_filename(original_filename):
    """إنشاء اسم فريد للملف"""
    file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    return f"{uuid.uuid4().hex}.{file_extension}" if file_extension else f"{uuid.uuid4().hex}"

def save_file_and_create_record(file, unique_filename, original_filename, title, description):
    """حفظ الملف وإنشاء سجل في قاعدة البيانات"""
    # حفظ الملف في مجلد التحميلات
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)

    # إنشاء سجل جديد في قاعدة البيانات
    new_file = File(
        filename=unique_filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        file_type=file.content_type,
        title=title,
        description=description,
        user_id=g.user.id  # ربط الملف بالمستخدم الحالي
    )

    db.session.add(new_file)
    db.session.commit()

    # تسجيل نشاط رفع الملف
    log_activity('رفع ملف', f'تم رفع ملف جديد: {original_filename} (ID: {new_file.id})')

    flash('تم رفع الملف بنجاح', 'success')
    return redirect(url_for('index'))

@app.route('/file/<int:file_id>')
def file_details(file_id):
    """عرض تفاصيل الملف"""
    file = File.query.get_or_404(file_id)
    return render_template('file.html', file=file)

@app.route('/download/<int:file_id>')
def download_file(file_id):
    """تنزيل الملف"""
    file = File.query.get_or_404(file_id)
    return send_from_directory(
        os.path.dirname(file.file_path),
        os.path.basename(file.file_path),
        as_attachment=True,
        download_name=file.original_filename
    )

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    """حذف الملف"""
    file = File.query.get_or_404(file_id)

    # التحقق من صلاحية الحذف:
    # 1. المستخدم هو مالك الملف
    # 2. أو المستخدم هو مشرف
    if file.user_id != g.user.id and not g.user.is_admin:
        flash('ليس لديك صلاحية لحذف هذا الملف', 'error')
        return redirect(url_for('index'))

    # حذف الملف من نظام الملفات
    if os.path.exists(file.file_path):
        os.remove(file.file_path)

    # تخزين معلومات الملف قبل حذفه لاستخدامها في سجل النشاط
    file_info = f"{file.original_filename} (ID: {file.id})"

    # حذف السجل من قاعدة البيانات
    db.session.delete(file)
    db.session.commit()

    # تسجيل نشاط حذف الملف
    log_activity('حذف ملف', f'تم حذف الملف: {file_info}')

    flash('تم حذف الملف بنجاح', 'success')

    # إعادة التوجيه إلى الصفحة السابقة
    referrer = request.referrer
    if referrer and 'my-files' in referrer:
        return redirect(url_for('my_files'))
    elif referrer and 'explore' in referrer:
        return redirect(url_for('explore_files'))
    else:
        return redirect(url_for('index'))

# وظائف إدارة المستخدمين
@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    # إذا كان المستخدم مسجل دخوله بالفعل، توجيهه إلى الصفحة الرئيسية
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # طباعة معلومات تصحيح الأخطاء
        print(f"محاولة تسجيل دخول: {username}")

        # التحقق من إدخال اسم المستخدم وكلمة المرور
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return render_template('login.html')

        # البحث عن المستخدم في قاعدة البيانات
        user = User.query.filter_by(username=username).first()

        # طباعة معلومات تصحيح الأخطاء
        print(f"تم العثور على المستخدم: {user is not None}")

        # التحقق من صحة كلمة المرور
        if user and user.check_password(password):
            # طباعة معلومات تصحيح الأخطاء
            print(f"كلمة المرور صحيحة للمستخدم: {username}")

            # التحقق من أن الحساب نشط
            if not user.is_active:
                flash('تم تعطيل حسابك. يرجى التواصل مع المشرف', 'error')
                return render_template('login.html')

            # تخزين معرف المستخدم في الجلسة
            session.clear()
            session['user_id'] = user.id

            # طباعة معلومات تصحيح الأخطاء
            print(f"تم تخزين معرف المستخدم في الجلسة: {user.id}")
            print(f"محتوى الجلسة: {session}")

            # تحديث تاريخ آخر تسجيل دخول
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            try:
                # تسجيل نشاط تسجيل الدخول
                log_activity('تسجيل دخول', f'تم تسجيل دخول المستخدم {user.username}', user.id)
            except Exception as e:
                print(f"خطأ في تسجيل النشاط: {str(e)}")

            flash(f'مرحبًا {user.username}! تم تسجيل دخولك بنجاح', 'success')
            return redirect(url_for('index'))
        else:
            # طباعة معلومات تصحيح الأخطاء
            print(f"كلمة المرور غير صحيحة للمستخدم: {username}")

            # رسالة خطأ في حالة عدم صحة اسم المستخدم أو كلمة المرور
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')

    # عرض صفحة تسجيل الدخول
    return render_template('login.html')

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    # تسجيل نشاط تسجيل الخروج إذا كان المستخدم مسجل دخوله
    if g.user:
        user_id = g.user.id
        username = g.user.username
        log_activity('تسجيل خروج', f'تم تسجيل خروج المستخدم {username}', user_id)

    # مسح الجلسة
    session.pop('user_id', None)
    session.clear()

    # إعادة تعيين g.user
    g.user = None

    flash('تم تسجيل خروجك بنجاح', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل - تم تعطيلها للمستخدمين العاديين"""
    # توجيه المستخدم إلى صفحة تسجيل الدخول مع رسالة
    flash('التسجيل متاح فقط من خلال المشرف. يرجى التواصل مع مسؤول النظام للحصول على حساب.', 'info')
    return redirect(url_for('login'))

# صفحات المستخدم
@app.route('/profile')
@login_required
def profile():
    """صفحة الملف الشخصي للمستخدم - عرض معلومات المستخدم فقط"""
    return render_template('profile.html')

@app.route('/my-files')
@login_required
def my_files():
    """صفحة ملفاتي - عرض ملفات المستخدم"""
    # استخراج معايير البحث والفلترة من الطلب
    search_query = request.args.get('search', '')
    file_type = request.args.get('file_type', '')
    sort_by = request.args.get('sort_by', 'date_desc')

    # بناء استعلام قاعدة البيانات - فقط ملفات المستخدم الحالي
    query = File.query.filter_by(user_id=g.user.id)

    # تطبيق البحث إذا تم تحديده
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                File.original_filename.like(search_term),
                File.description.like(search_term)
            )
        )

    # تطبيق فلترة نوع الملف إذا تم تحديدها
    if file_type:
        if file_type == 'image':
            query = query.filter(File.file_type.startswith(IMAGE_FILE_TYPE))
        elif file_type == 'document':
            query = query.filter(
                db.or_(
                    File.file_type == PDF_FILE_TYPE,
                    File.file_type == MSWORD_FILE_TYPE,
                    File.file_type.startswith(DOCX_FILE_TYPE)
                )
            )
        elif file_type == 'spreadsheet':
            query = query.filter(
                db.or_(
                    File.file_type == EXCEL_FILE_TYPE,
                    File.file_type.startswith(XLSX_FILE_TYPE)
                )
            )
        elif file_type == 'text':
            query = query.filter(File.file_type == TEXT_FILE_TYPE)
        elif file_type == 'other':
            query = query.filter(
                db.and_(
                    ~File.file_type.startswith(IMAGE_FILE_TYPE),
                    ~File.file_type.startswith(PDF_FILE_TYPE),
                    ~File.file_type.startswith(MSWORD_FILE_TYPE),
                    ~File.file_type.startswith(DOCX_FILE_TYPE),
                    ~File.file_type.startswith(EXCEL_FILE_TYPE),
                    ~File.file_type.startswith(XLSX_FILE_TYPE),
                    ~File.file_type.startswith(TEXT_FILE_TYPE)
                )
            )

    # تطبيق الترتيب
    if sort_by == 'date_asc':
        query = query.order_by(File.upload_date.asc())
    elif sort_by == 'date_desc':
        query = query.order_by(File.upload_date.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(File.original_filename.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(File.original_filename.desc())
    elif sort_by == 'size_asc':
        query = query.order_by(File.file_size.asc())
    elif sort_by == 'size_desc':
        query = query.order_by(File.file_size.desc())
    else:
        query = query.order_by(File.upload_date.desc())

    # تنفيذ الاستعلام
    files = query.all()

    # إعداد قائمة بأنواع الملفات للفلترة
    file_types = [
        {'value': '', 'label': 'جميع الملفات'},
        {'value': 'image', 'label': 'صور'},
        {'value': 'document', 'label': 'مستندات'},
        {'value': 'spreadsheet', 'label': 'جداول بيانات'},
        {'value': 'text', 'label': 'ملفات نصية'},
        {'value': 'other', 'label': 'أنواع أخرى'}
    ]

    # إعداد قائمة بخيارات الترتيب
    sort_options = [
        {'value': 'date_desc', 'label': 'الأحدث أولاً'},
        {'value': 'date_asc', 'label': 'الأقدم أولاً'},
        {'value': 'name_asc', 'label': 'الاسم (أ-ي)'},
        {'value': 'name_desc', 'label': 'الاسم (ي-أ)'},
        {'value': 'size_asc', 'label': 'الحجم (الأصغر أولاً)'},
        {'value': 'size_desc', 'label': 'الحجم (الأكبر أولاً)'}
    ]

    return render_template(
        'my_files.html',
        files=files,
        search_query=search_query,
        file_type=file_type,
        sort_by=sort_by,
        file_types=file_types,
        sort_options=sort_options
    )

# صفحات المشرف
@app.route('/admin')
@admin_required
def admin_dashboard():
    """لوحة تحكم المشرف"""
    # إحصائيات المستخدمين
    users = User.query.all()
    active_users = [user for user in users if user.is_active]
    admin_users = [user for user in users if user.is_admin]

    # إحصائيات الملفات
    files = File.query.all()
    total_size = sum(file.file_size for file in files)
    image_files = [file for file in files if file.is_image]
    document_files = [file for file in files if file.is_document]
    spreadsheet_files = [file for file in files if file.is_spreadsheet]
    text_files = [file for file in files if file.is_text]

    # إحصائيات سجل الأنشطة
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    total_activities = ActivityLog.query.count()
    login_activities = ActivityLog.query.filter_by(action='تسجيل دخول').count()
    upload_activities = ActivityLog.query.filter_by(action='رفع ملف').count()
    delete_activities = ActivityLog.query.filter_by(action='حذف ملف').count()

    # إحصائيات النشاط حسب المستخدم
    user_activities = {}
    for user in users:
        count = ActivityLog.query.filter_by(user_id=user.id).count()
        if count > 0:
            user_activities[user.username] = count

    # ترتيب المستخدمين حسب عدد الأنشطة (تنازلياً)
    user_activities = dict(sorted(user_activities.items(), key=lambda item: item[1], reverse=True)[:5])

    return render_template(
        'admin/dashboard.html',
        users=users,
        files=files,
        active_users=active_users,
        admin_users=admin_users,
        total_size=total_size,
        image_files=image_files,
        document_files=document_files,
        spreadsheet_files=spreadsheet_files,
        text_files=text_files,
        recent_activities=recent_activities,
        total_activities=total_activities,
        login_activities=login_activities,
        upload_activities=upload_activities,
        delete_activities=delete_activities,
        user_activities=user_activities
    )

@app.route('/admin/users')
@admin_required
def admin_users():
    """إدارة المستخدمين"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/activity-log')
@admin_required
def admin_activity_log():
    """عرض سجل الأنشطة"""
    # استخراج معايير البحث والفلترة من الطلب
    search_query = request.args.get('search', '')
    user_id = request.args.get('user_id', '')
    action_type = request.args.get('action_type', '')
    sort_by = request.args.get('sort_by', 'date_desc')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # بناء استعلام قاعدة البيانات
    query = ActivityLog.query

    # تطبيق البحث إذا تم تحديده
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                ActivityLog.details.like(search_term),
                ActivityLog.action.like(search_term),
                ActivityLog.ip_address.like(search_term)
            )
        )

    # تطبيق فلترة المستخدم إذا تم تحديدها
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)

    # تطبيق فلترة نوع الإجراء إذا تم تحديدها
    if action_type:
        query = query.filter(ActivityLog.action == action_type)

    # تطبيق فلترة التاريخ إذا تم تحديدها
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(ActivityLog.timestamp >= date_from_obj)
        except ValueError:
            flash('تنسيق تاريخ البداية غير صحيح', 'error')

    if date_to:
        try:
            # إضافة يوم واحد لتضمين اليوم المحدد بالكامل
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(ActivityLog.timestamp <= date_to_obj)
        except ValueError:
            flash('تنسيق تاريخ النهاية غير صحيح', 'error')

    # تطبيق الترتيب
    if sort_by == 'date_asc':
        query = query.order_by(ActivityLog.timestamp.asc())
    else:  # date_desc هو الافتراضي
        query = query.order_by(ActivityLog.timestamp.desc())

    # تنفيذ الاستعلام
    logs = query.all()

    # الحصول على قائمة المستخدمين للفلترة
    users = User.query.all()

    # الحصول على قائمة أنواع الإجراءات للفلترة
    action_types = db.session.query(ActivityLog.action).distinct().all()
    action_types = [action[0] for action in action_types]

    # إحصائيات إضافية
    stats = {
        'total': len(logs),
        'logins': len([log for log in logs if log.action == 'تسجيل دخول']),
        'logouts': len([log for log in logs if log.action == 'تسجيل خروج']),
        'uploads': len([log for log in logs if log.action == 'رفع ملف']),
        'deletes': len([log for log in logs if log.action == 'حذف ملف']),
        'user_adds': len([log for log in logs if log.action == 'إضافة مستخدم']),
        'user_edits': len([log for log in logs if log.action == 'تعديل مستخدم']),
        'user_deletes': len([log for log in logs if log.action == 'حذف مستخدم'])
    }

    return render_template(
        'admin/activity_log.html',
        logs=logs,
        users=users,
        action_types=action_types,
        search_query=search_query,
        user_id=user_id,
        action_type=action_type,
        sort_by=sort_by,
        date_from=date_from,
        date_to=date_to,
        stats=stats
    )

@app.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def admin_add_user():
    """إضافة مستخدم جديد"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form

        if not username or not email or not password:
            flash('يرجى ملء جميع الحقول المطلوبة', 'error')
            return redirect(url_for('admin_add_user'))

        # التحقق من عدم وجود مستخدم بنفس اسم المستخدم أو البريد الإلكتروني
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم مستخدم بالفعل', 'error')
            return redirect(url_for('admin_add_user'))

        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return redirect(url_for('admin_add_user'))

        # إنشاء مستخدم جديد
        new_user = User(username=username, email=email, is_admin=is_admin)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # تسجيل نشاط إضافة مستخدم جديد
        log_activity('إضافة مستخدم', f'تم إضافة مستخدم جديد: {username} (ID: {new_user.id})')

        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin/add_user.html')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    """تعديل مستخدم"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        is_active = 'is_active' in request.form

        if not username or not email:
            flash('يرجى ملء جميع الحقول المطلوبة', 'error')
            return redirect(url_for('admin_edit_user', user_id=user.id))

        # التحقق من عدم وجود مستخدم آخر بنفس اسم المستخدم أو البريد الإلكتروني
        username_exists = User.query.filter(User.username == username, User.id != user.id).first()
        if username_exists:
            flash('اسم المستخدم مستخدم بالفعل', 'error')
            return redirect(url_for('admin_edit_user', user_id=user.id))

        email_exists = User.query.filter(User.email == email, User.id != user.id).first()
        if email_exists:
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return redirect(url_for('admin_edit_user', user_id=user.id))

        # تحديث بيانات المستخدم
        user.username = username
        user.email = email
        user.is_admin = is_admin
        user.is_active = is_active

        if password:
            user.set_password(password)

        db.session.commit()

        # تسجيل نشاط تعديل المستخدم
        log_activity('تعديل مستخدم', f'تم تعديل بيانات المستخدم: {username} (ID: {user.id})')

        flash('تم تحديث بيانات المستخدم بنجاح', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """حذف مستخدم"""
    user = User.query.get_or_404(user_id)

    if user.id == session.get('user_id'):
        flash('لا يمكنك حذف حسابك الخاص', 'error')
        return redirect(url_for('admin_users'))

    # تخزين معلومات المستخدم قبل حذفه لاستخدامها في سجل النشاط
    user_info = f"{user.username} (ID: {user.id})"

    # حذف المستخدم
    db.session.delete(user)
    db.session.commit()

    # تسجيل نشاط حذف المستخدم
    log_activity('حذف مستخدم', f'تم حذف المستخدم: {user_info}')

    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('admin_users'))

@app.cli.command("init-db")
def init_db_command():
    """أمر لإنشاء قاعدة البيانات"""
    with app.app_context():
        db.create_all()

        # إنشاء مستخدم مشرف افتراضي إذا لم يكن موجودًا
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("تم إنشاء مستخدم مشرف افتراضي (admin/admin123)")

        print("تم إنشاء قاعدة البيانات بنجاح!")

@app.cli.command("create-admin")
def create_admin_command():
    """أمر لإنشاء مستخدم مشرف جديد"""
    with app.app_context():
        username = input("اسم المستخدم: ")
        email = input("البريد الإلكتروني: ")
        password = input("كلمة المرور: ")

        admin = User(username=username, email=email, is_admin=True)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        print(f"تم إنشاء مستخدم مشرف جديد: {username}")

if __name__ == '__main__':
    # إنشاء قاعدة البيانات عند بدء التطبيق إذا لم تكن موجودة
    with app.app_context():
        # إعادة إنشاء قاعدة البيانات بالكامل
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
        print("تم إنشاء مستخدم مشرف افتراضي (admin/admin123)")
        print("تم إنشاء مستخدم عادي للاختبار (user/user123)")

    # تشغيل التطبيق على جميع واجهات الشبكة (0.0.0.0) بدلاً من localhost فقط
    app.run(host='0.0.0.0', port=5000, debug=True)




















