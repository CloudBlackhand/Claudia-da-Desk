#!/usr/bin/env python3
"""
Teste SUPER SIMPLES de conexão PostgreSQL
"""
import os
import psycopg2

print("🔍 DIAGNÓSTICO COMPLETO DE CONEXÃO POSTGRESQL")
print("=" * 50)

# 1. Verificar variáveis de ambiente
print("\n📋 VARIÁVEIS DE AMBIENTE:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NÃO ENCONTRADA')[:50]}...")
print(f"DATABASE_PRIVATE_URL: {os.getenv('DATABASE_PRIVATE_URL', 'NÃO ENCONTRADA')[:50]}...")
print(f"DATABASE_PUBLIC_URL: {os.getenv('DATABASE_PUBLIC_URL', 'NÃO ENCONTRADA')[:50]}...")

# 2. Tentar diferentes URLs
urls_to_try = [
    ('DATABASE_PRIVATE_URL', os.getenv('DATABASE_PRIVATE_URL')),
    ('DATABASE_URL', os.getenv('DATABASE_URL')),
    ('DATABASE_PUBLIC_URL', os.getenv('DATABASE_PUBLIC_URL'))
]

print("\n🔄 TESTANDO CONEXÕES:")
for name, url in urls_to_try:
    if not url:
        print(f"❌ {name}: Não encontrada")
        continue
    
    print(f"\n🔄 Testando {name}:")
    print(f"   URL: {url[:50]}...")
    
    try:
        conn = psycopg2.connect(url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ SUCESSO! Versão: {version}")
        
        # Testar query simples
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"   📊 Banco: {db_info[0]}, Usuário: {db_info[1]}")
        
        cursor.close()
        conn.close()
        print(f"   🎉 {name} FUNCIONA PERFEITAMENTE!")
        break
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

print("\n" + "=" * 50)
print("🏁 DIAGNÓSTICO CONCLUÍDO")
