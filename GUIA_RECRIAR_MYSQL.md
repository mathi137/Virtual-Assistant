# 🔄 Guia: Recriar Serviço MySQL no Railway

## ⚠️ IMPORTANTE: Backup Primeiro!

Antes de deletar o serviço MySQL, **salve os dados importantes**:

### Opção 1: Exportar via Railway CLI

```bash
railway login
railway link
railway connect mysql

# Dentro do MySQL
SELECT * FROM user;
SELECT * FROM client;
# Copie os dados importantes
```

### Opção 2: Anotar Dados Manualmente

Acesse o Railway Dashboard → MySQL → Data e anote:

- ✅ Usuários cadastrados
- ✅ Clientes cadastrados
- ✅ Outras informações importantes

---

## 📋 Passo a Passo

### 1️⃣ Deletar o Serviço MySQL Atual

1. Acesse o **Railway Dashboard**
2. Clique no serviço **MySQL** (o que você estava visualizando)
3. Vá em **Settings** (última aba)
4. Role até o final da página
5. Clique em **🗑️ Delete Service**
6. Digite o nome do serviço para confirmar
7. Clique em **Delete**

### 2️⃣ Criar Novo Serviço MySQL

1. No Dashboard do projeto, clique em **+ New**
2. Selecione **Database**
3. Escolha **MySQL**
4. Aguarde alguns segundos (o Railway cria automaticamente)

### 3️⃣ Conectar ao Backend

1. Clique no serviço **backend**
2. Vá em **Variables**
3. Verifique se existe a variável `DATABASE_URL`
4. Se não existir, adicione:

   ```
   DATABASE_URL=mysql+aiomysql://${{MySQL.MYSQL_USER}}:${{MySQL.MYSQL_PASSWORD}}@${{MySQL.MYSQL_HOST}}:${{MySQL.MYSQL_PORT}}/${{MySQL.MYSQL_DATABASE}}
   ```

5. Ou simplesmente:
   ```
   DATABASE_URL=${{MySQL.DATABASE_URL}}
   ```
   E depois edite para adicionar `+aiomysql` após `mysql`:
   ```
   mysql+aiomysql://user:pass@host:port/database
   ```

### 4️⃣ Fazer Redeploy do Backend

1. Ainda no serviço **backend**
2. Vá em **Deployments**
3. Clique nos três pontinhos ⋮ do último deployment
4. Clique em **Redeploy**

Ou force um novo deploy fazendo um commit:

```bash
git commit --allow-empty -m "Trigger redeploy"
git push
```

### 5️⃣ Verificar Logs

1. Clique no serviço **backend**
2. Vá em **Deployments**
3. Clique no deployment ativo
4. Observe os logs

Você deve ver:

```
INFO sqlalchemy.engine.Engine CREATE TABLE user ...
INFO sqlalchemy.engine.Engine CREATE TABLE client ...
INFO sqlalchemy.engine.Engine CREATE TABLE platform ...
...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6️⃣ Criar Usuário Inicial

Acesse a API e crie um novo usuário admin:

```bash
curl -X POST "https://seu-backend.railway.app/api/v1/user/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "otavio@adm.com",
    "password": "sua_senha_aqui"
  }'
```

Ou use o Postman/Insomnia para fazer o POST.

---

## ✅ Verificação Final

1. **Acesse o MySQL no Railway:**

   - Clique no serviço MySQL
   - Vá em **Data**
   - Verifique se as tabelas foram criadas:
     - ✅ `user`
     - ✅ `client` (com a coluna `agent_id`)
     - ✅ `platform`
     - ✅ `message`
     - ✅ `chat`

2. **Teste a API:**

   ```bash
   # Login
   curl -X POST "https://seu-backend.railway.app/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=otavio@adm.com&password=sua_senha"

   # Listar clientes (deve retornar array vazio no início)
   curl "https://seu-backend.railway.app/api/v1/client/" \
     -H "Authorization: Bearer SEU_TOKEN"
   ```

---

## 🎯 Vantagens de Recriar

✅ Schema 100% atualizado com todos os campos  
✅ Sem necessidade de migrações manuais  
✅ Banco limpo sem dados inconsistentes  
✅ Resolve todos os erros de "Unknown column"  
✅ Mais rápido que executar migrações

---

## 📝 Notas

- O processo todo leva menos de 5 minutos
- Todos os dados antigos serão perdidos (por isso o backup!)
- O Railway recria automaticamente as variáveis de ambiente
- O `init_db()` no código cria automaticamente todas as tabelas
- A estrutura fica idêntica ao modelo Python

---

## ❓ Problemas?

Se após recriar ainda houver erros:

1. **Verifique a `DATABASE_URL`:**
   - Deve ter `mysql+aiomysql://` (não apenas `mysql://`)
2. **Verifique os logs do backend:**
   - Procure por `CREATE TABLE` nos logs
3. **Verifique se todas as tabelas foram criadas:**

   - Railway Dashboard → MySQL → Data → Tables

4. **Força um novo deploy:**
   ```bash
   git commit --allow-empty -m "Force redeploy"
   git push
   ```
