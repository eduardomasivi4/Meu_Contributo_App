from django.contrib.auth.hashers import check_password
from .models import Usuario, Turma

class ProfessorAuthService:
    
    @staticmethod
    def verificar_se_diretor_turma(usuario):
        """Verifica se o professor é diretor de alguma turma"""
        return usuario.is_diretor_turma
    
    @staticmethod
    def autenticar_professor(email=None, turma=None, senha=None):
        """Autentica o professor com base no tipo de login"""
        
        if email:
            try:
                usuario = Usuario.objects.get(email_institucional=email)
                if usuario.verificar_senha(senha) and usuario.tipo in ['professor', 'diretor_turma', 'coordenador']:
                    return usuario, None
            except Usuario.DoesNotExist:
                return None, "E-mail não encontrado"
            return None, "Senha incorreta"
        
        elif turma:
            try:
                turma_obj = Turma.objects.get(nome=turma)
                if turma_obj.diretor_turma:
                    usuario = turma_obj.diretor_turma.usuario
                    if usuario.verificar_senha(senha):
                        return usuario, None
                    return None, "Palavra-passe incorreta"
                return None, "Esta turma não possui diretor designado"
            except Turma.DoesNotExist:
                return None, "Turma não encontrada"
        
        return None, "Dados de autenticação inválidos"
    
    @staticmethod
    def determinar_redirecionamento(usuario):
        """Determina para onde o usuário deve ser redirecionado"""
        
        is_diretor = usuario.is_diretor_turma
        is_coordenador = usuario.is_coordenador
        
        if is_diretor:
            if is_coordenador:
                return 'selecionar_perfil_3'
            else:
                return 'selecionar_perfil_2'
        else:
            if is_coordenador:
                return 'coordenador_dashboard'
            else:
                return 'professor_dashboard'


class ProfessorLoginValidator:
    
    @staticmethod
    def validar_email(email):
        if not email or '@' not in email:
            return False, "E-mail inválido"
        return True, ""
    
    @staticmethod
    def validar_turma(turma):
        if not turma:
            return False, "Selecione uma turma"
        return True, ""
    
    @staticmethod
    def validar_senha(senha):
        if not senha or len(senha) < 4:
            return False, "A senha deve ter pelo menos 4 caracteres"
        return True, ""