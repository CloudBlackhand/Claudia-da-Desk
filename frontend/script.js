// Estado global da aplicação
let appState = {
    clientes: [],
    stats: { total: 0, cobrados: 0, nao_cobrados: 0 },
    disparoAtivo: false,
    clientesSelecionados: new Set(),
    categorias: [],
    categoriaEditando: null,
    botAtivo: false,
    mensagens: []
};

// Elementos DOM
const elements = {
    // Status
    wahaStatus: document.getElementById('waha-status'),
    hfStatus: document.getElementById('hf-status'),
    
    // Upload
    uploadBtn: document.getElementById('upload-btn'),
    jsonFile: document.getElementById('json-file'),
    uploadStatus: document.getElementById('upload-status'),
    
    // Stats
    totalClientes: document.getElementById('total-clientes'),
    naoCobrados: document.getElementById('nao-cobrados'),
    cobrados: document.getElementById('cobrados'),
    refreshStats: document.getElementById('refresh-stats'),
    
    // Template
    templateText: document.getElementById('template-text'),
    saveTemplate: document.getElementById('save-template'),
    
    // Disparo
    dispararTodos: document.getElementById('disparar-todos'),
    dispararNaoCobrados: document.getElementById('disparar-nao-cobrados'),
    dispararCobrados: document.getElementById('disparar-cobrados'),
    pararDisparo: document.getElementById('parar-disparo'),
    disparoProgress: document.getElementById('disparo-progress'),
    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),
    progressPercent: document.getElementById('progress-percent'),
    logContent: document.getElementById('log-content'),
    
    // Clientes
    filtroClientes: document.getElementById('filtro-clientes'),
    refreshClientes: document.getElementById('refresh-clientes'),
    marcarCobrados: document.getElementById('marcar-cobrados'),
    selectAll: document.getElementById('select-all'),
    clientesTbody: document.getElementById('clientes-tbody'),
    
    // Modal
    confirmModal: document.getElementById('confirm-modal'),
    modalTitle: document.getElementById('modal-title'),
    modalMessage: document.getElementById('modal-message'),
    modalCancel: document.getElementById('modal-cancel'),
    modalConfirm: document.getElementById('modal-confirm'),
    
    // Bot Control
    botStatus: document.getElementById('bot-status'),
    toggleBot: document.getElementById('toggle-bot'),
    refreshBotStatus: document.getElementById('refresh-bot-status'),
    modoColeta: document.getElementById('modo-coleta'),
    
    // Mensagens
    refreshMensagens: document.getElementById('refresh-mensagens'),
    totalMensagens: document.getElementById('total-mensagens'),
    mensagensList: document.getElementById('mensagens-list'),
    
    // Categorias
    addCategoria: document.getElementById('add-categoria'),
    refreshCategorias: document.getElementById('refresh-categorias'),
    categoriasGrid: document.getElementById('categorias-grid'),
    
    // Modal Categoria
    categoriaModal: document.getElementById('categoria-modal'),
    categoriaModalTitle: document.getElementById('categoria-modal-title'),
    categoriaForm: document.getElementById('categoria-form'),
    categoriaNome: document.getElementById('categoria-nome'),
    categoriaResposta: document.getElementById('categoria-resposta'),
    categoriaAtivo: document.getElementById('categoria-ativo'),
    categoriaCancel: document.getElementById('categoria-cancel'),
    categoriaSave: document.getElementById('categoria-save'),
    
    // Loading
    loadingOverlay: document.getElementById('loading-overlay')
};

// Utilitários
const utils = {
    showLoading: () => elements.loadingOverlay.classList.add('show'),
    hideLoading: () => elements.loadingOverlay.classList.remove('show'),
    
    showModal: (title, message, onConfirm) => {
        elements.modalTitle.textContent = title;
        elements.modalMessage.textContent = message;
        elements.modalConfirm.onclick = onConfirm;
        elements.confirmModal.style.display = 'block';
    },
    
    hideModal: () => {
        elements.confirmModal.style.display = 'none';
        elements.modalConfirm.onclick = null;
    },
    
    addLogEntry: (message, type = 'info') => {
        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${timestamp}] ${message}`;
        elements.logContent.appendChild(entry);
        elements.logContent.scrollTop = elements.logContent.scrollHeight;
    },
    
    formatCurrency: (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value || 0);
    },
    
    formatPhone: (phone) => {
        if (!phone) return 'N/A';
        const cleaned = phone.replace(/\D/g, '');
        if (cleaned.length === 11) {
            return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7)}`;
        }
        return phone;
    }
};

