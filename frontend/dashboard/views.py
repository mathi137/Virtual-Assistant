from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import json
import requests

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
            stats = {
                'total_users': len(users_data) if users_data else 0,
                'active_users': len([u for u in users_data if not u.get('disabled', False)]) if users_data else 0,
            }
            
            context = {
                'stats': stats,
                'recent_users': users_data[:5] if users_data else []
            }
            
            return render(request, 'dashboard/home.html', context)
            
        except Exception as e:
            messages.error(request, f'Erro ao carregar dashboard: {str(e)}')
            return render(request, 'dashboard/home.html', {'stats': {}, 'recent_users': []})


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


class SignupView(View):
    """View de cadastro"""
    
    def get(self, request):
        if request.session.get('access_token'):
            return redirect('dashboard:home')
        return render(request, 'dashboard/signup.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email e senha são obrigatórios')
            return render(request, 'dashboard/signup.html')
        
        try:
            api_service = APIService()
            user = api_service.create_user(email, password)
            
            if user:
                messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
                return redirect('dashboard:login')
            else:
                messages.error(request, 'Erro ao criar conta')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
        
        return render(request, 'dashboard/signup.html')


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


class AgentListView(View):
    """Lista de agentes do usuário"""
    
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            current_user = api_service.get_current_user()
            
            if not current_user:
                messages.error(request, 'Sessão expirada. Por favor, faça login novamente.')
                request.session.flush()
                return redirect('dashboard:login')
            
            user_id = current_user.get('id')
            if not user_id:
                messages.error(request, 'Erro ao obter ID do usuário')
                request.session.flush()
                return redirect('dashboard:login')
            
            agents = api_service.get_agents_by_user(user_id)
            
            context = {'agents': agents or []}
            return render(request, 'dashboard/agents/list.html', context)
            
        except Exception as e:
            messages.error(request, f'Erro ao carregar agentes: {str(e)}')
            # If it's an authentication error, clear session and redirect to login
            if '401' in str(e) or 'credentials' in str(e).lower():
                request.session.flush()
                return redirect('dashboard:login')
            return render(request, 'dashboard/agents/list.html', {'agents': []})


class AgentCreateView(View):
    """Criar agente"""
    
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        return render(request, 'dashboard/agents/create.html')
    
    def post(self, request):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        name = request.POST.get('name')
        image = request.POST.get('image', '')
        system_prompt = request.POST.get('system_prompt', '')
        platform_name = request.POST.get('platform_name', '')
        token = request.POST.get('token', '')
        
        if not name:
            messages.error(request, 'Nome é obrigatório')
            return render(request, 'dashboard/agents/create.html')
        
        if not system_prompt:
            messages.error(request, 'System prompt é obrigatório')
            return render(request, 'dashboard/agents/create.html')
        
        if not platform_name:
            messages.error(request, 'Plataforma é obrigatória')
            return render(request, 'dashboard/agents/create.html')
        
        if not token:
            messages.error(request, 'Token é obrigatório')
            return render(request, 'dashboard/agents/create.html')
        
        # Map platform name to platform_id (1=telegram, 2=whatsapp)
        platform_id_map = {
            'telegram': 1,
            'whatsapp': 2
        }
        platform_id = platform_id_map.get(platform_name.lower())
        
        if not platform_id:
            messages.error(request, 'Plataforma inválida')
            return render(request, 'dashboard/agents/create.html')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            current_user = api_service.get_current_user()
            
            if not current_user:
                messages.error(request, 'Erro ao obter informações do usuário')
                request.session.flush()
                return redirect('dashboard:login')
            
            data = {
                'user_id': current_user.get('id'),
                'name': name,
                'image': image if image else None,
                'system_prompt': system_prompt,
                'tokens': [{
                    'platform_id': platform_id,
                    'platform_name': platform_name.lower(),
                    'token': token
                }]
            }
            
            agent = api_service.create_agent(data)
            
            if agent:
                messages.success(request, 'Agente criado com sucesso!')
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Erro ao criar agente. Verifique os dados e tente novamente.')
                
        except requests.exceptions.HTTPError as e:
            # Handle 401 authentication errors
            if '401' in str(e):
                messages.error(request, 'Sessão expirada. Por favor, faça login novamente.')
                request.session.flush()
                return redirect('dashboard:login')
            messages.error(request, f'Erro ao criar agente: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erro ao criar agente: {str(e)}')
        
        return render(request, 'dashboard/agents/create.html')


