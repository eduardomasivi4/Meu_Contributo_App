from django.urls import path
from . import views

urlpatterns = [
    # Tela Inicial
    path('', views.index, name='index'),
    
    # ==================== ALUNO ====================
    # Páginas
    path('aluno/login/', views.login_aluno, name='login_aluno'),
    path('aluno/dashboard/', views.dashboard_aluno, name='dashboard_aluno'),
    path('aluno/atividades/', views.atividades, name='atividades'),
    path('aluno/loja/', views.loja, name='loja'),
    path('aluno/historico/', views.historico, name='historico'),
    path('aluno/comprovativo/<int:transacao_id>/', views.gerar_comprovativo, name='gerar_comprovativo'),
    path('aluno/solicitacao/<int:solicitacao_id>/comprovativo/', views.gerar_comprovativo_solicitacao, name='gerar_comprovativo_solicitacao'),
    
    # APIs Aluno
    path('api/aluno/verificar-processo/', views.verificar_processo, name='verificar_processo'),
    path('api/aluno/validar-senha/', views.validar_senha, name='validar_senha'),
    path('api/aluno/resgatar/<int:beneficio_id>/', views.api_resgatar_beneficio, name='api_resgatar'),
    path('api/aluno/solicitar/<int:beneficio_id>/', views.api_solicitar_beneficio, name='api_solicitar_beneficio'),
    path('api/solicitacao/<int:solicitacao_id>/status/', views.api_status_solicitacao, name='api_status_solicitacao'),
     
    # ==================== PROFESSOR ====================
    # Login e autenticação
    path('professor/login/', views.login_professor, name='login_professor'),
    path('api/professor/verificar/', views.verificar_credenciais_professor, name='verificar_credenciais_professor'),
    path('professor/selecionar-perfil/', views.selecionar_perfil, name='selecionar_perfil'),
    path('api/professor/redirecionar/', views.redirecionar_perfil, name='redirecionar_perfil'),
    
    # Dashboard e disciplinas
    path('professor/dashboard/', views.dashboard_professor, name='dashboard_professor'),
    path('api/turmas-por-disciplina/<int:disciplina_id>/', views.get_turmas_por_disciplina, name='get_turmas_por_disciplina'),
    path('turma/<int:turma_id>/', views.turma_detail, name='turma_detail'),
    path('atividade/criar/<int:turma_id>/', views.criar_atividade, name='criar_atividade'),
    path('atividade/distribuir/<int:atividade_id>/', views.distribuir_pontos, name='distribuir_pontos'),
    

    # ==================== DIRETOR DE TURMA ====================
    
    path('diretor/dashboard/', views.diretor_dashboard, name='diretor_dashboard'),  # ← Nome correto
    path('diretor/aluno/adicionar-pontos/<int:aluno_id>/', views.diretor_adicionar_pontos, name='diretor_adicionar_pontos'),
    path('diretor/aluno/reduzir-pontos/<int:aluno_id>/', views.diretor_reduzir_pontos, name='diretor_reduzir_pontos'),
    path('diretor/atividade/distribuir/<int:atividade_id>/', views.diretor_distribuir_pontos, name='diretor_distribuir_pontos'),


    # ==================== COORDENADOR ====================
    
    path('coordenador/dashboard/', views.coordenador_dashboard, name='coordenador_dashboard'),
    path('coordenador/atividades-curriculares/', views.coordenador_atividades_curriculares, name='coordenador_atividades_curriculares'),
    path('coordenador/atividade/criar/', views.coordenador_criar_atividade, name='coordenador_criar_atividade'),
    path('coordenador/atividade/editar/<int:pk>/', views.coordenador_editar_atividade, name='coordenador_editar_atividade'),
    path('coordenador/atividade/eliminar/<int:pk>/', views.coordenador_eliminar_atividade, name='coordenador_eliminar_atividade'),
    path('api/coordenador/buscar-atividades/', views.api_buscar_atividades, name='api_buscar_atividades'),

    # ==================== DIRETOR PEDAGÓGICO ====================

    path('diretor-pedagogico/dashboard/', views.diretor_pedagogico_dashboard, name='diretor_pedagogico_dashboard'),

    # ==================== APROVAÇÃO DE SOLICITAÇÕES (Diretor de Turma / Coordenador / Diretor Pedagógico) ====================

    path('api/aprovador/solicitacoes/', views.api_solicitacoes_aprovador, name='api_solicitacoes_aprovador'),
    path('api/aprovador/solicitacao/<int:solicitacao_id>/votar/', views.api_votar_solicitacao, name='api_votar_solicitacao'),
    path('aprovador/solicitacao/<int:solicitacao_id>/atividades/', views.ver_atividades_aluno, name='ver_atividades_aluno'),

]
