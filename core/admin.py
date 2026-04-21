from django.contrib import admin
from .models import (
    Usuario, Turma, Disciplina, DisciplinaTurma,
    Atividade, PerfilAluno, Transacao, Beneficio,
    ResgateBeneficio, PerfilProfessor, PerfilDiretorTurma,
    PerfilCoordenador
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'get_full_name', 'tipo', 'is_active']
    list_filter = ['tipo', 'is_professor', 'is_coordenador', 'is_diretor_turma']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('username', 'first_name', 'last_name', 'email', 'telefone', 'tipo')
        }),
        ('Cargos', {
            'fields': ('is_professor', 'is_coordenador', 'is_diretor_turma', 'turma_vinculada')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso', 'ano']
    list_filter = ['curso', 'ano']
    search_fields = ['nome']


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(DisciplinaTurma)
class DisciplinaTurmaAdmin(admin.ModelAdmin):
    list_display = ['disciplina', 'turma']
    list_filter = ['turma__curso', 'turma__ano']
    search_fields = ['disciplina__nome', 'turma__nome']


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'disciplina', 'data_inicio', 'data_fim', 'max_pontos_por_aluno']
    list_filter = ['disciplina', 'data_inicio']
    search_fields = ['nome', 'descricao']
    filter_horizontal = ['turmas']


@admin.register(PerfilAluno)
class PerfilAlunoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'numero_processo', 'turma', 'saldo_pontos']
    list_filter = ['turma']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'numero_processo']


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'quantidade', 'tipo', 'data', 'professor']
    list_filter = ['tipo', 'data']
    search_fields = ['aluno__usuario__username', 'descricao']
    date_hierarchy = 'data'


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'custo_pontos', 'categoria', 'disponivel', 'estoque']
    list_filter = ['categoria', 'disponivel']
    search_fields = ['nome']


@admin.register(ResgateBeneficio)
class ResgateBeneficioAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'beneficio', 'data_resgate', 'pontos_gastos', 'status']
    list_filter = ['status', 'data_resgate']
    search_fields = ['aluno__usuario__username', 'beneficio__nome']


@admin.register(PerfilProfessor)
class PerfilProfessorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'disciplina']
    search_fields = ['usuario__username', 'disciplina__nome']


@admin.register(PerfilDiretorTurma)
class PerfilDiretorTurmaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'turma']
    search_fields = ['usuario__username', 'turma__nome']


@admin.register(PerfilCoordenador)
class PerfilCoordenadorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'departamento']
    search_fields = ['usuario__username', 'departamento']