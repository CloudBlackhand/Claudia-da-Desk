import os
import requests
import json
import logging
from typing import Dict, List, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WahaClient:
    def __init__(self):
        self.api_key = os.getenv('WAHA_API_KEY')
        self.api_url = os.getenv('WAHA_API_URL', 'http://localhost:3000')
        self.session_name = 'default'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
        }
        
        if not self.api_key:
            logger.warning("WAHA_API_KEY não encontrada - modo offline")
    
    def start_session(self) -> bool:
        """Inicia sessão Waha com store habilitado"""
        if not self.api_key:
            logger.warning("WAHA_API_KEY não configurada - pulando inicialização")
            return False
            
        try:
            url = f"{self.api_url}/api/sessions/start"
            
            payload = {
                "name": self.session_name,
                "config": {
                    "noweb": {
                        "store": {
                            "enabled": True,
                            "fullSync": False
                        }
                    }
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Sessão Waha '{self.session_name}' iniciada com store habilitado")
                return True
            else:
                logger.error(f"Erro ao iniciar sessão Waha: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar sessão Waha: {e}")
            return False
    
    def get_session_status(self) -> Dict:
        """Verifica status da sessão"""
        try:
            url = f"{self.api_url}/api/sessions/{self.session_name}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao verificar status da sessão: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao verificar status da sessão: {e}")
            return {}
    
    def send_message(self, phone: str, message: str) -> bool:
        """Envia mensagem via WhatsApp"""
        try:
            # Limpar número de telefone (remover caracteres especiais)
            clean_phone = ''.join(filter(str.isdigit, phone))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            url = f"{self.api_url}/api/sendText"
            
            payload = {
                "session": self.session_name,
                "chatId": f"{clean_phone}@c.us",
                "text": message
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Mensagem enviada para {phone} com sucesso")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem para {phone}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {phone}: {e}")
            return False
    
    def get_chat_messages(self, phone: str, limit: int = 10) -> List[Dict]:
        """Busca histórico de mensagens do chat"""
        try:
            # Limpar número de telefone
            clean_phone = ''.join(filter(str.isdigit, phone))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            chat_id = f"{clean_phone}@c.us"
            url = f"{self.api_url}/api/{self.session_name}/chats/{chat_id}/messages"
            
            params = {
                "limit": limit,
                "direction": "before"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Erro ao buscar mensagens do chat {phone}: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens do chat {phone}: {e}")
            return []
    
    def get_chats(self) -> List[Dict]:
        """Lista todos os chats ativos"""
        try:
            url = f"{self.api_url}/api/{self.session_name}/chats"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Erro ao buscar chats: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao buscar chats: {e}")
            return []
    
    def setup_webhook(self, webhook_url: str) -> bool:
        """Configura webhook para receber mensagens"""
        try:
            url = f"{self.api_url}/api/sessions/{self.session_name}/webhook"
            
            payload = {
                "url": webhook_url,
                "events": ["message"]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Webhook configurado: {webhook_url}")
                return True
            else:
                logger.error(f"Erro ao configurar webhook: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {e}")
            return False
    
    def stop_session(self) -> bool:
        """Para a sessão Waha"""
        try:
            url = f"{self.api_url}/api/sessions/{self.session_name}/stop"
            response = requests.post(url, headers=self.headers)
            
            if response.status_code == 200:
                logger.info(f"Sessão Waha '{self.session_name}' parada")
                return True
            else:
                logger.error(f"Erro ao parar sessão Waha: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao parar sessão Waha: {e}")
            return False

# Instância global do cliente Waha
waha_client = WahaClient()

