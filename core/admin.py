from django.contrib import admin
from .models import (
    Usuario, Turma, PerfilAluno, PerfilProfessor, 
    PerfilDiretorTurma, PerfilCoordenador, Atividade, 
    Inscricao, Beneficio, ResgateBeneficio, Transacao
)

admin.site.register(Usuario)
admin.site.register(Turma)
admin.site.register(PerfilAluno)
admin.site.register(PerfilProfessor)
admin.site.register(PerfilDiretorTurma)
admin.site.register(PerfilCoordenador)
admin.site.register(Atividade)
admin.site.register(Inscricao)
admin.site.register(Beneficio)
admin.site.register(ResgateBeneficio)
admin.site.register(Transacao)