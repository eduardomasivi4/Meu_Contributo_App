from django.shortcuts import redirect
from django.urls import resolve

class ProfessorAccessMiddleware:
    
    EXEMPT_URLS = [
        'login_professor', 'logout_professor', 'index', 'login_aluno',
        'verificar_credenciais_professor', 'selecionar_perfil', 'redirecionar_perfil'
    ]
    
    PROFESSOR_URLS = [
        'dashboard_professor', 'turma_detail', 'criar_atividade_criterios',
        'iniciar_atividade_professor', 'terminar_atividade_professor',
        'ver_registros_atividade', 'criar_grupos_atividade', 'iniciar_atividade_professor_v2'
    ]
    
    DIRETOR_URLS = [
        'diretor_dashboard', 'diretor_distribuir_pontos_limite',
        'diretor_limpar_distribuicao', 'diretor_ver_distribuicao'
    ]
    
    COORDENADOR_URLS = [
        'coordenador_cultural_dashboard', 'coordenador_ciencia_dashboard',
        'coordenador_criar_atividade_separado', 'coordenador_editar_atividade',
        'coordenador_eliminar_atividade', 'coordenador_ver_registos',
        'api_buscar_atividades'
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                current_url = resolve(request.path_info).url_name
            except:
                current_url = None
            
            perfil_ativo = request.session.get('perfil_ativo', None)
            
            if current_url in self.EXEMPT_URLS:
                return self.get_response(request)
            
            if perfil_ativo == 'professor' and current_url not in self.PROFESSOR_URLS:
                return redirect('dashboard_professor')
            if perfil_ativo == 'diretor' and current_url not in self.DIRETOR_URLS:
                return redirect('diretor_dashboard')
            if perfil_ativo == 'coordenador' and current_url not in self.COORDENADOR_URLS:
                return redirect('coordenador_cultural_dashboard')
        
        return self.get_response(request)