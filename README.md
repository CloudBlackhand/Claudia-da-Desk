# 🤖 Bot WhatsApp - Sistema de Cobrança

Sistema completo de disparo de mensagens via WhatsApp com IA conversacional para cobrança, integrado com Waha API e Hugging Face.

## ✨ Funcionalidades

- **📤 Disparo de Mensagens**: Envio em massa com controle de duplicatas
- **🤖 Bot Conversacional**: Respostas automáticas via Hugging Face
- **📊 Dashboard Completo**: Interface web para gerenciamento
- **💾 Controle de Duplicatas**: Sistema evita cobrar a mesma pessoa múltiplas vezes
- **📱 Integração Waha**: Usa NOWEB engine com armazenamento de conversas
- **🎯 Filtros Inteligentes**: Disparar para todos, cobrados ou não cobrados
- **📝 Templates Personalizáveis**: Mensagens customizáveis com variáveis

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Serviços      │
│   (HTML/CSS/JS) │◄──►│   (Flask)       │◄──►│   Externos      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   Waha API      │
                       │   (Dados)       │    │   + HuggingFace │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Deploy no Railway

### 1. Preparar o Projeto

```bash
# Clone o repositório
git clone <seu-repositorio>
cd bot-whatsapp-cobranca

# Instalar dependências localmente (opcional)
cd backend
pip install -r requirements.txt
```

### 2. Configurar Railway

