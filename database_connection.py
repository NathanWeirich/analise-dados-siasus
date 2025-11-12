"""
Módulo de conexão com o banco de dados MySQL.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


class DatabaseConnection:
    """Classe para gerenciar conexões com o banco de dados MySQL"""
    
    def __init__(self):
        """Inicializa a configuração da conexão a partir das variáveis de ambiente"""
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '3306'),
            'database': os.getenv('DB_DATABASE', 'datasus_db'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        self.connection = None
    
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                return self.connection
        except Error as e:
            print(f"✗ Erro ao conectar ao MySQL: {e}")
            return None
    
    def disconnect(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Conexão com o banco de dados fechada.")


def get_database_connection():
    """Retorna uma nova conexão com o banco de dados"""
    db = DatabaseConnection()
    return db.connect()
