from django.urls import path
from . import views

urlpatterns = [
    # Tela Inicial
    path('', views.index, name='index'),
    
    # ALUNO
    path('aluno/login/', views.login_aluno, name='login_aluno'),
    path('aluno/dashboard/', views.dashboard_aluno, name='dashboard_aluno'),
    path('aluno/atividades/', views.atividades, name='atividades'),
    path('aluno/loja/', views.loja, name='loja'),

    # ALUNO - APIs
    path('api/aluno/verificar-processo/', views.verificar_processo, name='verificar_processo'),
    path('api/aluno/validar-senha/', views.validar_senha, name='validar_senha'),
    path('api/aluno/resgatar/<int:beneficio_id>/', views.api_resgatar_beneficio, name='api_resgatar'),
    
    # PROFESSOR
    path('professor/login/', views.login_professor, name='login_professor'),
    path('professor/selecionar-perfil/', views.selecionar_perfil, name='selecionar_perfil'),
    path('professor/dashboard/', views.dashboard_professor, name='dashboard_professor'),
    
    # DIRETOR DE TURMA
    path('diretor/dashboard/', views.diretor_turma, name='diretor_turma'),
    
    # COORDENADOR
    path('coordenador/dashboard/', views.coordenador_atividades, name='coordenador_atividades'),
]