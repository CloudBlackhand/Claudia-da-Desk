#!/usr/bin/env python3
"""
Teste simples para verificar se a estrutura está correta
"""
import os
import sys

print("=== TESTE DE ESTRUTURA ===")
print(f"Diretório atual: {os.getcwd()}")
print(f"Arquivos na raiz: {os.listdir('.')}")

# Verificar se backend existe
if os.path.exists('backend'):
    print("✅ Pasta backend encontrada")
    print(f"Arquivos no backend: {os.listdir('backend')}")
else:
    print("❌ Pasta backend não encontrada")

# Verificar se frontend existe
if os.path.exists('frontend'):
    print("✅ Pasta frontend encontrada")
    print(f"Arquivos no frontend: {os.listdir('frontend')}")
else:
    print("❌ Pasta frontend não encontrada")

# Verificar se requirements.txt existe
if os.path.exists('requirements.txt'):
    print("✅ requirements.txt encontrado")
    with open('requirements.txt', 'r') as f:
        print(f"Conteúdo: {f.read().strip()}")
else:
    print("❌ requirements.txt não encontrado")

print("=== FIM DO TESTE ===")
