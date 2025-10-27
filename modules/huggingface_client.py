import os
import requests
import json
import logging
from typing import Dict, List, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceClient:
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model_name = os.getenv('HUGGINGFACE_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2')
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        if not self.api_key:
            logger.warning("HUGGINGFACE_API_KEY não encontrada - Modo offline ativado")
            self.api_key = None
    
    def generate_response(self, prompt: str, max_length: int = 200) -> str:
        """Gera resposta usando modelo Hugging Face"""
        if not self.api_key:
            logger.warning("HuggingFace client em modo offline - retornando resposta padrão")
            return "Desculpe, o serviço de IA está temporariamente indisponível."
            
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1
                }
            }
            
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verificar se é uma lista (formato padrão)
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Remover o prompt original da resposta
                    if prompt in generated_text:
                        generated_text = generated_text.replace(prompt, '').strip()
                    return generated_text
                else:
                    logger.error(f"Formato de resposta inesperado: {result}")
                    return self._get_fallback_response()
            else:
                logger.error(f"Erro na API Hugging Face: {response.status_code} - {response.text}")
                return self._get_fallback_response()
                
        except requests.exceptions.Timeout:
            logger.error("Timeout na API Hugging Face")
            return self._get_fallback_response()
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return self._get_fallback_response()
    
    def create_cobranca_prompt(self, cliente_data: Dict, message_history: List[Dict], current_message: str) -> str:
        """Cria prompt contextualizado para cobrança"""
        
        # Personalidade do bot
        personality = """Você é um assistente virtual especializado em cobrança. Seu papel é:
- Ser educado, respeitoso e empático
- Focar em auxiliar o cliente a regularizar sua situação
- Oferecer informações claras sobre débitos
- Encaminhar para canais de pagamento quando apropriado
- Manter tom profissional mas acolhedor
- Evitar ser agressivo ou pressionar demais
- Responder de forma concisa (máximo 2-3 frases)"""
        
        # Contexto do cliente
        cliente_context = f"""
CONTEXTO DO CLIENTE:
- Nome: {cliente_data.get('nome', 'Cliente')}
- Protocolo: {cliente_data.get('protocolo', 'N/A')}
- Documento: {cliente_data.get('documento', 'N/A')}
- Débito FPD: R$ {cliente_data.get('fpd_cobrado', 0):.2f}
- Débito SPD: R$ {cliente_data.get('spd_cobrado', 0):.2f}
- Urgência: {cliente_data.get('urgencia_geral', 'Normal')}
"""
        
        # Histórico da conversa
        conversation_history = ""
        if message_history:
            conversation_history = "\nHISTÓRICO DA CONVERSA:\n"
            for msg in message_history[-5:]:  # Últimas 5 mensagens
                sender = "Cliente" if msg.get('fromMe') == False else "Bot"
                text = msg.get('body', '')
                conversation_history += f"- {sender}: {text}\n"
        
        # Mensagem atual
        current_msg = f"\nMENSAGEM ATUAL DO CLIENTE:\n{current_message}"
        
        # Instrução final
        instruction = "\n\nRESPONDA de forma natural e útil ao cliente, mantendo o contexto da conversa e focando em auxiliar na regularização do débito."
        
        # Montar prompt completo
        full_prompt = f"{personality}\n{cliente_context}{conversation_history}{current_msg}{instruction}"
        
        return full_prompt
    
    def _get_fallback_response(self) -> str:
        """Resposta padrão quando API falha"""
        fallback_responses = [
            "Obrigado pelo seu contato. Para mais informações sobre seu débito, entre em contato conosco pelo telefone.",
            "Entendo sua preocupação. Nossa equipe pode auxiliar você melhor. Entre em contato conosco.",
            "Obrigado pela mensagem. Para regularizar sua situação, entre em contato conosco pelos nossos canais oficiais.",
            "Agradecemos seu contato. Para informações sobre pagamento, entre em contato conosco."
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def test_connection(self) -> bool:
        """Testa conexão com API Hugging Face"""
        try:
            test_prompt = "Olá, como você está?"
            response = self.generate_response(test_prompt, max_length=50)
            return len(response) > 0
        except Exception as e:
            logger.error(f"Erro ao testar conexão Hugging Face: {e}")
            return False

# Instância global do cliente (será criada apenas quando necessário)
hf_client = None

def get_huggingface_client():
    """Retorna instância do cliente HuggingFace, criando se necessário"""
    global hf_client
    if hf_client is None:
        hf_client = HuggingFaceClient()
    return hf_client

