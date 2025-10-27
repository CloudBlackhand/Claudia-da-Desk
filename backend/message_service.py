import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from database import db
from waha_client import waha_client

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
        logger.info("MessageService inicializado")
    
    def importar_json(self, json_data: Dict) -> Dict:
        """Importa dados do JSON para PostgreSQL"""
        try:
            clientes = json_data.get('clientes_encontrados', [])
            importados = 0
            erros = 0
            
            for cliente in clientes:
                try:
                    # Verificar se protocolo já existe
                    existing = db.execute_query(
                        "SELECT id FROM clientes WHERE protocolo = %s",
                        (cliente.get('protocolo'),)
                    )
                    
                    if existing:
                        # Atualizar cliente existente
                        db.execute_update("""
                            UPDATE clientes SET
                                nome = %s, documento = %s, telefone1 = %s, telefone2 = %s,
                                fonte_sheets = %s, fpd_status = %s, fpd_cobrado = %s, fpd_pago = %s,
                                spd_status = %s, spd_cobrado = %s, spd_pago = %s, urgencia_geral = %s
                            WHERE protocolo = %s
                        """, (
                            cliente.get('nome'),
                            cliente.get('documento'),
                            cliente.get('telefone1'),
                            cliente.get('telefone2'),
                            cliente.get('fonte_sheets'),
                            cliente.get('fpd', {}).get('status'),
                            cliente.get('fpd', {}).get('cobrado', 0),
                            cliente.get('fpd', {}).get('pago', 0),
                            cliente.get('spd', {}).get('status'),
                            cliente.get('spd', {}).get('cobrado', 0),
                            cliente.get('spd', {}).get('pago', 0),
                            cliente.get('urgencia_geral'),
                            cliente.get('protocolo')
                        ))
                    else:
                        # Inserir novo cliente
                        db.execute_insert("""
                            INSERT INTO clientes (
                                protocolo, nome, documento, telefone1, telefone2, fonte_sheets,
                                fpd_status, fpd_cobrado, fpd_pago, spd_status, spd_cobrado, spd_pago, urgencia_geral
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            cliente.get('protocolo'),
                            cliente.get('nome'),
                            cliente.get('documento'),
                            cliente.get('telefone1'),
                            cliente.get('telefone2'),
                            cliente.get('fonte_sheets'),
                            cliente.get('fpd', {}).get('status'),
                            cliente.get('fpd', {}).get('cobrado', 0),
                            cliente.get('fpd', {}).get('pago', 0),
                            cliente.get('spd', {}).get('status'),
                            cliente.get('spd', {}).get('cobrado', 0),
                            cliente.get('spd', {}).get('pago', 0),
                            cliente.get('urgencia_geral')
                        ))
                    
                    importados += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao importar cliente {cliente.get('protocolo')}: {e}")
                    erros += 1
            
            return {
                'sucesso': True,
                'importados': importados,
                'erros': erros,
                'total': len(clientes)
            }
            
        except Exception as e:
            logger.error(f"Erro ao importar JSON: {e}")
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def get_clientes(self, filtro: str = 'todos', limit: int = 100, offset: int = 0) -> List[Dict]:
        """Busca clientes com filtro"""
        try:
            where_clause = ""
            params = []
            
            if filtro == 'cobrados':
                where_clause = "WHERE cobrado = 1"
            elif filtro == 'nao_cobrados':
                where_clause = "WHERE cobrado = 0"
            
            query = f"""
                SELECT * FROM clientes 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params = [limit, offset]
            
            return db.execute_query(query, params)
            
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas dos clientes"""
        try:
            total = db.execute_query("SELECT COUNT(*) as total FROM clientes")[0]['total']
            cobrados = db.execute_query("SELECT COUNT(*) as cobrados FROM clientes WHERE cobrado = 1")[0]['cobrados']
            nao_cobrados = total - cobrados
            
            return {
                'total': total,
                'cobrados': cobrados,
                'nao_cobrados': nao_cobrados
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            return {'total': 0, 'cobrados': 0, 'nao_cobrados': 0}
    
    def get_template(self) -> str:
        """Busca template atual"""
        try:
            result = db.execute_query("SELECT template_text FROM templates ORDER BY updated_at DESC LIMIT 1")
            if result:
                return result[0]['template_text']
            return ""
        except Exception as e:
            logger.error(f"Erro ao buscar template: {e}")
            return ""
    
    def update_template(self, template: str) -> bool:
        """Atualiza template"""
        try:
            db.execute_insert("""
                INSERT INTO templates (template_text) VALUES (%s)
            """, (template,))
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar template: {e}")
            return False
    
    def format_message(self, template: str, cliente: Dict) -> str:
        """Formata mensagem com dados do cliente"""
        try:
            # Substituir variáveis no template
            message = template.format(
                nome=cliente.get('nome', 'Cliente'),
                protocolo=cliente.get('protocolo', 'N/A'),
                documento=cliente.get('documento', 'N/A'),
                fpd_cobrado=cliente.get('fpd_cobrado', 0),
                spd_cobrado=cliente.get('spd_cobrado', 0),
                urgencia_geral=cliente.get('urgencia_geral', 'Normal')
            )
            return message
        except Exception as e:
            logger.error(f"Erro ao formatar mensagem: {e}")
            return template
    
    def iniciar_disparo(self, filtro: str = 'nao_cobrados') -> Dict:
        """Inicia processo de disparo"""
        if self.disparo_ativo:
            return {'sucesso': False, 'erro': 'Disparo já em andamento'}
        
        try:
            # Buscar clientes para disparo
            clientes = self.get_clientes(filtro, limit=1000)
            
            if not clientes:
                return {'sucesso': False, 'erro': 'Nenhum cliente encontrado para disparo'}
            
            # Inicializar estatísticas
            self.disparo_ativo = True
            self.disparo_stats = {
                'total': len(clientes),
                'enviados': 0,
                'erros': 0,
                'inicio': datetime.now()
            }
            
            # Buscar template
            template = self.get_template()
            if not template:
                self.disparo_ativo = False
                return {'sucesso': False, 'erro': 'Template não encontrado'}
            
            # Iniciar disparo em background (simulado)
            # Em produção, usar threading ou queue
            self._processar_disparo(clientes, template)
            
            return {
                'sucesso': True,
                'total': len(clientes),
                'filtro': filtro
            }
            
        except Exception as e:
            self.disparo_ativo = False
            logger.error(f"Erro ao iniciar disparo: {e}")
            return {'sucesso': False, 'erro': str(e)}
    
    def _processar_disparo(self, clientes: List[Dict], template: str):
        """Processa disparo de mensagens"""
        try:
            for cliente in clientes:
                if not self.disparo_ativo:
                    break
                
                try:
                    # Formatar mensagem
                    message = self.format_message(template, cliente)
                    
                    # Tentar telefone1 primeiro, depois telefone2
                    telefone = cliente.get('telefone1')
                    if not telefone:
                        telefone = cliente.get('telefone2')
                    
                    if telefone:
                        # Enviar mensagem
                        sucesso = waha_client.send_message(telefone, message)
                        
                        if sucesso:
                            # Marcar como cobrado
                            db.execute_update(
                                "UPDATE clientes SET cobrado = 1, data_cobranca = %s WHERE id = %s",
                                (datetime.now(), cliente['id'])
                            )
                            self.disparo_stats['enviados'] += 1
                        else:
                            self.disparo_stats['erros'] += 1
                    else:
                        self.disparo_stats['erros'] += 1
                        logger.warning(f"Cliente {cliente.get('protocolo')} sem telefone")
                    
                    # Delay entre mensagens (evitar rate limit)
                    import time
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar cliente {cliente.get('protocolo')}: {e}")
                    self.disparo_stats['erros'] += 1
            
            # Finalizar disparo
            self.disparo_ativo = False
            logger.info(f"Disparo finalizado: {self.disparo_stats}")
            
        except Exception as e:
            self.disparo_ativo = False
            logger.error(f"Erro no processamento do disparo: {e}")
    
    def get_disparo_status(self) -> Dict:
        """Retorna status do disparo atual"""
        return {
            'ativo': self.disparo_ativo,
            'stats': self.disparo_stats
        }
    
    def parar_disparo(self) -> bool:
        """Para disparo em andamento"""
        self.disparo_ativo = False
        return True
    
    def marcar_cobrados(self, cliente_ids: List[int]) -> bool:
        """Marca clientes como cobrados manualmente"""
        try:
            for cliente_id in cliente_ids:
                db.execute_update(
                    "UPDATE clientes SET cobrado = 1, data_cobranca = %s WHERE id = %s",
                    (datetime.now(), cliente_id)
                )
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar clientes como cobrados: {e}")
            return False

# Instância global do serviço
message_service = MessageService()

