import os
from dotenv import load_dotenv

load_dotenv()

def get_database_config():
    return {
        'server': os.getenv('DB_SERVER', 'DESKTOP-TKLGRVF\\SQLEXPRESS'),
        'database': os.getenv('DB_DATABASE', 'ControlVehiculos'),
        'username': os.getenv('DB_USERNAME', 'sa'),
        'password': os.getenv('DB_PASSWORD', 'sa')
    }