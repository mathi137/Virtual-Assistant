from django.db import models
from django.contrib.auth.models import AbstractUser


class User(models.Model):
    """
    Modelo de usuário para visualização no dashboard.
    Os dados reais vêm da API FastAPI.
    """
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(unique=True)
    disabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        managed = False  # Django não gerenciará esta tabela
        db_table = 'api_user'  # Tabela fictícia
    
    def __str__(self):
        return self.email
    
    @property
    def is_active(self):
        return not self.disabled


class DashboardStats(models.Model):
    """
    Modelo para estatísticas do dashboard.
    Dados calculados em tempo real via API.
    """
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    disabled_users = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False  # Django não gerenciará esta tabela
        db_table = 'dashboard_stats'  # Tabela fictícia
    
    def __str__(self):
        return f"Stats - Users: {self.total_users}"