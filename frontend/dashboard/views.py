from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
import json

from .services import APIService


class DashboardView(View):
    """Página principal do dashboard"""
    
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            
            # Buscar estatísticas básicas
            users_data = api_service.get_users()
            clients_data = api_service.get_clients()
            
            stats = {
                'total_users': len(users_data) if users_data else 0,
                'active_users': len([u for u in users_data if not u.get('disabled', False)]) if users_data else 0,
                'total_clients': len(clients_data) if clients_data else 0,
                'clients_with_bots': len([c for c in clients_data if c.get('agent_id')]) if clients_data else 0,
            }
            
            context = {
                'stats': stats,
                'recent_users': users_data[:5] if users_data else [],
                'recent_clients': clients_data[:5] if clients_data else []
            }
            
            return render(request, 'dashboard/home.html', context)
            
        except Exception as e:
            messages.error(request, f'Erro ao carregar dashboard: {str(e)}')
            return render(request, 'dashboard/home.html', {'stats': {}, 'recent_users': [], 'recent_clients': []})


class LoginView(View):
    """View de login"""
    
    def get(self, request):
        if request.session.get('access_token'):
            return redirect('dashboard:home')
        return render(request, 'dashboard/login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email e senha são obrigatórios')
            return render(request, 'dashboard/login.html')
        
        try:
            api_service = APIService()
            token = api_service.login(email, password)
            
            if token:
                request.session['access_token'] = token
                request.session['user_email'] = email
                messages.success(request, 'Login realizado com sucesso!')
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Credenciais inválidas')
                
        except Exception as e:
            messages.error(request, f'Erro ao fazer login: {str(e)}')
        
        return render(request, 'dashboard/login.html')


class LogoutView(View):
    """View de logout"""
    
    def get(self, request):
        request.session.flush()
        messages.success(request, 'Logout realizado com sucesso!')
        return redirect('dashboard:login')


class UserListView(View):
    """Lista de usuários"""
    
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            users = api_service.get_users()
            
            context = {'users': users or []}
            return render(request, 'dashboard/users/list.html', context)
            
        except Exception as e:
            messages.error(request, f'Erro ao carregar usuários: {str(e)}')
            return render(request, 'dashboard/users/list.html', {'users': []})


