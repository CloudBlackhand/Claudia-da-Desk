import os
import json
import logging
from datetime import datetime
from database_test import db

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageService:
    def __init__(self):
        self.disparo_ativo = False
        self.disparo_stats = {
            'total': 0,
            'enviados': 0,
            'erros': 0,
            'inicio': None
        }
        logger.info("MessageService inicializado em modo offline")
    
    def importar_json(self, json_data: dict) -> dict:
        """Importa dados do JSON para PostgreSQL"""
        logger.warning("Modo offline - importação não disponível")
        return {
            'sucesso': False,
            'erro': 'Modo offline - banco não disponível'
        }
    
    def get_clientes(self, filtro: str = 'todos', limit: int = 100, offset: int = 0) -> list:
        """Busca clientes com filtro"""
        logger.warning("Modo offline - busca de clientes não disponível")
        return []
    
    def get_stats(self) -> dict:
        """Retorna estatísticas dos clientes"""
        logger.warning("Modo offline - estatísticas não disponíveis")
        return {'total': 0, 'cobrados': 0, 'nao_cobrados': 0}
    
    def get_template(self) -> str:
        """Busca template atual"""
        logger.warning("Modo offline - template não disponível")
        return "Template não disponível em modo offline"
    
    def update_template(self, template: str) -> bool:
        """Atualiza template"""
        logger.warning("Modo offline - atualização de template não disponível")
        return False
    
    def format_message(self, template: str, cliente: dict) -> str:
        """Formata mensagem com dados do cliente"""
        logger.warning("Modo offline - formatação de mensagem não disponível")
        return template
    
    def iniciar_disparo(self, filtro: str = 'nao_cobrados') -> dict:
        """Inicia processo de disparo"""
        logger.warning("Modo offline - disparo não disponível")
        return {'sucesso': False, 'erro': 'Modo offline - disparo não disponível'}
    
    def get_disparo_status(self) -> dict:
        """Retorna status do disparo atual"""
        return {
            'ativo': False,
            'stats': self.disparo_stats
        }
    
    def parar_disparo(self) -> bool:
        """Para disparo em andamento"""
        logger.warning("Modo offline - parar disparo não disponível")
        return False
    
    def marcar_cobrados(self, cliente_ids: list) -> bool:
        """Marca clientes como cobrados manualmente"""
        logger.warning("Modo offline - marcar cobrados não disponível")
        return False

# Instância global do serviço
message_service = MessageService()
