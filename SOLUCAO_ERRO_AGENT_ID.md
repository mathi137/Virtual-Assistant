# 🔧 Solução do Erro: Unknown column 'client.agent_id'

## ❌ Problema Identificado

A aplicação está falhando com o seguinte erro:

```
pymysql.err.OperationalError: (1054, "Unknown column 'client.agent_id' in 'field list'")
```

### Causa

O modelo Python `Client` foi atualizado para incluir o campo `agent_id`, mas o schema do banco de dados MySQL no Railway ainda não possui essa coluna.

## ✅ Solução

Criou 3 arquivos para resolver o problema:

### 1. **SQL Manual** (`backend/migrations/add_agent_id_to_client.sql`)

- Contém o SQL puro para adicionar a coluna

### 2. **Script Python** (`backend/migrations/run_migration.py`)

- Script automatizado para executar a migração
- Verifica se a coluna já existe antes de adicionar
- Usa as credenciais do `.env`

### 3. **Documentação** (`backend/migrations/README.md`)

- Instruções completas de como executar

## 🚀 Como Executar a Migração no Railway

### Opção 1: Via Railway CLI (Recomendado para produção)

1. **Conecte ao banco MySQL do Railway:**

   ```bash
   railway connect mysql
   ```

2. **Execute o SQL:**

   ```sql
   ALTER TABLE client ADD COLUMN agent_id INT NULL AFTER user_id;
   CREATE INDEX idx_client_agent_id ON client(agent_id);
   ```

3. **Verifique:**
   ```sql
   DESCRIBE client;
   ```

### Opção 2: Via Railway Dashboard

1. Acesse o Railway Dashboard
2. Vá para o serviço MySQL
3. Abra o "Query Editor" ou "Database Admin"
4. Execute o SQL:
   ```sql
   ALTER TABLE client ADD COLUMN agent_id INT NULL AFTER user_id;
   CREATE INDEX idx_client_agent_id ON client(agent_id);
   ```

### Opção 3: Via Script Python Localmente

**IMPORTANTE:** Você precisará das credenciais do banco Railway no seu `.env`

1. **Configure o `.env` com DATABASE_URL do Railway:**

   ```bash
   # No Railway, copie a DATABASE_URL do MySQL plugin
   DATABASE_URL=mysql+aiomysql://user:password@host:port/railway
   ```

2. **Execute a migração:**
   ```bash
   cd backend
   python -m migrations.run_migration
   ```

## 📋 Verificação Pós-Migração

Após executar a migração:

1. **Verifique se a coluna foi adicionada:**

   ```sql
   DESCRIBE client;
   ```

   Você deve ver `agent_id` na lista de colunas.

2. **Reinicie a aplicação no Railway:**

   - O Railway reiniciará automaticamente ao fazer um novo deploy
   - Ou force um redeploy

3. **Teste a aplicação:**
   - Tente acessar `GET /api/v1/client/`
   - Tente criar um novo cliente `POST /api/v1/client/`

## 🔄 Reversão (Se Necessário)

Se precisar reverter a mudança:

```sql
DROP INDEX idx_client_agent_id ON client;
ALTER TABLE client DROP COLUMN agent_id;
```

## 📝 Notas Importantes

- ✅ A coluna é `NULL` por padrão, então registros existentes não serão afetados
- ✅ Foi adicionado um índice para melhorar a performance de queries
- ✅ A migração é idempotente (pode ser executada múltiplas vezes sem erros)
- ⚠️ Backup do banco de dados é sempre recomendado antes de alterações

## 🎯 Próximos Passos

Considere implementar um sistema de migração adequado:

1. **Alembic** (Python)
2. **Flask-Migrate** (se usar Flask)
3. **SQLAlchemy Alembic** (recomendado para FastAPI)

Isso evitará problemas futuros com schema inconsistente entre código e banco de dados.