class UserCreateView(View):
    """Criar usuário"""
    
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        return render(request, 'dashboard/users/create.html')
    
    def post(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email e senha são obrigatórios')
            return render(request, 'dashboard/users/create.html')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            user = api_service.create_user(email, password)
            
            if user:
                messages.success(request, 'Usuário criado com sucesso!')
                return redirect('dashboard:user_list')
            else:
                messages.error(request, 'Erro ao criar usuário')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')
        
        return render(request, 'dashboard/users/create.html')


class UserDetailView(View):
    """Detalhes do usuário"""
    
    def get(self, request, user_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            user = api_service.get_user(user_id)
            
            if user:
                context = {'user': user}
                return render(request, 'dashboard/users/detail.html', context)
            else:
                messages.error(request, 'Usuário não encontrado')
                return redirect('dashboard:user_list')
                
        except Exception as e:
            messages.error(request, f'Erro ao carregar usuário: {str(e)}')
            return redirect('dashboard:user_list')


class UserEditView(View):
    """Editar usuário"""
    
    def get(self, request, user_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            user = api_service.get_user(user_id)
            
            if user:
                context = {'user': user}
                return render(request, 'dashboard/users/edit.html', context)
            else:
                messages.error(request, 'Usuário não encontrado')
                return redirect('dashboard:user_list')
                
        except Exception as e:
            messages.error(request, f'Erro ao carregar usuário: {str(e)}')
            return redirect('dashboard:user_list')
    
    def post(self, request, user_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        data = {}
        if email:
            data['email'] = email
        if password:
            data['password'] = password
        
        if not data:
            messages.error(request, 'Pelo menos um campo deve ser preenchido')
            return redirect('dashboard:user_edit', user_id=user_id)
        
        try:
            api_service = APIService(request.session.get('access_token'))
            user = api_service.update_user(user_id, data)
            
            if user:
                messages.success(request, 'Usuário atualizado com sucesso!')
                return redirect('dashboard:user_detail', user_id=user_id)
            else:
                messages.error(request, 'Erro ao atualizar usuário')
                
        except Exception as e:
            messages.error(request, f'Erro ao atualizar usuário: {str(e)}')
        
        return redirect('dashboard:user_edit', user_id=user_id)


class UserDeleteView(View):
    """Deletar usuário"""
    
    def post(self, request, user_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            success = api_service.delete_user(user_id)
            
            if success:
                messages.success(request, 'Usuário deletado com sucesso!')
            else:
                messages.error(request, 'Erro ao deletar usuário')
                
        except Exception as e:
            messages.error(request, f'Erro ao deletar usuário: {str(e)}')
        
        return redirect('dashboard:user_list')


# ========== CLIENT VIEWS ==========

class ClientListView(View):
    """Lista de clientes"""
    
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            clients = api_service.get_clients()
            
            context = {'clients': clients or []}
            return render(request, 'dashboard/clients/list.html', context)
            
        except Exception as e:
            messages.error(request, f'Erro ao carregar clientes: {str(e)}')
            return render(request, 'dashboard/clients/list.html', {'clients': []})


class ClientCreateView(View):
    """Criar cliente"""
    
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        return render(request, 'dashboard/clients/create.html')
    
    def post(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        system_prompt = request.POST.get('system_prompt')
        create_bot = request.POST.get('create_bot') == 'on'
        
        # Validações
        if not name or not email or not password:
            messages.error(request, 'Nome, email e senha são obrigatórios')
            return render(request, 'dashboard/clients/create.html')
        
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem')
            return render(request, 'dashboard/clients/create.html')
        
        if create_bot and not system_prompt:
            messages.error(request, 'Prompt do sistema é obrigatório para criar um bot')
            return render(request, 'dashboard/clients/create.html')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            client = api_service.create_client(
                name, 
                email, 
                password,
                system_prompt if create_bot else None
            )
            
            if client:
                messages.success(request, f'Cliente {name} criado com sucesso!')
                if create_bot:
                    messages.info(request, 'Bot criado e vinculado ao cliente!')
                return redirect('dashboard:client_list')
            else:
                messages.error(request, 'Erro ao criar cliente')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar cliente: {str(e)}')
        
        return render(request, 'dashboard/clients/create.html')


class ClientDetailView(View):
    """Detalhes do cliente"""
    
    def get(self, request, client_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            client = api_service.get_client(client_id)
            
            if client:
                # Buscar informações do bot se existir
                bot_info = None
                if client.get('agent_id'):
                    bot_info = api_service.get_agent(client['agent_id'])
                
                context = {
                    'client': client,
                    'bot_info': bot_info
                }
                return render(request, 'dashboard/clients/detail.html', context)
            else:
                messages.error(request, 'Cliente não encontrado')
                return redirect('dashboard:client_list')
                
        except Exception as e:
            messages.error(request, f'Erro ao carregar cliente: {str(e)}')
            return redirect('dashboard:client_list')


class ClientEditView(View):
    """Editar cliente"""
    
    def get(self, request, client_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            client = api_service.get_client(client_id)
            
            if client:
                # Buscar bot se existir
                bot_info = None
                if client.get('agent_id'):
                    bot_info = api_service.get_agent(client['agent_id'])
                
                context = {
                    'client': client,
                    'bot_info': bot_info
                }
                return render(request, 'dashboard/clients/edit.html', context)
            else:
                messages.error(request, 'Cliente não encontrado')
                return redirect('dashboard:client_list')
                
        except Exception as e:
            messages.error(request, f'Erro ao carregar cliente: {str(e)}')
            return redirect('dashboard:client_list')
    
    def post(self, request, client_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        system_prompt = request.POST.get('system_prompt')
        
        data = {}
        if name:
            data['name'] = name
        if email:
            data['email'] = email
        if password:
            data['password'] = password
        
        if not data and not system_prompt:
            messages.error(request, 'Pelo menos um campo deve ser preenchido')
            return redirect('dashboard:client_edit', client_id=client_id)
        
        try:
            api_service = APIService(request.session.get('access_token'))
            
            # Atualizar cliente
            if data:
                client = api_service.update_client(client_id, data)
                if not client:
                    messages.error(request, 'Erro ao atualizar cliente')
                    return redirect('dashboard:client_edit', client_id=client_id)
            
            # Atualizar bot se system_prompt foi fornecido
            if system_prompt:
                client_data = api_service.get_client(client_id)
                if client_data and client_data.get('agent_id'):
                    api_service.update_agent(client_data['agent_id'], {'system_prompt': system_prompt})
            
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('dashboard:client_detail', client_id=client_id)
                
        except Exception as e:
            messages.error(request, f'Erro ao atualizar cliente: {str(e)}')
        
        return redirect('dashboard:client_edit', client_id=client_id)


class ClientDeleteView(View):
    """Deletar cliente"""
    
    def post(self, request, client_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            success = api_service.delete_client(client_id)
            
            if success:
                messages.success(request, 'Cliente deletado com sucesso!')
            else:
                messages.error(request, 'Erro ao deletar cliente')
                
        except Exception as e:
            messages.error(request, f'Erro ao deletar cliente: {str(e)}')
        
        return redirect('dashboard:client_list')


class ClientChatView(View):
    """Chat com o bot do cliente"""
    
    def get(self, request, client_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            client = api_service.get_client(client_id)
            
            if not client:
                messages.error(request, 'Cliente não encontrado')
                return redirect('dashboard:client_list')
            
            context = {'client': client}
            return render(request, 'dashboard/clients/chat.html', context)
            
        except Exception as e:
            messages.error(request, f'Erro ao carregar chat: {str(e)}')
            return redirect('dashboard:client_list')
    
    def post(self, request, client_id):
        """API endpoint para enviar mensagens"""
        if not request.session.get('access_token'):
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        try:
            data = json.loads(request.body)
            message = data.get('message')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            api_service = APIService(request.session.get('access_token'))
            client = api_service.get_client(client_id)
            
            if not client or not client.get('agent_id'):
                return JsonResponse({'error': 'Cliente ou bot não encontrado'}, status=404)
            
            # Gerar um chat_id numérico único baseado no client_id
            # Para testes web, usamos um ID fixo por cliente
            chat_id = 10000 + client_id  # IDs de chat web começam em 10000
            
            # Chamar API de chat do backend
            response = api_service.chat_with_agent(
                agent_id=client['agent_id'],
                chat_id=chat_id,
                message=message,
                user_id=client.get('user_id', 1)
            )
            
            if response and 'response' in response:
                return JsonResponse({'response': response['response']})
            else:
                return JsonResponse({'error': 'Erro ao processar mensagem'}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# ========== CLIENT AREA VIEWS (for actual clients to login and chat) ==========

class ClientLoginView(View):
    """Login view for clients"""
    
    def get(self, request):
        if request.session.get('client_access_token'):
            return redirect('dashboard:client_dashboard')
        return render(request, 'client/login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email e senha são obrigatórios')
            return render(request, 'client/login.html')
        
        try:
            import requests
            from django.conf import settings
            
            # Call backend API for client login
            response = requests.post(
                f"{settings.API_BASE_URL}/client/login",
                data={
                    'username': email,
                    'password': password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                request.session['client_access_token'] = data['access_token']
                request.session['client_data'] = data['client']
                messages.success(request, f'Bem-vindo, {data["client"]["name"]}!')
                return redirect('dashboard:client_dashboard')
            else:
                messages.error(request, 'Email ou senha incorretos')
                
        except Exception as e:
            messages.error(request, f'Erro ao fazer login: {str(e)}')
        
        return render(request, 'client/login.html')


class ClientDashboardView(View):
    """Dashboard view for logged-in clients"""
    
    def get(self, request):
        if not request.session.get('client_access_token'):
            return redirect('dashboard:client_login')
        
        client_data = request.session.get('client_data')
        
        if not client_data:
            messages.error(request, 'Sessão expirada. Faça login novamente.')
            return redirect('dashboard:client_login')
        
        context = {'client': client_data}
        return render(request, 'client/dashboard.html', context)


class ClientChatAPIView(View):
    """API endpoint for client chat"""
    
    def post(self, request):
        if not request.session.get('client_access_token'):
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        try:
            data = json.loads(request.body)
            message = data.get('message')
            agent_id = data.get('agent_id')
            client_id = data.get('client_id')
            
            if not message or not agent_id or not client_id:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            import requests
            from django.conf import settings
            
            # Generate unique chat_id for this client
            chat_id = 20000 + client_id  # Client web chats start at 20000
            
            # Call backend API
            response = requests.post(
                f"{settings.API_BASE_URL}/agent/chat/",
                json={
                    "chat": {
                        "id": chat_id,
                        "agent_id": agent_id,
                        "platform_id": 1,  # Web platform
                        "user_id": client_id
                    },
                    "message": {
                        "text": message
                    }
                },
                headers={
                    'Authorization': f'Bearer {request.session.get("client_access_token")}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'response': data.get('response', '')})
            else:
                return JsonResponse({'error': 'Erro ao processar mensagem'}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ClientLogoutView(View):
    """Logout view for clients"""
    
    def get(self, request):
        request.session.pop('client_access_token', None)
        request.session.pop('client_data', None)
        messages.success(request, 'Logout realizado com sucesso!')
        return redirect('dashboard:client_login')