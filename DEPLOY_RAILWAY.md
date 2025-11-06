# Deploy no Railway.app - Guia Rápido 🚀

## Por que Railway?
✅ Deploy automático do GitHub  
✅ Suporte nativo a Docker Compose  
✅ $5 de crédito grátis por mês  
✅ MySQL incluído  
✅ SSL automático  

## Passo a Passo

### 1. Preparar o GitHub
```bash
git add .
git commit -m "feat: configuração para deploy no Railway"
git push origin master
```

### 2. Criar conta no Railway
1. Acesse: https://railway.app/
2. Clique em **"Start a New Project"**
3. Conecte sua conta do GitHub

### 3. Deploy do Projeto

#### Opção A: Deploy via Dashboard (MAIS FÁCIL)
1. No Railway, clique em **"New Project"**
2. Escolha **"Deploy from GitHub repo"**
3. Selecione o repositório **"Virtual-Assistant"**
4. Railway vai detectar automaticamente o `docker-compose.yml`

#### Opção B: Deploy via CLI
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Fazer login
railway login

# Iniciar projeto
railway init

# Deploy
railway up
```

### 4. Configurar Banco de Dados
1. No dashboard do Railway, clique em **"+ New"**
2. Selecione **"Database" → "MySQL"**
3. Railway criará o banco automaticamente

### 5. Adicionar Variáveis de Ambiente

No Railway Dashboard, vá em cada serviço e adicione:

#### Backend Service
```
SECRET_KEY=seu_secret_key_aqui_gere_um_novo
DATABASE_URL=mysql+pymysql://root:senha@mysql:3306/virtual_assistant
OPENAI_API_KEY=sua_chave_openai_aqui
ACCESS_TOKEN_EXPIRE_SECONDS=86400
CORS_ORIGINS=https://seu-frontend.railway.app
```

#### Frontend Service
```
DEBUG=False
SECRET_KEY=seu_django_secret_key_aqui
API_BASE_URL=https://seu-backend.railway.app
ALLOWED_HOSTS=seu-frontend.railway.app
```

**⚠️ IMPORTANTE:** Railway gera automaticamente `DATABASE_URL` quando você adiciona MySQL. Use essa variável!

### 6. Conectar os Serviços
Railway conecta automaticamente os containers que dependem uns dos outros.

1. O MySQL receberá uma URL interna
2. Configure `DATABASE_URL` no backend para apontar para o MySQL
3. Configure `API_BASE_URL` no frontend para apontar para o backend

### 7. Acessar sua Aplicação
Após o deploy, Railway fornecerá URLs públicas:
- **Backend**: `https://seu-backend.railway.app`
- **Frontend**: `https://seu-frontend.railway.app`
- **API Docs**: `https://seu-backend.railway.app/api/v1/docs`

## Dicas Importantes

### Gerar SECRET_KEY
```python
# Python
import secrets
print(secrets.token_urlsafe(32))
```

### Monitorar Logs
No dashboard Railway:
- Clique no serviço
- Vá em **"Logs"** para ver em tempo real

### Custo
- **$5/mês grátis** (500 horas de execução)
- Suficiente para desenvolvimento e testes
- Upgrade quando necessário

### Redeploy Automático
Qualquer `git push` para master dispara redeploy automático! 🎉

## Troubleshooting

### Erro de conexão com MySQL
- Verifique se DATABASE_URL está correta
- Use a URL interna fornecida pelo Railway
- Formato: `mysql+pymysql://user:pass@railway.internal:3306/db`

### CORS errors
- Adicione a URL do frontend em `CORS_ORIGINS` do backend
- Formato: `https://seu-frontend.railway.app`

### Build falha
- Verifique os logs de build no Railway
- Confirme que Dockerfile está correto
- Verifique dependências no requirements.txt

## Próximos Passos
1. ✅ Fazer push do código
2. ✅ Criar projeto no Railway
3. ✅ Adicionar variáveis de ambiente
4. ✅ Testar a aplicação
5. ✅ Configurar domínio customizado (opcional)

---

**Precisa de ajuda?** 
- Documentação: https://docs.railway.app/
- Discord: https://discord.gg/railway
