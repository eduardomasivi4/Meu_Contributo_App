from django.shortcuts import redirect
from django.urls import resolve

class ProfessorAccessMiddleware:
    
    EXEMPT_URLS = ['login_professor', 'logout_professor', 'index', 'login_aluno']
    PROFESSOR_URLS = ['professor_dashboard']
    DIRETOR_URLS = ['diretor_dashboard']
    COORDENADOR_URLS = ['coordenador_dashboard']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            perfil_ativo = request.session.get('perfil_ativo', None)
            
            if current_url in self.EXEMPT_URLS:
                return self.get_response(request)
            
            if perfil_ativo == 'professor' and current_url not in self.PROFESSOR_URLS:
                return redirect('professor_dashboard')
            
            if perfil_ativo == 'diretor' and current_url not in self.DIRETOR_URLS:
                return redirect('diretor_dashboard')
            
            if perfil_ativo == 'coordenador' and current_url not in self.COORDENADOR_URLS:
                return redirect('coordenador_dashboard')
        
        return self.get_response(request)