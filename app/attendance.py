from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import db, User, Attendance, Backup
from .utils import generate_token, get_current_hour_slot, verify_token, get_current_date
import qrcode
from io import BytesIO
import base64
import json
from datetime import datetime

attendance = Blueprint('attendance', __name__)

"""
@attendance.route('/')
@login_required
def dashboard():
    date = get_current_date()
    user = current_user

    if user.role in ['admin', 'teacher']:
        students = User.query.filter_by(role='student').all()
        attendances_by_student = {}
        total_all = 0
        for student in students:
            atts = Attendance.query.filter_by(user_id=student.id, date=date).order_by(Attendance.timestamp.desc()).all()
            attendances_by_student[student.id] = atts
            total_all += len(atts)
        backups = Backup.query.order_by(Backup.created_at.desc()).all() if user.role == 'admin' else []
        return render_template('dashboard_admin.html',
                               students=students,
                               attendances_by_student=attendances_by_student,
                               date=date,
                               total_all=total_all,
                               backups=backups)
    else:
        my_attendances = Attendance.query.filter_by(user_id=user.id, date=date).order_by(Attendance.timestamp.desc()).all()
        total_mine = len(my_attendances)
        return render_template('dashboard_student.html',
                               attendances=my_attendances,
                               total=total_mine,
                               date=date)
"""

@attendance.route('/')
@login_required
def dashboard():
    user = current_user

    if user.role in ['admin', 'teacher']:
        students = User.query.filter_by(role='student').all()
        attendances_by_student = {}
        total_all = 0
        for student in students:
            # Todas las asistencias, sin filtro de fecha
            atts = Attendance.query.filter_by(user_id=student.id).order_by(Attendance.date.desc(), Attendance.timestamp.desc()).all()
            attendances_by_student[student.id] = atts
            total_all += len(atts)
        backups = Backup.query.order_by(Backup.created_at.desc()).all() if user.role == 'admin' else []
        return render_template('dashboard_admin.html',
                               students=students,
                               attendances_by_student=attendances_by_student,
                               total_all=total_all,
                               backups=backups)
    else:
        # Todas las asistencias del estudiante
        my_attendances = Attendance.query.filter_by(user_id=user.id).order_by(Attendance.date.desc(), Attendance.timestamp.desc()).all()
        total_mine = len(my_attendances)
        return render_template('dashboard_student.html',
                               attendances=my_attendances,
                               total=total_mine)

@attendance.route('/qr')
@login_required
def show_qr():
    if current_user.role not in ['teacher', 'admin']:
        flash('No tienes permiso para ver el QR')
        return redirect(url_for('attendance.dashboard'))
    slot = get_current_hour_slot()
    token = generate_token(slot)
    base_url = request.host_url.rstrip('/')
    qr_url = f"{base_url}{url_for('attendance.record_attendance')}?token={token}"
    img = qrcode.make(qr_url)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return render_template('qr_display.html', qr_image=img_str, qr_url=qr_url, slot=slot, token=token)

@attendance.route('/asistencia')
def record_attendance():
    token = request.args.get('token')
    if not token:
        flash('Token no proporcionado')
        return redirect(url_for('auth.login'))
    slot = get_current_hour_slot()
    if not verify_token(token, slot):
        flash('Token inválido o expirado')
        return redirect(url_for('auth.login'))
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.full_path))
    if current_user.role != 'student':
        flash('Solo estudiantes pueden registrar asistencia')
        return redirect(url_for('attendance.dashboard'))
    date = get_current_date()
    if Attendance.query.filter_by(user_id=current_user.id, date=date, hour_slot=slot).first():
        flash('Ya registraste asistencia en este horario')
        return redirect(url_for('attendance.dashboard'))
    nueva = Attendance(user_id=current_user.id, date=date, hour_slot=slot, token_used=token)
    db.session.add(nueva)
    db.session.commit()
    flash('Asistencia registrada correctamente')
    return redirect(url_for('attendance.dashboard'))

@attendance.route('/reset_attendance', methods=['POST'])
@login_required
def reset_attendance():
    if current_user.role != 'admin':
        flash('Solo administradores pueden reiniciar')
        return redirect(url_for('attendance.dashboard'))
    date = get_current_date()
    asistencias = Attendance.query.all() 
    #asistencias = Attendance.query.filter_by(date=date).all()
    if not asistencias:
        flash('No hay asistencias para reiniciar')
        return redirect(url_for('attendance.dashboard'))
    datos = []
    for att in asistencias:
        datos.append({
            'user_id': att.user_id,
            'date': att.date.isoformat(),
            'hour_slot': att.hour_slot,
            'timestamp': att.timestamp.isoformat() if att.timestamp else None,
            'token_used': att.token_used
        })
    total_backups = Backup.query.count()
    desc = f"Backup_{total_backups+1}_asistencias_{date}"
    backup = Backup(data=json.dumps(datos), description=desc)
    db.session.add(backup)
    for att in asistencias:
        db.session.delete(att)
    db.session.commit()
    flash('Asistencias reiniciadas y respaldadas')
    return redirect(url_for('attendance.dashboard'))

@attendance.route('/load_backup/<int:backup_id>')
@login_required
def load_backup(backup_id):
    if current_user.role != 'admin':
        flash('Solo administradores pueden cargar backups')
        return redirect(url_for('attendance.dashboard'))
    backup = Backup.query.get_or_404(backup_id)
    datos = json.loads(backup.data)
    date = get_current_date()
    Attendance.query.filter_by(date=date).delete()
    for item in datos:
        if not User.query.get(item['user_id']):
            continue
        att = Attendance(
            user_id=item['user_id'],
            date=datetime.fromisoformat(item['date']).date(),
            hour_slot=item['hour_slot'],
            timestamp=datetime.fromisoformat(item['timestamp']) if item['timestamp'] else None,
            token_used=item.get('token_used')
        )
        db.session.add(att)
    db.session.commit()
    flash('Backup cargado exitosamente')
    return redirect(url_for('attendance.dashboard'))

@attendance.route('/delete_student/<int:user_id>', methods=['POST'])
@login_required
def delete_student(user_id):
    if current_user.role != 'admin':
        flash('Solo administradores pueden eliminar estudiantes')
        return redirect(url_for('attendance.dashboard'))
    student = User.query.get_or_404(user_id)
    if student.role != 'student':
        flash('Solo se pueden eliminar estudiantes')
        return redirect(url_for('attendance.dashboard'))
    Attendance.query.filter_by(user_id=student.id).delete()
    db.session.delete(student)
    db.session.commit()
    flash('Estudiante eliminado correctamente')
    return redirect(url_for('attendance.dashboard'))
