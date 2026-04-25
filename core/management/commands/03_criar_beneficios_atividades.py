from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from core.models import (
    Turma, Disciplina, Atividade, Beneficio,
    CriterioAtividade, GrupoAtividade, PerfilAluno,
    Usuario, PerfilProfessor
)


class Command(BaseCommand):
    help = 'PASSO 3: Criar Benefícios e Atividades'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n🚀 PASSO 3: CRIANDO BENEFÍCIOS E ATIVIDADES\n'))

        # =========================================================
        # 1. BUSCAR DEPENDÊNCIAS
        # =========================================================
        try:
            turma_12ea = Turma.objects.get(nome='12ª EA')
            turma_12id = Turma.objects.get(nome='12ª ID')
            disciplina_fisica = Disciplina.objects.get(nome='Física')
            disciplina_matematica = Disciplina.objects.get(nome='Matemática')
            prof1 = Usuario.objects.get(username='professor.carlos')
            prof2 = Usuario.objects.get(username='professor.ana')
            self.stdout.write('   ✅ Dependências encontradas')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ ERRO: {e}'))
            return

        hoje = date.today()

        # =========================================================
        # 2. BENEFÍCIOS
        # =========================================================
        self.stdout.write('\n🎁 Criando benefícios...')
        beneficios_fixos = [
            {'nome': 'Boletim de Notas', 'descricao': 'Impressão oficial do boletim', 'custo': 200, 'categoria': 'academico', 'estoque': -1},
            {'nome': 'Internet 7 dias', 'descricao': 'Wi-Fi de alta velocidade por 7 dias', 'custo': 300, 'categoria': 'tecnologia', 'estoque': 50},
            {'nome': 'Internet 30 dias', 'descricao': 'Wi-Fi de alta velocidade por 30 dias', 'custo': 1000, 'categoria': 'tecnologia', 'estoque': 20},
            {'nome': 'Certificado de Mérito', 'descricao': 'Certificado oficial de reconhecimento', 'custo': 150, 'categoria': 'premios', 'estoque': -1},
            {'nome': 'Dia sem Uniforme', 'descricao': 'Permissão para trajes civis por um dia', 'custo': 80, 'categoria': 'eventos', 'estoque': 100},
            {'nome': 'Acesso à Biblioteca', 'descricao': 'Acesso especial à biblioteca após horas', 'custo': 50, 'categoria': 'academico', 'estoque': -1},
            {'nome': 'Mochila Escolar', 'descricao': 'Mochila oficial do colégio', 'custo': 500, 'categoria': 'premios', 'estoque': 10},
        ]
        
        for b in beneficios_fixos:
            beneficio, created = Beneficio.objects.get_or_create(
                nome=b['nome'],
                defaults={
                    'descricao': b['descricao'],
                    'custo_pontos': b['custo'],
                    'categoria': b['categoria'],
                    'estoque': b['estoque'],
                    'disponivel': True
                }
            )
            if created:
                self.stdout.write(f'   ✅ Benefício: {b["nome"]}')
        
        self.stdout.write(self.style.SUCCESS(f'   ✅ Total: {Beneficio.objects.count()} benefícios'))

        # =========================================================
        # 3. ATIVIDADES DO COORDENADOR
        # =========================================================
        self.stdout.write('\n📝 Criando atividades do coordenador...')
        
        # Actividade 1: Cultural - Já distribuída
        atividade_cultural1 = Atividade.objects.create(
            nome='Feira de Ciências 2024',
            descricao='Apresentação de projectos científicos pelos alunos',
            criterios_avaliacao='Participação, qualidade do projecto, apresentação',
            created_at=hoje - timedelta(days=15),
            finalizada=True,
            distribuida=True,
            tipo_atividade='cultural',
            todos_cursos=True,
            pontos_turma=300,
            pontos_ja_distribuidos=300
        )
        atividade_cultural1.turmas.set([turma_12ea, turma_12id])
        CriterioAtividade.objects.create(atividade=atividade_cultural1, nome='Participação', pontos=100)
        CriterioAtividade.objects.create(atividade=atividade_cultural1, nome='Qualidade do Projecto', pontos=150)
        CriterioAtividade.objects.create(atividade=atividade_cultural1, nome='Apresentação', pontos=50)
        self.stdout.write(f'   ✅ Actividade: Feira de Ciências 2024 (Cultural - Distribuída)')
        
        # Actividade 2: Cultural - Aguardando distribuição
        atividade_cultural2 = Atividade.objects.create(
            nome='Olimpíadas de Cultura Africana',
            descricao='Actividade interdisciplinar sobre cultura africana',
            criterios_avaliacao='Participação, trabalho de pesquisa, apresentação',
            created_at=hoje - timedelta(days=5),
            finalizada=True,
            distribuida=False,
            tipo_atividade='cultural',
            todos_cursos=False,
            cursos_associados='eletronica',
            pontos_turma=200
        )
        atividade_cultural2.turmas.set([turma_12ea])
        CriterioAtividade.objects.create(atividade=atividade_cultural2, nome='Participação na abertura', pontos=100)
        CriterioAtividade.objects.create(atividade=atividade_cultural2, nome='Apresentação de trabalho', pontos=100)
        self.stdout.write(f'   ✅ Actividade: Olimpíadas de Cultura Africana (Cultural - Aguardando)')
        
        # Actividade 3: Ciência - Em andamento
        atividade_ciencia1 = Atividade.objects.create(
            nome='Workshop de Robótica',
            descricao='Aprenda a programar robôs educativos',
            criterios_avaliacao='Participação, projecto final',
            created_at=hoje - timedelta(days=2),
            finalizada=False,
            distribuida=False,
            tipo_atividade='ciencia_tecnologia',
            todos_cursos=True
        )
        atividade_ciencia1.turmas.set([turma_12ea, turma_12id])
        CriterioAtividade.objects.create(atividade=atividade_ciencia1, nome='Participação', pontos=150)
        CriterioAtividade.objects.create(atividade=atividade_ciencia1, nome='Projecto Final', pontos=200)
        self.stdout.write(f'   ✅ Actividade: Workshop de Robótica (Ciência - Em andamento)')
        
        # Actividade 4: Ciência - Com distribuição parcial
        atividade_ciencia2 = Atividade.objects.create(
            nome='Hackathon de Programação',
            descricao='24 horas de programação em equipa',
            criterios_avaliacao='Criatividade, funcionalidade, apresentação',
            created_at=hoje - timedelta(days=10),
            finalizada=True,
            distribuida=False,
            tipo_atividade='ciencia_tecnologia',
            todos_cursos=False,
            cursos_associados='informatica',
            pontos_turma=500,
            pontos_ja_distribuidos=200
        )
        atividade_ciencia2.turmas.set([turma_12id])
        CriterioAtividade.objects.create(atividade=atividade_ciencia2, nome='Criatividade', pontos=150)
        CriterioAtividade.objects.create(atividade=atividade_ciencia2, nome='Funcionalidade', pontos=250)
        CriterioAtividade.objects.create(atividade=atividade_ciencia2, nome='Apresentação', pontos=100)
        self.stdout.write(f'   ✅ Actividade: Hackathon de Programação (Ciência - Distribuição Parcial)')

        # =========================================================
        # 4. ATIVIDADES CURRICULARES DO PROFESSOR
        # =========================================================
        self.stdout.write('\n📝 Criando actividades curriculares...')
        
        # Actividade 1: Física
        atividade_fisica = Atividade.objects.create(
            nome='Prova Trimestral de Física',
            descricao='Avaliação de conhecimentos sobre circuitos eléctricos',
            criterios_avaliacao='Resolução de problemas, justificação científica',
            created_at=hoje - timedelta(days=8),
            finalizada=True,
            disciplina=disciplina_fisica
        )
        atividade_fisica.turmas.set([turma_12ea])
        CriterioAtividade.objects.create(atividade=atividade_fisica, nome='Resolução de Problemas', pontos=60)
        CriterioAtividade.objects.create(atividade=atividade_fisica, nome='Justificação Científica', pontos=40)
        self.stdout.write(f'   ✅ Actividade: Prova Trimestral de Física')
        
        # Actividade 2: Matemática (com grupos)
        atividade_matematica = Atividade.objects.create(
            nome='Trabalho de Estatística',
            descricao='Análise estatística de dados recolhidos na turma',
            criterios_avaliacao='Recolha de dados, análise, apresentação',
            created_at=hoje - timedelta(days=3),
            finalizada=True,
            disciplina=disciplina_matematica
        )
        atividade_matematica.turmas.set([turma_12id])
        crit1 = CriterioAtividade.objects.create(atividade=atividade_matematica, nome='Recolha de Dados', pontos=30)
        crit2 = CriterioAtividade.objects.create(atividade=atividade_matematica, nome='Análise Estatística', pontos=50)
        crit3 = CriterioAtividade.objects.create(atividade=atividade_matematica, nome='Apresentação', pontos=20)
        crit4 = CriterioAtividade.objects.create(atividade=atividade_matematica, nome='Atraso na Entrega', pontos=-15)
        
        # Criar grupos
        alunos_turma_12id = PerfilAluno.objects.filter(turma=turma_12id)
        alunos_list = list(alunos_turma_12id)
        
        if len(alunos_list) >= 4:
            grupo1 = GrupoAtividade.objects.create(atividade=atividade_matematica, nome='Grupo A - Estatística')
            grupo1.alunos.set([alunos_list[0], alunos_list[1]])
            grupo2 = GrupoAtividade.objects.create(atividade=atividade_matematica, nome='Grupo B - Probabilidade')
            grupo2.alunos.set([alunos_list[2], alunos_list[3]])
            self.stdout.write(f'   ✅ Grupos criados para Trabalho de Estatística')
        
        self.stdout.write(f'   ✅ Actividade: Trabalho de Estatística (com grupos)')
        
        # Actividade 3: Física - Em andamento
        atividade_fisica2 = Atividade.objects.create(
            nome='Experiência de Laboratório',
            descricao='Construção de um circuito eléctrico simples',
            criterios_avaliacao='Montagem, medições, relatório',
            created_at=hoje - timedelta(days=1),
            finalizada=False,
            disciplina=disciplina_fisica
        )
        atividade_fisica2.turmas.set([turma_12ea])
        CriterioAtividade.objects.create(atividade=atividade_fisica2, nome='Montagem do Circuito', pontos=40)
        CriterioAtividade.objects.create(atividade=atividade_fisica2, nome='Medições Correctas', pontos=40)
        CriterioAtividade.objects.create(atividade=atividade_fisica2, nome='Relatório', pontos=20)
        self.stdout.write(f'   ✅ Actividade: Experiência de Laboratório (Em andamento)')

        # =========================================================
        # RESUMO FINAL
        # =========================================================
        self.stdout.write(self.style.SUCCESS('\n✅ PASSO 3 CONCLUÍDO COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS(f'   - Benefícios: {Beneficio.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Atividades Coordenador: {Atividade.objects.filter(disciplina__isnull=True).count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Atividades Professor: {Atividade.objects.filter(disciplina__isnull=False).count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Grupos: {GrupoAtividade.objects.count()}'))