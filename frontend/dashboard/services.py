import requests
import json
from django.conf import settings
from typing import Optional, Dict, List, Any


class APIService:
    """
    Serviço para comunicação com a API FastAPI do backend.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        self.base_url = settings.API_BASE_URL
        self.access_token = access_token
        self.session = requests.Session()
        
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Faz uma requisição HTTP para a API.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 204:  # No Content
                return True
            elif response.status_code >= 200 and response.status_code < 300:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return True
            else:
                print(f"Erro na API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {str(e)}")
            return None
    
    def login(self, email: str, password: str) -> Optional[str]:
        """
        Realiza login e retorna o token de acesso.
        """
        data = {
            'username': email,  # A API FastAPI usa 'username' para o email
            'password': password
        }
        
        # Para login, usar form data ao invés de JSON
        try:
            url = f"{self.base_url}/auth/token"
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('access_token')
            else:
                print(f"Erro no login: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão no login: {str(e)}")
            return None
    
    def get_users(self) -> Optional[List[Dict]]:
        """
        Busca todos os usuários.
        """
        return self._make_request('GET', '/user/')
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """
        Busca um usuário específico por ID.
        """
        return self._make_request('GET', f'/user/{user_id}')
    
    def create_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Cria um novo usuário.
        """
        data = {
            'email': email,
            'password': password
        }
        return self._make_request('POST', '/user/', data=data)
    
    def update_user(self, user_id: int, data: Dict) -> Optional[Dict]:
        """
        Atualiza dados de um usuário.
        """
        return self._make_request('PUT', f'/user/{user_id}', data=data)
    
    def delete_user(self, user_id: int) -> bool:
        """
        Deleta um usuário.
        """
        result = self._make_request('DELETE', f'/user/{user_id}')
        return result is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """
        Busca dados do usuário autenticado.
        """
        return self._make_request('GET', '/user/me/')
    
    def update_current_user(self, data: Dict) -> Optional[Dict]:
        """
        Atualiza dados do usuário autenticado.
        """
        return self._make_request('PUT', '/user/me/', data=data)
    
    def delete_current_user(self) -> bool:
        """
        Deleta conta do usuário autenticado.
        """
        result = self._make_request('DELETE', '/user/me/')
        return result is not None