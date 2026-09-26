from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from .models import db, Task, Submission, User, Subject
from .utils import get_current_date
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import markdown

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----- VISTA DETALLE DE TAREA -----
@tasks_bp.route('/task/<int:task_id>')
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    description_html = markdown.markdown(task.description)
    return render_template('view_task.html', task=task, description_html=description_html)

# ----- DESCARGA DE ARCHIVO (CORREGIDO) -----
@tasks_bp.route('/download/<int:submission_id>')
@login_required
def download_submission(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    if not (current_user.id == sub.student_id or current_user.role in ['admin', 'teacher']):
        flash('No tienes permiso')
        return redirect(url_for('tasks.index'))
    
    # Ya no concatenamos con current_app.root_path, usamos la ruta absoluta guardada
    file_path = sub.file_path
    if not os.path.exists(file_path):
        flash('El archivo ya no existe')
        return redirect(request.referrer or url_for('tasks.index'))
    return send_file(file_path, as_attachment=False)

# ----- ADMIN / TEACHER (sin cambios) -----
@tasks_bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role not in ['admin', 'teacher']:
        flash('No tienes permiso')
        return redirect(url_for('attendance.dashboard'))
    tasks = Task.query.order_by(Task.due_date.desc()).all()
    return render_template('admin_tasks.html', tasks=tasks)

@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if current_user.role not in ['admin', 'teacher']:
        flash('No tienes permiso')
        return redirect(url_for('attendance.dashboard'))
    subjects = Subject.query.order_by(Subject.name).all()
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        if not all([subject_id, title, description, due_date]):
            flash('Todos los campos son obligatorios')
        else:
            try:
                due = datetime.strptime(due_date, '%Y-%m-%d').date()
                subject = Subject.query.get(int(subject_id))
                if not subject:
                    flash('Materia no válida')
                    return render_template('create_task.html', subjects=subjects)
            except ValueError:
                flash('Fecha inválida')
                return render_template('create_task.html', subjects=subjects)
            task = Task(subject_id=subject.id, title=title, description=description, due_date=due)
            db.session.add(task)
            db.session.commit()
            flash('Tarea creada exitosamente')
            return redirect(url_for('tasks.admin_dashboard'))
    return render_template('create_task.html', subjects=subjects)

@tasks_bp.route('/task/<int:task_id>/submissions')
@login_required
def view_submissions(task_id):
    if current_user.role not in ['admin', 'teacher']:
        flash('No tienes permiso')
        return redirect(url_for('attendance.dashboard'))
    task = Task.query.get_or_404(task_id)
    submissions = Submission.query.filter_by(task_id=task_id).all()
    students = User.query.filter_by(role='student').all()
    sub_map = {sub.student_id: sub for sub in submissions}
    return render_template('admin_submissions.html', task=task, students=students, sub_map=sub_map)

@tasks_bp.route('/submission/<int:submission_id>/status', methods=['POST'])
@login_required
def update_submission_status(submission_id):
    if current_user.role not in ['admin', 'teacher']:
        flash('No tienes permiso')
        return redirect(url_for('attendance.dashboard'))
    sub = Submission.query.get_or_404(submission_id)
    action = request.form.get('action')
    if action == 'accept':
        sub.status = 'accepted'
        sub.feedback = None
    elif action == 'reject':
        sub.status = 'rejected'
        sub.feedback = request.form.get('feedback', '').strip()
        if not sub.feedback:
            flash('Debes proporcionar un comentario para rechazar')
            return redirect(request.referrer)
    else:
        flash('Acción no válida')
        return redirect(request.referrer)
    db.session.commit()
    flash(f'Tarea {sub.status}')
    return redirect(request.referrer)

# ----- ELIMINAR TAREA (Admin) (CORREGIDO) -----
@tasks_bp.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    if current_user.role != 'admin':
        flash('Solo administradores pueden eliminar tareas')
        return redirect(url_for('tasks.admin_dashboard'))
    task = Task.query.get_or_404(task_id)
    # Eliminar submissions y archivos asociados
    for sub in task.submissions:
        # Usamos la ruta absoluta guardada
        file_path = sub.file_path
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.delete(sub)
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada correctamente')
    return redirect(url_for('tasks.admin_dashboard'))

# ----- GESTIÓN DE MATERIAS (sin cambios) -----
@tasks_bp.route('/subjects')
@login_required
def admin_subjects():
    if current_user.role not in ['admin', 'teacher']:
        flash('No tienes permiso')
        return redirect(url_for('attendance.dashboard'))
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin_subjects.html', subjects=subjects)

@tasks_bp.route('/subject/create', methods=['GET', 'POST'])
@login_required
def create_subject():
    if current_user.role not in ['admin', 'teacher']:
        flash('No tienes permiso')
        return redirect(url_for('attendance.dashboard'))
    if request.method == 'POST':
        name = request.form.get('name').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('El nombre de la materia es obligatorio')
        elif Subject.query.filter_by(name=name).first():
            flash('Ya existe una materia con ese nombre')
        else:
            subject = Subject(name=name, description=description)
            db.session.add(subject)
            db.session.commit()
            flash('Materia creada exitosamente')
            return redirect(url_for('tasks.admin_subjects'))
    return render_template('create_subject.html')

@tasks_bp.route('/subject/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if current_user.role != 'admin':
        flash('Solo administradores pueden eliminar materias')
        return redirect(url_for('tasks.admin_subjects'))
    subject = Subject.query.get_or_404(subject_id)
    if subject.tasks:
        flash('No se puede eliminar una materia que tiene tareas asociadas')
        return redirect(url_for('tasks.admin_subjects'))
    db.session.delete(subject)
    db.session.commit()
    flash('Materia eliminada correctamente')
    return redirect(url_for('tasks.admin_subjects'))

@tasks_bp.route('/subject/<int:subject_id>/students')
@login_required
def subject_students(subject_id):
    if current_user.role not in ['admin', 'teacher']:
        flash('No tienes permiso')
        return redirect(url_for('attendance.dashboard'))
    subject = Subject.query.get_or_404(subject_id)
    students = subject.students.all()
    return render_template('subject_students.html', subject=subject, students=students)

# ----- ESTUDIANTE: GESTIÓN DE INSCRIPCIONES (sin cambios) -----
@tasks_bp.route('/my_subjects')
@login_required
def student_subjects():
    if current_user.role != 'student':
        flash('Acceso solo para estudiantes')
        return redirect(url_for('tasks.index'))
    all_subjects = Subject.query.order_by(Subject.name).all()
    my_subjects = current_user.subjects.all()
    my_subject_ids = [s.id for s in my_subjects]
    return render_template('student_subjects.html', all_subjects=all_subjects, my_subject_ids=my_subject_ids)

@tasks_bp.route('/enroll/<int:subject_id>', methods=['POST'])
@login_required
def enroll_subject(subject_id):
    if current_user.role != 'student':
        flash('Acción no permitida')
        return redirect(url_for('tasks.index'))
    subject = Subject.query.get_or_404(subject_id)
    if subject not in current_user.subjects:
        current_user.subjects.append(subject)
        db.session.commit()
        flash(f'Te has inscrito en {subject.name}')
    else:
        flash('Ya estás inscrito en esta materia')
    return redirect(url_for('tasks.student_subjects'))

@tasks_bp.route('/unenroll/<int:subject_id>', methods=['POST'])
@login_required
def unenroll_subject(subject_id):
    if current_user.role != 'student':
        flash('Acción no permitida')
        return redirect(url_for('tasks.index'))
    subject = Subject.query.get_or_404(subject_id)
    if subject in current_user.subjects:
        current_user.subjects.remove(subject)
        db.session.commit()
        flash(f'Te has dado de baja de {subject.name}')
    else:
        flash('No estás inscrito en esta materia')
    return redirect(url_for('tasks.student_subjects'))

# ----- SUBIR ARCHIVO (CORREGIDO) -----
@tasks_bp.route('/upload/<int:task_id>', methods=['POST'])
@login_required
def upload_submission(task_id):
    if current_user.role != 'student':
        flash('No tienes permiso')
        return redirect(url_for('attendance.dashboard'))
    task = Task.query.get_or_404(task_id)
    if get_current_date() > task.due_date:
        flash('La fecha límite ya pasó')
        return redirect(url_for('tasks.student_dashboard'))
    if 'file' not in request.files:
        flash('No se seleccionó archivo')
        return redirect(url_for('tasks.student_dashboard'))
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó archivo')
        return redirect(url_for('tasks.student_dashboard'))
    if not allowed_file(file.filename):
        flash('Solo se permiten archivos PDF')
        return redirect(url_for('tasks.student_dashboard'))

    # Guardar archivo en /app/uploads (ruta absoluta)
    filename = secure_filename(f"{current_user.id}_{task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
    upload_folder = '/app/uploads'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    submission = Submission.query.filter_by(task_id=task_id, student_id=current_user.id).first()
    if submission:
        if submission.status == 'accepted':
            flash('Esta tarea ya fue aceptada, no se puede modificar')
            if os.path.exists(file_path):
                os.remove(file_path)
            return redirect(url_for('tasks.student_dashboard'))
        # Eliminar archivo anterior (usando la ruta absoluta guardada)
        old_path = submission.file_path
        if os.path.exists(old_path):
            os.remove(old_path)
        # Actualizar con la nueva ruta absoluta
        submission.file_path = file_path  # ruta absoluta
        submission.updated_at = datetime.utcnow()
        submission.status = 'submitted'
        submission.feedback = None
    else:
        submission = Submission(
            task_id=task_id,
            student_id=current_user.id,
            file_path=file_path,  # ruta absoluta
            status='submitted'
        )
        db.session.add(submission)

    db.session.commit()
    flash('Archivo subido correctamente')
    return redirect(url_for('tasks.student_dashboard'))

# ----- STUDENT DASHBOARD (sin cambios) -----
@tasks_bp.route('/')
@login_required
def index():
    if current_user.role in ['admin', 'teacher']:
        return redirect(url_for('tasks.admin_dashboard'))
    else:
        return redirect(url_for('tasks.student_dashboard'))

@tasks_bp.route('/student')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('tasks.admin_dashboard'))
    my_subject_ids = [s.id for s in current_user.subjects.all()]
    tasks = Task.query.filter(Task.subject_id.in_(my_subject_ids), Task.due_date >= get_current_date()).order_by(Task.due_date).all() if my_subject_ids else []
    submissions = Submission.query.filter_by(student_id=current_user.id).all()
    sub_by_task = {sub.task_id: sub for sub in submissions}
    accepted_count = Submission.query.filter_by(student_id=current_user.id, status='accepted').count()
    return render_template('student_tasks.html', tasks=tasks, sub_by_task=sub_by_task, accepted_count=accepted_count)
