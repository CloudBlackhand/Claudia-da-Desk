#!/usr/bin/env python3
"""
Entry point para Railway
"""
import os
import sys

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importar e executar o app
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)