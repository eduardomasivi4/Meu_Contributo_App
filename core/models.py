from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.core.exceptions import ValidationError


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
    
    is_professor = models.BooleanField(default=False)
    is_coordenador_cultural = models.BooleanField(default=False)
    is_coordenador_ciencia = models.BooleanField(default=False)
    is_diretor_turma = models.BooleanField(default=False)
    turma_vinculada = models.ForeignKey('Turma', on_delete=models.SET_NULL, null=True, blank=True)
    
    groups = models.ManyToManyField('auth.Group', related_name='core_usuario_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='core_usuario_set', blank=True)
    
    class Meta:
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} - {self.get_tipo_display()}"
    
    def get_cargos(self):
        cargos = []
        if self.is_professor:
            cargos.append('professor')
        if self.is_coordenador_cultural:
            cargos.append('coordenador_cultural')
        if self.is_coordenador_ciencia:
            cargos.append('coordenador_ciencia')
        if self.is_diretor_turma:
            cargos.append('diretor_turma')
        return cargos


class Turma(models.Model):
    CURSO_CHOICES = (
        ('eletronica', 'Eletrónica e Telecomunicações'),
        ('informatica', 'Informática'),
    )
    ANO_CHOICES = (
        ('10ª', '10ª Classe'),
        ('11ª', '11ª Classe'),
        ('12ª', '12ª Classe'),
    )
    
    nome = models.CharField(max_length=20)
    curso = models.CharField(max_length=20, choices=CURSO_CHOICES)
    ano = models.CharField(max_length=10, choices=ANO_CHOICES)
    horario = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['nome', 'curso']
        ordering = ['curso', 'ano', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_curso_display()}"
    
    @property
    def total_alunos(self):
        return self.alunos.count()


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    
    class Meta:
        ordering = ['nome']
    
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
    TIPO_CHOICES = (
        ('cultural', 'Cultural'),
        ('ciencia_tecnologia', 'Ciência e Tecnologia'),
    )
    CURSO_CHOICES = (
        ('eletronica', 'Eletrónica e Telecomunicações'),
        ('informatica', 'Informática'),
    )
    
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
    finalizada = models.BooleanField(default=False)
    interrompe_aula = models.BooleanField(default=False)
    criado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='atividades_criadas')
    
    pontos_turma = models.IntegerField(default=0)
    distribuida = models.BooleanField(default=False)
    pontos_ja_distribuidos = models.IntegerField(default=0)
    
    tipo_atividade = models.CharField(max_length=20, choices=TIPO_CHOICES, default='cultural')
    cursos_associados = models.CharField(max_length=20, choices=CURSO_CHOICES, null=True, blank=True)
    todos_cursos = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.nome
    
    @property
    def get_cursos_display(self):
        if self.todos_cursos:
            return "Ambos os cursos"
        elif self.cursos_associados:
            return dict(self.CURSO_CHOICES).get(self.cursos_associados, self.cursos_associados)
        return "Não especificado"
    
    @property
    def pontos_restantes(self):
        return self.pontos_turma - self.pontos_ja_distribuidos


class PerfilAluno(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_aluno')
    numero_processo = models.CharField(max_length=20, unique=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='alunos')
    saldo_pontos = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.numero_processo}"
    
    def get_turma_nome(self):
        return self.turma.nome if self.turma else 'Sem turma'


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
        sinal = '+' if self.quantidade > 0 else ''
        return f"{self.aluno.usuario.username} - {self.tipo}: {sinal}{self.quantidade} pts"


class Beneficio(models.Model):
    CATEGORIA_CHOICES = (
        ('academico', 'Académico'),
        ('tecnologia', 'Tecnologia'),
        ('premios', 'Prémios'),
        ('eventos', 'Eventos'),
    )
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    custo_pontos = models.IntegerField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    disponivel = models.BooleanField(default=True)
    estoque = models.IntegerField(default=-1)
    
    class Meta:
        ordering = ['categoria', 'custo_pontos']
    
    def __str__(self):
        return f"{self.nome} - {self.custo_pontos} pts"


class ResgateBeneficio(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )
    
    aluno = models.ForeignKey(PerfilAluno, on_delete=models.CASCADE, related_name='resgates')
    beneficio = models.ForeignKey(Beneficio, on_delete=models.CASCADE, related_name='resgates')
    data_resgate = models.DateTimeField(auto_now_add=True)
    pontos_gastos = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    class Meta:
        ordering = ['-data_resgate']
    
    def __str__(self):
        return f"{self.aluno.usuario.username} - {self.beneficio.nome}"


class PerfilProfessor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_professor')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.SET_NULL, null=True, blank=True)
    turmas = models.ManyToManyField(Turma, blank=True, related_name='professores')
    
    def __str__(self):
        return f"{self.usuario.username} - {self.disciplina.nome if self.disciplina else 'Sem disciplina'}"


class PerfilDiretorTurma(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_diretor')
    turma = models.OneToOneField(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='diretor')
    
    def __str__(self):
        return f"{self.usuario.username} - {self.turma.nome if self.turma else 'Sem turma'}"


class PerfilCoordenador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_coordenador')
    departamento = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.departamento}"


class CriterioAtividade(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='criterios')
    nome = models.CharField(max_length=200)
    pontos = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        sinal = '+' if self.pontos >= 0 else ''
        return f"{self.nome} ({sinal}{self.pontos} pts)"


class RegistroAtividadeAluno(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='registros_alunos')
    aluno = models.ForeignKey(PerfilAluno, on_delete=models.CASCADE)
    criterio = models.ForeignKey(CriterioAtividade, on_delete=models.CASCADE)
    pontos_atribuidos = models.IntegerField()
    data_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_registro']
    
    def __str__(self):
        sinal = '+' if self.pontos_atribuidos >= 0 else ''
        return f"{self.aluno.usuario.username} - {self.criterio.nome} ({sinal}{self.pontos_atribuidos})"


class GrupoAtividade(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='grupos')
    nome = models.CharField(max_length=100)
    alunos = models.ManyToManyField(PerfilAluno, related_name='grupos_atividade')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['atividade', 'nome']]
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.nome} ({self.atividade.nome})"
    
    @property
    def total_alunos(self):
        return self.alunos.count()