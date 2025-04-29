from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, RegistrosUsoVehiculos, Vehiculo, UsuariosVehiculos, MotivosSalida
from datetime import datetime
from sqlalchemy.orm import aliased
from flask import send_file
import pandas as pd
import io
from flask_weasyprint import HTML, render_pdf
from flask import Response


registros_usos_vehiculos_bp = Blueprint('registros_usos_vehiculos', __name__)


@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos', methods=['GET'])
def lista_registros_usos_vehiculos():
    # Crear alias para el usuario que autoriza
    Autorizador = aliased(UsuariosVehiculos)

    # Obtener los parámetros del filtro
    nro_orden = request.args.get('nro_orden', '').strip()
    conductor = request.args.get('conductor', '').strip()
    autorizado_por = request.args.get('autorizado_por', '').strip()
    destino = request.args.get('destino', '').strip()

    # Construir la consulta base
    query = db.session.query(
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
     .join(MotivosSalida, RegistrosUsoVehiculos.MotivoID == MotivosSalida.MotivoID)

    # Aplicar filtros si se proporcionan
    if nro_orden:
        query = query.filter(RegistrosUsoVehiculos.NroOrden.ilike(f"%{nro_orden}%"))
    if conductor:
        query = query.filter(
            (UsuariosVehiculos.Nombre.ilike(f"%{conductor}%")) |
            (UsuariosVehiculos.Apellido.ilike(f"%{conductor}%"))
        )
    if autorizado_por:
        query = query.filter(
            (Autorizador.Nombre.ilike(f"%{autorizado_por}%")) |
            (Autorizador.Apellido.ilike(f"%{autorizado_por}%"))
        )
    if destino:
        query = query.filter(RegistrosUsoVehiculos.Destino.ilike(f"%{destino}%"))

    # Ejecutar la consulta
    registros = query.all()

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
        RegistrosUsoVehiculos.RegistroID,  # Asegúrate de incluir RegistroID
        RegistrosUsoVehiculos.FechaSalida,
        RegistrosUsoVehiculos.FechaRetorno,
        RegistrosUsoVehiculos.Destino,
        RegistrosUsoVehiculos.Observaciones,
        RegistrosUsoVehiculos.RASP,
        RegistrosUsoVehiculos.NroOrden,
        RegistrosUsoVehiculos.KilometrajeSalida,
        RegistrosUsoVehiculos.KilometrajeRetorno,
        RegistrosUsoVehiculos.CombustibleUtilizado.label('LitrosCargados'),
        Vehiculo.Marca,
        Vehiculo.Modelo,
        Vehiculo.Placa,
        UsuariosVehiculos.Nombre.label('NombreUsuario'),
        UsuariosVehiculos.Apellido.label('ApellidoUsuario'),
        Autorizador.Nombre.label('NombreAutorizador'),
        Autorizador.Apellido.label('ApellidoAutorizador'),
        MotivosSalida.Descripcion.label('MotivoDescripcion')
    ).join(Vehiculo, RegistrosUsoVehiculos.VehiculoID == Vehiculo.VehiculoID) \
     .join(UsuariosVehiculos, RegistrosUsoVehiculos.UsuarioID == UsuariosVehiculos.UsuarioID) \
     .join(Autorizador, RegistrosUsoVehiculos.AutorizadoPorID == Autorizador.UsuarioID) \
     .join(MotivosSalida, RegistrosUsoVehiculos.MotivoID == MotivosSalida.MotivoID) \
     .filter(RegistrosUsoVehiculos.RegistroID == id) \
     .first()

    if not registro:
        flash('El registro no existe.', 'error')
        return redirect(url_for('registros_usos_vehiculos.lista_registros_usos_vehiculos'))

    # Renderizar la plantilla de detalle
    return render_template('registros_usos_vehiculos/detalle.html', registro=registro)