class AgentEditView(View):
    """Editar agente"""
    
    def get(self, request, agent_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            agent = api_service.get_agent(agent_id)
            
            if agent:
                context = {'agent': agent}
                return render(request, 'dashboard/agents/edit.html', context)
            else:
                messages.error(request, 'Agente não encontrado')
                return redirect('dashboard:home')
                
        except Exception as e:
            messages.error(request, f'Erro ao carregar agente: {str(e)}')
            return redirect('dashboard:home')
    
    def post(self, request, agent_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        name = request.POST.get('name')
        image = request.POST.get('image', '')
        system_prompt = request.POST.get('system_prompt', '')
        platform_name = request.POST.get('platform_name', '')
        token = request.POST.get('token', '')
        
        if not name:
            messages.error(request, 'Nome é obrigatório')
            return redirect('dashboard:agent_edit', agent_id=agent_id)
        
        if not system_prompt:
            messages.error(request, 'System prompt é obrigatório')
            return redirect('dashboard:agent_edit', agent_id=agent_id)
        
        if not platform_name:
            messages.error(request, 'Plataforma é obrigatória')
            return redirect('dashboard:agent_edit', agent_id=agent_id)
        
        if not token:
            messages.error(request, 'Token é obrigatório')
            return redirect('dashboard:agent_edit', agent_id=agent_id)
        
        # Map platform name to platform_id (1=telegram, 2=whatsapp)
        platform_id_map = {
            'telegram': 1,
            'whatsapp': 2
        }
        platform_id = platform_id_map.get(platform_name.lower())
        
        if not platform_id:
            messages.error(request, 'Plataforma inválida')
            return redirect('dashboard:agent_edit', agent_id=agent_id)
        
        try:
            api_service = APIService(request.session.get('access_token'))
            
            data = {
                'name': name,
                'image': image if image else None,
                'system_prompt': system_prompt,
                'tokens': [{
                    'platform_id': platform_id,
                    'platform_name': platform_name.lower(),
                    'token': token
                }]
            }
            
            agent = api_service.update_agent(agent_id, data)
            
            if agent:
                messages.success(request, 'Agente atualizado com sucesso!')
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Erro ao atualizar agente')
                
        except requests.exceptions.HTTPError as e:
            # Handle 401 authentication errors
            if '401' in str(e):
                messages.error(request, 'Sessão expirada. Por favor, faça login novamente.')
                request.session.flush()
                return redirect('dashboard:login')
            messages.error(request, f'Erro ao atualizar agente: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar agente: {str(e)}')
        
        return redirect('dashboard:agent_edit', agent_id=agent_id)


class AgentDeleteView(View):
    """Deletar agente"""
    
    def post(self, request, agent_id):
        if not request.session.get('access_token'):
            return redirect('dashboard:login')
        
        try:
            api_service = APIService(request.session.get('access_token'))
            success = api_service.delete_agent(agent_id)
            
            if success:
                messages.success(request, 'Agente deletado com sucesso!')
            else:
                messages.error(request, 'Erro ao deletar agente')
                
        except Exception as e:
            messages.error(request, f'Erro ao deletar agente: {str(e)}')
        
        return redirect('dashboard:home')


class WebSocketView(View):
    """Handle WebSocket upgrade requests - returns 400 as WebSocket is not supported"""
    
    def get(self, request):
        return HttpResponse('WebSocket is not supported', status=400)
    
    def post(self, request):
        return HttpResponse('WebSocket is not supported', status=400)