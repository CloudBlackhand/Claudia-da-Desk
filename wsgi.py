#!/usr/bin/env python3
"""
WSGI entry point para Railway
"""
import os
import sys

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importar o app Flask
from app import app

# Para uso com gunicorn
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Iniciando servidor WSGI na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
