from ..database.Connection import get_connection

class Ejemplo:
    def __init__(self):
        self.connection = get_connection()

    def ejecutar_consulta(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Error en la consulta: {str(e)}")
            return None
        
    def cerrar_conexion(self):
        if self.connection:
            self.connection.close()