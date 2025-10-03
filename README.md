# PIE IV - Projeto Integrador e Extensionista

Sistema completo desenvolvido como projeto acadêmico, implementando uma arquitetura moderna e escalável.

## Arquitetura do Projeto

Este projeto foi estruturado seguindo o padrão de microserviços, permitindo escalabilidade e manutenibilidade. Cada aplicação pode ser desenvolvida, testada e implantada independentemente.

```
virtual-assistant/
├── backend/           # API RESTful com FastAPI
├── frontend/          # Interface web
├── chatbot/           # Interface Telegram/Whatsapp
├── docker-compose.yml # Orquestração dos serviços
└── README.md          # Este arquivo
```

## Aplicações

### Backend API

**Status:** Concluído - CRUD de usuários

API RESTful desenvolvida com FastAPI, MySQL e autenticação JWT.

- **Tecnologias:** FastAPI, SQLModel, MySQL, Docker
- **Funcionalidades:** Autenticação, CRUD de usuários, validações
- **Documentação:** [backend/README.md](./backend/README.md)
- **URL Local:** http://localhost:8000
- **Swagger:** http://localhost:8000/api/v1/docs

### Frontend Web

**Status:** Concluído - Dashboard de gerenciamento

Interface web responsiva para gerenciamento do sistema PIE IV.

- **Tecnologias:** Django, Bootstrap, Python, Requests
- **Funcionalidades:** Dashboard, CRUD de usuários, autenticação JWT, interface responsiva
- **Documentação:** [frontend/README.md](./frontend/README.md)
- **URL Local:** http://localhost:3000

### ChatBot

**Status:** Planejado

Interface de chatbot para interação com a API.

- **Tecnologias:** FastAPI ou Flask, Telegram e/ou Whatsapp
- **Funcionalidades:** Conversas em tempo real, integração com serviços externos, ...
- **URL Local:** http://localhost:5000 (planejado)

## Executando o Projeto Completo

### Pré-requisitos

- Docker
- Docker Compose
- Git

### Início Rápido

1. **Clone o repositório:**

```bash
git clone <url-do-repositorio>
cd virtual-assistant
```

2. **Configure as variáveis de ambiente:**

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite as configurações conforme necessário
nano .env
```

3. **Inicie todos os serviços:**

```bash
docker compose up -d --build
```
