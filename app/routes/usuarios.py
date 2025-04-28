from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, UsuariosVehiculos

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios')
def lista_usuarios():
    usuarios = UsuariosVehiculos.query.all()
    return render_template('usuarios/lista.html', usuarios=usuarios)

@usuarios_bp.route('/usuarios/crear', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        try:
            nuevo_usuario = UsuariosVehiculos(
                Nombre=request.form['nombre'],
                Apellido=request.form['apellido'],
                DocumentoIdentidad=request.form['documento_identidad'],
                Telefono=request.form['telefono'],
                Correo=request.form['correo'],
                Cargo=request.form['cargo']
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios.lista_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el usuario: {str(e)}', 'error')
            print(f"Error: {str(e)}")

    return render_template('usuarios/crear.html')

@usuarios_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = UsuariosVehiculos.query.get_or_404(id)

    if request.method == 'POST':
        try:
            usuario.Nombre = request.form['nombre']
            usuario.Apellido = request.form['apellido']
            usuario.DocumentoIdentidad = request.form['documento_identidad']
            usuario.Telefono = request.form['telefono']
            usuario.Correo = request.form['correo']
            usuario.Cargo = request.form['cargo']

            db.session.commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('usuarios.lista_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el usuario: {str(e)}', 'error')

    return render_template('usuarios/editar.html', usuario=usuario)

@usuarios_bp.route('/usuarios/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    usuario = UsuariosVehiculos.query.get_or_404(id)
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el usuario: {str(e)}', 'error')
    return redirect(url_for('usuarios.lista_usuarios'))
