from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, time, date, timedelta


class Usuario(AbstractUser):
    TIPO_USUARIO = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('diretor_turma', 'Diretor de Turma'),
        ('coordenador', 'Coordenador de Atividades'),
        ('diretor_pedagogico', 'Diretor Pedagógico'),
        ('admin', 'Administrador'),
    )
    
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='aluno')
    telefone = models.CharField(max_length=15, blank=True)
    
    # Cargos adicionais
    is_professor = models.BooleanField(default=False)
    is_coordenador = models.BooleanField(default=False)
    is_diretor_turma = models.BooleanField(default=False)
    is_diretor_pedagogico = models.BooleanField(default=False)
    turma_vinculada = models.ForeignKey('Turma', on_delete=models.SET_NULL, null=True, blank=True)
    # Curso do qual o coordenador é responsável (usado para identificar "o coordenador do
    # curso do aluno" nas solicitações de benefícios). Em branco = coordenador geral,
    # considerado válido para qualquer curso.
    curso_coordenado = models.CharField(max_length=20, choices=(
        ('eletronica', 'Eletrónica e Telecomunicações'),
        ('informatica', 'Informática'),
    ), blank=True)
    
    groups = models.ManyToManyField('auth.Group', related_name='core_usuario_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='core_usuario_set', blank=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_tipo_display()}"
    
    def get_cargos(self):
        cargos = []
        if self.is_professor:
            cargos.append('professor')
        if self.is_coordenador:
            cargos.append('coordenador')
        if self.is_diretor_turma:
            cargos.append('diretor_turma')
        if self.is_diretor_pedagogico:
            cargos.append('diretor_pedagogico')
        return cargos

class Turma(models.Model):
    CURSO_CHOICES = (
        ('eletronica', 'Eletrónica e Telecomunicações'),
        ('informatica', 'Informática'),
    )
    
    nome = models.CharField(max_length=20)
    curso = models.CharField(max_length=20, choices=CURSO_CHOICES)
    ano = models.CharField(max_length=10)
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
    TIPO_CHOICES = (
        ('cultural', 'Cultural'),
        ('ciencia_tecnologia', 'Ciência e Tecnologia'),
    )
    
    CURSO_CHOICES = (
        ('eletronica', 'Eletrónica e Telecomunicações'),
        ('informatica', 'Informática'),
    )
    
    # Campos existentes...
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
    interrompe_aula = models.BooleanField(default=False, verbose_name='Interrompe aula?', help_text='Marque se esta atividade interrompe as aulas normais')
    
    # NOVOS CAMPOS PARA COORDENADOR
    tipo_atividade = models.CharField(max_length=20, choices=TIPO_CHOICES, default='cultural')
    cursos_associados = models.CharField(max_length=20, choices=CURSO_CHOICES, null=True, blank=True)
    todos_cursos = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nome
    
    @property
    def get_cursos_display(self):
        if self.todos_cursos:
            return "Ambos os cursos"
        elif self.cursos_associados:
            return dict(self.CURSO_CHOICES).get(self.cursos_associados, self.cursos_associados)
        return "Não especificado"


# ==================== ALUNO ====================

class PerfilAluno(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_aluno')
    numero_processo = models.CharField(max_length=20, unique=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='alunos')
    saldo_pontos = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.numero_processo}"
    
    def get_turma_nome(self):
        return self.turma.nome if self.turma else 'Sem turma'
    
    def get_curso_display(self):
        return self.turma.get_curso_display() if self.turma else 'Sem curso'

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



class SolicitacaoBeneficio(models.Model):
    """
    Pedido de um benefício pelo aluno, sujeito a votação dos 3 aprovadores
    (Diretor de Turma, Coordenador do Curso e Diretor Pedagógico) em vigor
    no momento do pedido. Ver 'lógicas de alteração no sistema.md'.
    """
    STATUS_CHOICES = (
        ('aguardando', 'Aguardando Análise'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
    )
    VOTO_CHOICES = (
        ('pendente', 'Pendente'),
        ('aceitar', 'Aceitar'),
        ('recusar', 'Recusar'),
    )
    PRAZO_SEGUNDOS = 60

    aluno = models.ForeignKey(PerfilAluno, on_delete=models.CASCADE, related_name='solicitacoes_beneficio')
    beneficio = models.ForeignKey(Beneficio, on_delete=models.CASCADE, related_name='solicitacoes')

    # ---- Snapshot (congelamento de dados no momento da solicitação) ----
    aluno_nome = models.CharField(max_length=150)
    aluno_processo = models.CharField(max_length=20)
    aluno_turma_nome = models.CharField(max_length=20)
    aluno_curso_nome = models.CharField(max_length=50)
    beneficio_nome = models.CharField(max_length=100)
    beneficio_descricao = models.TextField(blank=True)

    # ---- Aprovadores em vigor no momento da solicitação ----
    aprovador_diretor_turma = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitacoes_como_diretor_turma')
    aprovador_coordenador = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitacoes_como_coordenador')
    aprovador_diretor_pedagogico = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitacoes_como_diretor_pedagogico')

    # ---- Votos ----
    voto_diretor_turma = models.CharField(max_length=10, choices=VOTO_CHOICES, default='pendente')
    voto_coordenador = models.CharField(max_length=10, choices=VOTO_CHOICES, default='pendente')
    voto_diretor_pedagogico = models.CharField(max_length=10, choices=VOTO_CHOICES, default='pendente')
    voto_diretor_turma_em = models.DateTimeField(null=True, blank=True)
    voto_coordenador_em = models.DateTimeField(null=True, blank=True)
    voto_diretor_pedagogico_em = models.DateTimeField(null=True, blank=True)

    # ---- Estado ----
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    prazo_final = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aguardando')
    decidido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_solicitacao']

    def __str__(self):
        return f"{self.aluno_nome} - {self.beneficio_nome} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.pk is None and not self.prazo_final:
            self.prazo_final = timezone.now() + timedelta(seconds=self.PRAZO_SEGUNDOS)
        super().save(*args, **kwargs)

    # ---- Regras de negócio ----

    def papel_do_usuario(self, usuario):
        """Devolve qual dos 3 papéis de aprovador o utilizador ocupa nesta solicitação, ou None."""
        if self.aprovador_diretor_turma_id and self.aprovador_diretor_turma_id == usuario.id:
            return 'diretor_turma'
        if self.aprovador_coordenador_id and self.aprovador_coordenador_id == usuario.id:
            return 'coordenador'
        if self.aprovador_diretor_pedagogico_id and self.aprovador_diretor_pedagogico_id == usuario.id:
            return 'diretor_pedagogico'
        return None

    def tempo_restante_segundos(self):
        restante = (self.prazo_final - timezone.now()).total_seconds()
        return max(0, int(restante))

    def avaliar_estado(self):
        """
        Avalia se a solicitação já pode/deve ser finalizada, aplicando as regras:
        - Unanimidade (3 aceitar) ou 1 recusar -> decisão imediata (a qualquer momento).
        - Findo o prazo de 60s sem decisão: maioria entre os votos registados, se houver
          quórum de pelo menos 2; caso contrário, reprovação automática por falta de quórum.
        A decisão, uma vez tomada, é imutável (chamadas seguintes não têm efeito).
        Seguro para chamar a qualquer momento (idempotente).
        """
        if self.status != 'aguardando':
            return self.status

        votos = [self.voto_diretor_turma, self.voto_coordenador, self.voto_diretor_pedagogico]

        if 'recusar' in votos:
            self._finalizar('reprovado')
            return self.status

        if votos.count('aceitar') == 3:
            self._finalizar('aprovado')
            return self.status

        if timezone.now() >= self.prazo_final:
            registados = [v for v in votos if v != 'pendente']
            if len(registados) >= 2:
                aceitar = registados.count('aceitar')
                recusar = registados.count('recusar')
                self._finalizar('aprovado' if aceitar > recusar else 'reprovado')
            else:
                self._finalizar('reprovado')  # falta de quórum

        return self.status

    def _finalizar(self, resultado):
        self.status = resultado
        self.decidido_em = timezone.now()
        self.save(update_fields=['status', 'decidido_em'])

    def registrar_voto(self, papel, voto):
        """
        Regista o voto de um aprovador ('diretor_turma' | 'coordenador' | 'diretor_pedagogico').
        Devolve (sucesso: bool, mensagem: str).
        """
        if voto not in ('aceitar', 'recusar'):
            return False, 'Voto inválido.'
        if papel not in ('diretor_turma', 'coordenador', 'diretor_pedagogico'):
            return False, 'Aprovador inválido.'

        self.avaliar_estado()
        if self.status != 'aguardando':
            return False, 'Esta solicitação já foi decidida e a decisão é imutável.'

        campo_voto = f'voto_{papel}'
        campo_data = f'voto_{papel}_em'
        if getattr(self, campo_voto) != 'pendente':
            return False, 'O seu voto já foi registado e não pode ser alterado.'

        setattr(self, campo_voto, voto)
        setattr(self, campo_data, timezone.now())
        self.save(update_fields=[campo_voto, campo_data])
        self.avaliar_estado()
        return True, 'Voto registado com sucesso.'


# ==================== PERFIS ====================

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
