from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, RegistrosUsoVehiculos, Vehiculo, UsuariosVehiculos, MotivosSalida
from datetime import datetime
from sqlalchemy.orm import aliased

registros_usos_vehiculos_bp = Blueprint('registros_usos_vehiculos', __name__)


@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos')
def lista_registros_usos_vehiculos():

    # Crear alias para el usuario que autoriza
    Autorizador = aliased(UsuariosVehiculos)

    registros = db.session.query(
    RegistrosUsoVehiculos.RegistroID,
    RegistrosUsoVehiculos.FechaSalida,
    RegistrosUsoVehiculos.FechaRetorno,
    RegistrosUsoVehiculos.KilometrajeSalida,
    RegistrosUsoVehiculos.KilometrajeRetorno,
    RegistrosUsoVehiculos.CombustibleUtilizado,
    RegistrosUsoVehiculos.Destino,
    RegistrosUsoVehiculos.Observaciones,
    RegistrosUsoVehiculos.RASP,
    RegistrosUsoVehiculos.NroOrden,
    Vehiculo.Placa.label('PlacaVehiculo'),
    UsuariosVehiculos.Nombre.label('NombreUsuario'),
    UsuariosVehiculos.Apellido.label('ApellidoUsuario'),
    Autorizador.Nombre.label('NombreAutorizador'),
    Autorizador.Apellido.label('ApellidoAutorizador'),
    MotivosSalida.Descripcion.label('MotivoDescripcion'),
).join(Vehiculo, RegistrosUsoVehiculos.VehiculoID == Vehiculo.VehiculoID) \
 .join(UsuariosVehiculos, RegistrosUsoVehiculos.UsuarioID == UsuariosVehiculos.UsuarioID) \
 .join(Autorizador, RegistrosUsoVehiculos.AutorizadoPorID == Autorizador.UsuarioID) \
 .join(MotivosSalida, RegistrosUsoVehiculos.MotivoID == MotivosSalida.MotivoID) \
 .all()

    return render_template('registros_usos_vehiculos/lista.html', registros=registros)

