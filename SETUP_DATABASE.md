# 🗄️ Configuração do Banco PostgreSQL no Railway

## 📋 Passo a Passo

### 1. Instalar Railway CLI (se não tiver)
```bash
# Linux/Mac
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 -useb | iex
```

### 2. Fazer Login no Railway
```bash
railway login
```

### 3. Conectar ao Projeto
```bash
railway link -p 7e3ed4cd-ecd1-4142-9bf4-e0c13a4fe487
```

### 4. Executar Script de Configuração
```bash
railway run python setup_database.py
```

## 🎯 O que o Script Faz

✅ **Cria 4 tabelas:**
- `clientes` - Dados dos clientes para cobrança
- `templates` - Templates de mensagens personalizáveis  
- `mensagens_recebidas` - Histórico de mensagens dos clientes
- `categorias_resposta` - Categorias para respostas automáticas

✅ **Insere dados padrão:**
- Template de mensagem de cobrança
- 5 categorias de resposta automática
- Configurações iniciais

## 🔍 Verificar se Funcionou

Após executar o script, você pode verificar no Railway:

1. Acesse o painel do PostgreSQL
2. Vá em "Database" → "Data" 
3. Deve aparecer as 4 tabelas criadas

## 🚀 Próximos Passos

Após configurar o banco:

1. **Testar a aplicação** - Acesse a URL do Railway
2. **Upload de dados** - Use o JSON de teste para importar clientes
3. **Configurar Waha** - Adicionar WAHA_API_KEY nas variáveis de ambiente
4. **Configurar Hugging Face** - Adicionar HUGGINGFACE_API_KEY (opcional)

## 🆘 Se Der Erro

Se o script falhar:

1. Verifique se está conectado ao projeto correto:
   ```bash
   railway status
   ```

2. Verifique as variáveis de ambiente:
   ```bash
   railway variables
   ```

3. Execute novamente:
   ```bash
   railway run python setup_database.py
   ```

