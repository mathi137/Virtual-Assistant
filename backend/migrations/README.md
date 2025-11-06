# Database Migrations

Este diretório contém scripts de migração para atualizar o schema do banco de dados.

---

## 🔄 RECRIAR SERVIÇO MYSQL (Recomendado)

Se você está com problemas de schema, é mais fácil **recriar o serviço MySQL** no Railway. Veja o guia completo: [GUIA_RECRIAR_MYSQL.md](../../GUIA_RECRIAR_MYSQL.md)

---

## Migração Atual: Adicionar agent_id à tabela client

### Problema

O modelo `Client` foi atualizado para incluir o campo `agent_id`, mas o banco de dados ainda não possui essa coluna, causando o erro:

```
pymysql.err.OperationalError: (1054, "Unknown column 'client.agent_id' in 'field list'")
```

### Solução

#### Opção 1: Executar o script Python (Recomendado)

1. Certifique-se de que o arquivo `.env` está configurado com `DATABASE_URL`
2. Execute o script de migração:
   ```bash
   cd backend
   python -m migrations.run_migration
   ```

#### Opção 2: Executar SQL manualmente

Se preferir executar o SQL diretamente no banco de dados:

```sql
-- Adicionar a coluna agent_id
ALTER TABLE client
ADD COLUMN agent_id INT NULL AFTER user_id;

-- Adicionar índice para melhor performance
CREATE INDEX idx_client_agent_id ON client(agent_id);
```

### Verificação

Após executar a migração, reinicie a aplicação. O erro não deve mais ocorrer.

### Reversão

Se precisar reverter a migração:

```sql
-- Remover o índice
DROP INDEX idx_client_agent_id ON client;

-- Remover a coluna
ALTER TABLE client DROP COLUMN agent_id;
```

## Futuras Migrações

Para adicionar novas migrações:

1. Crie um arquivo SQL descritivo em `migrations/`
2. Opcionalmente, crie um script Python correspondente
3. Documente no README
4. Execute antes de fazer deploy
