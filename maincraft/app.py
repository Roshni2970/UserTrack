from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Role, AuditLog
from datetime import datetime

import os
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key_usertrack_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_action(action, target, notes=""):
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        actor_name=current_user.username if current_user.is_authenticated else "System",
        action=action,
        target=target,
        ip_address=request.remote_addr,
        notes=notes
    )
    db.session.add(log)
    db.session.commit()

# --- Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.status != 'Active':
                flash('Your account is deactivated.', 'error')
                return redirect(url_for('login'))
            login_user(user, remember=True if request.form.get('remember') else False)
            log_action('Login', user.email)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_action('Logout', current_user.email)
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(status='Active').count()
    inactive_users = User.query.filter_by(status='Inactive').count()
    
    # Recent activity
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                           total_users=total_users, 
                           active_users=active_users, 
                           inactive_users=inactive_users,
                           recent_logs=recent_logs)

@app.route('/users')
@login_required
def users_list():
    users = User.query.all()
    return render_template('users_list.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
@login_required
def user_new():
    roles = Role.query.all()
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or username already exists.', 'error')
            return redirect(url_for('user_new'))
            
        new_user = User(
            username=username,
            email=email,
            full_name=request.form.get('full_name'),
            role_id=request.form.get('role_id'),
            department=request.form.get('department'),
            status=request.form.get('status', 'Active'),
            phone=request.form.get('phone'),
            notes=request.form.get('notes')
        )
        if request.form.get('dob'):
            new_user.dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()
            
        new_user.set_password(request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
        log_action('Create User', new_user.email)
        flash('User created successfully.', 'success')
        return redirect(url_for('users_list'))
    
    return render_template('user_form.html', roles=roles, user=None)

@app.route('/users/<int:id>')
@login_required
def user_profile(id):
    user = User.query.get_or_404(id)
    activity = AuditLog.query.filter_by(user_id=user.id).order_by(AuditLog.timestamp.desc()).all()
    return render_template('user_profile.html', user=user, activity=activity)

@app.route('/roles')
@login_required
def roles_list():
    roles = Role.query.all()
    return render_template('roles.html', roles=roles)

@app.route('/logs')
@login_required
def logs_list():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/archive')
@login_required
def archive():
    archived_users = User.query.filter_by(status='Deleted').all()
    return render_template('archive.html', archived_users=archived_users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Role.query.first():
            roles = [Role(name='Super Admin'), Role(name='Admin'), Role(name='Moderator'), Role(name='Viewer')]
            db.session.add_all(roles)
            db.session.commit()
            
            admin_user = User(
                username='admin',
                email='admin@usertrack.com',
                full_name='System Administrator',
                role_id=roles[0].id,
                status='Active'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            
    app.run(debug=True)
