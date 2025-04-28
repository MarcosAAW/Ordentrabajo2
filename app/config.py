class Config:
    SECRET_KEY = 'sa'
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc:///?odbc_connect=' +
        'DRIVER={ODBC Driver 17 for SQL Server};' +  # Cambiar aquí
        'SERVER=DESKTOP-TKLGRVF\\SQLEXPRESS;' +
        'DATABASE=ControlVehiculos;' +
        'Trusted_Connection=yes;'
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración para el tiempo de expiración de la sesión
    PERMANENT_SESSION_LIFETIME = 600  # 10 minutos (en segundos)
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Cambiar a True si usas HTTPS
    SESSION_REFRESH_EACH_REQUEST = True
