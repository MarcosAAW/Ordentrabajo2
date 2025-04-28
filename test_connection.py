import pyodbc

def test_sql_connection():
    try:
        # Configura estos valores según tu servidor
        server = 'DESKTOP-TKLGRVF\\SQLEXPRESS'  # Ajusta al nombre de tu servidor
        database = 'ControlVehiculos'
        
        # String de conexión usando Windows Authentication
        connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        
        print("Intentando conectar...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print("¡Conexión exitosa!")
        
        # Prueba una consulta simple
        cursor.execute('SELECT @@VERSION')
        row = cursor.fetchone()
        print("\nVersión del servidor:", row[0])
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print("Error de conexión:")
        print(str(e))

if __name__ == "__main__":
    test_sql_connection()