from django.urls import path
from . import views

urlpatterns = [
    # ==================== TELA INICIAL ====================
    path('', views.index, name='index'),
    
    # ==================== ALUNO ====================
    path('aluno/login/', views.login_aluno, name='login_aluno'),
    path('aluno/dashboard/', views.dashboard_aluno, name='dashboard_aluno'),
    path('aluno/atividades/', views.atividades, name='atividades'),
    path('aluno/loja/', views.loja, name='loja'),
    path('aluno/historico/', views.historico, name='historico'),
    path('aluno/comprovativo/<int:transacao_id>/', views.gerar_comprovativo, name='gerar_comprovativo'),
    
    path('api/aluno/verificar-processo/', views.verificar_processo, name='verificar_processo'),
    path('api/aluno/validar-senha/', views.validar_senha, name='validar_senha'),
    path('api/aluno/resgatar/<int:beneficio_id>/', views.api_resgatar_beneficio, name='api_resgatar'),
     
    # ==================== PROFESSOR ====================
    path('professor/login/', views.login_professor, name='login_professor'),
    path('api/professor/verificar/', views.verificar_credenciais_professor, name='verificar_credenciais_professor'),
    path('professor/selecionar-perfil/', views.selecionar_perfil, name='selecionar_perfil'),
    path('api/professor/redirecionar/', views.redirecionar_perfil, name='redirecionar_perfil'),
    
    path('professor/dashboard/', views.dashboard_professor, name='dashboard_professor'),
    path('api/turmas-por-disciplina/<int:disciplina_id>/', views.get_turmas_por_disciplina, name='get_turmas_por_disciplina'),
    path('turma/<int:turma_id>/', views.turma_detail, name='turma_detail'),
        
    path('professor/atividade/criar/<int:turma_id>/', views.criar_atividade_com_criterios, name='criar_atividade_criterios'),
    path('professor/atividade/iniciar/<int:atividade_id>/', views.iniciar_atividade_professor, name='iniciar_atividade_professor'),
    path('professor/atividade/terminar/<int:atividade_id>/', views.terminar_atividade_professor, name='terminar_atividade_professor'),
    path('professor/atividade/registos/<int:atividade_id>/', views.ver_registros_atividade, name='ver_registros_atividade'),
    
    path('professor/atividade/grupos/<int:atividade_id>/', views.criar_grupos_atividade, name='criar_grupos_atividade'),
    path('professor/atividade/iniciar-v2/<int:atividade_id>/', views.iniciar_atividade_professor_v2, name='iniciar_atividade_professor_v2'),
    path('api/grupo/aplicar-criterio/<int:grupo_id>/<int:criterio_id>/', views.api_aplicar_criterio_grupo, name='api_aplicar_criterio_grupo'),

    path('professor/atividade/editar/<int:atividade_id>/', views.editar_atividade_professor, name='editar_atividade_professor'),
    path('professor/atividade/eliminar/<int:atividade_id>/', views.eliminar_atividade_professor, name='eliminar_atividade_professor'),

    # ==================== DIRETOR ====================
    path('diretor/dashboard/', views.diretor_dashboard, name='diretor_dashboard'),
    path('diretor/atividade/distribuir-limite/<int:atividade_id>/', views.diretor_distribuir_pontos_limite, name='diretor_distribuir_pontos_limite'),
    path('diretor/atividade/limpar-distribuicao/<int:atividade_id>/', views.diretor_limpar_distribuicao, name='diretor_limpar_distribuicao'),
    path('diretor/atividade/ver-distribuicao/<int:atividade_id>/', views.diretor_ver_distribuicao, name='diretor_ver_distribuicao'),

    # ==================== COORDENADOR ====================
    path('coordenador/dashboard/', views.coordenador_redirecionar_dashboard, name='coordenador_dashboard'),
    path('coordenador/cultural/dashboard/', views.coordenador_cultural_dashboard, name='coordenador_cultural_dashboard'),
    path('coordenador/ciencia/dashboard/', views.coordenador_ciencia_dashboard, name='coordenador_ciencia_dashboard'),
    path('coordenador/atividade/criar/', views.coordenador_criar_atividade_separado, name='coordenador_criar_atividade_separado'),
    path('coordenador/atividade/editar/<int:pk>/', views.coordenador_editar_atividade, name='coordenador_editar_atividade'),
    path('coordenador/atividade/eliminar/<int:pk>/', views.coordenador_eliminar_atividade, name='coordenador_eliminar_atividade'),
    path('coordenador/atividade/registos/<int:pk>/', views.coordenador_ver_registos, name='coordenador_ver_registos'),
    
    path('coordenador/atividade/iniciar/<int:pk>/', views.coordenador_iniciar_atividade, name='coordenador_iniciar_atividade'),
    path('coordenador/atividade/terminar/<int:pk>/', views.coordenador_terminar_atividade, name='coordenador_terminar_atividade'),
    
    path('api/coordenador/buscar-atividades/', views.api_buscar_atividades, name='api_buscar_atividades'),
]