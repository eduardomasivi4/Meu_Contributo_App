from django.contrib import admin
from .models import (
    Usuario, Turma, Disciplina, DisciplinaTurma, Atividade,
    PerfilAluno, Transacao, Beneficio, ResgateBeneficio,
    PerfilProfessor, PerfilDiretorTurma, PerfilCoordenador,
    CriterioAtividade, RegistroAtividadeAluno, GrupoAtividade
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo', 'is_active']
    list_filter = ['tipo', 'is_professor', 'is_coordenador_cultural', 'is_coordenador_ciencia', 'is_diretor_turma']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso', 'ano', 'total_alunos']
    list_filter = ['curso', 'ano']
    search_fields = ['nome']
    
    def total_alunos(self, obj):
        return obj.alunos.count()


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(DisciplinaTurma)
class DisciplinaTurmaAdmin(admin.ModelAdmin):
    list_display = ['disciplina', 'turma']
    list_filter = ['turma__curso', 'turma__ano']


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'disciplina', 'tipo_atividade', 'created_at', 'finalizada', 'distribuida']
    list_filter = ['finalizada', 'distribuida', 'tipo_atividade']
    search_fields = ['nome', 'descricao']
    filter_horizontal = ['turmas']


@admin.register(PerfilAluno)
class PerfilAlunoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'numero_processo', 'turma', 'saldo_pontos']
    list_filter = ['turma']
    search_fields = ['usuario__username', 'numero_processo']


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'quantidade', 'tipo', 'data', 'professor']
    list_filter = ['tipo', 'data']


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'custo_pontos', 'categoria', 'disponivel', 'estoque']


@admin.register(ResgateBeneficio)
class ResgateBeneficioAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'beneficio', 'data_resgate', 'pontos_gastos', 'status']


@admin.register(PerfilProfessor)
class PerfilProfessorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'disciplina']


@admin.register(PerfilDiretorTurma)
class PerfilDiretorTurmaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'turma']


@admin.register(PerfilCoordenador)
class PerfilCoordenadorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'departamento']


@admin.register(CriterioAtividade)
class CriterioAtividadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'atividade', 'pontos', 'created_at']


@admin.register(RegistroAtividadeAluno)
class RegistroAtividadeAlunoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'atividade', 'criterio', 'pontos_atribuidos', 'data_registro']


@admin.register(GrupoAtividade)
class GrupoAtividadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'atividade', 'total_alunos', 'created_at']
    
    def total_alunos(self, obj):
        return obj.alunos.count()