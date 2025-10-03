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