@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos/detalle/<int:id>/exportar_excel', methods=['GET'])
def exportar_detalle_excel(id):
    # Crear alias para el usuario que autoriza
    Autorizador = aliased(UsuariosVehiculos)

    # Obtener los datos del registro
    registro = db.session.query(
        RegistrosUsoVehiculos.FechaSalida,
        RegistrosUsoVehiculos.FechaRetorno,
        RegistrosUsoVehiculos.Destino,
        RegistrosUsoVehiculos.Observaciones,
        RegistrosUsoVehiculos.RASP,
        RegistrosUsoVehiculos.NroOrden,
        RegistrosUsoVehiculos.KilometrajeSalida,
        RegistrosUsoVehiculos.KilometrajeRetorno,
        RegistrosUsoVehiculos.CombustibleUtilizado.label('LitrosCargados'),
        Vehiculo.Marca,
        Vehiculo.Modelo,
        Vehiculo.Placa,
        UsuariosVehiculos.Nombre.label('NombreUsuario'),
        UsuariosVehiculos.Apellido.label('ApellidoUsuario'),
        Autorizador.Nombre.label('NombreAutorizador'),
        Autorizador.Apellido.label('ApellidoAutorizador'),
        MotivosSalida.Descripcion.label('MotivoDescripcion')
    ).join(Vehiculo, RegistrosUsoVehiculos.VehiculoID == Vehiculo.VehiculoID) \
     .join(UsuariosVehiculos, RegistrosUsoVehiculos.UsuarioID == UsuariosVehiculos.UsuarioID) \
     .join(Autorizador, RegistrosUsoVehiculos.AutorizadoPorID == Autorizador.UsuarioID) \
     .join(MotivosSalida, RegistrosUsoVehiculos.MotivoID == MotivosSalida.MotivoID) \
     .filter(RegistrosUsoVehiculos.RegistroID == id) \
     .first()

    if not registro:
        flash('El registro no existe.', 'error')
        return redirect(url_for('registros_usos_vehiculos.lista_registros_usos_vehiculos'))

    # Convertir los datos a un DataFrame de pandas
    data = {
        'Número de Orden': [registro.NroOrden],
        'Conductor': [f"{registro.NombreUsuario} {registro.ApellidoUsuario}"],
        'Autorizado por': [f"{registro.NombreAutorizador} {registro.ApellidoAutorizador}"],
        'RASP': [registro.RASP],
        'Vehículo': [f"{registro.Marca} {registro.Modelo}"],
        'Placa': [registro.Placa],
        'Fecha de Salida': [registro.FechaSalida],
        'Fecha de Retorno': [registro.FechaRetorno],
        'Kilometraje de Salida': [registro.KilometrajeSalida],
        'Kilometraje de Retorno': [registro.KilometrajeRetorno],
        'Litros Cargados': [registro.LitrosCargados],
        'Motivo de Salida': [registro.MotivoDescripcion],
        'Destino': [registro.Destino],
        'Observaciones': [registro.Observaciones]
    }
    df = pd.DataFrame(data)

    # Guardar el DataFrame en un archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Detalle')
    output.seek(0)

    # Enviar el archivo Excel como respuesta
    return send_file(output, as_attachment=True, download_name=f"Detalle_Registro_{registro.NroOrden}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

#Para exportar la lista completa, el de arriba es solo para un unico detalle
@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos/exportar_lista_excel', methods=['GET'])
def exportar_lista_excel():
   # Crear alias para el usuario que autoriza
    Autorizador = aliased(UsuariosVehiculos)

    # Obtener todos los registros
    registros = db.session.query(
        RegistrosUsoVehiculos.FechaSalida,
        RegistrosUsoVehiculos.FechaRetorno,
        RegistrosUsoVehiculos.Destino,
        RegistrosUsoVehiculos.Observaciones,
        RegistrosUsoVehiculos.RASP,
        RegistrosUsoVehiculos.NroOrden,
        RegistrosUsoVehiculos.KilometrajeSalida,
        RegistrosUsoVehiculos.KilometrajeRetorno,
        RegistrosUsoVehiculos.CombustibleUtilizado.label('LitrosCargados'),
        Vehiculo.Marca,
        Vehiculo.Modelo,
        Vehiculo.Placa,
        UsuariosVehiculos.Nombre.label('NombreUsuario'),
        UsuariosVehiculos.Apellido.label('ApellidoUsuario'),
        Autorizador.Nombre.label('NombreAutorizador'),
        Autorizador.Apellido.label('ApellidoAutorizador'),
        MotivosSalida.Descripcion.label('MotivoDescripcion')
    ).join(Vehiculo, RegistrosUsoVehiculos.VehiculoID == Vehiculo.VehiculoID) \
     .join(UsuariosVehiculos, RegistrosUsoVehiculos.UsuarioID == UsuariosVehiculos.UsuarioID) \
     .join(Autorizador, RegistrosUsoVehiculos.AutorizadoPorID == Autorizador.UsuarioID) \
     .join(MotivosSalida, RegistrosUsoVehiculos.MotivoID == MotivosSalida.MotivoID) \
     .all()

    # Convertir los datos a un DataFrame de pandas
    data = [{
        'Número de Orden': registro.NroOrden,
        'Conductor': f"{registro.NombreUsuario} {registro.ApellidoUsuario}",
        'Autorizado por': f"{registro.NombreAutorizador} {registro.ApellidoAutorizador}",
        'RASP': registro.RASP,
        'Vehículo': f"{registro.Marca} {registro.Modelo}",
        'Placa': registro.Placa,
        'Fecha de Salida': registro.FechaSalida,
        'Fecha de Retorno': registro.FechaRetorno,
        'Kilometraje de Salida': registro.KilometrajeSalida,
        'Kilometraje de Retorno': registro.KilometrajeRetorno,
        'Litros Cargados': registro.LitrosCargados,
        'Motivo de Salida': registro.MotivoDescripcion,
        'Destino': registro.Destino,
        'Observaciones': registro.Observaciones
    } for registro in registros]

    df = pd.DataFrame(data)

    # Guardar el DataFrame en un archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Lista de Registros')
    output.seek(0)

    # Enviar el archivo Excel como respuesta
    return send_file(output, as_attachment=True, download_name="Lista_Registros_Usos_Vehiculos.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@registros_usos_vehiculos_bp.route('/registros_usos_vehiculos/detalle/<int:id>/imprimir_pdf', methods=['GET'])
def imprimir_detalle_pdf(id):
    # Crear alias para el usuario que autoriza
    Autorizador = aliased(UsuariosVehiculos)

    # Obtener los datos del registro
    registro = db.session.query(
        RegistrosUsoVehiculos.FechaSalida,
        RegistrosUsoVehiculos.FechaRetorno,
        RegistrosUsoVehiculos.Destino,
        RegistrosUsoVehiculos.Observaciones,
        RegistrosUsoVehiculos.RASP,
        RegistrosUsoVehiculos.NroOrden,
        RegistrosUsoVehiculos.KilometrajeSalida,
        RegistrosUsoVehiculos.KilometrajeRetorno,
        RegistrosUsoVehiculos.CombustibleUtilizado.label('LitrosCargados'),
        Vehiculo.Marca,
        Vehiculo.Modelo,
        Vehiculo.Placa,
        UsuariosVehiculos.Nombre.label('NombreUsuario'),
        UsuariosVehiculos.Apellido.label('ApellidoUsuario'),
        Autorizador.Nombre.label('NombreAutorizador'),
        Autorizador.Apellido.label('ApellidoAutorizador'),
        MotivosSalida.Descripcion.label('MotivoDescripcion')
    ).join(Vehiculo, RegistrosUsoVehiculos.VehiculoID == Vehiculo.VehiculoID) \
     .join(UsuariosVehiculos, RegistrosUsoVehiculos.UsuarioID == UsuariosVehiculos.UsuarioID) \
     .join(Autorizador, RegistrosUsoVehiculos.AutorizadoPorID == Autorizador.UsuarioID) \
     .join(MotivosSalida, RegistrosUsoVehiculos.MotivoID == MotivosSalida.MotivoID) \
     .filter(RegistrosUsoVehiculos.RegistroID == id) \
     .first()

    if not registro:
        flash('El registro no existe.', 'error')
        return redirect(url_for('registros_usos_vehiculos.lista_registros_usos_vehiculos'))

    # Renderizar el HTML para el PDF
    html = render_template('registros_usos_vehiculos/informe_pdf.html', registro=registro)

    # Generar el PDF
    pdf = HTML(string=html).write_pdf()

    # Crear la respuesta con el encabezado 'inline'
    response = Response(pdf, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=Detalle_Registro.pdf'
    return response