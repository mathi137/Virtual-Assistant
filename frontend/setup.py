#!/usr/bin/env python
"""
Script de inicialização do Frontend Django
"""
import os
import sys
import django
from pathlib import Path

# Adiciona o diretório do projeto ao PATH
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def create_directories():
    """Cria diretórios necessários"""
    dirs = [
        BASE_DIR / 'static',
        BASE_DIR / 'staticfiles',
        BASE_DIR / 'media',
        BASE_DIR / 'logs',
    ]
    
    for directory in dirs:
        directory.mkdir(exist_ok=True)
        print(f"✓ Diretório criado: {directory}")

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    print("🔍 Verificando ambiente...")
    
    # Verifica arquivo .env
    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado. Copiando .env.example...")
        import shutil
        shutil.copy(BASE_DIR / '.env.example', env_file)
        print("✓ Arquivo .env criado. Configure as variáveis antes de prosseguir.")
    
    # Verifica dependências
    try:
        import django
        import requests
        print("✓ Dependências principais encontradas")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    return True

def run_migrations():
    """Executa migrações do Django"""
    print("📦 Executando migrações...")
    from django.core.management import execute_from_command_line
    
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✓ Migrações executadas com sucesso")
    except Exception as e:
        print(f"❌ Erro nas migrações: {e}")
        return False
    
    return True

def collect_static():
    """Coleta arquivos estáticos"""
    print("🎨 Coletando arquivos estáticos...")
    from django.core.management import execute_from_command_line
    
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✓ Arquivos estáticos coletados")
    except Exception as e:
        print(f"⚠️  Erro ao coletar estáticos: {e}")

def main():
    """Função principal"""
    print("🚀 Inicializando Frontend PIE IV...")
    print("=" * 50)
    
    # Verifica ambiente
    if not check_environment():
        return
    
    # Cria diretórios
    create_directories()
    
    # Executa migrações
    if not run_migrations():
        return
    
    # Coleta arquivos estáticos
    collect_static()
    
    print("=" * 50)
    print("✅ Frontend inicializado com sucesso!")
    print()
    print("Para executar o servidor de desenvolvimento:")
    print("  python manage.py runserver 0.0.0.0:3000")
    print()
    print("URLs disponíveis:")
    print("  Dashboard: http://localhost:3000")
    print("  Admin:     http://localhost:3000/admin")
    print()
    print("Certifique-se de que o backend está rodando em:")
    print("  API:       http://localhost:8000")

if __name__ == '__main__':
    main()