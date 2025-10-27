import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv

# Importar módulos do projeto (versão de teste)
from database_test import db
from waha_client import waha_client
from huggingface_client import hf_client
from message_service_test import message_service
from intent_classifier import intent_classifier

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    """Serve o frontend"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/health')
def health_check():
    """Healthcheck endpoint para Railway"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/test')
def test_endpoint():
    """Endpoint de teste simples"""
    return jsonify({'message': 'Teste OK', 'status': 'working'})

@app.route('/status')
def status_endpoint():
    """Endpoint de status detalhado"""
    status = {
        'app': 'running',
        'timestamp': datetime.now().isoformat(),
        'database': 'offline_mode',
        'waha': 'unknown',
        'huggingface': 'unknown'
    }
    
    # Verificar Waha
    if waha_client.api_key:
        status['waha'] = 'configured'
    else:
        status['waha'] = 'not_configured'
    
    # Verificar Hugging Face
    if hf_client.api_key:
        status['huggingface'] = 'configured'
    else:
        status['huggingface'] = 'not_configured'
    
    return jsonify(status)

@app.route('/<path:filename>')
def static_files(filename):
    """Serve arquivos estáticos do frontend"""
    return send_from_directory('../frontend', filename)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'erro': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'erro': 'Erro interno do servidor'}), 500

# ==================== INICIALIZAÇÃO ====================

def init_app():
    """Inicializa aplicação"""
    logger.info("Aplicação iniciada com sucesso em modo de teste")

if __name__ == '__main__':
    init_app()
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Iniciando servidor de teste na porta {port}")
    print(f"📊 Status: http://localhost:{port}/status")
    print(f"❤️ Health: http://localhost:{port}/health")
    print(f"🧪 Teste: http://localhost:{port}/test")
    app.run(host='0.0.0.0', port=port, debug=True)
