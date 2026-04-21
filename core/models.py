from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, time, date


class Usuario(AbstractUser):
    TIPO_USUARIO = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('diretor_turma', 'Diretor de Turma'),
        ('coordenador', 'Coordenador de Atividades'),
        ('admin', 'Administrador'),
    )
    
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='aluno')
    telefone = models.CharField(max_length=15, blank=True)
    
    # Cargos adicionais
    is_professor = models.BooleanField(default=False)
    is_coordenador = models.BooleanField(default=False)
    is_diretor_turma = models.BooleanField(default=False)
    turma_vinculada = models.CharField(max_length=20, blank=True, null=True)
    
    groups = models.ManyToManyField('auth.Group', related_name='core_usuario_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='core_usuario_set', blank=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_tipo_display()}"

class Turma(models.Model):
    CURSO_CHOICES = (
        ('eletronica', 'Eletrónica e Telecomunicações'),
        ('informatica', 'Informática'),
    )
    
    nome = models.CharField(max_length=20)  # 10ª EA, 10ª ID, etc.
    curso = models.CharField(max_length=20, choices=CURSO_CHOICES)
    ano = models.CharField(max_length=10)  # 10ª, 11ª, 12ª
    horario = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['nome', 'curso']
    
    def __str__(self):
        return f"{self.nome} - {self.get_curso_display()}"

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

class DisciplinaTurma(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='turmas_relacionadas')
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='disciplinas_relacionadas')
    
    class Meta:
        unique_together = ['disciplina', 'turma']
    
    def __str__(self):
        return f"{self.disciplina.nome} - {self.turma.nome}"

class Atividade(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    criterios_avaliacao = models.TextField()
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fim = models.TimeField(null=True, blank=True)
    max_pontos_por_aluno = models.IntegerField(default=100)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='atividades', null=True, blank=True)
    turmas = models.ManyToManyField(Turma, related_name='atividades', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome



# ==================== ALUNO ====================

class PerfilAluno(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_aluno')
    numero_processo = models.CharField(max_length=20, unique=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='alunos')
    saldo_pontos = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.numero_processo}"

class Transacao(models.Model):
    TIPO_CHOICES = (
        ('adicao', 'Adição'),
        ('remocao', 'Remoção'),
        ('distribuicao', 'Distribuição'),
        ('resgate', 'Resgate'),
    )
    
    aluno = models.ForeignKey(PerfilAluno, on_delete=models.CASCADE, related_name='transacoes')
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    professor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_professor': True})
    atividade = models.ForeignKey(Atividade, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.aluno.usuario.username} - {self.tipo}: {self.quantidade} pts"

class Inscricao(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    )
    
    aluno = models.ForeignKey(PerfilAluno, on_delete=models.CASCADE, related_name='inscricoes')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='inscricoes')
    data_inscricao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    pontos_ganhos = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['aluno', 'atividade']
    
    def __str__(self):
        return f"{self.aluno.usuario.username} - {self.atividade.nome}"

class Beneficio(models.Model):
    CATEGORIA_CHOICES = (
        ('academico', 'Académico'),
        ('tecnologia', 'Tecnologia'),
    )
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    custo_pontos = models.IntegerField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    disponivel = models.BooleanField(default=True)
    estoque = models.IntegerField(default=-1)
    
    def __str__(self):
        return f"{self.nome} - {self.custo_pontos} pts"

class ResgateBeneficio(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('entregue', 'Entregue'),
    )
    
    aluno = models.ForeignKey(PerfilAluno, on_delete=models.CASCADE, related_name='resgates')
    beneficio = models.ForeignKey(Beneficio, on_delete=models.CASCADE, related_name='resgates')
    data_resgate = models.DateTimeField(auto_now_add=True)
    pontos_gastos = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    def __str__(self):
        return f"{self.aluno.usuario.username} - {self.beneficio.nome}"



# ==================== PROFESSOR (placeholder) ====================

class PerfilProfessor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_professor')
    disciplina = models.CharField(max_length=100)
    turmas = models.ManyToManyField(Turma, blank=True, related_name='professores')
    
    def __str__(self):
        return f"{self.usuario.username} - {self.disciplina}"

class PerfilDiretorTurma(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_diretor')
    turma = models.OneToOneField(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='diretor')
    
    def __str__(self):
        return f"{self.usuario.username}"

class PerfilCoordenador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_coordenador')
    departamento = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.departamento}"

