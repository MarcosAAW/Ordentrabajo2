import pyodbc
from ..config.config import get_database_config

def get_connection():
    try:
        config = get_database_config()
        connection_string = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"Trusted_Connection=yes;"
        )
        connection = pyodbc.connect(connection_string)
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
        return None

def test_connection():
    conn = get_connection()
    if conn:
        print("Conexión exitosa a la base de datos")
        conn.close()
    else:
        print("No se pudo conectar a la base de datos")