1. **Criar conta no Railway**: [railway.app](https://railway.app)

2. **Conectar repositório GitHub**:
   - New Project → Deploy from GitHub repo
   - Selecionar seu repositório

3. **Adicionar PostgreSQL**:
   - Add Service → Database → PostgreSQL
   - Railway criará automaticamente a `DATABASE_URL`

4. **Configurar variáveis de ambiente**:
   ```
   WAHA_API_KEY=sua_chave_waha_aqui
   WAHA_API_URL=https://sua-instancia-waha.com
   HUGGINGFACE_API_KEY=sua_chave_huggingface_aqui
   HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
   PORT=5000
   ```

### 3. Deploy Automático

O Railway detectará automaticamente:
- **Procfile**: Comando de inicialização
- **railway.json**: Configurações de deploy
- **requirements.txt**: Dependências Python

## 🔧 Configuração Local

### Pré-requisitos

- Python 3.8+
- PostgreSQL
- Instância Waha rodando
- Chave API Hugging Face

### Instalação

```bash
# 1. Clonar repositório
git clone <seu-repositorio>
cd bot-whatsapp-cobranca

# 2. Instalar dependências
cd backend
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas configurações

# 4. Executar aplicação
python app.py
```

### Variáveis de Ambiente

```env
# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/bot_cobranca

# Waha API
WAHA_API_KEY=sua_chave_waha
WAHA_API_URL=http://localhost:3000

# Hugging Face
HUGGINGFACE_API_KEY=sua_chave_hf
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Servidor
PORT=5000
```

## 📱 Configuração do Waha

### 1. Instalar Waha

```bash
# Via Docker (recomendado)
docker run -d --name waha \
  -p 3000:3000 \
  -e WAHA_API_KEY=sua_chave_aqui \
  devlikeapro/waha:latest
```

### 2. Configurar Sessão

O sistema automaticamente configura a sessão Waha com:
- **Engine**: NOWEB
- **Store**: Habilitado (armazena conversas)
- **FullSync**: False (3 meses de histórico)

### 3. Webhook

O webhook é configurado automaticamente para receber mensagens dos clientes.

## 🤖 Configuração Hugging Face

### 1. Obter API Key

1. Acesse [huggingface.co](https://huggingface.co)
2. Crie uma conta
3. Vá em Settings → Access Tokens
4. Crie um novo token

### 2. Modelos Recomendados

- `mistralai/Mistral-7B-Instruct-v0.2` (gratuito, boa qualidade)
- `HuggingFaceH4/zephyr-7b-beta` (gratuito, rápido)
- `meta-llama/Llama-2-7b-chat-hf` (requer aprovação)

## 📊 Como Usar

### 1. Upload de Dados

1. Acesse a interface web
2. Clique em "Selecionar Arquivo JSON"
3. Faça upload do arquivo com dados dos clientes
4. Aguarde a importação

### 2. Configurar Template

```text
Olá {nome}!

Identificamos um débito em seu protocolo {protocolo}.

Valores em aberto:
• FPD: R$ {fpd_cobrado}
• SPD: R$ {spd_cobrado}

Urgência: {urgencia_geral}

Para regularizar sua situação, entre em contato conosco.

Atenciosamente,
Equipe de Cobrança
```

**Variáveis disponíveis:**
- `{nome}` - Nome do cliente
- `{protocolo}` - Número do protocolo
- `{documento}` - CPF/CNPJ
- `{fpd_cobrado}` - Valor FPD em aberto
- `{spd_cobrado}` - Valor SPD em aberto
- `{urgencia_geral}` - Nível de urgência

### 3. Disparar Mensagens

- **Disparar Todos**: Envia para todos os clientes
- **Disparar Não Cobrados**: Apenas clientes não cobrados
- **Disparar Cobrados**: Apenas clientes já cobrados

### 4. Bot Conversacional

Quando clientes respondem às mensagens:
1. Bot busca dados do cliente no banco
2. Recupera histórico da conversa do Waha Store
3. Gera resposta contextualizada via Hugging Face
4. Envia resposta automaticamente

## 🗄️ Estrutura do Banco

### Tabela `clientes`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | Chave primária |
| protocolo | VARCHAR | Protocolo único |
| nome | VARCHAR | Nome do cliente |
| documento | VARCHAR | CPF/CNPJ |
| telefone1 | VARCHAR | Telefone principal |
| telefone2 | VARCHAR | Telefone secundário |
| fpd_cobrado | DECIMAL | Valor FPD em aberto |
| spd_cobrado | DECIMAL | Valor SPD em aberto |
| urgencia_geral | VARCHAR | Nível de urgência |
| **cobrado** | INTEGER | **0=não cobrado, 1=cobrado** |
| data_cobranca | TIMESTAMP | Data da última cobrança |
| created_at | TIMESTAMP | Data de criação |

### Tabela `templates`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | Chave primária |
| template_text | TEXT | Texto do template |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data de atualização |

## 🔒 Segurança

- **Rate Limiting**: Delay entre mensagens para evitar bloqueio
- **Controle de Duplicatas**: Sistema evita cobrar a mesma pessoa
- **Validação de Dados**: Verificação de arquivos e inputs
- **Logs Detalhados**: Rastreamento de todas as operações

## 🐛 Troubleshooting

### Problemas Comuns

**1. Waha não conecta**
- Verifique se a instância Waha está rodando
- Confirme a `WAHA_API_KEY` e `WAHA_API_URL`
- Teste a conexão via interface

**2. Hugging Face falha**
- Verifique a `HUGGINGFACE_API_KEY`
- Confirme se o modelo está disponível
- Teste a conexão via interface

**3. Banco não conecta**
- Verifique a `DATABASE_URL`
- Confirme se o PostgreSQL está rodando
- Teste a conexão

**4. Disparo não funciona**
- Verifique se há clientes no banco
- Confirme se o template está configurado
- Verifique os logs de erro

### Logs

Os logs são exibidos na interface web em tempo real. Para logs detalhados do servidor, verifique o console do Railway.

## 📈 Monitoramento

### Métricas Disponíveis

- Total de clientes
- Clientes cobrados vs não cobrados
- Status do disparo em tempo real
- Logs de operações

### Status dos Serviços

A interface mostra o status em tempo real:
- 🟢 **Waha**: Conectado/Desconectado
- 🟢 **Hugging Face**: Conectado/Desconectado

## 🤝 Suporte

Para suporte técnico:
1. Verifique os logs na interface
2. Confirme as configurações
3. Teste as conexões via interface
4. Consulte a documentação do Waha e Hugging Face

## 📄 Licença

Este projeto é de uso interno. Não redistribuir sem autorização.

---

**Desenvolvido para sistema de cobrança automatizada com IA conversacional** 🤖💬


