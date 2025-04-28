from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Vehiculo, TipoCombustible

vehiculos_bp = Blueprint('vehiculos', __name__)

@vehiculos_bp.route('/vehiculos')
def lista_vehiculos():
    vehiculos = Vehiculo.query.all()
    return render_template('vehiculos/lista.html', vehiculos=vehiculos)

@vehiculos_bp.route('/vehiculos/crear', methods=['GET', 'POST'])
def crear_vehiculo():
    if request.method == 'POST':
        try:
            nuevo_vehiculo = Vehiculo(
                Placa=request.form['placa'],
                Marca=request.form['marca'],
                Modelo=request.form['modelo'],
                KilometrajeActual=float(request.form['kilometraje']),
                TipoCombustibleID=int(request.form['tipo_combustible'])
            )
            db.session.add(nuevo_vehiculo)
            db.session.commit()
            flash('Vehículo creado exitosamente', 'success')
            return redirect(url_for('vehiculos.lista_vehiculos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el vehículo: {str(e)}', 'error')
            print(f"Error: {str(e)}")  # Para debugging
    
    # Obtener tipos de combustible para el formulario
    tipos_combustible = TipoCombustible.query.all()
    return render_template('vehiculos/crear.html', tipos_combustible=tipos_combustible)

@vehiculos_bp.route('/vehiculos/editar/<int:id>', methods=['GET', 'POST'])
def editar_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    tipos_combustible = TipoCombustible.query.all()
    
    if request.method == 'POST':
        try:
            print(request.form)  # Depuración: Verifica los datos enviados
            vehiculo.Placa = request.form['placa']
            vehiculo.Marca = request.form['marca']
            vehiculo.Modelo = request.form['modelo']
            vehiculo.KilometrajeActual = float(request.form['kilometraje'])
            vehiculo.TipoCombustibleID = int(request.form['tipo_combustible'])
            
            db.session.commit()
            flash('Vehículo actualizado exitosamente', 'success')
            return redirect(url_for('vehiculos.lista_vehiculos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el vehículo: {str(e)}', 'error')
    
    return render_template('vehiculos/editar.html', vehiculo=vehiculo, tipos_combustible=tipos_combustible)

@vehiculos_bp.route('/vehiculos/eliminar/<int:id>', methods=['POST'])
def eliminar_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    try:
        db.session.delete(vehiculo)
        db.session.commit()
        flash('Vehículo eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el vehículo: {str(e)}', 'error')
    return redirect(url_for('vehiculos.lista_vehiculos'))

