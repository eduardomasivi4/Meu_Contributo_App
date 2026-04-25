"""
Script para popular o banco de dados com dados iniciais.
Execute com: python manage.py popular_dados
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import (
    Usuario, Turma, Disciplina, DisciplinaTurma, PerfilAluno, 
    PerfilProfessor, PerfilDiretorTurma, Beneficio, Atividade, CriterioAtividade
)


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('POPULANDO BANCO DE DADOS'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # ==================== 1. CRIAR TURMAS ====================
        self.stdout.write('\n1. Criando turmas...')
        
        turmas_data = [
            # Eletrónica
            {'nome': 'ET10A', 'curso': 'eletronica', 'ano': '10ª'},
            {'nome': 'ET10B', 'curso': 'eletronica', 'ano': '10ª'},
            {'nome': 'ET11A', 'curso': 'eletronica', 'ano': '11ª'},
            {'nome': 'ET11B', 'curso': 'eletronica', 'ano': '11ª'},
            {'nome': 'ET12A', 'curso': 'eletronica', 'ano': '12ª'},
            {'nome': 'ET12B', 'curso': 'eletronica', 'ano': '12ª'},
            # Informática
            {'nome': 'INF10A', 'curso': 'informatica', 'ano': '10ª'},
            {'nome': 'INF10B', 'curso': 'informatica', 'ano': '10ª'},
            {'nome': 'INF11A', 'curso': 'informatica', 'ano': '11ª'},
            {'nome': 'INF11B', 'curso': 'informatica', 'ano': '11ª'},
            {'nome': 'INF12A', 'curso': 'informatica', 'ano': '12ª'},
            {'nome': 'INF12B', 'curso': 'informatica', 'ano': '12ª'},
        ]
        
        turmas = {}
        for t_data in turmas_data:
            turma, created = Turma.objects.get_or_create(
                nome=t_data['nome'],
                curso=t_data['curso'],
                defaults={'ano': t_data['ano']}
            )
            turmas[t_data['nome']] = turma
            if created:
                self.stdout.write(f'  ✓ Turma {t_data["nome"]} criada')
        
        # ==================== 2. CRIAR DISCIPLINAS ====================
        self.stdout.write('\n2. Criando disciplinas...')
        
        disciplinas_data = [
            'Matemática', 'Português', 'Inglês', 'Física', 'Química',
            'Programação', 'Redes de Computadores', 'Eletrónica Geral',
            'Bases de Dados', 'Desenvolvimento Web', 'Educação Física'
        ]
        
        disciplinas = {}
        for disc_nome in disciplinas_data:
            disciplina, created = Disciplina.objects.get_or_create(nome=disc_nome)
            disciplinas[disc_nome] = disciplina
            if created:
                self.stdout.write(f'  ✓ Disciplina {disc_nome} criada')
        
        # ==================== 3. ASSOCIAR DISCIPLINAS ÀS TURMAS ====================
        self.stdout.write('\n3. Associando disciplinas às turmas...')
        
        for turma in Turma.objects.all():
            # Disciplinas gerais para todas as turmas
            for disc_nome in ['Matemática', 'Português', 'Inglês', 'Educação Física']:
                disciplina = disciplinas[disc_nome]
                DisciplinaTurma.objects.get_or_create(disciplina=disciplina, turma=turma)
            
            # Disciplinas específicas por curso
            if turma.curso == 'eletronica':
                for disc_nome in ['Física', 'Química', 'Eletrónica Geral']:
                    disciplina = disciplinas[disc_nome]
                    DisciplinaTurma.objects.get_or_create(disciplina=disciplina, turma=turma)
            else:
                for disc_nome in ['Programação', 'Redes de Computadores', 'Bases de Dados', 'Desenvolvimento Web']:
                    disciplina = disciplinas[disc_nome]
                    DisciplinaTurma.objects.get_or_create(disciplina=disciplina, turma=turma)
        
        self.stdout.write('  ✓ Associações criadas')
        
        # ==================== 4. CRIAR USUÁRIOS ADMIN ====================
        self.stdout.write('\n4. Criando usuário admin...')
        
        admin, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@colegioarvore.ao',
                'password': make_password('admin123'),
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'tipo': 'admin',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            self.stdout.write('  ✓ Usuário admin criado (senha: admin123)')
        
        # ==================== 5. CRIAR PROFESSORES ====================
        self.stdout.write('\n5. Criando professores...')
        
        professores_data = [
            {'username': 'prof_joao', 'email': 'joao.silva@colegioarvore.ao', 'nome': 'João', 'sobrenome': 'Silva', 'disciplina': 'Matemática'},
            {'username': 'prof_maria', 'email': 'maria.santos@colegioarvore.ao', 'nome': 'Maria', 'sobrenome': 'Santos', 'disciplina': 'Português'},
            {'username': 'prof_carlos', 'email': 'carlos.pereira@colegioarvore.ao', 'nome': 'Carlos', 'sobrenome': 'Pereira', 'disciplina': 'Programação'},
            {'username': 'prof_ana', 'email': 'ana.oliveira@colegioarvore.ao', 'nome': 'Ana', 'sobrenome': 'Oliveira', 'disciplina': 'Eletrónica Geral'},
            {'username': 'prof_pedro', 'email': 'pedro.costa@colegioarvore.ao', 'nome': 'Pedro', 'sobrenome': 'Costa', 'disciplina': 'Física'},
        ]
        
        for p_data in professores_data:
            usuario, created = Usuario.objects.get_or_create(
                username=p_data['username'],
                defaults={
                    'email': p_data['email'],
                    'password': make_password('professor123'),
                    'first_name': p_data['nome'],
                    'last_name': p_data['sobrenome'],
                    'tipo': 'professor',
                    'is_professor': True
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Professor {p_data["username"]} criado')
            
            disciplina = disciplinas.get(p_data['disciplina'])
            PerfilProfessor.objects.update_or_create(
                usuario=usuario,
                defaults={'disciplina': disciplina}
            )
        
        # ==================== 6. CRIAR DIRETORES DE TURMA ====================
        self.stdout.write('\n6. Criando diretores de turma...')
        
        diretores_data = [
            {'username': 'diretor_et10a', 'email': 'diretor.et10a@colegioarvore.ao', 'nome': 'Diretor', 'sobrenome': 'ET10A', 'turma': 'ET10A'},
            {'username': 'diretor_inf10a', 'email': 'diretor.inf10a@colegioarvore.ao', 'nome': 'Diretor', 'sobrenome': 'INF10A', 'turma': 'INF10A'},
            {'username': 'diretor_et11a', 'email': 'diretor.et11a@colegioarvore.ao', 'nome': 'Diretor', 'sobrenome': 'ET11A', 'turma': 'ET11A'},
            {'username': 'diretor_inf11a', 'email': 'diretor.inf11a@colegioarvore.ao', 'nome': 'Diretor', 'sobrenome': 'INF11A', 'turma': 'INF11A'},
        ]
        
        for d_data in diretores_data:
            usuario, created = Usuario.objects.get_or_create(
                username=d_data['username'],
                defaults={
                    'email': d_data['email'],
                    'password': make_password('diretor123'),
                    'first_name': d_data['nome'],
                    'last_name': d_data['sobrenome'],
                    'tipo': 'diretor_turma',
                    'is_diretor_turma': True
                }
            )
            
            turma = turmas.get(d_data['turma'])
            if turma:
                usuario.turma_vinculada = turma
                usuario.save()
            
            if created:
                self.stdout.write(f'  ✓ Diretor {d_data["username"]} criado')
        
        # ==================== 7. CRIAR COORDENADORES ====================
        self.stdout.write('\n7. Criando coordenadores...')
        
        coordenadores_data = [
            {'username': 'coord_cultural', 'email': 'cultural@colegioarvore.ao', 'nome': 'Coordenador', 'sobrenome': 'Cultural', 'is_cultural': True},
            {'username': 'coord_ciencia', 'email': 'ciencia@colegioarvore.ao', 'nome': 'Coordenador', 'sobrenome': 'Ciência', 'is_ciencia': True},
        ]
        
        for c_data in coordenadores_data:
            usuario, created = Usuario.objects.get_or_create(
                username=c_data['username'],
                defaults={
                    'email': c_data['email'],
                    'password': make_password('coordenador123'),
                    'first_name': c_data['nome'],
                    'last_name': c_data['sobrenome'],
                    'tipo': 'coordenador',
                    'is_coordenador_cultural': c_data.get('is_cultural', False),
                    'is_coordenador_ciencia': c_data.get('is_ciencia', False),
                }
            )
            if created:
                self.stdout.write(f'  ✓ Coordenador {c_data["username"]} criado')
        
        # ==================== 8. CRIAR ALUNOS ====================
        self.stdout.write('\n8. Criando alunos...')
        
        alunos_por_turma = {
            'ET10A': ['20241001', '20241002', '20241003', '20241004', '20241005'],
            'ET10B': ['20241006', '20241007', '20241008', '20241009', '20241010'],
            'INF10A': ['20242001', '20242002', '20242003', '20242004', '20242005'],
            'INF10B': ['20242006', '20242007', '20242008', '20242009', '20242010'],
            'ET11A': ['20241101', '20241102', '20241103', '20241104', '20241105'],
            'INF11A': ['20242101', '20242102', '20242103', '20242104', '20242105'],
        }
        
        nomes = ['João', 'Maria', 'Pedro', 'Ana', 'Lucas', 'Beatriz', 'Rafael', 'Camila', 'Gabriel', 'Juliana']
        sobrenomes = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima', 'Gomes']
        
        aluno_index = 0
        for turma_nome, processos in alunos_por_turma.items():
            turma = turmas.get(turma_nome)
            if not turma:
                continue
                
            for i, processo in enumerate(processos):
                nome = nomes[(aluno_index + i) % len(nomes)]
                sobrenome = sobrenomes[(aluno_index + i) % len(sobrenomes)]
                username = f'aluno_{processo}'
                
                usuario, created = Usuario.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@aluno.colegioarvore.ao',
                        'password': make_password(processo),
                        'first_name': nome,
                        'last_name': sobrenome,
                        'tipo': 'aluno'
                    }
                )
                
                if created:
                    PerfilAluno.objects.create(
                        usuario=usuario,
                        numero_processo=processo,
                        turma=turma,
                        saldo_pontos=100
                    )
                    self.stdout.write(f'  ✓ Aluno {nome} {sobrenome} ({processo}) criado')
                    aluno_index += 1
        
        # ==================== 9. CRIAR BENEFÍCIOS ====================
        self.stdout.write('\n9. Criando benefícios...')
        
        beneficios_data = [
            {'nome': 'Acesso Wi-Fi 1 Mês', 'descricao': 'Acesso gratuito à internet Wi-Fi por 30 dias', 'custo': 200, 'categoria': 'tecnologia'},
            {'nome': 'Desconto na Cantina', 'descricao': '10% de desconto nas compras da cantina por 1 semana', 'custo': 150, 'categoria': 'academico'},
            {'nome': 'Material Escolar', 'descricao': 'Kit com cadernos e canetas', 'custo': 300, 'categoria': 'academico'},
            {'nome': 'Camiseta do Colégio', 'descricao': 'Camiseta oficial do CAF', 'custo': 250, 'categoria': 'premios'},
            {'nome': 'Excursão Cultural', 'descricao': 'Participação em excursão cultural', 'custo': 500, 'categoria': 'eventos'},
            {'nome': 'Troféu de Mérito', 'descricao': 'Troféu de reconhecimento', 'custo': 400, 'categoria': 'premios'},
            {'nome': 'Curso Online', 'descricao': 'Curso online de programação', 'custo': 600, 'categoria': 'tecnologia'},
            {'nome': 'Cinema', 'descricao': 'Ingresso para cinema', 'custo': 180, 'categoria': 'eventos'},
        ]
        
        for b_data in beneficios_data:
            beneficio, created = Beneficio.objects.get_or_create(
                nome=b_data['nome'],
                defaults={
                    'descricao': b_data['descricao'],
                    'custo_pontos': b_data['custo'],
                    'categoria': b_data['categoria'],
                    'disponivel': True,
                    'estoque': 10
                }
            )
            if created:
                self.stdout.write(f'  ✓ Benefício "{b_data["nome"]}" criado ({b_data["custo"]} pts)')
        
        # ==================== 10. CRIAR ATIVIDADES EXEMPLO ====================
        self.stdout.write('\n10. Criando atividades de exemplo...')
        
        # Atividade cultural
        atividade_cultural, created = Atividade.objects.get_or_create(
            nome='Festival de Talentos',
            tipo_atividade='cultural',
            defaults={
                'descricao': 'Evento cultural com apresentações artísticas',
                'criterios_avaliacao': 'Participação\nQualidade da apresentação\nOriginalidade',
                'max_pontos_por_aluno': 200,
                'todos_cursos': True,
                'finalizada': False
            }
        )
        if created:
            for turma in Turma.objects.all()[:6]:
                atividade_cultural.turmas.add(turma)
            self.stdout.write('  ✓ Atividade cultural "Festival de Talentos" criada')
        
        # Atividade ciência
        atividade_ciencia, created = Atividade.objects.get_or_create(
            nome='Feira de Ciências',
            tipo_atividade='ciencia_tecnologia',
            defaults={
                'descricao': 'Apresentação de projetos científicos',
                'criterios_avaliacao': 'Pesquisa\nInovação\nApresentação',
                'max_pontos_por_aluno': 250,
                'todos_cursos': True,
                'finalizada': False
            }
        )
        if created:
            for turma in Turma.objects.all()[:6]:
                atividade_ciencia.turmas.add(turma)
            self.stdout.write('  ✓ Atividade científica "Feira de Ciências" criada')
        
        # ==================== RESULTADO FINAL ====================
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('POPULAÇÃO CONCLUÍDA COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'\n📊 RESUMO:')
        self.stdout.write(f'   Turmas: {Turma.objects.count()}')
        self.stdout.write(f'   Disciplinas: {Disciplina.objects.count()}')
        self.stdout.write(f'   Professores: {Usuario.objects.filter(is_professor=True).count()}')
        self.stdout.write(f'   Diretores: {Usuario.objects.filter(is_diretor_turma=True).count()}')
        self.stdout.write(f'   Coordenadores: {Usuario.objects.filter(is_coordenador_cultural=True).count() + Usuario.objects.filter(is_coordenador_ciencia=True).count()}')
        self.stdout.write(f'   Alunos: {PerfilAluno.objects.count()}')
        self.stdout.write(f'   Benefícios: {Beneficio.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n🔐 CREDENCIAIS:'))
        self.stdout.write('   ADMIN: admin@colegioarvore.ao / admin123')
        self.stdout.write('   PROFESSOR: joao.silva@colegioarvore.ao / professor123')
        self.stdout.write('   DIRETOR: diretor.et10a@colegioarvore.ao / diretor123')
        self.stdout.write('   COORDENADOR CULTURAL: cultural@colegioarvore.ao / coordenador123')
        self.stdout.write('   COORDENADOR CIÊNCIA: ciencia@colegioarvore.ao / coordenador123')
        self.stdout.write('   ALUNO: aluno_20241001@aluno.colegioarvore.ao / 20241001')