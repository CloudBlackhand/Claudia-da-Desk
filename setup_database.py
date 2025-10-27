#!/usr/bin/env python3
"""
Script para configurar o banco de dados PostgreSQL no Railway
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Cria as tabelas necessárias no PostgreSQL"""
    
    # Obter DATABASE_URL das variáveis de ambiente
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL não encontrada!")
        logger.info("Execute: railway run python setup_database.py")
        return False
    
    try:
        # Conectar ao banco
        logger.info("Conectando ao PostgreSQL...")
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # SQL para criar tabela de clientes
        create_clientes_table = """
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            protocolo VARCHAR(255) UNIQUE NOT NULL,
            nome VARCHAR(255) NOT NULL,
            documento VARCHAR(255),
            telefone1 VARCHAR(20),
            telefone2 VARCHAR(20),
            fonte_sheets VARCHAR(255),
            fpd_status INTEGER DEFAULT 0,
            fpd_cobrado DECIMAL(10,2) DEFAULT 0,
            fpd_pago DECIMAL(10,2) DEFAULT 0,
            spd_status INTEGER DEFAULT 0,
            spd_cobrado DECIMAL(10,2) DEFAULT 0,
            spd_pago DECIMAL(10,2) DEFAULT 0,
            urgencia_geral VARCHAR(255),
            cobrado INTEGER DEFAULT 0,
            data_cobranca TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # SQL para criar tabela de templates
        create_templates_table = """
        CREATE TABLE IF NOT EXISTS templates (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            conteudo TEXT NOT NULL,
            ativo BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # SQL para criar tabela de mensagens recebidas
        create_mensagens_table = """
        CREATE TABLE IF NOT EXISTS mensagens_recebidas (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            telefone VARCHAR(20) NOT NULL,
            mensagem TEXT NOT NULL,
            intent VARCHAR(100),
            resposta TEXT,
            data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # SQL para criar tabela de categorias de resposta
        create_categorias_table = """
        CREATE TABLE IF NOT EXISTS categorias_resposta (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            palavras_chave TEXT,
            resposta_padrao TEXT NOT NULL,
            ativo BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Executar criação das tabelas
        logger.info("Criando tabela 'clientes'...")
        cursor.execute(create_clientes_table)
        
        logger.info("Criando tabela 'templates'...")
        cursor.execute(create_templates_table)
        
        logger.info("Criando tabela 'mensagens_recebidas'...")
        cursor.execute(create_mensagens_table)
        
        logger.info("Criando tabela 'categorias_resposta'...")
        cursor.execute(create_categorias_table)
        
        # Inserir template padrão
        template_padrao = """
        Olá {nome}! 

Este é um lembrete sobre seu protocolo {protocolo}.

Valores em aberto:
- FPD: R$ {fpd_cobrado}
- SPD: R$ {spd_cobrado}

Urgência: {urgencia_geral}

Para regularizar sua situação, entre em contato conosco.

Atenciosamente,
Equipe de Cobrança
        """.strip()
        
        logger.info("Inserindo template padrão...")
        cursor.execute("""
            INSERT INTO templates (nome, conteudo, ativo) 
            VALUES ('Template Padrão', %s, true)
            ON CONFLICT DO NOTHING
        """, (template_padrao,))
        
        # Inserir categorias padrão
        categorias_padrao = [
            ("Dúvidas sobre valores", "valor, quanto, quanto devo, quanto tenho", "Para esclarecer sobre valores, consulte seu protocolo {protocolo}. FPD: R$ {fpd_cobrado}, SPD: R$ {spd_cobrado}."),
            ("Formas de pagamento", "pagamento, pagar, como pagar, boleto, pix", "Você pode pagar via PIX, boleto bancário ou cartão. Entre em contato para obter os dados de pagamento."),
            ("Negociação", "negociar, parcelar, desconto, acordo", "Entendemos sua situação. Entre em contato para discutir opções de negociação."),
            ("Protesto", "protesto, cartório, protestado", "Para resolver questões de protesto, entre em contato urgentemente conosco."),
            ("Outros", "outro, outros, geral", "Para outras informações, entre em contato conosco pelo telefone ou WhatsApp.")
        ]
        
        logger.info("Inserindo categorias padrão...")
        for nome, palavras, resposta in categorias_padrao:
            cursor.execute("""
                INSERT INTO categorias_resposta (nome, palavras_chave, resposta_padrao, ativo) 
                VALUES (%s, %s, %s, true)
                ON CONFLICT DO NOTHING
            """, (nome, palavras, resposta))
        
        # Verificar se as tabelas foram criadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tabelas = cursor.fetchall()
        logger.info(f"Tabelas criadas: {[t[0] for t in tabelas]}")
        
        # Fechar conexão
        cursor.close()
        conn.close()
        
        logger.info("✅ Banco de dados configurado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar banco: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configurando banco de dados PostgreSQL...")
    success = create_tables()
    if success:
        print("✅ Configuração concluída!")
    else:
        print("❌ Falha na configuração!")
        exit(1)
