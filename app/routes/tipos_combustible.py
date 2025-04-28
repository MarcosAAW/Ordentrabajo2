from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, TipoCombustible

tipos_combustible_bp = Blueprint('tipos_combustible', __name__)

@tipos_combustible_bp.route('/tipos_combustible')
def lista_tipos_combustible():
    tipos = TipoCombustible.query.all()
    return render_template('tipos_combustible/lista.html', tipos_combustible=tipos)

@tipos_combustible_bp.route('/tipos_combustible/crear', methods=['GET', 'POST'])
def crear_tipo_combustible():
    if request.method == 'POST':
        try:
            nuevo_tipo = TipoCombustible(
                Tipo=request.form['tipo']
            )
            db.session.add(nuevo_tipo)
            db.session.commit()
            flash('Tipo de combustible creado exitosamente', 'success')
            return redirect(url_for('tipos_combustible.lista_tipos_combustible'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el tipo de combustible: {str(e)}', 'error')
            print(f"Error: {str(e)}")
    return render_template('tipos_combustible/crear.html')

@tipos_combustible_bp.route('/tipos_combustible/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_combustible(id):
    tipo = TipoCombustible.query.get_or_404(id)
    if request.method == 'POST':
        try:
            tipo.Tipo = request.form['tipo']
            db.session.commit()
            flash('Tipo de combustible actualizado exitosamente', 'success')
            return redirect(url_for('tipos_combustible.lista_tipos_combustible'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el tipo de combustible: {str(e)}', 'error')
    return render_template('tipos_combustible/editar.html', tipo_combustible=tipo)

@tipos_combustible_bp.route('/tipos_combustible/eliminar/<int:id>', methods=['POST'])
def eliminar_tipo_combustible(id):
    tipo = TipoCombustible.query.get_or_404(id)
    try:
        db.session.delete(tipo)
        db.session.commit()
        flash('Tipo de combustible eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el tipo de combustible: {str(e)}', 'error')
    return redirect(url_for('tipos_combustible.lista_tipos_combustible'))
