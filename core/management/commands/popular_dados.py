import random
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from core.models import (
    Usuario, Turma, Disciplina, DisciplinaTurma,
    PerfilAluno, Atividade, Transacao, Beneficio,
    ResgateBeneficio, PerfilProfessor
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
        # 3. ALUNOS (NOMES REAIS ORGANIZADOS POR TURMA)
        # =========================================================
        self.stdout.write('👨‍🎓 Criando alunos...')
        
        # Nomes reais para alunos do Colégio Árvore da Felicidade
        # Organizados por turma (4 alunos por turma)
        alunos_por_turma = {
            '10ª ID': [
                ('202400001', 'Alice Fernandes', 'alice.fernandes'),
                ('202400002', 'Bruno Cardoso', 'bruno.cardoso'),
                ('202400003', 'Carla Mendes', 'carla.mendes'),
                ('202400004', 'Diogo Lopes', 'diogo.lopes'),
            ],
            '10ª IB': [
                ('202400005', 'Elena Santos', 'elena.santos'),
                ('202400006', 'Fábio Gomes', 'fabio.gomes'),
                ('202400007', 'Gabriela Costa', 'gabriela.costa'),
                ('202400008', 'Hugo Pereira', 'hugo.pereira'),
            ],
            '11ª ID': [
                ('202400009', 'Inês Rodrigues', 'ines.rodrigues'),
                ('202400010', 'João Almeida', 'joao.almeida'),
                ('202400011', 'Lara Ferreira', 'lara.ferreira'),
                ('202400012', 'Miguel Carvalho', 'miguel.carvalho'),
            ],
            '11ª IB': [
                ('202400013', 'Natália Ribeiro', 'natalia.ribeiro'),
                ('202400014', 'Oscar Martins', 'oscar.martins'),
                ('202400015', 'Patrícia Monteiro', 'patricia.monteiro'),
                ('202400016', 'Ricardo Nunes', 'ricardo.nunes'),
            ],
            '12ª ID': [
                ('202400017', 'Sofia Ramos', 'sofia.ramos'),
                ('202400018', 'Tomás Batista', 'tomas.batista'),
                ('202400019', 'Úrsula Matos', 'ursula.matos'),
                ('202400020', 'Vítor Pires', 'vitor.pires'),
            ],
            '12ª IB': [
                ('202400021', 'Wanda Castro', 'wanda.castro'),
                ('202400022', 'Xavier Neves', 'xavier.neves'),
                ('202400023', 'Yara Machado', 'yara.machado'),
                ('202400024', 'Zacarias Barbosa', 'zacarias.barbosa'),
            ],
            '10ª EA': [
                ('202400025', 'Adriana Vieira', 'adriana.vieira'),
                ('202400026', 'Bernardo Leal', 'bernardo.leal'),
                ('202400027', 'Cristiano Soares', 'cristiano.soares'),
                ('202400028', 'Daniela Cunha', 'daniela.cunha'),
            ],
            '10ª EE': [
                ('202400029', 'Eduardo Brito', 'eduardo.brito'),
                ('202400030', 'Filipa Cruz', 'filipa.cruz'),
                ('202400031', 'Gonçalo Tavares', 'goncalo.tavares'),
                ('202400032', 'Helena Marques', 'helena.marques'),
            ],
            '11ª EA': [
                ('202400033', 'Igor Lima', 'igor.lima'),
                ('202400034', 'Jéssica Rocha', 'jessica.rocha'),
                ('202400035', 'Kevin Silva', 'kevin.silva'),
                ('202400036', 'Lúcia Gonçalves', 'lucia.goncalves'),
            ],
            '11ª EE': [
                ('202400037', 'Manuel Abreu', 'manuel.abreu'),
                ('202400038', 'Nádia Simões', 'nadia.simoes'),
                ('202400039', 'Olga Andrade', 'olga.andrade'),
                ('202400040', 'Paulo Mota', 'paulo.mota'),
            ],
            '12ª EA': [
                ('202400041', 'Raquel Leite', 'raquel.leite'),
                ('202400042', 'Sérgio Pinheiro', 'sergio.pinheiro'),
                ('202400043', 'Tânia Dias', 'tania.dias'),
                ('202400044', 'Ulisses Neves', 'ulisses.neves'),
            ],
            '12ª EE': [
                ('202400045', 'Vera Cardoso', 'vera.cardoso'),
                ('202400046', 'Wilson Santos', 'wilson.santos'),
                ('202400047', 'Xénia Luz', 'xenia.luz'),
                ('202400048', 'Yuri Mendes', 'yuri.mendes'),
            ],
        }
        
        for turma_nome, alunos_lista in alunos_por_turma.items():
            turma = turmas.get(turma_nome)
            if not turma:
                continue
                
            for processo, nome_completo, username in alunos_lista:
                primeiro = nome_completo.split()[0]
                ultimo = nome_completo.split()[1]
                email = f"{username}@aluno.colegioarvore.ao"
                
                usuario, created = Usuario.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': primeiro,
                        'last_name': ultimo,
                        'email': email,
                        'password': make_password('aluno9999'),
                        'tipo': 'aluno'
                    }
                )
                
                if not created:
                    usuario.first_name = primeiro
                    usuario.last_name = ultimo
                    usuario.email = email
                    usuario.save()
                
                PerfilAluno.objects.get_or_create(
                    usuario=usuario,
                    defaults={
                        'numero_processo': processo,
                        'turma': turma,
                        'saldo_pontos': 9999
                    }
                )
                
                self.stdout.write(f'      - {processo}: {nome_completo} - {turma_nome}')
        
        self.stdout.write(f'   ✅ {PerfilAluno.objects.count()} alunos criados.')

        # =========================================================
        # 4. PROFESSORES
        # =========================================================
        self.stdout.write('👨‍🏫 Criando professores...')
        
        primeira_disciplina = Disciplina.objects.first()
        
        # Professor apenas
        prof_only, _ = Usuario.objects.get_or_create(
            username='professor.carlos',
            defaults={
                'first_name': 'Carlos', 'last_name': 'Mendes',
                'email': 'professor@colegioarvore.ao',
                'password': make_password('prof123'),
                'tipo': 'professor', 'is_professor': True
            }
        )
        if primeira_disciplina:
            PerfilProfessor.objects.get_or_create(
                usuario=prof_only,
                defaults={'disciplina': primeira_disciplina}
            )
        self.stdout.write('      - professor@colegioarvore.ao (Professor Carlos Mendes)')
        
        # Coordenador apenas
        coord_only, _ = Usuario.objects.get_or_create(
            username='coordenador.ana',
            defaults={
                'first_name': 'Ana', 'last_name': 'Paula',
                'email': 'coordenador@colegioarvore.ao',
                'password': make_password('coord123'),
                'tipo': 'coordenador', 'is_coordenador': True
            }
        )
        self.stdout.write('      - coordenador@colegioarvore.ao (Coordenadora Ana Paula)')
        
        # Diretor apenas
        turma_12ea = turmas.get('12ª EA')
        diretor_only, _ = Usuario.objects.get_or_create(
            username='diretor.joao',
            defaults={
                'first_name': 'João', 'last_name': 'Zinga',
                'email': 'diretor@colegioarvore.ao',
                'password': make_password('diretor123'),
                'tipo': 'diretor_turma', 'is_diretor_turma': True,
                'turma_vinculada': turma_12ea
            }
        )
        self.stdout.write('      - diretor@colegioarvore.ao (Diretor João Zinga)')
        
        # Professor + Coordenador
        prof_coord, _ = Usuario.objects.get_or_create(
            username='prof.coord.ricardo',
            defaults={
                'first_name': 'Ricardo', 'last_name': 'Lima',
                'email': 'prof.coord@colegioarvore.ao',
                'password': make_password('multi123'),
                'tipo': 'professor', 'is_professor': True, 'is_coordenador': True
            }
        )
        if primeira_disciplina:
            PerfilProfessor.objects.get_or_create(
                usuario=prof_coord,
                defaults={'disciplina': primeira_disciplina}
            )
        self.stdout.write('      - prof.coord@colegioarvore.ao (Professor Ricardo Lima + Coordenador)')
        
        # Professor + Diretor
        turma_11id = turmas.get('11ª ID')
        prof_diretor, _ = Usuario.objects.get_or_create(
            username='prof.diretor.marcos',
            defaults={
                'first_name': 'Marcos', 'last_name': 'Silva',
                'email': 'prof.diretor@colegioarvore.ao',
                'password': make_password('multi123'),
                'tipo': 'professor', 'is_professor': True, 'is_diretor_turma': True,
                'turma_vinculada': turma_11id
            }
        )
        if primeira_disciplina:
            PerfilProfessor.objects.get_or_create(
                usuario=prof_diretor,
                defaults={'disciplina': primeira_disciplina}
            )
        self.stdout.write('      - prof.diretor@colegioarvore.ao (Professor Marcos Silva + Diretor)')
        
        # Super usuário (todos os cargos)
        turma_10ee = turmas.get('10ª EE')
        todos_cargos, _ = Usuario.objects.get_or_create(
            username='super.user',
            defaults={
                'first_name': 'Super', 'last_name': 'User',
                'email': 'super.user@colegioarvore.ao',
                'password': make_password('super123'),
                'tipo': 'professor',
                'is_professor': True, 'is_coordenador': True, 'is_diretor_turma': True,
                'turma_vinculada': turma_10ee
            }
        )
        if primeira_disciplina:
            PerfilProfessor.objects.get_or_create(
                usuario=todos_cargos,
                defaults={'disciplina': primeira_disciplina}
            )
        self.stdout.write('      - super.user@colegioarvore.ao (Super User - todos os perfis)')
        
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
        atividade_count = 0
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
                atividade_count += 1
        self.stdout.write(f'   ✅ {atividade_count} atividades criadas.')

        # =========================================================
        # 7. RESGATES DE BENEFÍCIOS
        # =========================================================
        self.stdout.write('🛒 Criando resgates de benefícios...')
        resgates_count = 0
        beneficios_disponiveis = list(Beneficio.objects.filter(disponivel=True))
        
        for aluno in PerfilAluno.objects.all():
            if random.random() < 0.3 and beneficios_disponiveis:
                beneficio = random.choice(beneficios_disponiveis)
                if aluno.saldo_pontos >= beneficio.custo_pontos:
                    ResgateBeneficio.objects.create(
                        aluno=aluno,
                        beneficio=beneficio,
                        pontos_gastos=beneficio.custo_pontos,
                        status='confirmado'
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
        
        # Distribuição de pontos por atividades
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
        
        # Transações adicionais (adição e remoção)
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
        self.stdout.write('   ALUNOS:')
        for aluno in PerfilAluno.objects.all().order_by('numero_processo'):
            self.stdout.write(f'      - {aluno.numero_processo}: {aluno.usuario.get_full_name()} (senha: aluno9999) - Turma: {aluno.turma.nome if aluno.turma else "Sem turma"}')
        self.stdout.write('   PROFESSOR: professor@colegioarvore.ao / prof123')
        self.stdout.write('   COORDENADOR: coordenador@colegioarvore.ao / coord123')
        self.stdout.write('   DIRETOR: diretor@colegioarvore.ao / diretor123')
        self.stdout.write('   PROF+COORD: prof.coord@colegioarvore.ao / multi123')
        self.stdout.write('   PROF+DIRETOR: prof.diretor@colegioarvore.ao / multi123')
        self.stdout.write('   SUPER: super.user@colegioarvore.ao / super123')