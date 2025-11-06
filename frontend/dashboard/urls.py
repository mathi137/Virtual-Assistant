from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User routes (ADMs)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Client routes (ADMIN managing clients)
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:client_id>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:client_id>/edit/', views.ClientEditView.as_view(), name='client_edit'),
    path('clients/<int:client_id>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('clients/<int:client_id>/chat/', views.ClientChatView.as_view(), name='client_chat'),
    
    # API routes for AJAX
    path('api/chat/<int:client_id>/', views.ClientChatView.as_view(), name='api_chat'),
    
    # CLIENT AREA (for actual clients to login and use their chatbot)
    path('client/login/', views.ClientLoginView.as_view(), name='client_login'),
    path('client/logout/', views.ClientLogoutView.as_view(), name='client_logout'),
    path('client/dashboard/', views.ClientDashboardView.as_view(), name='client_dashboard'),
    path('client/chat/', views.ClientChatAPIView.as_view(), name='client_chat_api'),
]