import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        logger.info("Database inicializado em modo offline")
        # Não conectar automaticamente - conectar apenas quando necessário
    
    def ensure_connection(self):
        """Garante que há uma conexão ativa com o banco"""
        if not self.connection:
            self.connect()
            self.create_tables()
    
    def connect(self):
        """Conecta ao banco PostgreSQL"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                logger.warning("DATABASE_URL não encontrada - usando modo offline")
                return
            
            self.connection = psycopg2.connect(database_url)
            logger.info("Conectado ao PostgreSQL com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar ao PostgreSQL: {e}")
            # Não falhar - permitir que a aplicação inicie sem banco
    
    def create_tables(self):
        """Cria as tabelas necessárias"""
        if not self.connection:
            logger.warning("Sem conexão com banco - pulando criação de tabelas")
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Tabela de clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    protocolo VARCHAR(50) UNIQUE NOT NULL,
                    nome VARCHAR(255) NOT NULL,
                    documento VARCHAR(20),
                    telefone1 VARCHAR(20),
                    telefone2 VARCHAR(20),
                    fonte_sheets VARCHAR(100),
                    fpd_status INTEGER,
                    fpd_cobrado DECIMAL(10,2),
                    fpd_pago DECIMAL(10,2),
                    spd_status INTEGER,
                    spd_cobrado DECIMAL(10,2),
                    spd_pago DECIMAL(10,2),
                    urgencia_geral VARCHAR(50),
                    cobrado INTEGER DEFAULT 0,
                    data_cobranca TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de templates de mensagem
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id SERIAL PRIMARY KEY,
                    template_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de categorias de resposta
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias_resposta (
                    id SERIAL PRIMARY KEY,
                    categoria VARCHAR(50) UNIQUE NOT NULL,
                    nome_exibicao VARCHAR(100) NOT NULL,
                    resposta_padrao TEXT NOT NULL,
                    ativo BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela para armazenar mensagens recebidas dos clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensagens_recebidas (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER REFERENCES clientes(id),
                    telefone VARCHAR(20) NOT NULL,
                    mensagem TEXT NOT NULL,
                    categoria_classificada VARCHAR(50),
                    confianca_classificacao DECIMAL(3,2),
                    respondida BOOLEAN DEFAULT FALSE,
                    resposta_enviada TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela para controlar status do bot
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_status (
                    id SERIAL PRIMARY KEY,
                    bot_ativo BOOLEAN DEFAULT FALSE,
                    modo_coleta BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Inserir status inicial do bot se não existir
            cursor.execute("SELECT COUNT(*) FROM bot_status")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO bot_status (bot_ativo, modo_coleta) VALUES (FALSE, TRUE)
                """)
            
            # Inserir template padrão se não existir
            cursor.execute("SELECT COUNT(*) FROM templates")
            if cursor.fetchone()[0] == 0:
                template_padrao = """Olá {nome}!

Identificamos um débito em seu protocolo {protocolo}.

Valores em aberto:
• FPD: R$ {fpd_cobrado}
• SPD: R$ {spd_cobrado}

Urgência: {urgencia_geral}

Para regularizar sua situação, entre em contato conosco.

Atenciosamente,
Equipe de Cobrança"""
                
                cursor.execute("""
                    INSERT INTO templates (template_text) VALUES (%s)
                """, (template_padrao,))
            
            # Inserir categorias padrão se não existirem
            cursor.execute("SELECT COUNT(*) FROM categorias_resposta")
            if cursor.fetchone()[0] == 0:
                categorias_padrao = [
                    ('indignacao', 'Indignação', 'Entendemos sua frustração. Podemos revisar sua situação. Entre em contato conosco para esclarecimentos.'),
                    ('duvida_valor', 'Dúvida sobre Valor', 'Os valores se referem ao protocolo {protocolo}. Para detalhes, entre em contato conosco.'),
                    ('pedido_desconto', 'Pedido de Desconto', 'Podemos avaliar condições especiais. Entre em contato para negociação.'),
                    ('confirmacao_pagamento', 'Confirmação de Pagamento', 'Verificaremos seu pagamento. Aguarde nosso retorno em breve.'),
                    ('negociacao', 'Negociação', 'Temos opções de parcelamento. Entre em contato para discutirmos.'),
                    ('promessa_pagamento', 'Promessa de Pagamento', 'Anotamos seu compromisso. Aguardamos o pagamento na data combinada.'),
                    ('contestacao', 'Contestação', 'Vamos revisar seu caso. Entre em contato para esclarecimentos.'),
                    ('dados_incorretos', 'Dados Incorretos', 'Vamos verificar seus dados cadastrais. Entre em contato para atualização.'),
                    ('agradecimento', 'Agradecimento', 'Estamos à disposição para ajudar!'),
                    ('outras', 'Outras', 'Obrigado pelo contato. Nossa equipe retornará em breve.')
                ]
                
                for categoria, nome_exibicao, resposta_padrao in categorias_padrao:
                    cursor.execute("""
                        INSERT INTO categorias_resposta (categoria, nome_exibicao, resposta_padrao) 
                        VALUES (%s, %s, %s)
                    """, (categoria, nome_exibicao, resposta_padrao))
            
            self.connection.commit()
            cursor.close()
            logger.info("Tabelas criadas/verificadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            self.connection.rollback()
            raise
    
    def get_cursor(self):
        """Retorna cursor com RealDictCursor para resultados como dicionário"""
        self.ensure_connection()
        if not self.connection:
            raise Exception("Sem conexão com banco de dados")
        return self.connection.cursor(cursor_factory=RealDictCursor)
    
    def execute_query(self, query, params=None):
        """Executa query e retorna resultados"""
        try:
            self.ensure_connection()
            if not self.connection:
                logger.warning("Sem conexão com banco - retornando lista vazia")
                return []
            cursor = self.get_cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            return []
    
    def execute_insert(self, query, params=None):
        """Executa insert e retorna ID inserido"""
        try:
            self.ensure_connection()
            if not self.connection:
                logger.warning("Sem conexão com banco - insert falhou")
                return None
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            inserted_id = cursor.fetchone()[0] if cursor.description else None
            self.connection.commit()
            cursor.close()
            return inserted_id
        except Exception as e:
            logger.error(f"Erro ao executar insert: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def execute_update(self, query, params=None):
        """Executa update"""
        try:
            self.ensure_connection()
            if not self.connection:
                logger.warning("Sem conexão com banco - update falhou")
                return 0
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Erro ao executar update: {e}")
            if self.connection:
                self.connection.rollback()
            return 0
    
    def close(self):
        """Fecha conexão com banco"""
        if self.connection:
            self.connection.close()
            logger.info("Conexão com PostgreSQL fechada")

# Instância global do banco
db = Database()

