from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]