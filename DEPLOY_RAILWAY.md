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

**IMPORTANTE:** Railway precisa de serviços separados para cada componente.

#### Passo 3.1: Deploy do Backend

1. No Railway, clique em **"New Project"**
2. Escolha **"Deploy from GitHub repo"**
3. Selecione o repositório **"Virtual-Assistant"**
4. Railway detectará o `Dockerfile` na raiz (configurado para o backend)

#### Passo 3.2: Adicionar MySQL

1. No mesmo projeto, clique **"+ New"**
2. Selecione **"Database" → "MySQL"**
3. Railway cria e fornece a `DATABASE_URL` automaticamente

#### Passo 3.3: Configurar Variáveis do Backend

No serviço do backend, adicione:

```
SECRET_KEY=seu_secret_key_aqui_gere_um_novo
OPENAI_API_KEY=sua_chave_openai_aqui
ACCESS_TOKEN_EXPIRE_SECONDS=86400
CORS_ORIGINS=*
```

**Nota:** Railway injeta automaticamente `DATABASE_URL` do MySQL!

#### Passo 3.4: Deploy do Frontend (Separado)

1. Crie um **NOVO projeto** no Railway
2. Deploy do mesmo repositório **"Virtual-Assistant"**
3. Mas na configuração, especifique o **Root Directory: `frontend`**
4. Railway detectará o `Dockerfile` do frontend

#### Passo 3.5: Configurar Variáveis do Frontend

```
DEBUG=False
SECRET_KEY=seu_django_secret_key_aqui
API_BASE_URL=https://seu-backend.railway.app
ALLOWED_HOSTS=.railway.app
```

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

### Erro: "No pyproject.toml found"
- ✅ **RESOLVIDO**: Criado `Dockerfile` na raiz que copia a pasta `backend/`
- O erro acontecia porque Railway buildava da raiz, mas pyproject.toml está em `backend/`

### Erro de conexão com MySQL
- Verifique se DATABASE_URL está correta
- Railway injeta automaticamente quando você adiciona o MySQL
- Formato: `mysql+aiomysql://user:pass@mysql.railway.internal:3306/railway`

### CORS errors
- Use `CORS_ORIGINS=*` no backend (ou especifique o domínio do frontend)
- Formato: `https://seu-frontend.railway.app`

### Build falha
- Verifique os logs de build no Railway
- Confirme que todas as dependências estão no `pyproject.toml`
- Para frontend, verifique `requirements.txt`

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
