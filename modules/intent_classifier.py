import os
import requests
import re
import logging
from typing import Dict, Tuple, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.wit_token = os.getenv('WIT_AI_TOKEN')
        self.wit_url = "https://api.wit.ai/message"
        
        # Palavras-chave para fallback
        self.keywords = {
            'indignacao': [
                'absurdo', 'idiota', 'palhaçada', 'não devo', 'mentira', 'caralho',
                'ridículo', 'burro', 'estúpido', 'bobagem', 'nonsense', 'lixo',
                'merda', 'porra', 'puta', 'fdp', 'filho da puta', 'vai se foder',
                'que merda', 'que porra', 'que absurdo', 'que palhaçada', 'idoita',
                'não devo nada', 'não devo', 'não pago', 'não vou pagar'
            ],
            'duvida_valor': [
                'quanto', 'valor', 'por que', 'como assim', 'quanto é', 'quanto custa',
                'de onde vem', 'explicar', 'detalhar', 'breakdown', 'composição',
                'por que esse valor', 'de onde saiu', 'como calcularam'
            ],
            'pedido_desconto': [
                'desconto', 'reduzir', 'diminuir', 'negociar', 'abater', 'desconto',
                'redução', 'diminuir valor', 'baixar preço', 'condições especiais',
                'promoção', 'oferta', 'melhor preço'
            ],
            'confirmacao_pagamento': [
                'já paguei', 'paguei', 'paguei ontem', 'paguei hoje', 'já foi pago',
                'pagamento feito', 'boleto pago', 'transferência feita', 'pix enviado',
                'dinheiro enviado', 'valor pago', 'quitado'
            ],
            'negociacao': [
                'parcelar', 'parcelamento', 'dividir', 'acordo', 'negociar',
                'condições de pagamento', 'prazo', 'parcela', 'mensalidade',
                'como pagar', 'formas de pagamento'
            ],
            'promessa_pagamento': [
                'vou pagar', 'pago amanhã', 'pago na sexta', 'pago no final do mês',
                'pago quando receber', 'pago no salário', 'compromisso', 'prometo pagar',
                'garanto que pago', 'vou quitar'
            ],
            'contestacao': [
                'não devo', 'não é meu', 'não sou eu', 'erro', 'não reconheço',
                'não é minha conta', 'não fiz', 'não contratei', 'não solicitei',
                'não tenho nada', 'não tenho débito'
            ],
            'dados_incorretos': [
                'nome errado', 'telefone errado', 'endereço errado', 'cpf errado',
                'dados errados', 'informação errada', 'não é meu nome', 'não é meu telefone',
                'atualizar dados', 'corrigir dados', 'dados desatualizados', 'está errado',
                'errado no sistema', 'nome está errado', 'telefone está errado'
            ],
            'agradecimento': [
                'obrigado', 'valeu', 'obrigada', 'muito obrigado', 'agradeço',
                'obrigado pela ajuda', 'valeu pela ajuda', 'muito obrigado',
                'agradecido', 'grato', 'thanks', 'thank you'
            ]
        }
    
    def classify_intent(self, message: str) -> Tuple[str, float]:
        """
        Classifica a intenção da mensagem usando abordagem híbrida
        Retorna: (categoria, confiança)
        """
        message_lower = message.lower().strip()
        
        # Primeiro, tentar Wit.ai se token estiver disponível
        if self.wit_token:
            wit_result = self._classify_with_wit(message_lower)
            if wit_result:
                return wit_result
        
        # Fallback para palavras-chave
        return self._classify_with_keywords(message_lower)
    
    def _classify_with_wit(self, message: str) -> Optional[Tuple[str, float]]:
        """Classifica usando Wit.ai"""
        try:
            headers = {
                'Authorization': f'Bearer {self.wit_token}',
                'Content-Type': 'application/json'
            }
            
            params = {'q': message}
            
            response = requests.get(self.wit_url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                intents = data.get('intents', [])
                
                if intents:
                    # Pegar a intenção com maior confiança
                    best_intent = max(intents, key=lambda x: x.get('confidence', 0))
                    confidence = best_intent.get('confidence', 0)
                    intent_name = best_intent.get('name', '')
                    
                    # Mapear intenções do Wit.ai para nossas categorias
                    category_mapping = {
                        'indignation': 'indignacao',
                        'value_question': 'duvida_valor',
                        'discount_request': 'pedido_desconto',
                        'payment_confirmation': 'confirmacao_pagamento',
                        'negotiation': 'negociacao',
                        'payment_promise': 'promessa_pagamento',
                        'contestation': 'contestacao',
                        'wrong_data': 'dados_incorretos',
                        'thanks': 'agradecimento'
                    }
                    
                    category = category_mapping.get(intent_name, 'outras')
                    
                    # Só aceitar se confiança for alta o suficiente
                    if confidence >= 0.6:
                        logger.info(f"Wit.ai classificou como '{category}' com confiança {confidence:.2f}")
                        return (category, confidence)
                    else:
                        logger.info(f"Wit.ai confiança baixa ({confidence:.2f}), usando fallback")
                        return None
                else:
                    logger.info("Wit.ai não encontrou intenções, usando fallback")
                    return None
            else:
                logger.warning(f"Erro na API Wit.ai: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao usar Wit.ai: {e}")
            return None
    
    def _classify_with_keywords(self, message: str) -> Tuple[str, float]:
        """Classifica usando palavras-chave"""
        message_words = re.findall(r'\b\w+\b', message)
        message_text = ' '.join(message_words)
        
        category_scores = {}
        
        # Calcular score para cada categoria
        for category, keywords in self.keywords.items():
            score = 0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                if keyword in message_text:
                    # Dar peso maior para palavras-chave mais específicas
                    if len(keyword.split()) > 1:  # Frases completas
                        score += 3
                    else:  # Palavras simples
                        score += 1
            
            if score > 0:
                # Normalizar score (0-1)
                category_scores[category] = min(score / (total_keywords * 0.3), 1.0)
        
        if category_scores:
            # Pegar categoria com maior score
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]
            
            logger.info(f"Classificação por palavras-chave: '{best_category}' com confiança {confidence:.2f}")
            return (best_category, confidence)
        else:
            # Nenhuma categoria encontrada
            logger.info("Nenhuma categoria identificada, usando 'outras'")
            return ('outras', 0.1)
    
    def get_category_description(self, category: str) -> str:
        """Retorna descrição da categoria"""
        descriptions = {
            'indignacao': 'Cliente irritado, contestando débito com raiva',
            'duvida_valor': 'Questionamento sobre valores cobrados',
            'pedido_desconto': 'Solicitação de desconto ou redução',
            'confirmacao_pagamento': 'Cliente diz que já pagou',
            'negociacao': 'Proposta de parcelamento ou acordo',
            'promessa_pagamento': 'Compromisso de pagar em data futura',
            'contestacao': 'Alegação de que não deve ou dados incorretos',
            'dados_incorretos': 'Informações cadastrais erradas',
            'agradecimento': 'Cliente agradece ou confirma recebimento',
            'outras': 'Casos não classificados (resposta genérica)'
        }
        return descriptions.get(category, 'Categoria desconhecida')

# Instância global do classificador (será criada apenas quando necessário)
intent_classifier = None

def get_intent_classifier():
    """Retorna instância do classificador de intenções, criando se necessário"""
    global intent_classifier
    if intent_classifier is None:
        intent_classifier = IntentClassifier()
    return intent_classifier
