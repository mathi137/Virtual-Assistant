# Backend API

API RESTful desenvolvida com FastAPI e MySQL para o projeto PIE IV.

## Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLModel** - ORM baseado em SQLAlchemy com tipagem
- **MySQL** - Banco de dados relacional
- **JWT** - Autenticação via tokens
- **Bcrypt** - Hash de senhas
- **Docker** - Containerização

## Funcionalidades

### Autenticação
- [x] Login com email e senha
- [x] Geração de tokens JWT
- [x] Proteção de rotas com middleware

### Gerenciamento de Usuários
- [x] CRUD completo de usuários
- [x] Hash automático de senhas
- [x] Validação de dados de entrada
- [x] Rotas protegidas para perfil do usuário

## Rotas da API

### Autenticação

#### POST `/auth/token`
Realiza login e retorna token de acesso.

**Parâmetros (form-data):**
```
username: user@example.com  (email do usuário)
password: senha123
```

**Resposta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Usuários

#### POST `/users/`
Cria um novo usuário.

**Body:**
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "id": 1,
  "email": "usuario@example.com"
}
```

#### GET `/users/{user_id}`
Busca um usuário pelo ID.

**Resposta:**
```json
{
  "id": 1,
  "email": "usuario@example.com"
}
```

#### PUT `/users/{user_id}`
Atualiza dados de um usuário.

**Body (campos opcionais):**
```json
{
  "email": "novo@example.com",
  "password": "novasenha123"
}
```

**Resposta:**
```json
{
  "id": 1,
  "email": "novo@example.com"
}
```

#### DELETE `/users/{user_id}`
Remove um usuário (soft delete).

**Resposta:** `204 No Content`

### Perfil do Usuário (Rotas Protegidas)

> **Nota:** Todas as rotas abaixo requerem autenticação via token Bearer.

#### GET `/users/me/`
Retorna dados do usuário autenticado.

**Headers:**
```
Authorization: Bearer {token}
```

**Resposta:**
```json
{
  "id": 1,
  "email": "usuario@example.com"
}
```

#### PUT `/users/me/`
Atualiza dados do usuário autenticado.

**Headers:**
```
Authorization: Bearer {token}
```

**Body (campos opcionais):**
```json
{
  "email": "novo@example.com",
  "password": "novasenha123"
}
```

**Resposta:**
```json
{
  "id": 1,
  "email": "novo@example.com"
}
```

#### DELETE `/users/me/`
Remove conta do usuário autenticado.

**Headers:**
```
Authorization: Bearer {token}
```

**Resposta:** `204 No Content`

## Executando o Projeto

### Pré-requisitos
- Docker
- Docker Compose

### Passos

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd virtual-assistant/backend
```

2. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Inicie os serviços:**
```bash
docker compose up -d
```

4. **Acesse a API:**
```
- URL base: `http://localhost:8000`
- Documentação Swagger: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`
```

## Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Para acessar rotas protegidas:

1. Faça login via `/auth/token`
2. Use o token retornado no header `Authorization: Bearer {token}`
3. O token expira em no tempo definido por variável de ambiente

## Validações

### UserUpdate
- Pelo menos um campo deve ser fornecido para atualização
- Campos extras são rejeitados automaticamente
- Senhas são automaticamente criptografadas

### Segurança
- Senhas são hasheadas com bcrypt
- Tokens JWT com expiração configurável
- Validação de dados de entrada com Pydantic
- Proteção contra campos extras nas requisições
