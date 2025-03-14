from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret-key-random'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cấu hình upload avatar
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'avatars')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255), nullable=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, done
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    finished_time = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)        # Ngày dự kiến hoàn thành
    priority = db.Column(db.String(20), default='trung bình') # cao, trung bình, thấp
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

# -------------------- HÀM HỖ TRỢ --------------------
def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# -------------------- ROUTES CHÍNH --------------------
@app.route('/')
def home():
    user = current_user()
    if user:
        tasks = Task.query.filter_by(user_id=user.id).order_by(Task.id.desc()).all()
    else:
        tasks = []
    return render_template('index.html', user=user, tasks=tasks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Mật khẩu và xác nhận mật khẩu không khớp!")
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại!")
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công, hãy đăng nhập.")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if user.is_blocked:
                flash('Tài khoản của bạn đã bị khóa!')
                return redirect(url_for('login'))
            session['user_id'] = user.id
            flash('Đăng nhập thành công!')
            return redirect(url_for('home'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Bạn đã đăng xuất.')
    return redirect(url_for('home'))

# -------------------- ROUTES ADMIN --------------------
@app.route('/admin')
def admin():
    user = current_user()
    if not user or not user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('home'))
    if user.is_blocked:
        flash('Tài khoản của bạn đã bị khóa!')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin.html', user=user, users=users)

@app.route('/admin/block_user/<int:user_id>')
def block_user(user_id):
    user = current_user()
    if not user or not user.is_admin:
        flash('Bạn không có quyền.')
        return redirect(url_for('home'))
    target_user = User.query.get_or_404(user_id)
    target_user.is_blocked = True
    db.session.commit()
    flash(f'Đã khóa user {target_user.username}.')
    return redirect(url_for('admin'))

@app.route('/admin/unblock_user/<int:user_id>')
def unblock_user(user_id):
    user = current_user()
    if not user or not user.is_admin:
        flash('Bạn không có quyền.')
        return redirect(url_for('home'))
    target_user = User.query.get_or_404(user_id)
    target_user.is_blocked = False
    db.session.commit()
    flash(f'Đã mở khóa user {target_user.username}.')
    return redirect(url_for('admin'))
@app.route('/admin/user_tasks/<int:user_id>')
def admin_user_tasks(user_id):
    user = current_user()
    # Chỉ cho admin truy cập
    if not user or not user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('home'))
    
    target_user = User.query.get_or_404(user_id)
    tasks = Task.query.filter_by(user_id=target_user.id).order_by(Task.id.desc()).all()
    return render_template('admin_user_tasks.html', user=user, target_user=target_user, tasks=tasks)

@app.route('/admin/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = current_user()
    if not user or not user.is_admin:
        flash('Bạn không có quyền.')
        return redirect(url_for('home'))
    if user.is_blocked:
        return redirect(url_for('home'))
    target_user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_password = request.form['new_password']
        target_user.password = generate_password_hash(new_password)
        db.session.commit()
        flash(f'Đã đổi mật khẩu cho {target_user.username}.')
        return redirect(url_for('admin'))
    return render_template('reset_password.html', target_user=target_user)

# -------------------- ROUTES QUẢN LÝ CATEGORY --------------------
@app.route('/categories', methods=['GET', 'POST'])
def categories():
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash('Tạo category thành công.')
        return redirect(url_for('categories'))
    categories = Category.query.all()
    return render_template('categories.html', user=user, categories=categories)

@app.route('/categories/edit/<int:cat_id>', methods=['GET', 'POST'])
def edit_category(cat_id):
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập.')
        return redirect(url_for('login'))
    cat = Category.query.get_or_404(cat_id)
    if request.method == 'POST':
        new_name = request.form['name']
        cat.name = new_name
        db.session.commit()
        flash('Cập nhật phân loại thành công.')
        return redirect(url_for('categories'))
    return render_template('edit_category.html', user=user, category=cat)

@app.route('/categories/delete/<int:cat_id>', methods=['POST'])
def delete_category(cat_id):
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập.')
        return redirect(url_for('login'))
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Đã xóa phân loại.')
    return redirect(url_for('categories'))

# -------------------- ROUTES UPLOAD AVATAR --------------------
@app.route('/upload_avatar', methods=['GET', 'POST'])
def upload_avatar():
    user = current_user()
    if not user:
        flash("Bạn cần đăng nhập để upload avatar.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'avatar' not in request.files:
            flash('Không có file nào được chọn.')
            return redirect(request.url)
        file = request.files['avatar']
        if file.filename == '':
            flash('Bạn chưa chọn file.')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        user.avatar = f'avatars/{filename}'
        db.session.commit()
        flash("Cập nhật avatar thành công!")
        return redirect(url_for('home'))
    return render_template('upload_avatar.html', user=user)

# -------------------- ROUTES QUẢN LÝ TASK --------------------
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập để quản lý công việc.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content', '')
        priority = request.form.get('priority', 'trung bình')
        due_date_str = request.form.get('due_date', '')
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
        # Lấy phân loại (category) từ trường 'category'
        category_id = request.form.get('category', None)
        new_task = Task(
            title=title,
            content=content,
            user_id=user.id,
            due_date=due_date,
            priority=priority,
            category_id=category_id if category_id and category_id != '' else None
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Tạo task thành công.')
        return redirect(url_for('tasks'))
    page = request.args.get('page', 1, type=int)
    pagination = Task.query.filter_by(user_id=user.id).order_by(Task.id.desc()).paginate(page=page, per_page=5)
    tasks_list = pagination.items
    categories = Category.query.all()
    return render_template('tasks.html', user=user, tasks=tasks_list, categories=categories, pagination=pagination)

@app.route('/tasks/finish/<int:task_id>', methods=['POST'])
def finish_task(task_id):
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập.')
        return redirect(url_for('login'))
    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id and not user.is_admin:
        flash('Bạn không có quyền.')
        return redirect(url_for('tasks'))
    task.status = 'done'
    task.finished_time = datetime.utcnow()
    db.session.commit()
    flash('Đã đánh dấu task hoàn thành.')
    return redirect(url_for('tasks'))

@app.route('/delete_tasks', methods=['POST'])
def delete_tasks():
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập.')
        return redirect(url_for('login'))
    task_ids = request.form.getlist('task_ids')
    for tid in task_ids:
        task = Task.query.get(tid)
        if task and (task.user_id == user.id or user.is_admin):
            db.session.delete(task)
    db.session.commit()
    flash('Đã xóa các task được chọn.')
    return redirect(url_for('tasks'))

@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập.')
        return redirect(url_for('login'))
    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id and not user.is_admin:
        flash('Bạn không có quyền.')
        return redirect(url_for('tasks'))
    db.session.delete(task)
    db.session.commit()
    flash('Đã xóa task.')
    return redirect(url_for('tasks'))

# -------------------- KHỞI CHẠY APP --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='ben2xx4').first():
            admin_user = User(
                username='ben2xx4',
                password=generate_password_hash('ben2xx4'),
                is_admin=True,
                is_blocked=False
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
