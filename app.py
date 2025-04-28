from flask import Flask, render_template, flash, redirect, url_for, session
from app.config import Config
from flask_login import LoginManager, current_user
from app.models import db, Login
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)

# Importar y registrar las rutas
from app.routes.vehiculos import vehiculos_bp
from app.routes.tipos_combustible import tipos_combustible_bp
from app.routes.registrosusosvehiculos import registros_usos_vehiculos_bp
from app.routes.usuarios import usuarios_bp
from app.routes.motivos_salida import motivos_salida_bp
from app.routes.login import login_bp

app.register_blueprint(vehiculos_bp)
app.register_blueprint(tipos_combustible_bp)
app.register_blueprint(registros_usos_vehiculos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(motivos_salida_bp)
app.register_blueprint(login_bp)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Configurar la ruta de login para redirigir usuarios no autenticados
login_manager.login_view = 'login.login'  # Asegúrate de que 'login.login' es el nombre correcto de tu vista de login

# Definir el user_loader
@login_manager.user_loader
def load_user(user_id):
    return Login.query.get(int(user_id))

@app.route('/')
def index():
    # Verificar si el usuario está autenticado
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))  # Redirige a la página principal si ya está autenticado
    return redirect(url_for('login.login'))  # Redirige al login si no está autenticado

@app.route('/index')
def main_page():
    if 'login_success' in session:
        flash('Inicio de sesión exitoso', 'success')
        session.pop('login_success')  # Limpiar la bandera
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        # Crear las tablas si no existen (solo para desarrollo)
        try:
            db.create_all()
            print("Tablas creadas exitosamente")
        except Exception as e:
            print(f"Error al crear las tablas: {str(e)}")
    app.run(debug=True)


