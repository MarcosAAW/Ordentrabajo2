from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, MotivosSalida

motivos_salida_bp = Blueprint('motivos_salida', __name__)

@motivos_salida_bp.route('/motivos_salida')
def lista_motivos_salida():
    motivos = MotivosSalida.query.all()
    return render_template('motivos_salida/lista.html', motivos=motivos)

@motivos_salida_bp.route('/motivos_salida/crear', methods=['GET', 'POST'])
def crear_motivo_salida():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        
        if not descripcion:
            flash('La descripción es obligatoria', 'error')
        else:
            try:
                nuevo_motivo = MotivosSalida(Descripcion=descripcion)
                db.session.add(nuevo_motivo)
                db.session.commit()
                flash('Motivo de salida creado exitosamente', 'success')
                return redirect(url_for('motivos_salida.lista_motivos_salida'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear el motivo de salida: {str(e)}', 'error')
    
    return render_template('motivos_salida/crear.html')

@motivos_salida_bp.route('/motivos_salida/editar/<int:id>', methods=['GET', 'POST'])
def editar_motivo_salida(id):
    motivo = MotivosSalida.query.get_or_404(id)
    
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        
        if not descripcion:
            flash('La descripción es obligatoria', 'error')
        else:
            try:
                motivo.Descripcion = descripcion
                db.session.commit()
                flash('Motivo de salida actualizado exitosamente', 'success')
                return redirect(url_for('motivos_salida.lista_motivos_salida'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar el motivo de salida: {str(e)}', 'error')
    
    return render_template('motivos_salida/editar.html', motivo=motivo)

@motivos_salida_bp.route('/motivos_salida/eliminar/<int:id>', methods=['POST'])
def eliminar_motivo_salida(id):
    motivo = MotivosSalida.query.get_or_404(id)
    try:
        db.session.delete(motivo)
        db.session.commit()
        flash('Motivo de salida eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el motivo de salida: {str(e)}', 'error')
    return redirect(url_for('motivos_salida.lista_motivos_salida'))
