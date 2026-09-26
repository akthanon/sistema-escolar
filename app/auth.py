from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User
from .utils import get_current_date

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('attendance.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(request.args.get('next') or url_for('attendance.dashboard'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Auto-registro (cualquier persona)
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('attendance.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email', '')

        if not all([username, password, first_name, last_name]):
            flash('Todos los campos son obligatorios')
        elif User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe')
        elif len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres')
        else:
            nuevo = User(
                username=username,
                role='student',
                first_name=first_name,
                last_name=last_name,
                email=email,
                created_by=None  # se registró a sí mismo
            )
            nuevo.set_password(password)
            db.session.add(nuevo)
            db.session.commit()
            flash('Registro exitoso. Ya puedes iniciar sesión.')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

# Registro por admin/profesor (con límite de 50 totales por día)
@auth.route('/register_student', methods=['GET', 'POST'])
@login_required
def register_student():
    if current_user.role not in ['admin', 'teacher']:
        flash('No tienes permiso para registrar estudiantes')
        return redirect(url_for('attendance.dashboard'))

    today = get_current_date()
    total_registrados_hoy = User.query.filter(User.created_at >= today).count()
    MAX_REGISTROS_DIA = 50
    if total_registrados_hoy >= MAX_REGISTROS_DIA:
        flash(f'Límite de {MAX_REGISTROS_DIA} registros totales por día alcanzado')
        return redirect(url_for('attendance.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email', '')

        if not all([username, password, first_name, last_name]):
            flash('Todos los campos son obligatorios')
        elif User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe')
        elif len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres')
        else:
            nuevo = User(
                username=username,
                role='student',
                first_name=first_name,
                last_name=last_name,
                email=email,
                created_by=current_user.id
            )
            nuevo.set_password(password)
            db.session.add(nuevo)
            db.session.commit()
            flash('Estudiante registrado exitosamente')
            return redirect(url_for('auth.register_student'))

    return render_template('register_student.html')