@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos/crear', methods=['GET', 'POST'])
def crear_registro_uso_vehiculo():
    usuarios = UsuariosVehiculos.query.all()
    vehiculos = Vehiculo.query.all()
    motivos = MotivosSalida.query.all()

    # Calcular el siguiente número de orden
    ultimo_registro = RegistrosUsoVehiculos.query.order_by(RegistrosUsoVehiculos.RegistroID.desc()).first()
    if ultimo_registro and ultimo_registro.NroOrden:
        try:
            siguiente_nro_orden = f"{int(ultimo_registro.NroOrden) + 1:04d}"  # Incrementar y formatear como 4 dígitos
        except ValueError:
            siguiente_nro_orden = "0001"  # Si el último número no es válido, reiniciar a "0001"
    else:
        siguiente_nro_orden = "0001"  # Primer número de orden si no hay registros previos

    if request.method == 'POST':
        try:
            # Extraer datos del formulario
            fecha_salida = datetime.strptime(request.form['fecha_salida'], '%Y-%m-%dT%H:%M')
            fecha_retorno = datetime.strptime(request.form['fecha_retorno'], '%Y-%m-%dT%H:%M')
            kilometraje_salida = float(request.form['kilometraje_salida'])
            kilometraje_retorno = float(request.form['kilometraje_retorno'])
            combustible_utilizado = float(request.form['combustible_utilizado'])
            destino = request.form['destino']
            observaciones = request.form['observaciones']
            usuario_id = int(request.form['usuario_id'])
            vehiculo_id = int(request.form['vehiculo_marca_modelo'])
            motivo_id = int(request.form['motivo_id'])
            autorizado_por_id = int(request.form['autorizado_por_id'])
            RASP = request.form['RASP']

            # Usar el número de orden proporcionado o el generado automáticamente
            nro_orden = request.form.get('NroOrden', '').strip() or siguiente_nro_orden

            # Crear un nuevo registro
            nuevo_registro = RegistrosUsoVehiculos(
                FechaSalida=fecha_salida,
                FechaRetorno=fecha_retorno,
                KilometrajeSalida=kilometraje_salida,
                KilometrajeRetorno=kilometraje_retorno,
                CombustibleUtilizado=combustible_utilizado,
                Destino=destino,
                Observaciones=observaciones,
                UsuarioID=usuario_id,
                VehiculoID=vehiculo_id,
                MotivoID=motivo_id,
                AutorizadoPorID=autorizado_por_id,
                RASP=RASP,
                NroOrden=nro_orden  # Guardar el número de orden
            )
            db.session.add(nuevo_registro)
            db.session.commit()
            flash('Registro creado exitosamente', 'success')
            return redirect(url_for('registros_usos_vehiculos.lista_registros_usos_vehiculos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el registro de uso del vehículo: {str(e)}', 'error')

    return render_template('registros_usos_vehiculos/crear.html', usuarios=usuarios, vehiculos=vehiculos, motivos=motivos, siguiente_nro_orden=siguiente_nro_orden)


@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos/editar/<int:id>', methods=['GET', 'POST'])
def editar_registro_uso_vehiculo(id):
    registro = RegistrosUsoVehiculos.query.get_or_404(id)
    usuarios = UsuariosVehiculos.query.all()
    vehiculos = Vehiculo.query.all()
    motivos = MotivosSalida.query.all()
    
    if request.method == 'POST':
        try:
            # Convierte las fechas de los formularios
            registro.FechaSalida = datetime.strptime(request.form['fecha_salida'], '%Y-%m-%dT%H:%M')
            registro.FechaRetorno = datetime.strptime(request.form['fecha_retorno'], '%Y-%m-%dT%H:%M')
            registro.KilometrajeSalida = float(request.form['kilometraje_salida'])
            registro.KilometrajeRetorno = float(request.form['kilometraje_retorno'])
            registro.CombustibleUtilizado = float(request.form['combustible_utilizado'])
            registro.Destino = request.form['destino']
            registro.Observaciones = request.form['observaciones']
            registro.UsuarioID = int(request.form['usuario_id'])
            registro.VehiculoID = int(request.form['vehiculo_id'])
            registro.MotivoID = int(request.form['motivo_id'])
            registro.AutorizadoPorID = int(request.form['autorizado_por_id'])
            registro.RASP = request.form['RASP']
            registro.NroOrden = request.form['NroOrden']  # Permitir edición del número de orden
            
            db.session.commit()
            flash('Registro de uso de vehículo actualizado exitosamente', 'success')
            return redirect(url_for('registros_usos_vehiculos.lista_registros_usos_vehiculos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el registro de uso del vehículo: {str(e)}', 'error')
    
    return render_template('registros_usos_vehiculos/editar.html', registro=registro, usuarios=usuarios, vehiculos=vehiculos, motivos=motivos)

@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos/eliminar/<int:id>', methods=['POST'])
def eliminar_registro_uso_vehiculo(id):
    registro = RegistrosUsoVehiculos.query.get_or_404(id)
    try:
        db.session.delete(registro)
        db.session.commit()
        flash('Registro de uso de vehículo eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el registro de uso del vehículo: {str(e)}', 'error')
    return redirect(url_for('registros_usos_vehiculos.lista_registros_usos_vehiculos'))

@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos/detalle/<int:id>', methods=['GET'])
def detalle_registro_uso_vehiculo(id):
    # Crear alias para el usuario que autoriza
    Autorizador = aliased(UsuariosVehiculos)

    # Realizar las uniones necesarias para obtener los datos relacionados
    registro = db.session.query(
        RegistrosUsoVehiculos.FechaSalida,
        RegistrosUsoVehiculos.FechaRetorno,
        RegistrosUsoVehiculos.Destino,
        RegistrosUsoVehiculos.Observaciones,
        RegistrosUsoVehiculos.RASP,
        RegistrosUsoVehiculos.NroOrden,
        UsuariosVehiculos.Nombre.label('NombreUsuario'),
        UsuariosVehiculos.Apellido.label('ApellidoUsuario'),
        Autorizador.Nombre.label('NombreAutorizador'),
        Autorizador.Apellido.label('ApellidoAutorizador'),
        MotivosSalida.Descripcion.label('MotivoDescripcion')
    ).join(UsuariosVehiculos, RegistrosUsoVehiculos.UsuarioID == UsuariosVehiculos.UsuarioID) \
     .join(Autorizador, RegistrosUsoVehiculos.AutorizadoPorID == Autorizador.UsuarioID) \
     .join(MotivosSalida, RegistrosUsoVehiculos.MotivoID == MotivosSalida.MotivoID) \
     .filter(RegistrosUsoVehiculos.RegistroID == id) \
     .first()

    if not registro:
        flash('El registro no existe.', 'error')
        return redirect(url_for('registros_usos_vehiculos.lista_registros_usos_vehiculos'))

    # Renderizar la plantilla de detalle
    return render_template('registros_usos_vehiculos/detalle.html', registro=registro)