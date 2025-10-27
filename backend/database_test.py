import os
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        # Não conectar automaticamente - conectar apenas quando necessário
        logger.info("Database inicializado em modo offline")
    
    def ensure_connection(self):
        """Garante que há uma conexão ativa com o banco"""
        logger.warning("Modo offline - banco não disponível")
        return False
    
    def connect(self):
        """Conecta ao banco PostgreSQL"""
        logger.warning("Modo offline - conexão com banco não disponível")
        return False
    
    def create_tables(self):
        """Cria as tabelas necessárias"""
        logger.warning("Modo offline - criação de tabelas não disponível")
        return False
    
    def get_cursor(self):
        """Retorna cursor com RealDictCursor para resultados como dicionário"""
        logger.warning("Modo offline - cursor não disponível")
        raise Exception("Modo offline - banco não disponível")
    
    def execute_query(self, query, params=None):
        """Executa query e retorna resultados"""
        logger.warning("Modo offline - query não executada")
        return []
    
    def execute_insert(self, query, params=None):
        """Executa insert e retorna ID inserido"""
        logger.warning("Modo offline - insert não executado")
        return None
    
    def execute_update(self, query, params=None):
        """Executa update"""
        logger.warning("Modo offline - update não executado")
        return 0
    
    def close(self):
        """Fecha conexão com banco"""
        logger.info("Conexão fechada (modo offline)")

# Instância global do banco
db = Database()
