import random
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from core.models import (
    Usuario, Turma, Disciplina, DisciplinaTurma,
    PerfilAluno, Atividade, Transacao, Beneficio,
    ResgateBeneficio
)

class Command(BaseCommand):
    help = 'Popula todas as tabelas do sistema com dados coerentes'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Populando todas as tabelas do sistema...')

        # =========================================================
        # 1. TURMAS
        # =========================================================
        self.stdout.write('📚 Criando turmas...')
        turmas_info = [
            ('10ª ID', 'informatica', '10ª'), ('10ª IB', 'informatica', '10ª'),
            ('11ª ID', 'informatica', '11ª'), ('11ª IB', 'informatica', '11ª'),
            ('12ª ID', 'informatica', '12ª'), ('12ª IB', 'informatica', '12ª'),
            ('10ª EA', 'eletronica', '10ª'), ('10ª EE', 'eletronica', '10ª'),
            ('11ª EA', 'eletronica', '11ª'), ('11ª EE', 'eletronica', '11ª'),
            ('12ª EA', 'eletronica', '12ª'), ('12ª EE', 'eletronica', '12ª'),
        ]
        turmas = {}
        for nome, curso, ano in turmas_info:
            turma, _ = Turma.objects.get_or_create(nome=nome, defaults={'curso': curso, 'ano': ano})
            turmas[nome] = turma
        self.stdout.write(f'   ✅ {len(turmas)} turmas criadas.')

        # =========================================================
        # 2. DISCIPLINAS
        # =========================================================
        self.stdout.write('📖 Criando disciplinas...')
        disc_inf = {
            'DT': ['11ª'], 'Eletrotécnica': ['10ª', '11ª'], 'SEAC': ['10ª', '11ª', '12ª'],
            'TIC': ['10ª', '11ª'], 'TLP': ['10ª', '11ª', '12ª'], 'TREI': ['11ª', '12ª'],
        }
        disc_elec = {
            'D.T': ['11ª'], 'Eletrónica': ['10ª', '11ª', '12ª'], 'Informática': ['10ª'],
            'POL': ['10ª', '11ª', '12ª'], 'S.D.T': ['11ª'], 'T.T': ['10ª', '11ª', '12ª'],
            'Telecomunicações': ['12ª'],
        }
        disc_comuns = {
            'Empreendedorismo': ['10ª', '11ª', '12ª'], 'FAI': ['10ª', '11ª'],
            'Física': ['10ª', '11ª', '12ª'], 'Gestão de Projetos': ['12ª'],
            'Inglês': ['10ª', '11ª'], 'Língua Portuguesa': ['10ª', '11ª'],
            'Matemática': ['10ª', '11ª', '12ª'], 'OGI': ['12ª'], 'Química': ['10ª', '11ª'],
        }

        def associar_disciplina(nome, curso_filtro, anos):
            disc, _ = Disciplina.objects.get_or_create(nome=nome)
            for ano in anos:
                for turma in turmas.values():
                    if turma.curso == curso_filtro and turma.ano == ano:
                        DisciplinaTurma.objects.get_or_create(disciplina=disc, turma=turma)

        for nome, anos in disc_inf.items():
            associar_disciplina(nome, 'informatica', anos)
        for nome, anos in disc_elec.items():
            associar_disciplina(nome, 'eletronica', anos)
        for nome, anos in disc_comuns.items():
            disc, _ = Disciplina.objects.get_or_create(nome=nome)
            for ano in anos:
                for turma in turmas.values():
                    if turma.ano == ano:
                        DisciplinaTurma.objects.get_or_create(disciplina=disc, turma=turma)
        self.stdout.write(f'   ✅ {Disciplina.objects.count()} disciplinas criadas.')

        # =========================================================
        # 3. ALUNOS (saldo inicial 9999)
        # =========================================================
        self.stdout.write('👨‍🎓 Criando alunos...')
        first_names = ['João', 'Maria', 'José', 'Ana', 'Pedro', 'Paula', 'Lucas', 'Mariana', 'Carlos', 'Fernanda']
        last_names = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Costa', 'Ferreira', 'Almeida', 'Ribeiro']
        aluno_counter = 1
        for turma in turmas.values():
            for _ in range(4):
                primeiro = random.choice(first_names)
                ultimo = random.choice(last_names)
                username = f"{primeiro.lower()}.{ultimo.lower()}{aluno_counter}"
                processo = f"2024{str(aluno_counter).zfill(5)}"
                email = f"{username}@aluno.colegioarvore.ao"
                usuario, _ = Usuario.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': primeiro,
                        'last_name': ultimo,
                        'email': email,
                        'password': make_password('aluno9999'),
                        'tipo': 'aluno'
                    }
                )
                PerfilAluno.objects.get_or_create(
                    usuario=usuario,
                    defaults={
                        'numero_processo': processo,
                        'turma': turma,
                        'saldo_pontos': 9999
                    }
                )
                aluno_counter += 1
        self.stdout.write(f'   ✅ {PerfilAluno.objects.count()} alunos criados.')

        # =========================================================
        # 4. PROFESSORES
        # =========================================================
        self.stdout.write('👨‍🏫 Criando professores...')
        prof_only, _ = Usuario.objects.get_or_create(
            username='professor.apenas',
            defaults={
                'first_name': 'Carlos', 'last_name': 'Mendes',
                'email': 'professor@colegioarvore.ao',
                'password': make_password('prof123'),
                'tipo': 'professor', 'is_professor': True
            }
        )
        coord_only, _ = Usuario.objects.get_or_create(
            username='coordenador.apenas',
            defaults={
                'first_name': 'Ana', 'last_name': 'Paula',
                'email': 'coordenador@colegioarvore.ao',
                'password': make_password('coord123'),
                'tipo': 'coordenador', 'is_coordenador': True
            }
        )
        diretor_only, _ = Usuario.objects.get_or_create(
            username='diretor.apenas',
            defaults={
                'first_name': 'João', 'last_name': 'Zinga',
                'email': 'diretor@colegioarvore.ao',
                'password': make_password('diretor123'),
                'tipo': 'diretor_turma', 'is_diretor_turma': True,
                'turma_vinculada': '12ª EA'
            }
        )
        prof_coord, _ = Usuario.objects.get_or_create(
            username='prof.coord',
            defaults={
                'first_name': 'Ricardo', 'last_name': 'Lima',
                'email': 'prof.coord@colegioarvore.ao',
                'password': make_password('multi123'),
                'tipo': 'professor', 'is_professor': True, 'is_coordenador': True
            }
        )
        prof_diretor, _ = Usuario.objects.get_or_create(
            username='prof.diretor',
            defaults={
                'first_name': 'Marcos', 'last_name': 'Silva',
                'email': 'prof.diretor@colegioarvore.ao',
                'password': make_password('multi123'),
                'tipo': 'professor', 'is_professor': True, 'is_diretor_turma': True,
                'turma_vinculada': '11ª ID'
            }
        )
        todos_cargos, _ = Usuario.objects.get_or_create(
            username='super.user',
            defaults={
                'first_name': 'Super', 'last_name': 'User',
                'email': 'super.user@colegioarvore.ao',
                'password': make_password('super123'),
                'tipo': 'professor',
                'is_professor': True, 'is_coordenador': True, 'is_diretor_turma': True,
                'turma_vinculada': '10ª EE'
            }
        )
        self.stdout.write('   ✅ Professores criados.')

        # =========================================================
        # 5. BENEFÍCIOS
        # =========================================================
        self.stdout.write('🎁 Criando benefícios...')
        beneficios_lista = [
            {'nome': 'Boletim de Notas Oficial', 'descricao': 'Impressão colorida do boletim oficial', 'custo_pontos': 200, 'categoria': 'academico'},
            {'nome': 'Folhas para Provas (Professor)', 'descricao': '10 folhas pautadas para provas', 'custo_pontos': 30, 'categoria': 'academico'},
            {'nome': 'Folhas para Provas Trimestrais', 'descricao': '20 folhas pautadas', 'custo_pontos': 60, 'categoria': 'academico'},
            {'nome': 'Internet Grátis (7 dias)', 'descricao': 'Wi-Fi de alta velocidade por 7 dias', 'custo_pontos': 300, 'categoria': 'tecnologia'},
            {'nome': 'Internet Grátis (30 dias)', 'descricao': 'Wi-Fi por 30 dias', 'custo_pontos': 1000, 'categoria': 'tecnologia'},
            {'nome': 'Certificado de Mérito', 'descricao': 'Certificado oficial de reconhecimento', 'custo_pontos': 150, 'categoria': 'premios'},
            {'nome': 'Dia sem Uniforme', 'descricao': 'Permissão para trajes civis', 'custo_pontos': 80, 'categoria': 'eventos'},
        ]
        for b in beneficios_lista:
            Beneficio.objects.get_or_create(
                nome=b['nome'],
                defaults={
                    'descricao': b['descricao'],
                    'custo_pontos': b['custo_pontos'],
                    'categoria': b['categoria'],
                    'disponivel': True
                }
            )
        self.stdout.write(f'   ✅ {Beneficio.objects.count()} benefícios criados.')

        # =========================================================
        # 6. ATIVIDADES
        # =========================================================
        self.stdout.write('📝 Criando atividades...')
        hoje = date.today()
        for disciplina in Disciplina.objects.all():
            for j in range(2):
                nome_atv = f"{disciplina.nome} - Atividade {j+1}"
                data_inicio = hoje - timedelta(days=random.randint(5, 30))
                data_fim = data_inicio + timedelta(days=random.randint(1, 7))
                atividade = Atividade.objects.create(
                    nome=nome_atv,
                    descricao=f"Atividade avaliativa de {disciplina.nome}",
                    criterios_avaliacao="Participação, assiduidade, desempenho",
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    hora_inicio=time(8, 0),
                    hora_fim=time(12, 0),
                    max_pontos_por_aluno=random.randint(50, 200),
                    disciplina=disciplina
                )
                turmas_da_disciplina = Turma.objects.filter(disciplinas_relacionadas__disciplina=disciplina)
                atividade.turmas.set(turmas_da_disciplina)
        self.stdout.write(f'   ✅ {Atividade.objects.count()} atividades criadas.')

        # =========================================================
        # 7. RESGATES DE BENEFÍCIOS
        # =========================================================
        self.stdout.write('🛒 Criando resgates de benefícios...')
        resgates_count = 0
        beneficios_disponiveis = Beneficio.objects.filter(disponivel=True)
        for aluno in PerfilAluno.objects.all():
            if random.random() < 0.3:
                beneficio = random.choice(beneficios_disponiveis)
                if aluno.saldo_pontos >= beneficio.custo_pontos:
                    ResgateBeneficio.objects.create(
                        aluno=aluno,
                        beneficio=beneficio,
                        pontos_gastos=beneficio.custo_pontos,
                        status='confirmado',
                        data_resgate=timezone.now()
                    )
                    aluno.saldo_pontos -= beneficio.custo_pontos
                    aluno.save()
                    resgates_count += 1
        self.stdout.write(f'   ✅ {resgates_count} resgates de benefícios criados.')

        # =========================================================
        # 8. TRANSAÇÕES
        # =========================================================
        self.stdout.write('💰 Criando transações...')
        transacoes_count = 0
        for atividade in Atividade.objects.all():
            for turma in atividade.turmas.all():
                for aluno in PerfilAluno.objects.filter(turma=turma):
                    pontos = random.randint(10, atividade.max_pontos_por_aluno)
                    aluno.saldo_pontos += pontos
                    aluno.save()
                    Transacao.objects.create(
                        aluno=aluno,
                        quantidade=pontos,
                        tipo='distribuicao',
                        descricao=f"Pontos da atividade: {atividade.nome}",
                        professor=prof_only,
                        atividade=atividade
                    )
                    transacoes_count += 1
        for aluno in PerfilAluno.objects.all():
            Transacao.objects.create(
                aluno=aluno,
                quantidade=random.randint(10, 50),
                tipo='adicao',
                descricao="Participação ativa na aula",
                professor=prof_only
            )
            transacoes_count += 1
            Transacao.objects.create(
                aluno=aluno,
                quantidade=-random.randint(5, 20),
                tipo='remocao',
                descricao="Penalização por comportamento",
                professor=prof_only
            )
            transacoes_count += 1
        self.stdout.write(f'   ✅ {transacoes_count} transações criadas.')

        # =========================================================
        # 9. RELATÓRIO FINAL
        # =========================================================
        self.stdout.write(self.style.SUCCESS('\n🎉 POPULAÇÃO COMPLETA CONCLUÍDA!'))
        self.stdout.write('\n📊 RESUMO FINAL:')
        self.stdout.write(f'   - Turmas: {Turma.objects.count()}')
        self.stdout.write(f'   - Disciplinas: {Disciplina.objects.count()}')
        self.stdout.write(f'   - Alunos: {PerfilAluno.objects.count()}')
        self.stdout.write(f'   - Benefícios: {Beneficio.objects.count()}')
        self.stdout.write(f'   - Atividades: {Atividade.objects.count()}')
        self.stdout.write(f'   - Resgates: {ResgateBeneficio.objects.count()}')
        self.stdout.write(f'   - Transações: {Transacao.objects.count()}')
        self.stdout.write('\n🔑 CREDENCIAIS:')
        self.stdout.write('   ALUNO: qualquer número de processo - senha "aluno9999"')
        self.stdout.write('   PROFESSOR: professor@colegioarvore.ao / prof123')
        self.stdout.write('   COORDENADOR: coordenador@colegioarvore.ao / coord123')
        self.stdout.write('   DIRETOR: diretor@colegioarvore.ao / diretor123')
        self.stdout.write('   PROF+COORD: prof.coord@colegioarvore.ao / multi123')
        self.stdout.write('   PROF+DIRETOR: prof.diretor@colegioarvore.ao / multi123')
        self.stdout.write('   SUPER: super.user@colegioarvore.ao / super123')