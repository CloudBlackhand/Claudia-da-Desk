import os
import requests
import logging
from typing import Tuple

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.wit_token = os.getenv('WIT_AI_TOKEN')
        self.api_url = 'https://api.wit.ai/message'
        
        if not self.wit_token:
            logger.warning("WIT_AI_TOKEN não encontrada - usando classificação simples")
    
    def classify_intent(self, message: str) -> Tuple[str, float]:
        """
        Classifica a intenção da mensagem usando Wit.ai ou fallback simples
        Retorna: (categoria, confianca)
        """
        try:
            if self.wit_token:
                return self._classify_with_wit(message)
            else:
                return self._classify_simple(message)
        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            return self._classify_simple(message)
    
    def _classify_with_wit(self, message: str) -> Tuple[str, float]:
        """Classifica usando Wit.ai"""
        try:
            headers = {
                'Authorization': f'Bearer {self.wit_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'q': message,
                'v': '20231231'  # Versão da API
            }
            
            response = requests.get(self.api_url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair intenção do Wit.ai
                entities = data.get('entities', {})
                intents = entities.get('intent', [])
                
                if intents:
                    intent = intents[0]
                    categoria = intent.get('value', 'outras')
                    confianca = intent.get('confidence', 0.5)
                    
                    # Mapear intenções do Wit.ai para nossas categorias
                    categoria_mapeada = self._map_wit_intent(categoria)
                    return categoria_mapeada, confianca
                else:
                    return self._classify_simple(message)
            else:
                logger.warning(f"Wit.ai retornou status {response.status_code}")
                return self._classify_simple(message)
                
        except Exception as e:
            logger.error(f"Erro na API Wit.ai: {e}")
            return self._classify_simple(message)
    
    def _map_wit_intent(self, wit_intent: str) -> str:
        """Mapeia intenções do Wit.ai para nossas categorias"""
        mapping = {
            'indignation': 'indignacao',
            'anger': 'indignacao',
            'frustration': 'indignacao',
            'question_value': 'duvida_valor',
            'ask_value': 'duvida_valor',
            'discount_request': 'pedido_desconto',
            'payment_confirmation': 'confirmacao_pagamento',
            'negotiation': 'negociacao',
            'payment_promise': 'promessa_pagamento',
            'dispute': 'contestacao',
            'wrong_data': 'dados_incorretos',
            'thanks': 'agradecimento',
            'gratitude': 'agradecimento'
        }
        
        return mapping.get(wit_intent.lower(), 'outras')
    
    def _classify_simple(self, message: str) -> Tuple[str, float]:
        """Classificação simples baseada em palavras-chave"""
        message_lower = message.lower()
        
        # Palavras-chave para cada categoria
        keywords = {
            'indignacao': ['raiva', 'indignado', 'revoltado', 'absurdo', 'inaceitável', 'ridículo', 'escândalo'],
            'duvida_valor': ['valor', 'quanto', 'preço', 'custo', 'valor de', 'quanto custa', 'quanto é'],
            'pedido_desconto': ['desconto', 'desconta', 'redução', 'promoção', 'oferta', 'mais barato'],
            'confirmacao_pagamento': ['paguei', 'paguei o', 'pagamento feito', 'já paguei', 'transferi', 'depositei'],
            'negociacao': ['negociar', 'parcelar', 'parcela', 'condições', 'acordo', 'proposta'],
            'promessa_pagamento': ['vou pagar', 'pago amanhã', 'pago na sexta', 'pago semana que vem', 'comprometo'],
            'contestacao': ['não devo', 'não é meu', 'erro', 'não reconheço', 'não fiz', 'não foi eu'],
            'dados_incorretos': ['dados errados', 'nome errado', 'endereço errado', 'telefone errado', 'cpf errado'],
            'agradecimento': ['obrigado', 'obrigada', 'valeu', 'grato', 'agradecido', 'muito obrigado']
        }
        
        # Contar ocorrências de palavras-chave
        scores = {}
        for categoria, palavras in keywords.items():
            score = 0
            for palavra in palavras:
                if palavra in message_lower:
                    score += 1
            scores[categoria] = score
        
        # Encontrar categoria com maior score
        if scores:
            categoria_max = max(scores, key=scores.get)
            score_max = scores[categoria_max]
            
            if score_max > 0:
                # Calcular confiança baseada no score
                confianca = min(0.9, 0.5 + (score_max * 0.1))
                return categoria_max, confianca
        
        # Se não encontrou nada, retornar categoria padrão
        return 'outras', 0.3

# Instância global do classificador
intent_classifier = IntentClassifier()