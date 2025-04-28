# Sistema de Control de Vehículos

Este proyecto es un sistema de administración de vehículos que permite gestionar usuarios, vehículos, tipos de combustible, registros de uso, y más.

## Descripción

El Sistema de Control de Vehículos es una aplicación web diseñada para gestionar de manera eficiente los vehículos de una organización. Permite realizar tareas como la administración de usuarios, el registro de vehículos, la gestión de tipos de combustible y el control de registros de uso.

## Ejemplo de Uso

1. **Inicio de Sesión**:
   - Accede a la página de inicio de sesión en `http://127.0.0.1:5000/login`.
   - Ingresa tus credenciales para acceder al sistema.

2. **Gestión de Vehículos**:
   - Navega a la sección de vehículos desde el menú principal.
   - Agrega, edita o elimina vehículos según sea necesario.

3. **Registros de Uso**:
   - Registra el uso de un vehículo especificando el motivo, el conductor y otros detalles.

## Requisitos

- Python 3.11 o superior
- Flask
- SQLAlchemy
- Bootstrap (para estilos front-end)

## Instalación

1. Clona este repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Ordentrabajo2
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura la base de datos en `app/config.py`:
   - Asegúrate de que los parámetros de conexión sean correctos para tu entorno.

4. Ejecuta la aplicación:
   ```bash
   python app.py
   ```

5. Abre tu navegador y accede a:
   ```
   http://127.0.0.1:5000
   ```

## Estructura del Proyecto (Detallada)

- **app/**: Contiene la lógica principal de la aplicación.
  - `routes/`: Define las rutas para cada funcionalidad (usuarios, vehículos, etc.).
  - `models.py`: Define los modelos de base de datos.
  - `config.py`: Configuración de la aplicación (base de datos, sesiones, etc.).
- **static/**: Archivos estáticos como CSS y JavaScript.
  - `css/style.css`: Estilos globales para la aplicación.
  - `js/main.js`: Funciones JavaScript personalizadas.
- **templates/**: Plantillas HTML para las vistas.
  - `base.html`: Plantilla base que incluye el diseño general.
  - `index.html`: Página principal del sistema.
  - Subcarpetas para cada módulo (usuarios, vehículos, etc.).

## Capturas de Pantalla

_Agrega aquí capturas de pantalla de las principales funcionalidades para que los usuarios puedan visualizar cómo funciona el sistema._

## Funcionalidades

- Gestión de usuarios (crear, editar, eliminar).
- Administración de vehículos.
- Registro de tipos de combustible.
- Control de registros de uso de vehículos.

## Estilos

Los estilos globales están definidos en `static/css/style.css`. Puedes personalizarlos según tus necesidades.

## Pruebas

Ejecuta las pruebas con:
```bash
pytest
```

## Contribuciones

Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la licencia MIT.