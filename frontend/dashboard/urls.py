from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard - Agents list
    path('', views.AgentListView.as_view(), name='home'),
    
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Agent routes
    path('agents/create/', views.AgentCreateView.as_view(), name='agent_create'),
    path('agents/<int:agent_id>/edit/', views.AgentEditView.as_view(), name='agent_edit'),
    path('agents/<int:agent_id>/delete/', views.AgentDeleteView.as_view(), name='agent_delete'),
    
    # Commented out - keeping code but removing from URLs
    # path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    # path('users/', views.UserListView.as_view(), name='user_list'),
    # path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    # path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    # path('users/<int:user_id>/edit/', views.UserEditView.as_view(), name='user_edit'),
    # path('users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]