from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import (
    Usuario, Turma, Disciplina, DisciplinaTurma,
    PerfilAluno, Atividade, Transacao, Beneficio,
    ResgateBeneficio, PerfilProfessor
)


class Command(BaseCommand):
    help = 'Popula o banco com dados FIXOS e CONCRETOS para teste (versão com credenciais reduzidas + Diretor Pedagógico)'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Populando banco com dados FIXOS e CONCRETOS (credenciais reduzidas + Diretor Pedagógico)...')

        # =========================================================
        # 1. TURMAS (FIXAS)
        # =========================================================
        self.stdout.write('📚 Criando turmas...')
        turmas_info = [
            ('10ª ID', 'informatica', '10ª'),
            ('10ª IB', 'informatica', '10ª'),
            ('11ª ID', 'informatica', '11ª'),
            ('11ª IB', 'informatica', '11ª'),
            ('12ª ID', 'informatica', '12ª'),
            ('12ª IB', 'informatica', '12ª'),
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
        # 3. ALUNOS (1 POR TURMA - NOMES FIXOS)
        # =========================================================
        self.stdout.write('👨‍🎓 Criando alunos (1 por turma)...')
        
        alunos_fixos = [
            ('10ª ID', 'Ricardo Oliveira', '20240001', 1250),
            ('10ª IB', 'Lucas Almeida', '20240003', 2100),
            ('11ª ID', 'Rafael Lima', '20240005', 3420),
            ('11ª IB', 'Gabriel Souza', '20240007', 1560),
            ('12ª ID', 'André Rodrigues', '20240009', 4100),
            ('12ª IB', 'Thiago Mendes', '20240011', 2950),
            ('10ª EA', 'Pedro Henrique', '20240013', 890),
            ('10ª EE', 'Bruno Cardoso', '20240015', 1670),
            ('11ª EA', 'Felipe Augusto', '20240017', 2780),
            ('11ª EE', 'Vinícius Pereira', '20240019', 1890),
            ('12ª EA', 'Eduardo Martins', '20240021', 5230),
            ('12ª EE', 'Guilherme Castro', '20240023', 3670),
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
        # 4. PROFESSORES (1 POR DISCIPLINA)
        # =========================================================
        self.stdout.write('👨‍🏫 Criando professores para cada disciplina...')
        
        for disciplina in Disciplina.objects.all():
            nome_disc = disciplina.nome.lower().replace(' ', '_').replace('.', '').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            username = f"prof.{nome_disc}"
            first_name = f"Prof_{disciplina.nome.split()[0]}" if disciplina.nome else "Professor"
            last_name = disciplina.nome.split()[-1] if len(disciplina.nome.split()) > 1 else "Default"
            email = f"{username}@caf.ao"
            
            usuario, _ = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': make_password('prof123'),
                    'tipo': 'professor',
                    'is_professor': True
                }
            )
            PerfilProfessor.objects.get_or_create(
                usuario=usuario,
                defaults={'disciplina': disciplina}
            )
        
        # Professor genérico para atividades do coordenador (fallback)
        prof_generico, _ = Usuario.objects.get_or_create(
            username='professor.generico',
            defaults={
                'first_name': 'Generico', 'last_name': 'Professor',
                'email': 'prof.generico@caf.ao',
                'password': make_password('prof123'),
                'tipo': 'professor',
                'is_professor': True
            }
        )
        PerfilProfessor.objects.get_or_create(usuario=prof_generico)
        
        self.stdout.write(f'   ✅ {Usuario.objects.filter(is_professor=True).count()} professores criados.')

        # =========================================================
        # 5. DIRETORES DE TURMA (1 POR TURMA)
        # =========================================================
        self.stdout.write('👨‍🏫 Criando diretores de turma...')
        
        for turma_nome, turma in turmas.items():
            username = f"diretor.{turma_nome.lower().replace(' ', '_').replace('ª', 'a')}"
            email = f"{username}@caf.ao"
            first_name = f"Diretor_{turma_nome}"
            last_name = "Turma"
            
            usuario, _ = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': make_password('diretor123'),
                    'tipo': 'diretor_turma',
                    'is_diretor_turma': True,
                    'turma_vinculada': turma
                }
            )
        
        self.stdout.write(f'   ✅ {Usuario.objects.filter(is_diretor_turma=True).count()} diretores de turma criados.')

        # =========================================================
        # 6. COORDENADORES (1 POR CURSO)
        # =========================================================
        self.stdout.write('👨‍🏫 Criando coordenadores por curso...')
        
        cursos = ['informatica', 'eletronica']
        for curso in cursos:
            username = f"coordenador.{curso}"
            email = f"{username}@caf.ao"
            first_name = f"Coordenador_{curso.capitalize()}"
            last_name = "Curso"
            
            usuario, _ = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': make_password('coord123'),
                    'tipo': 'coordenador',
                    'is_coordenador': True
                }
            )
        
        self.stdout.write(f'   ✅ {Usuario.objects.filter(is_coordenador=True).count()} coordenadores criados.')

        # =========================================================
        # 7. DIRETOR PEDAGÓGICO (1 ÚNICO USUÁRIO)
        # =========================================================
        self.stdout.write('👨‍🏫 Criando Diretor Pedagógico...')
        
        diretor_pedagogico, _ = Usuario.objects.get_or_create(
            username='diretor.pedagogico',
            defaults={
                'first_name': 'Manuel',
                'last_name': 'Costa',
                'email': 'pedagogico@caf.ao',
                'password': make_password('pedagogico123'),
                'tipo': 'diretor_pedagogico',
                'is_diretor_pedagogico': True,
            }
        )
        self.stdout.write('   ✅ Diretor Pedagógico criado.')

        # =========================================================
        # 8. BENEFÍCIOS (FIXOS)
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
        # 9. ATIVIDADES DO COORDENADOR (FIXAS)
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
        # 10. ATIVIDADES DOS PROFESSORES (Curriculares - FIXAS)
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
        # 11. TRANSAÇÕES (Distribuição de pontos - adaptadas)
        # =========================================================
        self.stdout.write('💰 Criando transações...')
        
        transacoes_originais = [
            ('20240001', 'Feira de Ciências 2024', 300),
            ('20240005', 'Olimpíada de Matemática', 350),
            ('20240009', 'Prova Trimestral', 95),
            ('20240011', 'Prova Trimestral', 100),
            ('20240013', 'Workshop de Robótica', 250),
            ('20240017', 'Peça de Teatro "O Auto da Compadecida"', 200),
            ('20240021', 'Experiência de Laboratório', 120),
            ('20240023', 'Trabalho em Grupo', 80),
        ]
        transacoes_extras = [
            ('20240003', 'Feira de Ciências 2024', 280),
            ('20240007', 'Olimpíada de Matemática', 310),
            ('20240015', 'Workshop de Robótica', 230),
            ('20240019', 'Peça de Teatro "O Auto da Compadecida"', 190),
        ]
        todas_transacoes = transacoes_originais + transacoes_extras
        
        for processo, atividade_nome, pontos in todas_transacoes:
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
                    professor=prof_generico,
                    atividade=atividade
                )
        
        self.stdout.write(f'   ✅ {Transacao.objects.count()} transações criadas.')

        # =========================================================
        # 12. RESGATES DE BENEFÍCIOS (FIXOS)
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
        # 13. RELATÓRIO FINAL
        # =========================================================
        self.stdout.write(self.style.SUCCESS('\n🎉 POPULAÇÃO CONCLUÍDA COM DADOS FIXOS (CREDENCIAIS REDUZIDAS + DIRETOR PEDAGÓGICO)!'))
        self.stdout.write('\n📊 RESUMO:')
        self.stdout.write(f'   - Turmas: {Turma.objects.count()}')
        self.stdout.write(f'   - Disciplinas: {Disciplina.objects.count()}')
        self.stdout.write(f'   - Alunos: {PerfilAluno.objects.count()}')
        self.stdout.write(f'   - Professores (com perfil): {PerfilProfessor.objects.count()}')
        self.stdout.write(f'   - Diretores de turma: {Usuario.objects.filter(is_diretor_turma=True).count()}')
        self.stdout.write(f'   - Coordenadores: {Usuario.objects.filter(is_coordenador=True).count()}')
        self.stdout.write(f'   - Diretores Pedagógicos: {Usuario.objects.filter(is_diretor_pedagogico=True).count()}')
        self.stdout.write(f'   - Benefícios: {Beneficio.objects.count()}')
        self.stdout.write(f'   - Atividades Coordenador: {Atividade.objects.filter(disciplina__isnull=True).count()}')
        self.stdout.write(f'   - Atividades Professor: {Atividade.objects.filter(disciplina__isnull=False).count()}')
        self.stdout.write(f'   - Resgates: {ResgateBeneficio.objects.count()}')
        self.stdout.write(f'   - Transações: {Transacao.objects.count()}')
        
        self.stdout.write('\n🔑 CREDENCIAIS (FIXAS):')
        self.stdout.write('   ALUNO: qualquer número de processo - senha "aluno123"')
        self.stdout.write('   PROFESSOR (genérico): professor.generico@caf.ao / prof123')
        self.stdout.write('   (Professores por disciplina: prof.<disciplina>@caf.ao / prof123)')
        self.stdout.write('   COORDENADOR (Informática): coordenador.informatica@caf.ao / coord123')
        self.stdout.write('   COORDENADOR (Eletrónica): coordenador.eletronica@caf.ao / coord123')
        self.stdout.write('   DIRETOR DE TURMA: diretor.<turma>@caf.ao / diretor123 (ex: diretor.10a_id@caf.ao)')
        self.stdout.write('   DIRETOR PEDAGÓGICO: pedagogico@caf.ao / pedagogico123')
        
        self.stdout.write('\n📋 ALUNOS COM Nº PROCESSO:')
        for aluno in PerfilAluno.objects.all().order_by('numero_processo'):
            self.stdout.write(f'   - {aluno.numero_processo}: {aluno.usuario.get_full_name()} - {aluno.saldo_pontos} pts - Turma {aluno.turma.nome}')