// API calls
const api = {
    async request(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.erro || `Erro ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.erro || `Erro ${response.status}`);
        }
        
        return data;
    },
    
    async getStats() {
        return this.request('/api/stats');
    },
    
    async getClientes(filtro = 'todos', limit = 100, offset = 0) {
        const params = new URLSearchParams({ filtro, limit, offset });
        return this.request(`/api/clientes?${params}`);
    },
    
    async getTemplate() {
        return this.request('/api/template');
    },
    
    async updateTemplate(template) {
        return this.request('/api/template', {
            method: 'POST',
            body: JSON.stringify({ template })
        });
    },
    
    async iniciarDisparo(filtro) {
        return this.request('/api/disparar', {
            method: 'POST',
            body: JSON.stringify({ filtro })
        });
    },
    
    async getDisparoStatus() {
        return this.request('/api/status-disparo');
    },
    
    async pararDisparo() {
        return this.request('/api/parar-disparo', { method: 'POST' });
    },
    
    async marcarCobrados(clienteIds) {
        return this.request('/api/marcar-disparo', {
            method: 'POST',
            body: JSON.stringify({ cliente_ids: clienteIds })
        });
    },
    
    async getWahaStatus() {
        return this.request('/api/waha/status');
    },
    
    async startWahaSession() {
        return this.request('/api/waha/start', { method: 'POST' });
    },
    
    async testHuggingFace() {
        return this.request('/api/huggingface/test');
    }
};

// Funções principais
const app = {
    async init() {
        try {
            utils.showLoading();
            
            // Verificar status dos serviços
            await this.checkServices();
            
            // Carregar dados iniciais
            await this.loadStats();
            await this.loadTemplate();
            await this.loadClientes();
            
            // Configurar event listeners
            this.setupEventListeners();
            
            // Iniciar polling do status do disparo
            this.startDisparoPolling();
            
            utils.addLogEntry('Aplicação inicializada com sucesso', 'success');
            
        } catch (error) {
            console.error('Erro na inicialização:', error);
            utils.addLogEntry(`Erro na inicialização: ${error.message}`, 'error');
        } finally {
            utils.hideLoading();
        }
    },
    
    async checkServices() {
        try {
            // Verificar Waha
            const wahaStatus = await api.getWahaStatus();
            if (wahaStatus.sucesso && wahaStatus.status?.status === 'WORKING') {
                elements.wahaStatus.textContent = 'Conectado';
                elements.wahaStatus.className = 'status online';
            } else {
                elements.wahaStatus.textContent = 'Desconectado';
                elements.wahaStatus.className = 'status offline';
            }
        } catch (error) {
            elements.wahaStatus.textContent = 'Erro';
            elements.wahaStatus.className = 'status offline';
        }
        
        try {
            // Verificar Hugging Face
            const hfStatus = await api.testHuggingFace();
            if (hfStatus.sucesso) {
                elements.hfStatus.textContent = 'Conectado';
                elements.hfStatus.className = 'status online';
            } else {
                elements.hfStatus.textContent = 'Desconectado';
                elements.hfStatus.className = 'status offline';
            }
        } catch (error) {
            elements.hfStatus.textContent = 'Erro';
            elements.hfStatus.className = 'status offline';
        }
    },
    
    async loadStats() {
        try {
            const response = await api.getStats();
            if (response.sucesso) {
                appState.stats = response.stats;
                this.updateStatsDisplay();
            }
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    },
    
    updateStatsDisplay() {
        elements.totalClientes.textContent = appState.stats.total;
        elements.naoCobrados.textContent = appState.stats.nao_cobrados;
        elements.cobrados.textContent = appState.stats.cobrados;
    },
    
    async loadTemplate() {
        try {
            const response = await api.getTemplate();
            if (response.sucesso) {
                elements.templateText.value = response.template;
            }
        } catch (error) {
            console.error('Erro ao carregar template:', error);
        }
    },
    
    async loadClientes() {
        try {
            const filtro = elements.filtroClientes.value;
            const response = await api.getClientes(filtro);
            
            if (response.sucesso) {
                appState.clientes = response.clientes;
                this.renderClientes();
            }
        } catch (error) {
            console.error('Erro ao carregar clientes:', error);
        }
    },
    
    renderClientes() {
        const tbody = elements.clientesTbody;
        tbody.innerHTML = '';
        
        appState.clientes.forEach(cliente => {
            const row = document.createElement('tr');
            row.dataset.clienteId = cliente.id;
            
            const isSelected = appState.clientesSelecionados.has(cliente.id);
            if (isSelected) {
                row.classList.add('selected');
            }
            
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="cliente-checkbox" 
                           data-cliente-id="${cliente.id}" 
                           ${isSelected ? 'checked' : ''}>
                </td>
                <td>${cliente.nome || 'N/A'}</td>
                <td>${utils.formatPhone(cliente.telefone1)}</td>
                <td>${cliente.protocolo || 'N/A'}</td>
                <td>${utils.formatCurrency(cliente.fpd_cobrado)}</td>
                <td>${utils.formatCurrency(cliente.spd_cobrado)}</td>
                <td>
                    <span class="urgencia-badge ${cliente.urgencia_geral?.toLowerCase() || 'normal'}">
                        ${cliente.urgencia_geral || 'Normal'}
                    </span>
                </td>
                <td>
                    <span class="status-badge ${cliente.cobrado ? 'cobrado' : 'nao-cobrado'}">
                        ${cliente.cobrado ? 'Cobrado' : 'Não Cobrado'}
                    </span>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
        this.updateSelectAllState();
    },
    
    updateSelectAllState() {
        const checkboxes = document.querySelectorAll('.cliente-checkbox');
        const checkedBoxes = document.querySelectorAll('.cliente-checkbox:checked');
        
        elements.selectAll.checked = checkboxes.length > 0 && checkboxes.length === checkedBoxes.length;
        elements.selectAll.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < checkboxes.length;
        
        elements.marcarCobrados.style.display = checkedBoxes.length > 0 ? 'block' : 'none';
    },
    
    setupEventListeners() {
        // Upload
        elements.uploadBtn.addEventListener('click', () => elements.jsonFile.click());
        elements.jsonFile.addEventListener('change', this.handleFileUpload.bind(this));
        
        // Stats
        elements.refreshStats.addEventListener('click', this.loadStats.bind(this));
        
        // Template
        elements.saveTemplate.addEventListener('click', this.saveTemplate.bind(this));
        
        // Disparo
        elements.dispararTodos.addEventListener('click', () => this.iniciarDisparo('todos'));
        elements.dispararNaoCobrados.addEventListener('click', () => this.iniciarDisparo('nao_cobrados'));
        elements.dispararCobrados.addEventListener('click', () => this.iniciarDisparo('cobrados'));
        elements.pararDisparo.addEventListener('click', this.pararDisparo.bind(this));
        
        // Clientes
        elements.filtroClientes.addEventListener('change', this.loadClientes.bind(this));
        elements.refreshClientes.addEventListener('click', this.loadClientes.bind(this));
        elements.marcarCobrados.addEventListener('click', this.marcarCobradosSelecionados.bind(this));
        elements.selectAll.addEventListener('change', this.toggleSelectAll.bind(this));
        
        // Modal
        elements.modalCancel.addEventListener('click', utils.hideModal);
        elements.confirmModal.addEventListener('click', (e) => {
            if (e.target === elements.confirmModal) {
                utils.hideModal();
            }
        });
        
        // Cliente checkboxes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('cliente-checkbox')) {
                this.handleClienteSelection(e.target);
            }
        });
    },
    
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            utils.showLoading();
            elements.uploadStatus.innerHTML = 'Enviando arquivo...';
            
            const response = await api.uploadFile(file);
            
            if (response.sucesso) {
                elements.uploadStatus.innerHTML = `
                    ✅ Importação concluída!<br>
                    ${response.importados} clientes importados<br>
                    ${response.erros} erros
                `;
                elements.uploadStatus.className = 'upload-status success';
                
                // Recarregar dados
                await this.loadStats();
                await this.loadClientes();
                
                utils.addLogEntry(`Arquivo importado: ${response.importados} clientes`, 'success');
            } else {
                throw new Error(response.erro || 'Erro na importação');
            }
            
        } catch (error) {
            elements.uploadStatus.innerHTML = `❌ Erro: ${error.message}`;
            elements.uploadStatus.className = 'upload-status error';
            utils.addLogEntry(`Erro no upload: ${error.message}`, 'error');
        } finally {
            utils.hideLoading();
            elements.jsonFile.value = '';
        }
    },
    
    async saveTemplate() {
        const template = elements.templateText.value.trim();
        if (!template) {
            alert('Template não pode estar vazio!');
            return;
        }
        
        try {
            utils.showLoading();
            const response = await api.updateTemplate(template);
            
            if (response.sucesso) {
                utils.addLogEntry('Template salvo com sucesso', 'success');
                alert('Template salvo com sucesso!');
            } else {
                throw new Error('Erro ao salvar template');
            }
            
        } catch (error) {
            utils.addLogEntry(`Erro ao salvar template: ${error.message}`, 'error');
            alert(`Erro ao salvar template: ${error.message}`);
        } finally {
            utils.hideLoading();
        }
    },
    
    async iniciarDisparo(filtro) {
        const filtroText = {
            'todos': 'todos os clientes',
            'nao_cobrados': 'clientes não cobrados',
            'cobrados': 'clientes cobrados'
        }[filtro];
        
        utils.showModal(
            'Confirmar Disparo',
            `Deseja iniciar o disparo para ${filtroText}?`,
            async () => {
                utils.hideModal();
                await this.executarDisparo(filtro);
            }
        );
    },
    
    async executarDisparo(filtro) {
        try {
            utils.showLoading();
            utils.addLogEntry(`Iniciando disparo para ${filtro}...`, 'info');
            
            const response = await api.iniciarDisparo(filtro);
            
            if (response.sucesso) {
                appState.disparoAtivo = true;
                elements.disparoProgress.style.display = 'block';
                elements.pararDisparo.style.display = 'block';
                
                utils.addLogEntry(`Disparo iniciado: ${response.total} clientes`, 'success');
            } else {
                throw new Error(response.erro || 'Erro ao iniciar disparo');
            }
            
        } catch (error) {
            utils.addLogEntry(`Erro ao iniciar disparo: ${error.message}`, 'error');
            alert(`Erro ao iniciar disparo: ${error.message}`);
        } finally {
            utils.hideLoading();
        }
    },
    
    async pararDisparo() {
        try {
            const response = await api.pararDisparo();
            
            if (response.sucesso) {
                appState.disparoAtivo = false;
                elements.disparoProgress.style.display = 'none';
                elements.pararDisparo.style.display = 'none';
                
                utils.addLogEntry('Disparo parado pelo usuário', 'info');
            }
            
        } catch (error) {
            utils.addLogEntry(`Erro ao parar disparo: ${error.message}`, 'error');
        }
    },
    
    async updateDisparoStatus() {
        if (!appState.disparoAtivo) return;
        
        try {
            const response = await api.getDisparoStatus();
            
            if (response.sucesso) {
                const status = response.status;
                appState.disparoAtivo = status.ativo;
                
                if (status.ativo) {
                    const stats = status.stats;
                    const percent = stats.total > 0 ? (stats.enviados / stats.total) * 100 : 0;
                    
                    elements.progressFill.style.width = `${percent}%`;
                    elements.progressText.textContent = `${stats.enviados} / ${stats.total}`;
                    elements.progressPercent.textContent = `${Math.round(percent)}%`;
                } else {
                    // Disparo finalizado
                    elements.disparoProgress.style.display = 'none';
                    elements.pararDisparo.style.display = 'none';
                    
                    const stats = status.stats;
                    utils.addLogEntry(
                        `Disparo finalizado: ${stats.enviados} enviados, ${stats.erros} erros`, 
                        'success'
                    );
                    
                    // Recarregar dados
                    await this.loadStats();
                    await this.loadClientes();
                }
            }
            
        } catch (error) {
            console.error('Erro ao atualizar status do disparo:', error);
        }
    },
    
    startDisparoPolling() {
        setInterval(() => {
            this.updateDisparoStatus();
        }, 2000);
    },
    
    toggleSelectAll() {
        const isChecked = elements.selectAll.checked;
        const checkboxes = document.querySelectorAll('.cliente-checkbox');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            this.handleClienteSelection(checkbox);
        });
    },
    
    handleClienteSelection(checkbox) {
        const clienteId = parseInt(checkbox.dataset.clienteId);
        const row = checkbox.closest('tr');
        
        if (checkbox.checked) {
            appState.clientesSelecionados.add(clienteId);
            row.classList.add('selected');
        } else {
            appState.clientesSelecionados.delete(clienteId);
            row.classList.remove('selected');
        }
        
        this.updateSelectAllState();
    },
    
    async marcarCobradosSelecionados() {
        const clienteIds = Array.from(appState.clientesSelecionados);
        
        if (clienteIds.length === 0) {
            alert('Nenhum cliente selecionado!');
            return;
        }
        
        utils.showModal(
            'Confirmar Marcação',
            `Deseja marcar ${clienteIds.length} cliente(s) como cobrado(s)?`,
            async () => {
                utils.hideModal();
                
                try {
                    utils.showLoading();
                    const response = await api.marcarCobrados(clienteIds);
                    
                    if (response.sucesso) {
                        utils.addLogEntry(`${clienteIds.length} clientes marcados como cobrados`, 'success');
                        
                        // Limpar seleção
                        appState.clientesSelecionados.clear();
                        
                        // Recarregar dados
                        await this.loadStats();
                        await this.loadClientes();
                        
                        alert('Clientes marcados como cobrados com sucesso!');
                    } else {
                        throw new Error('Erro ao marcar clientes');
                    }
                    
                } catch (error) {
                    utils.addLogEntry(`Erro ao marcar clientes: ${error.message}`, 'error');
                    alert(`Erro ao marcar clientes: ${error.message}`);
                } finally {
                    utils.hideLoading();
                }
            }
        );
    }
};

// Controle do Bot
const botControl = {
    async loadBotStatus() {
        try {
            const response = await fetch('/api/bot/status');
            const data = await response.json();
            
            if (data.sucesso) {
                appState.botAtivo = data.bot_ativo;
                this.updateBotUI();
            } else {
                throw new Error(data.erro || 'Erro ao carregar status do bot');
            }
        } catch (error) {
            console.error('Erro ao carregar status do bot:', error);
            utils.addLogEntry(`Erro ao carregar status do bot: ${error.message}`, 'error');
        }
    },
    
    updateBotUI() {
        if (appState.botAtivo) {
            elements.botStatus.textContent = 'Ativo';
            elements.botStatus.className = 'status online';
            elements.toggleBot.textContent = '🔴 Desativar Bot';
            elements.toggleBot.className = 'btn btn-danger';
        } else {
            elements.botStatus.textContent = 'Desativado';
            elements.botStatus.className = 'status offline';
            elements.toggleBot.textContent = '🟢 Ativar Bot';
            elements.toggleBot.className = 'btn btn-success';
        }
    },
    
    async toggleBot() {
        try {
            utils.showLoading();
            
            const response = await fetch('/api/bot/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    bot_ativo: !appState.botAtivo
                })
            });
            
            const data = await response.json();
            
            if (data.sucesso) {
                appState.botAtivo = data.bot_ativo;
                this.updateBotUI();
                utils.addLogEntry(data.mensagem, 'success');
                alert(data.mensagem);
            } else {
                throw new Error(data.erro || 'Erro ao alterar status do bot');
            }
            
        } catch (error) {
            utils.addLogEntry(`Erro ao alterar status do bot: ${error.message}`, 'error');
            alert(`Erro ao alterar status do bot: ${error.message}`);
        } finally {
            utils.hideLoading();
        }
    }
};

// Gerenciamento de Mensagens
const mensagens = {
    async loadMensagens() {
        try {
            const response = await fetch('/api/mensagens?limit=20');
            const data = await response.json();
            
            if (data.sucesso) {
                appState.mensagens = data.mensagens;
                this.renderMensagens();
                elements.totalMensagens.textContent = `${data.total} mensagens`;
            } else {
                throw new Error(data.erro || 'Erro ao carregar mensagens');
            }
        } catch (error) {
            console.error('Erro ao carregar mensagens:', error);
            utils.addLogEntry(`Erro ao carregar mensagens: ${error.message}`, 'error');
        }
    },
    
    renderMensagens() {
        const list = elements.mensagensList;
        list.innerHTML = '';
        
        if (appState.mensagens.length === 0) {
            list.innerHTML = '<p class="no-messages">Nenhuma mensagem coletada ainda.</p>';
            return;
        }
        
        appState.mensagens.forEach(msg => {
            const messageCard = document.createElement('div');
            messageCard.className = 'message-card';
            
            const dataHora = new Date(msg.created_at).toLocaleString('pt-BR');
            const clienteNome = msg.nome || 'Cliente não identificado';
            const protocolo = msg.protocolo || 'N/A';
            
            messageCard.innerHTML = `
                <div class="message-header">
                    <div class="message-info">
                        <strong>${clienteNome}</strong> (${protocolo})
                        <span class="message-phone">${msg.telefone}</span>
                    </div>
                    <div class="message-meta">
                        <span class="message-time">${dataHora}</span>
                        ${msg.respondida ? '<span class="respondida-badge">Respondida</span>' : '<span class="nao-respondida-badge">Não respondida</span>'}
                    </div>
                </div>
                <div class="message-content">
                    <p class="message-text">${msg.mensagem}</p>
                    <div class="message-classification">
                        <span class="category-badge">${msg.categoria_classificada || 'N/A'}</span>
                        <span class="confidence-badge">${(msg.confianca_classificacao || 0).toFixed(2)}</span>
                    </div>
                </div>
            `;
            
            list.appendChild(messageCard);
        });
    }
};

// Gerenciamento de Categorias
const categorias = {
    async loadCategorias() {
        try {
            const response = await fetch('/api/categorias');
            const data = await response.json();
            
            if (data.sucesso) {
                appState.categorias = data.categorias;
                this.renderCategorias();
            } else {
                throw new Error(data.erro || 'Erro ao carregar categorias');
            }
        } catch (error) {
            console.error('Erro ao carregar categorias:', error);
            utils.addLogEntry(`Erro ao carregar categorias: ${error.message}`, 'error');
        }
    },
    
    renderCategorias() {
        const grid = elements.categoriasGrid;
        grid.innerHTML = '';
        
        appState.categorias.forEach(categoria => {
            const categoriaCard = document.createElement('div');
            categoriaCard.className = `categoria-card ${categoria.ativo ? 'ativo' : 'inativo'}`;
            
            categoriaCard.innerHTML = `
                <div class="categoria-header">
                    <h4>${categoria.nome_exibicao}</h4>
                    <div class="categoria-actions">
                        <button class="btn-icon edit-categoria" data-id="${categoria.id}" title="Editar">
                            ✏️
                        </button>
                        ${this.canDeleteCategoria(categoria.categoria) ? 
                            `<button class="btn-icon delete-categoria" data-id="${categoria.id}" title="Deletar">🗑️</button>` : 
                            ''
                        }
                    </div>
                </div>
                <div class="categoria-content">
                    <p class="categoria-resposta">${categoria.resposta_padrao}</p>
                    <div class="categoria-status">
                        <span class="status-badge ${categoria.ativo ? 'ativo' : 'inativo'}">
                            ${categoria.ativo ? 'Ativo' : 'Inativo'}
                        </span>
                    </div>
                </div>
            `;
            
            grid.appendChild(categoriaCard);
        });
        
        this.bindCategoriaEvents();
    },
    
    canDeleteCategoria(categoria) {
        const categoriasPadrao = ['indignacao', 'duvida_valor', 'pedido_desconto', 'confirmacao_pagamento', 
                                 'negociacao', 'promessa_pagamento', 'contestacao', 'dados_incorretos', 
                                 'agradecimento', 'outras'];
        return !categoriasPadrao.includes(categoria);
    },
    
    bindCategoriaEvents() {
        // Editar categoria
        document.querySelectorAll('.edit-categoria').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const categoriaId = parseInt(e.target.dataset.id);
                this.editCategoria(categoriaId);
            });
        });
        
        // Deletar categoria
        document.querySelectorAll('.delete-categoria').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const categoriaId = parseInt(e.target.dataset.id);
                this.deleteCategoria(categoriaId);
            });
        });
    },
    
    editCategoria(categoriaId) {
        const categoria = appState.categorias.find(c => c.id === categoriaId);
        if (!categoria) return;
        
        appState.categoriaEditando = categoriaId;
        
        elements.categoriaModalTitle.textContent = 'Editar Categoria';
        elements.categoriaNome.value = categoria.nome_exibicao;
        elements.categoriaResposta.value = categoria.resposta_padrao;
        elements.categoriaAtivo.checked = categoria.ativo;
        
        utils.showModal(elements.categoriaModal);
    },
    
    async deleteCategoria(categoriaId) {
        const categoria = appState.categorias.find(c => c.id === categoriaId);
        if (!categoria) return;
        
        utils.showModal(
            'Confirmar Exclusão',
            `Deseja realmente excluir a categoria "${categoria.nome_exibicao}"?`,
            async () => {
                utils.hideModal();
                
                try {
                    utils.showLoading();
                    const response = await fetch(`/api/categorias/${categoriaId}`, {
                        method: 'DELETE'
                    });
                    const data = await response.json();
                    
                    if (data.sucesso) {
                        utils.addLogEntry(`Categoria "${categoria.nome_exibicao}" excluída`, 'success');
                        await this.loadCategorias();
                        alert('Categoria excluída com sucesso!');
                    } else {
                        throw new Error(data.erro || 'Erro ao excluir categoria');
                    }
                    
                } catch (error) {
                    utils.addLogEntry(`Erro ao excluir categoria: ${error.message}`, 'error');
                    alert(`Erro ao excluir categoria: ${error.message}`);
                } finally {
                    utils.hideLoading();
                }
            }
        );
    },
    
    async saveCategoria() {
        const nome = elements.categoriaNome.value.trim();
        const resposta = elements.categoriaResposta.value.trim();
        const ativo = elements.categoriaAtivo.checked;
        
        if (!nome || !resposta) {
            alert('Nome e resposta são obrigatórios!');
            return;
        }
        
        try {
            utils.showLoading();
            
            let response;
            if (appState.categoriaEditando) {
                // Atualizar categoria existente
                response = await fetch(`/api/categorias/${appState.categoriaEditando}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nome_exibicao: nome,
                        resposta_padrao: resposta,
                        ativo: ativo
                    })
                });
            } else {
                // Criar nova categoria
                const categoria = nome.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
                response = await fetch('/api/categorias', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        categoria: categoria,
                        nome_exibicao: nome,
                        resposta_padrao: resposta
                    })
                });
            }
            
            const data = await response.json();
            
            if (data.sucesso) {
                const acao = appState.categoriaEditando ? 'atualizada' : 'criada';
                utils.addLogEntry(`Categoria "${nome}" ${acao}`, 'success');
                await this.loadCategorias();
                this.closeCategoriaModal();
                alert(`Categoria ${acao} com sucesso!`);
            } else {
                throw new Error(data.erro || 'Erro ao salvar categoria');
            }
            
        } catch (error) {
            utils.addLogEntry(`Erro ao salvar categoria: ${error.message}`, 'error');
            alert(`Erro ao salvar categoria: ${error.message}`);
        } finally {
            utils.hideLoading();
        }
    },
    
    openCategoriaModal() {
        appState.categoriaEditando = null;
        elements.categoriaModalTitle.textContent = 'Nova Categoria';
        elements.categoriaForm.reset();
        elements.categoriaAtivo.checked = true;
        utils.showModal(elements.categoriaModal);
    },
    
    closeCategoriaModal() {
        utils.hideModal(elements.categoriaModal);
        appState.categoriaEditando = null;
    }
};

// Inicializar aplicação quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    app.init();
    
    // Event listeners para controle do bot
    elements.toggleBot.addEventListener('click', () => botControl.toggleBot());
    elements.refreshBotStatus.addEventListener('click', () => botControl.loadBotStatus());
    
    // Event listeners para mensagens
    elements.refreshMensagens.addEventListener('click', () => mensagens.loadMensagens());
    
    // Event listeners para categorias
    elements.addCategoria.addEventListener('click', () => categorias.openCategoriaModal());
    elements.refreshCategorias.addEventListener('click', () => categorias.loadCategorias());
    elements.categoriaCancel.addEventListener('click', () => categorias.closeCategoriaModal());
    elements.categoriaForm.addEventListener('submit', (e) => {
        e.preventDefault();
        categorias.saveCategoria();
    });
    
    // Carregar dados na inicialização
    botControl.loadBotStatus();
    mensagens.loadMensagens();
    categorias.loadCategorias();
});


