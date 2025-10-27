#!/usr/bin/env python3
"""
Script para testar conexão com PostgreSQL no Railway
"""
import os
import psycopg2
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Testa conexão com PostgreSQL"""
    
    # Tentar primeiro DATABASE_PRIVATE_URL (para conexões internas)
    database_url = os.getenv('DATABASE_PRIVATE_URL') or os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL não encontrada!")
        return False
    
    logger.info(f"🔍 DATABASE_URL encontrada: {database_url[:50]}...")
    
    try:
        # Tentar conectar
        logger.info("🔄 Tentando conectar ao PostgreSQL...")
        conn = psycopg2.connect(database_url)
        
        # Testar query simples
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        logger.info(f"✅ Conectado com sucesso!")
        logger.info(f"📊 Versão PostgreSQL: {version}")
        
        # Verificar se há tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tabelas = cursor.fetchall()
        logger.info(f"📋 Tabelas existentes: {[t[0] for t in tabelas]}")
        
        # Fechar conexão
        cursor.close()
        conn.close()
        
        logger.info("🎉 Teste de conexão concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testando conexão com PostgreSQL...")
    success = test_database_connection()
    if success:
        print("✅ Conexão funcionando!")
    else:
        print("❌ Falha na conexão!")
        exit(1)
