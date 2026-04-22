from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import (
    Usuario, Turma, Disciplina, DisciplinaTurma,
    PerfilAluno, Atividade, Transacao, Beneficio,
    ResgateBeneficio, PerfilProfessor
)


class Command(BaseCommand):
    help = 'Popula o banco com dados FIXOS e CONCRETOS para teste'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Populando banco com dados FIXOS e CONCRETOS...')

        # =========================================================
        # 1. TURMAS (FIXAS)
        # =========================================================
        self.stdout.write('📚 Criando turmas...')
        turmas_info = [
            # Informática
            ('10ª ID', 'informatica', '10ª'),
            ('10ª IB', 'informatica', '10ª'),
            ('11ª ID', 'informatica', '11ª'),
            ('11ª IB', 'informatica', '11ª'),
            ('12ª ID', 'informatica', '12ª'),
            ('12ª IB', 'informatica', '12ª'),
            # Eletrónica
            ('10ª EA', 'eletronica', '10ª'),
            ('10ª EE', 'eletronica', '10ª'),
            ('11ª EA', 'eletronica', '11ª'),
            ('11ª EE', 'eletronica', '11ª'),
            ('12ª EA', 'eletronica', '12ª'),
            ('12ª EE', 'eletronica', '12ª'),
        ]
        turmas = {}
        for nome, curso, ano in turmas_info:
            turma, _ = Turma.objects.get_or_create(nome=nome, defaults={'curso': curso, 'ano': ano})
            turmas[nome] = turma
        self.stdout.write(f'   ✅ {len(turmas)} turmas criadas.')

        # =========================================================
        # 2. DISCIPLINAS (FIXAS)
        # =========================================================
        self.stdout.write('📖 Criando disciplinas...')
        
        disc_informatica = {
            'Eletrotécnica': ['10ª', '11ª'],
            'SEAC': ['10ª', '11ª', '12ª'],
            'TIC': ['10ª', '11ª'],
            'TLP': ['10ª', '11ª', '12ª'],
            'TREI': ['11ª', '12ª'],
        }
        
        disc_eletronica = {
            'Eletrónica': ['10ª', '11ª', '12ª'],
            'Informática': ['10ª'],
            'POL': ['10ª', '11ª', '12ª'],
            'S.D.T': ['11ª'],
            'T.T': ['10ª', '11ª', '12ª'],
            'Telecomunicações': ['12ª'],
        }
        
        disc_comuns = {
            'D.T': ['11ª'],
            'Empreendedorismo': ['10ª', '11ª', '12ª'],
            'FAI': ['10ª', '11ª'],
            'Física': ['10ª', '11ª', '12ª'],
            'Gestão de Projetos': ['12ª'],
            'Inglês': ['10ª', '11ª'],
            'Língua Portuguesa': ['10ª', '11ª'],
            'Matemática': ['10ª', '11ª', '12ª'],
            'OGI': ['12ª'],
            'Química': ['10ª', '11ª'],
        }

        def associar_disciplina(nome, curso_filtro, anos):
            disc, _ = Disciplina.objects.get_or_create(nome=nome)
            for ano in anos:
                for turma in turmas.values():
                    if turma.curso == curso_filtro and turma.ano == ano:
                        DisciplinaTurma.objects.get_or_create(disciplina=disc, turma=turma)

        def associar_disciplina_comum(nome, anos):
            disc, _ = Disciplina.objects.get_or_create(nome=nome)
            for ano in anos:
                for turma in turmas.values():
                    if turma.ano == ano:
                        DisciplinaTurma.objects.get_or_create(disciplina=disc, turma=turma)

        for nome, anos in disc_informatica.items():
            associar_disciplina(nome, 'informatica', anos)
        for nome, anos in disc_eletronica.items():
            associar_disciplina(nome, 'eletronica', anos)
        for nome, anos in disc_comuns.items():
            associar_disciplina_comum(nome, anos)
        
        self.stdout.write(f'   ✅ {Disciplina.objects.count()} disciplinas criadas.')

        # =========================================================
        # 3. ALUNOS (2 POR TURMA - NOMES FIXOS)
        # =========================================================
        self.stdout.write('👨‍🎓 Criando alunos...')
        
        # Lista fixa de alunos (2 por turma = 24 alunos)
        alunos_fixos = [
            # Turma 10ª ID
            ('10ª ID', 'Ricardo Oliveira', '20240001', 1250),
            ('10ª ID', 'Fernanda Santos', '20240002', 980),
            # Turma 10ª IB
            ('10ª IB', 'Lucas Almeida', '20240003', 2100),
            ('10ª IB', 'Beatriz Costa', '20240004', 1850),
            # Turma 11ª ID
            ('11ª ID', 'Rafael Lima', '20240005', 3420),
            ('11ª ID', 'Juliana Ferreira', '20240006', 2980),
            # Turma 11ª IB
            ('11ª IB', 'Gabriel Souza', '20240007', 1560),
            ('11ª IB', 'Mariana Silva', '20240008', 2230),
            # Turma 12ª ID
            ('12ª ID', 'André Rodrigues', '20240009', 4100),
            ('12ª ID', 'Camila Nunes', '20240010', 3870),
            # Turma 12ª IB
            ('12ª IB', 'Thiago Mendes', '20240011', 2950),
            ('12ª IB', 'Larissa Rocha', '20240012', 3120),
            # Turma 10ª EA
            ('10ª EA', 'Pedro Henrique', '20240013', 890),
            ('10ª EA', 'Amanda Lima', '20240014', 1340),
            # Turma 10ª EE
            ('10ª EE', 'Bruno Cardoso', '20240015', 1670),
            ('10ª EE', 'Tatiane Oliveira', '20240016', 1430),
            # Turma 11ª EA
            ('11ª EA', 'Felipe Augusto', '20240017', 2780),
            ('11ª EA', 'Natália Souza', '20240018', 2450),
            # Turma 11ª EE
            ('11ª EE', 'Vinícius Pereira', '20240019', 1890),
            ('11ª EE', 'Patrícia Lima', '20240020', 2120),
            # Turma 12ª EA
            ('12ª EA', 'Eduardo Martins', '20240021', 5230),
            ('12ª EA', 'Carolina Ribeiro', '20240022', 4980),
            # Turma 12ª EE
            ('12ª EE', 'Guilherme Castro', '20240023', 3670),
            ('12ª EE', 'Vanessa Alves', '20240024', 3890),
        ]
        
        for turma_nome, nome_completo, processo, saldo in alunos_fixos:
            turma = turmas[turma_nome]
            primeiro, ultimo = nome_completo.split()
            username = f"{primeiro.lower()}.{ultimo.lower()}".replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            email = f"{username}@aluno.caf.ao"
            
            usuario, _ = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': primeiro,
                    'last_name': ultimo,
                    'email': email,
                    'password': make_password('aluno123'),
                    'tipo': 'aluno'
                }
            )
            PerfilAluno.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'numero_processo': processo,
                    'turma': turma,
                    'saldo_pontos': saldo
                }
            )
        
        self.stdout.write(f'   ✅ {PerfilAluno.objects.count()} alunos criados.')

        # =========================================================
        # 4. USUÁRIOS (Professor, Coordenador, Diretor) - FIXOS
        # =========================================================
        self.stdout.write('👨‍🏫 Criando usuários...')
        
        primeira_disciplina = Disciplina.objects.first()
        turma_12ea = turmas.get('12ª EA')
        
        # Professor
        prof, _ = Usuario.objects.get_or_create(
            username='professor.carlos',
            defaults={
                'first_name': 'Carlos', 'last_name': 'Mendes',
                'email': 'professor@caf.ao',
                'password': make_password('prof123'),
                'tipo': 'professor', 'is_professor': True
            }
        )
        if primeira_disciplina:
            PerfilProfessor.objects.get_or_create(usuario=prof, defaults={'disciplina': primeira_disciplina})
        
        # Coordenador
        coord, _ = Usuario.objects.get_or_create(
            username='coordenador.ana',
            defaults={
                'first_name': 'Ana', 'last_name': 'Paula',
                'email': 'coordenador@caf.ao',
                'password': make_password('coord123'),
                'tipo': 'coordenador', 'is_coordenador': True
            }
        )
        
        # Diretor
        diretor, _ = Usuario.objects.get_or_create(
            username='diretor.joao',
            defaults={
                'first_name': 'João', 'last_name': 'Zinga',
                'email': 'diretor@caf.ao',
                'password': make_password('diretor123'),
                'tipo': 'diretor_turma', 'is_diretor_turma': True,
                'turma_vinculada': turma_12ea
            }
        )
        
        self.stdout.write('   ✅ Usuários criados.')

        # =========================================================
        # 5. BENEFÍCIOS (FIXOS)
        # =========================================================
        self.stdout.write('🎁 Criando benefícios...')
        beneficios_fixos = [
            {'nome': 'Boletim de Notas', 'descricao': 'Impressão oficial do boletim', 'custo': 200, 'categoria': 'academico', 'estoque': -1},
            {'nome': 'Internet 7 dias', 'descricao': 'Wi-Fi de alta velocidade por 7 dias', 'custo': 300, 'categoria': 'tecnologia', 'estoque': 50},
            {'nome': 'Internet 30 dias', 'descricao': 'Wi-Fi de alta velocidade por 30 dias', 'custo': 1000, 'categoria': 'tecnologia', 'estoque': 20},
            {'nome': 'Certificado de Mérito', 'descricao': 'Certificado oficial de reconhecimento', 'custo': 150, 'categoria': 'premios', 'estoque': -1},
            {'nome': 'Dia sem Uniforme', 'descricao': 'Permissão para trajes civis por um dia', 'custo': 80, 'categoria': 'eventos', 'estoque': 100},
        ]
        for b in beneficios_fixos:
            Beneficio.objects.get_or_create(
                nome=b['nome'],
                defaults={
                    'descricao': b['descricao'],
                    'custo_pontos': b['custo'],
                    'categoria': b['categoria'],
                    'estoque': b['estoque'],
                    'disponivel': True
                }
            )
        self.stdout.write(f'   ✅ {Beneficio.objects.count()} benefícios.')

        # =========================================================
        # 6. ATIVIDADES DO COORDENADOR (FIXAS)
        # =========================================================
        self.stdout.write('📝 Criando atividades do coordenador...')
        hoje = date.today()
        
        atividades_coord_fixas = [
            {'nome': 'Feira de Ciências 2024', 'tipo': 'ciencia_tecnologia', 'pontos': 300, 'interrompe': True, 
             'data_ini': hoje - timedelta(days=30), 'data_fim': hoje - timedelta(days=25)},
            {'nome': 'Workshop de Robótica', 'tipo': 'ciencia_tecnologia', 'pontos': 250, 'interrompe': False,
             'data_ini': hoje - timedelta(days=20), 'data_fim': hoje - timedelta(days=18)},
            {'nome': 'Peça de Teatro "O Auto da Compadecida"', 'tipo': 'cultural', 'pontos': 200, 'interrompe': True,
             'data_ini': hoje - timedelta(days=15), 'data_fim': hoje - timedelta(days=12)},
            {'nome': 'Concurso de Fotografia "Minha Escola"', 'tipo': 'cultural', 'pontos': 180, 'interrompe': False,
             'data_ini': hoje - timedelta(days=10), 'data_fim': hoje - timedelta(days=8)},
            {'nome': 'Olimpíada de Matemática', 'tipo': 'ciencia_tecnologia', 'pontos': 350, 'interrompe': True,
             'data_ini': hoje - timedelta(days=5), 'data_fim': hoje - timedelta(days=2)},
            {'nome': 'Clube de Leitura "Machado de Assis"', 'tipo': 'cultural', 'pontos': 150, 'interrompe': False,
             'data_ini': hoje - timedelta(days=25), 'data_fim': hoje - timedelta(days=22)},
        ]
        
        for ac in atividades_coord_fixas:
            atividade = Atividade.objects.create(
                nome=ac['nome'],
                descricao=f'Atividade {ac["tipo"]} organizada pelo coordenador',
                criterios_avaliacao='Participação, desempenho e criatividade',
                data_inicio=ac['data_ini'],
                data_fim=ac['data_fim'],
                hora_inicio=time(8, 0),
                hora_fim=time(12, 0),
                max_pontos_por_aluno=ac['pontos'],
                tipo_atividade=ac['tipo'],
                interrompe_aula=ac['interrompe']
            )
            atividade.turmas.set(turmas.values())
        
        self.stdout.write(f'   ✅ {Atividade.objects.filter(disciplina__isnull=True).count()} atividades do coordenador.')

        # =========================================================
        # 7. ATIVIDADES DOS PROFESSORES (Curriculares - FIXAS)
        # =========================================================
        self.stdout.write('📝 Criando atividades dos professores...')
        
        atividades_prof_fixas = [
            ('Matemática', 'Prova Trimestral', 100, hoje - timedelta(days=14), hoje - timedelta(days=10)),
            ('Matemática', 'Trabalho em Grupo', 80, hoje - timedelta(days=21), hoje - timedelta(days=18)),
            ('Física', 'Experiência de Laboratório', 120, hoje - timedelta(days=12), hoje - timedelta(days=9)),
            ('Física', 'Prova de Mecânica', 100, hoje - timedelta(days=7), hoje - timedelta(days=5)),
            ('Língua Portuguesa', 'Redação Dissertativa', 60, hoje - timedelta(days=18), hoje - timedelta(days=15)),
            ('Língua Portuguesa', 'Apresentação Oral', 70, hoje - timedelta(days=10), hoje - timedelta(days=8)),
            ('Inglês', 'Listening Test', 50, hoje - timedelta(days=22), hoje - timedelta(days=20)),
            ('Inglês', 'Apresentação de Diálogo', 65, hoje - timedelta(days=6), hoje - timedelta(days=4)),
            ('Química', 'Tabela Periódica', 90, hoje - timedelta(days=16), hoje - timedelta(days=13)),
            ('História', 'Seminário sobre Independência', 85, hoje - timedelta(days=9), hoje - timedelta(days=6)),
        ]
        
        for disc_nome, nome_atv, pontos, data_ini, data_fim in atividades_prof_fixas:
            disciplina = Disciplina.objects.filter(nome=disc_nome).first()
            if disciplina:
                atividade = Atividade.objects.create(
                    nome=nome_atv,
                    descricao=f'Atividade avaliativa de {disc_nome}',
                    criterios_avaliacao='Participação, assiduidade, qualidade das respostas',
                    data_inicio=data_ini,
                    data_fim=data_fim,
                    hora_inicio=time(8, 0),
                    hora_fim=time(12, 0),
                    max_pontos_por_aluno=pontos,
                    disciplina=disciplina,
                    interrompe_aula=False
                )
                turmas_disc = Turma.objects.filter(disciplinas_relacionadas__disciplina=disciplina)
                atividade.turmas.set(turmas_disc)
        
        self.stdout.write(f'   ✅ {Atividade.objects.filter(disciplina__isnull=False).count()} atividades dos professores.')

        # =========================================================
        # 8. TRANSAÇÕES (Distribuição de pontos - FIXAS)
        # =========================================================
        self.stdout.write('💰 Criando transações...')
        
        transacoes_fixas = [
            # (aluno_processo, atividade_nome, pontos)
            ('20240001', 'Feira de Ciências 2024', 300),
            ('20240002', 'Feira de Ciências 2024', 280),
            ('20240005', 'Olimpíada de Matemática', 350),
            ('20240006', 'Olimpíada de Matemática', 310),
            ('20240009', 'Prova Trimestral', 95),
            ('20240010', 'Prova Trimestral', 88),
            ('20240011', 'Prova Trimestral', 100),
            ('20240013', 'Workshop de Robótica', 250),
            ('20240014', 'Workshop de Robótica', 230),
            ('20240017', 'Peça de Teatro "O Auto da Compadecida"', 200),
            ('20240018', 'Peça de Teatro "O Auto da Compadecida"', 190),
            ('20240021', 'Experiência de Laboratório', 120),
            ('20240022', 'Experiência de Laboratório', 115),
            ('20240023', 'Trabalho em Grupo', 80),
            ('20240024', 'Trabalho em Grupo', 75),
        ]
        
        for processo, atividade_nome, pontos in transacoes_fixas:
            aluno = PerfilAluno.objects.filter(numero_processo=processo).first()
            atividade = Atividade.objects.filter(nome=atividade_nome).first()
            if aluno and atividade:
                aluno.saldo_pontos += pontos
                aluno.save()
                Transacao.objects.create(
                    aluno=aluno,
                    quantidade=pontos,
                    tipo='distribuicao',
                    descricao=f'Pontos da atividade: {atividade_nome}',
                    professor=prof,
                    atividade=atividade
                )
        
        self.stdout.write(f'   ✅ {Transacao.objects.count()} transações criadas.')

        # =========================================================
        # 9. RESGATES DE BENEFÍCIOS (FIXOS)
        # =========================================================
        self.stdout.write('🛒 Criando resgates...')
        
        resgates_fixos = [
            ('20240001', 'Internet 7 dias', 300),
            ('20240005', 'Certificado de Mérito', 150),
            ('20240009', 'Dia sem Uniforme', 80),
            ('20240011', 'Internet 30 dias', 1000),
            ('20240021', 'Boletim de Notas', 200),
        ]
        
        for processo, beneficio_nome, pontos in resgates_fixos:
            aluno = PerfilAluno.objects.filter(numero_processo=processo).first()
            beneficio = Beneficio.objects.filter(nome=beneficio_nome).first()
            if aluno and beneficio and aluno.saldo_pontos >= pontos:
                aluno.saldo_pontos -= pontos
                aluno.save()
                ResgateBeneficio.objects.create(
                    aluno=aluno,
                    beneficio=beneficio,
                    pontos_gastos=pontos,
                    status='confirmado'
                )
        
        self.stdout.write(f'   ✅ {ResgateBeneficio.objects.count()} resgates criados.')

        # =========================================================
        # 10. RELATÓRIO FINAL
        # =========================================================
        self.stdout.write(self.style.SUCCESS('\n🎉 POPULAÇÃO CONCLUÍDA COM DADOS FIXOS!'))
        self.stdout.write('\n📊 RESUMO:')
        self.stdout.write(f'   - Turmas: {Turma.objects.count()}')
        self.stdout.write(f'   - Disciplinas: {Disciplina.objects.count()}')
        self.stdout.write(f'   - Alunos: {PerfilAluno.objects.count()}')
        self.stdout.write(f'   - Benefícios: {Beneficio.objects.count()}')
        self.stdout.write(f'   - Atividades Coordenador: {Atividade.objects.filter(disciplina__isnull=True).count()}')
        self.stdout.write(f'   - Atividades Professor: {Atividade.objects.filter(disciplina__isnull=False).count()}')
        self.stdout.write(f'   - Resgates: {ResgateBeneficio.objects.count()}')
        self.stdout.write(f'   - Transações: {Transacao.objects.count()}')
        
        self.stdout.write('\n🔑 CREDENCIAIS (FIXAS):')
        self.stdout.write('   ALUNO: qualquer número de processo - senha "aluno123"')
        self.stdout.write('   PROFESSOR: professor@caf.ao / prof123')
        self.stdout.write('   COORDENADOR: coordenador@caf.ao / coord123')
        self.stdout.write('   DIRETOR: diretor@caf.ao / diretor123')
        
        self.stdout.write('\n📋 ALUNOS COM Nº PROCESSO:')
        for aluno in PerfilAluno.objects.all().order_by('numero_processo'):
            self.stdout.write(f'   - {aluno.numero_processo}: {aluno.usuario.get_full_name()} - {aluno.saldo_pontos} pts - Turma {aluno.turma.nome}')