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
    )
    
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='aluno')
    telefone = models.CharField(max_length=15, blank=True)
    foto = models.ImageField(upload_to='fotos/', null=True, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_usuario_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_usuario_set',
        blank=True,
    )
    
    def __str__(self):
        return f"{self.username} - {self.get_tipo_display()}"

class Turma(models.Model):
    CURSO_CHOICES = (
        ('eletronica', 'Eletrónica'),
        ('informatica', 'Informática'),
    )
    
    nome = models.CharField(max_length=20)
    curso = models.CharField(max_length=20, choices=CURSO_CHOICES)
    horario = models.CharField(max_length=100, blank=True)
    ano_letivo = models.CharField(max_length=9, default='2025')
    
    def __str__(self):
        return f"{self.nome} - {self.get_curso_display()}"

class PerfilAluno(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_aluno')
    numero_processo = models.CharField(max_length=20, unique=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='alunos')
    saldo_pontos = models.IntegerField(default=0)
    nivel = models.CharField(max_length=50, default='Iniciante')
    documento = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.numero_processo}"
    
    def atualizar_nivel(self):
        if self.saldo_pontos >= 3000:
            self.nivel = 'Mestre'
        elif self.saldo_pontos >= 2000:
            self.nivel = 'Explorador'
        elif self.saldo_pontos >= 1000:
            self.nivel = 'Aprendiz'
        else:
            self.nivel = 'Iniciante'
        self.save()

class Atividade(models.Model):
    CATEGORIA_CHOICES = (
        ('ciencia', 'Ciência e Tecnologia'),
        ('cultura', 'Culturais'),
    )
    
    STATUS_CHOICES = (
        ('disponivel', 'Disponível'),
        ('hoje', 'Hoje'),
        ('em_andamento', 'Em Andamento'),
        ('encerrada', 'Encerrada'),
    )
    
    nome = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    requisitos = models.TextField()
    pontuacao_total = models.IntegerField(default=0)
    
    # Campos de data e hora
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    
    interrompe_aula = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
    
    def calcular_status(self):
        """
        Calcula o status da atividade com base na data e hora atual
        """
        agora = timezone.localtime(timezone.now())
        data_atual = agora.date()
        hora_atual = agora.time()
        
        # Data da atividade
        data_atividade = self.data
        
        # 1. Se a data atual for ANTES da data da atividade
        if data_atual < data_atividade:
            return 'disponivel'
        
        # 2. Se a data atual for IGUAL à data da atividade
        if data_atual == data_atividade:
            # Se a hora atual for ANTES da hora de início
            if hora_atual < self.hora_inicio:
                return 'hoje'
            # Se a hora atual estiver ENTRE início e fim
            elif self.hora_inicio <= hora_atual <= self.hora_fim:
                return 'em_andamento'
            # Se a hora atual for DEPOIS da hora de fim
            else:
                return 'encerrada'
        
        # 3. Se a data atual for DEPOIS da data da atividade
        return 'encerrada'
    
    def get_status_display_text(self):
        """Retorna o texto amigável do status"""
        status_map = {
            'disponivel': 'Disponível',
            'hoje': 'Começa Hoje',
            'em_andamento': 'Em Andamento',
            'encerrada': 'Encerrada',
        }
        return status_map.get(self.calcular_status(), 'Disponível')
    
    def get_status_class(self):
        """Retorna a classe CSS para o status"""
        status_class_map = {
            'disponivel': 'status-disponivel',
            'hoje': 'status-hoje',
            'em_andamento': 'status-em_andamento',
            'encerrada': 'status-encerrada',
        }
        return status_class_map.get(self.calcular_status(), 'status-disponivel')

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

class Transacao(models.Model):
    TIPO_CHOICES = (
        ('adicao', 'Adição'),
        ('remocao', 'Remoção'),
        ('resgate', 'Resgate'),
        ('inscricao', 'Inscrição'),
    )
    
    aluno = models.ForeignKey(PerfilAluno, on_delete=models.CASCADE, related_name='transacoes')
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.aluno.usuario.username} - {self.tipo}: {self.quantidade} pts"



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

