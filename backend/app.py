import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv

# Importar módulos do projeto
from database import db
from waha_client import waha_client
from huggingface_client import hf_client
from message_service import message_service
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
        'database': 'unknown',
        'waha': 'unknown',
        'huggingface': 'unknown'
    }
    
    # Verificar banco
    try:
        db.ensure_connection()
        if db.connection:
            status['database'] = 'connected'
        else:
            status['database'] = 'not_configured'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
    
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

# ==================== API ENDPOINTS ====================

@app.route('/api/upload', methods=['POST'])
def upload_json():
    """Upload e importação do JSON"""
    try:
        if 'file' not in request.files:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo selecionado'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'sucesso': False, 'erro': 'Arquivo deve ser JSON'}), 400
        
        # Ler e parsear JSON
        json_data = json.load(file)
        
        # Importar dados
        resultado = message_service.importar_json(json_data)
        
        return jsonify(resultado)
        
    except json.JSONDecodeError:
        return jsonify({'sucesso': False, 'erro': 'JSON inválido'}), 400
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    """Lista clientes com filtros"""
    try:
        filtro = request.args.get('filtro', 'todos')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        clientes = message_service.get_clientes(filtro, limit, offset)
        
        return jsonify({
            'sucesso': True,
            'clientes': clientes,
            'total': len(clientes)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Estatísticas dos clientes"""
    try:
        stats = message_service.get_stats()
        return jsonify({
            'sucesso': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/disparar', methods=['POST'])
def iniciar_disparo():
    """Inicia disparo de mensagens"""
    try:
        data = request.get_json()
        filtro = data.get('filtro', 'nao_cobrados')
        
        resultado = message_service.iniciar_disparo(filtro)
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar disparo: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/status-disparo', methods=['GET'])
def get_disparo_status():
    """Status do disparo atual"""
    try:
        status = message_service.get_disparo_status()
        return jsonify({
            'sucesso': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar status do disparo: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/parar-disparo', methods=['POST'])
def parar_disparo():
    """Para disparo em andamento"""
    try:
        sucesso = message_service.parar_disparo()
        return jsonify({
            'sucesso': sucesso
        })
        
    except Exception as e:
        logger.error(f"Erro ao parar disparo: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/marcar-disparo', methods=['POST'])
def marcar_cobrados():
    """Marca clientes como cobrados"""
    try:
        data = request.get_json()
        cliente_ids = data.get('cliente_ids', [])
        
        if not cliente_ids:
            return jsonify({'sucesso': False, 'erro': 'Nenhum cliente selecionado'}), 400
        
        sucesso = message_service.marcar_cobrados(cliente_ids)
        
        return jsonify({
            'sucesso': sucesso
        })
        
    except Exception as e:
        logger.error(f"Erro ao marcar clientes: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/template', methods=['GET'])
def get_template():
    """Obtém template atual"""
    try:
        template = message_service.get_template()
        return jsonify({
            'sucesso': True,
            'template': template
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar template: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/template', methods=['POST'])
def update_template():
    """Atualiza template"""
    try:
        data = request.get_json()
        template = data.get('template', '')
        
        if not template.strip():
            return jsonify({'sucesso': False, 'erro': 'Template não pode estar vazio'}), 400
        
        sucesso = message_service.update_template(template)
        
        return jsonify({
            'sucesso': sucesso
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar template: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ==================== WEBHOOK ENDPOINTS ====================

@app.route('/api/webhook/waha', methods=['POST'])
def waha_webhook():
    """Webhook para receber mensagens do Waha"""
    try:
        data = request.get_json()
        
        # Verificar se é uma mensagem recebida (não enviada por nós)
        if data.get('event') == 'message' and not data.get('message', {}).get('fromMe', True):
            message_data = data.get('message', {})
            
            # Extrair informações da mensagem
            chat_id = message_data.get('chatId', '')
            phone = chat_id.replace('@c.us', '') if '@c.us' in chat_id else chat_id
            message_text = message_data.get('body', '')
            
            # Buscar dados do cliente
            cliente = db.execute_query(
                "SELECT * FROM clientes WHERE telefone1 = %s OR telefone2 = %s LIMIT 1",
                (phone, phone)
            )
            
            cliente_id = cliente[0]['id'] if cliente else None
            
            # Verificar status do bot
            bot_status = db.execute_query(
                "SELECT bot_ativo FROM bot_status ORDER BY id DESC LIMIT 1"
            )
            bot_ativo = bot_status[0]['bot_ativo'] if bot_status else False
            
            # Classificar mensagem para coleta de dados
            categoria, confianca = intent_classifier.classify_intent(message_text)
            
            # Salvar mensagem no banco
            db.execute_insert("""
                INSERT INTO mensagens_recebidas 
                (cliente_id, telefone, mensagem, categoria_classificada, confianca_classificacao)
                VALUES (%s, %s, %s, %s, %s)
            """, (cliente_id, phone, message_text, categoria, confianca))
            
            logger.info(f"Mensagem coletada de {phone}: '{message_text}' - Categoria: {categoria} ({confianca:.2f})")
            
            # Se bot estiver ativo, responder automaticamente
            if bot_ativo and cliente:
                cliente = cliente[0]
                
                # Buscar resposta predefinida para a categoria
                categoria_data = db.execute_query(
                    "SELECT * FROM categorias_resposta WHERE categoria = %s AND ativo = TRUE LIMIT 1",
                    (categoria,)
                )
                
                if categoria_data:
                    resposta_template = categoria_data[0]['resposta_padrao']
                    
                    # Substituir variáveis na resposta
                    resposta_final = resposta_template.format(
                        nome=cliente.get('nome', 'Cliente'),
                        protocolo=cliente.get('protocolo', 'N/A'),
                        documento=cliente.get('documento', 'N/A'),
                        fpd_cobrado=cliente.get('fpd_cobrado', 0),
                        spd_cobrado=cliente.get('spd_cobrado', 0),
                        urgencia_geral=cliente.get('urgencia_geral', 'Normal')
                    )
                    
                    # Enviar resposta
                    waha_client.send_message(phone, resposta_final)
                    
                    # Marcar como respondida
                    db.execute_update("""
                        UPDATE mensagens_recebidas 
                        SET respondida = TRUE, resposta_enviada = %s
                        WHERE telefone = %s AND mensagem = %s
                        ORDER BY created_at DESC LIMIT 1
                    """, (resposta_final, phone, message_text))
                    
                    logger.info(f"Resposta enviada para {phone} - Categoria: {categoria} (confiança: {confianca:.2f})")
                else:
                    logger.warning(f"Categoria '{categoria}' não encontrada no banco")
            else:
                logger.info(f"Bot desativado - Apenas coletando mensagem de {phone}")
            
        return jsonify({'sucesso': True})
        
    except Exception as e:
        logger.error(f"Erro no webhook Waha: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ==================== ENDPOINTS DE CONTROLE DO BOT ====================

@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """Retorna status atual do bot"""
    try:
        status = db.execute_query(
            "SELECT bot_ativo, modo_coleta FROM bot_status ORDER BY id DESC LIMIT 1"
        )
        
        if status:
            return jsonify({
                'sucesso': True,
                'bot_ativo': status[0]['bot_ativo'],
                'modo_coleta': status[0]['modo_coleta']
            })
        else:
            return jsonify({
                'sucesso': True,
                'bot_ativo': False,
                'modo_coleta': True
            })
        
    except Exception as e:
        logger.error(f"Erro ao buscar status do bot: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/bot/toggle', methods=['POST'])
def toggle_bot():
    """Liga/desliga o bot"""
    try:
        data = request.get_json()
        bot_ativo = data.get('bot_ativo', False)
        
        # Atualizar status do bot
        db.execute_update("""
            UPDATE bot_status 
            SET bot_ativo = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM bot_status ORDER BY id DESC LIMIT 1)
        """, (bot_ativo,))
        
        # Se não há registro, criar um
        if db.execute_query("SELECT COUNT(*) FROM bot_status")[0]['count'] == 0:
            db.execute_insert("""
                INSERT INTO bot_status (bot_ativo, modo_coleta) VALUES (%s, TRUE)
            """, (bot_ativo,))
        
        status_text = "ativado" if bot_ativo else "desativado"
        logger.info(f"Bot {status_text}")
        
        return jsonify({
            'sucesso': True,
            'bot_ativo': bot_ativo,
            'mensagem': f'Bot {status_text} com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao alterar status do bot: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/mensagens', methods=['GET'])
def get_mensagens():
    """Lista mensagens recebidas dos clientes"""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        mensagens = db.execute_query("""
            SELECT mr.*, c.nome, c.protocolo
            FROM mensagens_recebidas mr
            LEFT JOIN clientes c ON mr.cliente_id = c.id
            ORDER BY mr.created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        total = db.execute_query("SELECT COUNT(*) as total FROM mensagens_recebidas")[0]['total']
        
        return jsonify({
            'sucesso': True,
            'mensagens': mensagens,
            'total': total
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ==================== ENDPOINTS DE CATEGORIAS ====================

@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    """Lista todas as categorias de resposta"""
    try:
        categorias = db.execute_query(
            "SELECT * FROM categorias_resposta ORDER BY nome_exibicao"
        )
        
        return jsonify({
            'sucesso': True,
            'categorias': categorias
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar categorias: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/categorias', methods=['POST'])
def create_categoria():
    """Cria nova categoria de resposta"""
    try:
        data = request.get_json()
        categoria = data.get('categoria', '').strip()
        nome_exibicao = data.get('nome_exibicao', '').strip()
        resposta_padrao = data.get('resposta_padrao', '').strip()
        
        if not categoria or not nome_exibicao or not resposta_padrao:
            return jsonify({'sucesso': False, 'erro': 'Todos os campos são obrigatórios'}), 400
        
        # Verificar se categoria já existe
        existing = db.execute_query(
            "SELECT id FROM categorias_resposta WHERE categoria = %s",
            (categoria,)
        )
        
        if existing:
            return jsonify({'sucesso': False, 'erro': 'Categoria já existe'}), 400
        
        # Inserir nova categoria
        categoria_id = db.execute_insert("""
            INSERT INTO categorias_resposta (categoria, nome_exibicao, resposta_padrao)
            VALUES (%s, %s, %s) RETURNING id
        """, (categoria, nome_exibicao, resposta_padrao))
        
        return jsonify({
            'sucesso': True,
            'categoria_id': categoria_id
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar categoria: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/categorias/<int:categoria_id>', methods=['PUT'])
def update_categoria(categoria_id):
    """Atualiza categoria de resposta"""
    try:
        data = request.get_json()
        nome_exibicao = data.get('nome_exibicao', '').strip()
        resposta_padrao = data.get('resposta_padrao', '').strip()
        ativo = data.get('ativo', True)
        
        if not nome_exibicao or not resposta_padrao:
            return jsonify({'sucesso': False, 'erro': 'Nome e resposta são obrigatórios'}), 400
        
        # Atualizar categoria
        rows_affected = db.execute_update("""
            UPDATE categorias_resposta 
            SET nome_exibicao = %s, resposta_padrao = %s, ativo = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (nome_exibicao, resposta_padrao, ativo, categoria_id))
        
        if rows_affected == 0:
            return jsonify({'sucesso': False, 'erro': 'Categoria não encontrada'}), 404
        
        return jsonify({'sucesso': True})
        
    except Exception as e:
        logger.error(f"Erro ao atualizar categoria: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
def delete_categoria(categoria_id):
    """Deleta categoria de resposta"""
    try:
        # Verificar se é uma categoria padrão (não pode ser deletada)
        categoria_data = db.execute_query(
            "SELECT categoria FROM categorias_resposta WHERE id = %s",
            (categoria_id,)
        )
        
        if not categoria_data:
            return jsonify({'sucesso': False, 'erro': 'Categoria não encontrada'}), 404
        
        categoria = categoria_data[0]['categoria']
        categorias_padrao = ['indignacao', 'duvida_valor', 'pedido_desconto', 'confirmacao_pagamento', 
                           'negociacao', 'promessa_pagamento', 'contestacao', 'dados_incorretos', 
                           'agradecimento', 'outras']
        
        if categoria in categorias_padrao:
            return jsonify({'sucesso': False, 'erro': 'Categorias padrão não podem ser deletadas'}), 400
        
        # Deletar categoria
        rows_affected = db.execute_update(
            "DELETE FROM categorias_resposta WHERE id = %s",
            (categoria_id,)
        )
        
        if rows_affected == 0:
            return jsonify({'sucesso': False, 'erro': 'Categoria não encontrada'}), 404
        
        return jsonify({'sucesso': True})
        
    except Exception as e:
        logger.error(f"Erro ao deletar categoria: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ==================== ENDPOINTS DE CONFIGURAÇÃO ====================

@app.route('/api/waha/status', methods=['GET'])
def waha_status():
    """Status da sessão Waha"""
    try:
        status = waha_client.get_session_status()
        return jsonify({
            'sucesso': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar status Waha: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/waha/start', methods=['POST'])
def start_waha_session():
    """Inicia sessão Waha"""
    try:
        sucesso = waha_client.start_session()
        
        if sucesso:
            # Configurar webhook
            webhook_url = f"{request.host_url}api/webhook/waha"
            waha_client.setup_webhook(webhook_url)
        
        return jsonify({
            'sucesso': sucesso
        })
        
    except Exception as e:
        logger.error(f"Erro ao iniciar sessão Waha: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/huggingface/test', methods=['GET'])
def test_huggingface():
    """Testa conexão com Hugging Face"""
    try:
        sucesso = hf_client.test_connection()
        return jsonify({
            'sucesso': sucesso
        })
        
    except Exception as e:
        logger.error(f"Erro ao testar Hugging Face: {e}")
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

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
    logger.info("Aplicação iniciada com sucesso")

if __name__ == '__main__':
    init_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
