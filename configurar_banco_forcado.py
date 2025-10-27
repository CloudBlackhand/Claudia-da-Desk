#!/usr/bin/env python3
"""
Script para FORÇAR conexão PostgreSQL usando URL correta
"""
import os
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_postgresql():
    """Conecta ao PostgreSQL usando a URL correta"""
    
    # Lista de URLs para tentar (em ordem de prioridade)
    urls = [
        os.getenv('DATABASE_PRIVATE_URL'),
        os.getenv('DATABASE_URL'),
        os.getenv('DATABASE_PUBLIC_URL')
    ]
    
    # Remover URLs vazias
    urls = [url for url in urls if url]
    
    if not urls:
        logger.error("❌ Nenhuma URL de banco encontrada!")
        return None
    
    logger.info(f"🔍 Tentando {len(urls)} URLs de conexão...")
    
    for i, url in enumerate(urls, 1):
        logger.info(f"🔄 Tentativa {i}: {url[:50]}...")
        
        try:
            conn = psycopg2.connect(url)
            logger.info(f"✅ CONECTADO COM SUCESSO na tentativa {i}!")
            
            # Testar conexão
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            logger.info(f"📊 PostgreSQL: {version}")
            
            cursor.close()
            return conn
            
        except Exception as e:
            logger.warning(f"❌ Tentativa {i} falhou: {e}")
            continue
    
    logger.error("❌ Todas as tentativas de conexão falharam!")
    return None

def criar_tabelas_forcado():
    """Cria tabelas usando conexão forçada"""
    
    conn = conectar_postgresql()
    if not conn:
        logger.error("❌ Não foi possível conectar ao banco")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Criar tabela de clientes
        logger.info("📋 Criando tabela 'clientes'...")
        cursor.execute("""
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
        """)
        
        # Criar tabela de templates
        logger.info("📋 Criando tabela 'templates'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                conteudo TEXT NOT NULL,
                ativo BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Criar tabela de mensagens recebidas
        logger.info("📋 Criando tabela 'mensagens_recebidas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensagens_recebidas (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER REFERENCES clientes(id),
                telefone VARCHAR(20) NOT NULL,
                mensagem TEXT NOT NULL,
                intent VARCHAR(100),
                resposta TEXT,
                data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Criar tabela de categorias de resposta
        logger.info("📋 Criando tabela 'categorias_resposta'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias_resposta (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                palavras_chave TEXT,
                resposta_padrao TEXT NOT NULL,
                ativo BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Inserir template padrão
        logger.info("📝 Inserindo template padrão...")
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
        
        cursor.execute("""
            INSERT INTO templates (nome, conteudo, ativo) 
            VALUES ('Template Padrão', %s, true)
            ON CONFLICT DO NOTHING
        """, (template_padrao,))
        
        # Inserir categorias padrão
        logger.info("📝 Inserindo categorias padrão...")
        categorias_padrao = [
            ("Dúvidas sobre valores", "valor, quanto, quanto devo, quanto tenho", "Para esclarecer sobre valores, consulte seu protocolo {protocolo}. FPD: R$ {fpd_cobrado}, SPD: R$ {spd_cobrado}."),
            ("Formas de pagamento", "pagamento, pagar, como pagar, boleto, pix", "Você pode pagar via PIX, boleto bancário ou cartão. Entre em contato para obter os dados de pagamento."),
            ("Negociação", "negociar, parcelar, desconto, acordo", "Entendemos sua situação. Entre em contato para discutir opções de negociação."),
            ("Protesto", "protesto, cartório, protestado", "Para resolver questões de protesto, entre em contato urgentemente conosco."),
            ("Outros", "outro, outros, geral", "Para outras informações, entre em contato conosco pelo telefone ou WhatsApp.")
        ]
        
        for nome, palavras, resposta in categorias_padrao:
            cursor.execute("""
                INSERT INTO categorias_resposta (nome, palavras_chave, resposta_padrao, ativo) 
                VALUES (%s, %s, %s, true)
                ON CONFLICT DO NOTHING
            """, (nome, palavras, resposta))
        
        # Verificar tabelas criadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tabelas = cursor.fetchall()
        logger.info(f"✅ Tabelas criadas: {[t[0] for t in tabelas]}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("🎉 BANCO DE DADOS CONFIGURADO COM SUCESSO!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar banco: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 CONFIGURAÇÃO FORÇADA DO POSTGRESQL")
    print("=" * 50)
    
    success = criar_tabelas_forcado()
    if success:
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("❌ FALHA NA CONFIGURAÇÃO!")
        exit(1)
