from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('atividade/', views.atividade, name='atividade'),
    path('historico/', views.historico, name='historico'),
    path('credito/', views.credito, name='credito'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/imagem/', views.imagem, name='imagem'),
    path('logout/', views.logout_view, name='logout'),
]