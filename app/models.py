from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Float, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()  # Solo inicializamos SQLAlchemy aquí

class TipoCombustible(db.Model):
    __tablename__ = 'TiposCombustible'
    TipoCombustibleID = db.Column(Integer, primary_key=True)
    Tipo = db.Column(String(50), unique=True, nullable=False)

class Vehiculo(db.Model):
    __tablename__ = 'Vehiculos'
    
    VehiculoID = db.Column(Integer, primary_key=True)
    Placa = db.Column(String(20), unique=True, nullable=False)
    Marca = db.Column(String(50), nullable=False)
    Modelo = db.Column(String(50), nullable=False)
    KilometrajeActual = db.Column(Float, nullable=False)
    TipoCombustibleID = db.Column(Integer, ForeignKey('TiposCombustible.TipoCombustibleID'), nullable=False)

    tipo_combustible = db.relationship('TipoCombustible', backref='vehiculos', foreign_keys=[TipoCombustibleID])

class UsuariosVehiculos(db.Model):
    __tablename__ = 'UsuariosVehiculos'
    UsuarioID = db.Column(Integer, primary_key=True)
    Nombre = db.Column(String(100), nullable=False)
    Apellido = db.Column(String(100), nullable=False)
    DocumentoIdentidad = db.Column(String(50), unique=True, nullable=False)
    Telefono = db.Column(String(15))
    Correo = db.Column(String(100))
    Cargo = db.Column(String(100))

class MotivosSalida(db.Model):
    __tablename__ = 'MotivosSalida'
    MotivoID = db.Column(Integer, primary_key=True)
    Descripcion = db.Column(String(200), unique=True, nullable=False)

class RegistrosUsoVehiculos(db.Model):
    __tablename__ = 'RegistrosUsoVehiculos'
    AutorizadoPorID = db.Column(Integer, ForeignKey('UsuariosVehiculos.UsuarioID'), nullable=False)
    RegistroID = db.Column(Integer, primary_key=True)
    UsuarioID = db.Column(Integer, ForeignKey('UsuariosVehiculos.UsuarioID'), nullable=False)
    VehiculoID = db.Column(Integer, ForeignKey('Vehiculos.VehiculoID'), nullable=False)
    MotivoID = db.Column(Integer, ForeignKey('MotivosSalida.MotivoID'), nullable=False)
    FechaSalida = db.Column(db.DateTime, nullable=False)
    FechaRetorno = db.Column(db.DateTime)
    KilometrajeSalida = db.Column(Float, nullable=False)
    KilometrajeRetorno = db.Column(Float)
    CombustibleUtilizado = db.Column(Float)
    Destino = db.Column(String(200), nullable=False)
    Observaciones = db.Column(String(1000))
    RASP = db.Column(String(200), nullable=False)
    NroOrden = db.Column(String(200), nullable=True)

from werkzeug.security import generate_password_hash, check_password_hash

class Login(db.Model):
    __tablename__ = 'Login'
    
    LoginID = db.Column(Integer, primary_key=True)
    Usuario = db.Column(String(120), unique=True, nullable=False)
    Senha = db.Column(String(200), nullable=False)
    Rol = db.Column(String(50), nullable=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.LoginID)
