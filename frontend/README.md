# Frontend Dashboard - PIE IV

Dashboard web desenvolvido em Django para gerenciamento do sistema PIE IV.

## Tecnologias

- **Django 4.2.7** - Framework web Python
- **Bootstrap 5.3** - Framework CSS responsivo
- **Font Awesome** - Ícones
- **Requests** - Cliente HTTP para comunicação com API

## Funcionalidades

### Autenticação

- [x] Login via API FastAPI backend
- [x] Gerenciamento de sessão com tokens JWT
- [x] Logout com limpeza de sessão

### Dashboard Principal

- [x] Estatísticas de usuários
- [x] Visão geral do sistema
- [x] Ações rápidas
- [x] Interface responsiva

### Gerenciamento de Usuários

- [x] Listar todos os usuários
- [x] Criar novos usuários
- [x] Visualizar detalhes do usuário
- [x] Editar informações do usuário
- [x] Deletar usuários
- [x] Interface intuitiva com modais de confirmação

## Estrutura do Projeto

```
frontend/
├── core/                   # Configurações do Django
│   ├── settings.py        # Configurações principais
│   ├── urls.py           # URLs principais
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── dashboard/             # Aplicação principal
│   ├── views.py          # Views do dashboard
│   ├── urls.py           # URLs da aplicação
│   ├── models.py         # Modelos (apenas para referência)
│   ├── services.py       # Serviços de integração com API
│   └── apps.py           # Configuração da app
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   └── dashboard/        # Templates específicos
│       ├── home.html     # Página principal
│       ├── login.html    # Login
│       └── users/        # Templates de usuários
├── static/               # Arquivos estáticos (CSS, JS, imagens)
├── manage.py             # Script de gerenciamento Django
├── requirements.txt      # Dependências Python
├── Dockerfile           # Containerização
└── .env                 # Variáveis de ambiente
```

## Configuração e Execução

### Pré-requisitos

- Python 3.11+
- Backend API rodando (FastAPI)

### Método 1: Execução Local

1. **Instale as dependências:**

```bash
cd frontend
pip install -r requirements.txt
```

2. **Configure as variáveis de ambiente:**

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
# API_BASE_URL=http://localhost:8000/api/v1
```

3. **Execute as migrações:**

```bash
python manage.py migrate
```

4. **Crie um superusuário (opcional):**

```bash
python manage.py createsuperuser
```

5. **Inicie o servidor:**

```bash
python manage.py runserver 0.0.0.0:3000
```

6. **Acesse o dashboard:**

```
http://localhost:3000
```

### Método 2: Docker

1. **Construir a imagem:**

```bash
cd frontend
docker build -t pie4-frontend .
```

2. **Executar o container:**

```bash
docker run -p 3000:3000 --env-file .env pie4-frontend
```

### Método 3: Docker Compose (Recomendado)

Execute o docker-compose na raiz do projeto para subir frontend + backend:

```bash
cd ..  # Voltar para a raiz do projeto
docker compose up -d
```

## Integração com API Backend

O dashboard se comunica com a API FastAPI através da classe `APIService` localizada em `dashboard/services.py`.

### Endpoints Utilizados

- `POST /auth/token` - Login e obtenção de token JWT
- `GET /user/{id}` - Buscar usuário por ID
- `POST /user/` - Criar novo usuário
- `PUT /user/{id}` - Atualizar usuário
- `DELETE /user/{id}` - Deletar usuário
- `GET /user/me/` - Dados do usuário autenticado

### Autenticação

O sistema utiliza tokens JWT obtidos via login. O token é armazenado na sessão do Django e incluído automaticamente nos headers das requisições para a API:

```
Authorization: Bearer {token}
```

## Personalização

### Temas e Estilos

O dashboard utiliza Bootstrap 5 como base. Personalizações podem ser feitas:

1. **CSS customizado:** Adicione estilos em `static/css/custom.css`
2. **Templates:** Modifique os templates em `templates/dashboard/`
3. **Cores:** Altere as variáveis CSS no template `base.html`

### Funcionalidades Futuras

- [ ] Gerenciamento de agentes/bots
- [ ] Relatórios e analytics
- [ ] Upload de arquivos
- [ ] Notificações em tempo real
- [ ] Configurações de sistema
- [ ] Logs de auditoria

## Desenvolvimento

### Estrutura de Views

Todas as views herdam de `django.views.View` e implementam os métodos HTTP apropriados:

```python
class UserListView(View):
    def get(self, request):
        # Listar usuários
        pass
```

### Tratamento de Erros

Erros da API são capturados e exibidos como mensagens do Django:

```python
try:
    api_service = APIService(token)
    result = api_service.get_users()
except Exception as e:
    messages.error(request, f'Erro: {str(e)}')
```

### Sessão e Autenticação

O sistema gerencia a autenticação via sessão do Django:

```python
# Login
request.session['access_token'] = token
request.session['user_email'] = email

# Verificação
if not request.session.get('access_token'):
    return redirect('dashboard:login')

# Logout
request.session.flush()
```

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com API:**

   - Verifique se o backend está rodando
   - Confirme a URL da API no arquivo `.env`

2. **Problemas de CORS:**

   - O backend já está configurado para permitir CORS

3. **Token expirado:**

   - Faça logout e login novamente
   - Verifique as configurações de expiração no backend

4. **Estilos não carregam:**
   - Execute `python manage.py collectstatic`
   - Verifique as configurações de arquivos estáticos

## URLs Disponíveis

```
/                           # Dashboard principal
/login/                     # Login
/logout/                    # Logout
/users/                     # Lista de usuários
/users/create/             # Criar usuário
/users/{id}/               # Detalhes do usuário
/users/{id}/edit/          # Editar usuário
/users/{id}/delete/        # Deletar usuário
/admin/                    # Admin Django (se habilitado)
```

## Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request
