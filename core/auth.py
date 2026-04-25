from django.contrib.auth.hashers import check_password
from .models import Usuario, Turma

class ProfessorAuthService:
    
    @staticmethod
    def verificar_se_diretor_turma(usuario):
        return usuario.is_diretor_turma
    
    @staticmethod
    def autenticar_professor(email=None, turma=None, senha=None):
        if email:
            try:
                usuario = Usuario.objects.get(email=email)
                if usuario.check_password(senha) and usuario.tipo in ['professor', 'diretor_turma', 'coordenador']:
                    return usuario, None
            except Usuario.DoesNotExist:
                return None, "E-mail não encontrado"
            return None, "Palavra-passe incorreta"
        elif turma:
            try:
                turma_obj = Turma.objects.get(nome=turma)
                if hasattr(turma_obj, 'diretor') and turma_obj.diretor:
                    usuario = turma_obj.diretor.usuario
                    if usuario.check_password(senha):
                        return usuario, None
                    return None, "Palavra-passe incorreta"
                return None, "Esta turma não possui diretor designado"
            except Turma.DoesNotExist:
                return None, "Turma não encontrada"
        return None, "Dados de autenticação inválidos"
    
    @staticmethod
    def determinar_redirecionamento(usuario):
        is_diretor = usuario.is_diretor_turma
        is_coordenador = usuario.is_coordenador_cultural or usuario.is_coordenador_ciencia
        if is_diretor:
            if is_coordenador:
                return 'selecionar_perfil'
            else:
                return 'diretor_dashboard'
        else:
            if is_coordenador:
                return 'coordenador_cultural_dashboard'
            else:
                return 'dashboard_professor'


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
            return False, "A palavra-passe deve ter pelo menos 4 caracteres"
        return True, ""