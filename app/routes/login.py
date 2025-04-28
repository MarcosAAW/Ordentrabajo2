from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user
from app.models import Login, db
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

login_bp = Blueprint('login', __name__)

@login_bp.before_request
def make_session_permanent():
    session.permanent = True

@login_bp.before_request
def check_session_expiration():
    session_lifetime = timedelta(seconds=current_app.permanent_session_lifetime.total_seconds())
    now = datetime.utcnow()

    # Si no existe la clave 'last_activity', inicializarla
    if 'last_activity' not in session:
        session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S')

    # Convertir la última actividad a un objeto datetime
    last_activity_time = datetime.strptime(session['last_activity'], '%Y-%m-%d %H:%M:%S')

    # Verificar si la sesión ha expirado
    if 'session_expired' in session:
        session.pop('session_expired')  # Limpiar la bandera para evitar duplicados
        return redirect(url_for('login.login'))

    if now - last_activity_time > session_lifetime:
        print("La sesión ha expirado. Cerrando sesión...")
        logout_user()
        session.clear()  # Limpiar la sesión
        session['session_expired'] = True  # Establecer una bandera para evitar duplicados
        flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning')
        return redirect(url_for('login.login'))

    # Solo actualizar la última actividad si no ha expirado
    if now - last_activity_time <= session_lifetime:
        session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S')

    if 'logout_success' in session:
        flash('Has cerrado sesión exitosamente.', 'success')
        session.pop('logout_success')  # Limpiar la bandera

    if 'login_success' in session:
        session.pop('login_success')  # Limpiar la bandera
        return redirect(url_for('main_page'))

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario'].strip()
        password = request.form['senha'].strip()

        # Buscar al usuario en la base de datos
        user = Login.query.filter_by(Usuario=username).first()

        if user:
            if check_password_hash(user.Senha, password):
                login_user(user)
                session['login_success'] = True  # Establecer bandera para inicio de sesión exitoso
                return redirect(url_for('main_page'))
            else:
                flash('Contraseña incorrecta', 'danger')
        else:
            flash('Usuario no encontrado', 'danger')

    return render_template('login.html')

@login_bp.route('/create', methods=['GET', 'POST'])
def create():
    roles = ['Administrador', 'Usuario']  # Aquí puedes reemplazar con una consulta a la base de datos si los roles están almacenados allí

    if request.method == 'POST':
        username = request.form['usuario'].strip()
        password = request.form['senha'].strip()
        role = request.form['rol']

        # Verificar si el usuario ya existe
        user = Login.query.filter_by(Usuario=username).first()
        if user:
            flash('El usuario ya existe', 'danger')
            return redirect(url_for('login.create'))

        # Crear un nuevo usuario y agregarlo a la base de datos
        new_user = Login(Usuario=username, Rol=role)
        if hasattr(new_user, 'set_password'):
            new_user.set_password(password, method='pbkdf2:sha256')
        else:
            new_user.Senha = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario creado con éxito', 'success')
        return redirect(url_for('login.create'))

    return render_template('login/create.html', roles=roles)

@login_bp.route('/list', methods=['GET'])
def list():
    users = Login.query.all()  # Obtener todos los usuarios de la base de datos
    return render_template('login/list.html', users=users)

@login_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    user = Login.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('login.list'))

    if request.method == 'POST':
        user.Usuario = request.form['usuario'].strip()
        user.Rol = request.form['rol']
        if 'senha' in request.form and request.form['senha'].strip():
            user.Senha = generate_password_hash(request.form['senha'].strip(), method='pbkdf2:sha256')
        db.session.commit()
        flash('Usuario actualizado con éxito', 'success')
        return redirect(url_for('login.list'))

    roles = ['Administrador', 'Usuario']  # Aquí puedes reemplazar con una consulta a la base de datos si los roles están almacenados allí
    return render_template('login/edit.html', user=user, roles=roles)

@login_bp.route('/delete/<int:user_id>', methods=['POST'])
def delete(user_id):
    user = Login.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('login.list'))

    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado con éxito', 'success')
    return redirect(url_for('login.list'))

@login_bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('login.login'))

@login_bp.before_request
def debug_session():
    print(f"Session data: {session.items()}")
    print(f"Session permanent: {session.permanent}")

