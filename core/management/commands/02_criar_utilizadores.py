from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import (
    Usuario, PerfilAluno, Turma, Disciplina,
    PerfilProfessor, PerfilCoordenador, PerfilDiretorTurma
)


class Command(BaseCommand):
    help = 'PASSO 2: Criar Alunos, Professores, Coordenador, Diretor'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n🚀 PASSO 2: CRIANDO UTILIZADORES\n'))

        # =========================================================
        # 1. BUSCAR TURMAS EXISTENTES
        # =========================================================
        try:
            turma_12ea = Turma.objects.get(nome='12ª EA')
            turma_12id = Turma.objects.get(nome='12ª ID')
            self.stdout.write('   ✅ Turmas encontradas: 12ª EA, 12ª ID')
        except Turma.DoesNotExist:
            self.stdout.write(self.style.ERROR('   ❌ ERRO: Turmas não encontradas. Execute o script 01 primeiro!'))
            return

        # =========================================================
        # 2. ALUNOS
        # =========================================================
        self.stdout.write('\n👨‍🎓 Criando alunos...')
        
        alunos_12ea = [
            ('João', 'Silva', '20240021', 585),
            ('Maria', 'Santos', '20240022', 440),
            ('Pedro', 'Costa', '20240023', 320),
            ('Ana', 'Paula', '20240024', 540),
        ]
        
        for primeiro, ultimo, processo, saldo in alunos_12ea:
            username = f"{primeiro.lower()}.{ultimo.lower()}"
            email = f"{username}@aluno.caf.ao"
            
            usuario, created = Usuario.objects.get_or_create(
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
                    'turma': turma_12ea,
                    'saldo_pontos': saldo
                }
            )
            self.stdout.write(f'   ✅ Aluno: {primeiro} {ultimo} (12ª EA)')
        
        alunos_12id = [
            ('Carlos', 'Ferreira', '20240025', 680),
            ('Sofia', 'Reis', '20240026', 520),
            ('Lucas', 'Mendes', '20240027', 450),
            ('Beatriz', 'Lopes', '20240028', 610),
        ]
        
        for primeiro, ultimo, processo, saldo in alunos_12id:
            username = f"{primeiro.lower()}.{ultimo.lower()}"
            email = f"{username}@aluno.caf.ao"
            
            usuario, created = Usuario.objects.get_or_create(
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
                    'turma': turma_12id,
                    'saldo_pontos': saldo
                }
            )
            self.stdout.write(f'   ✅ Aluno: {primeiro} {ultimo} (12ª ID)')
        
        self.stdout.write(self.style.SUCCESS(f'   ✅ Total: {PerfilAluno.objects.count()} alunos'))

        # =========================================================
        # 3. DISCIPLINAS PARA PROFESSORES
        # =========================================================
        try:
            disciplina_fisica = Disciplina.objects.get(nome='Física')
            disciplina_matematica = Disciplina.objects.get(nome='Matemática')
            self.stdout.write('\n   ✅ Disciplinas encontradas: Física, Matemática')
        except Disciplina.DoesNotExist:
            self.stdout.write(self.style.ERROR('   ❌ ERRO: Disciplinas não encontradas!'))
            return

        # =========================================================
        # 4. PROFESSORES
        # =========================================================
        self.stdout.write('\n👨‍🏫 Criando professores...')
        
        # Professor 1 - Carlos Mendes (Física)
        prof1, created = Usuario.objects.get_or_create(
            username='professor.carlos',
            defaults={
                'first_name': 'Carlos', 'last_name': 'Mendes',
                'email': 'professor@caf.ao',
                'password': make_password('prof123'),
                'tipo': 'professor', 'is_professor': True
            }
        )
        perfil_prof1, _ = PerfilProfessor.objects.get_or_create(
            usuario=prof1,
            defaults={'disciplina': disciplina_fisica}
        )
        perfil_prof1.turmas.add(turma_12ea, turma_12id)
        self.stdout.write(f'   ✅ Professor: Carlos Mendes (Física) - Turmas: 12ª EA, 12ª ID')
        
        # Professor 2 - Ana Martins (Matemática)
        prof2, created = Usuario.objects.get_or_create(
            username='professor.ana',
            defaults={
                'first_name': 'Ana', 'last_name': 'Martins',
                'email': 'ana.martins@caf.ao',
                'password': make_password('prof123'),
                'tipo': 'professor', 'is_professor': True
            }
        )
        perfil_prof2, _ = PerfilProfessor.objects.get_or_create(
            usuario=prof2,
            defaults={'disciplina': disciplina_matematica}
        )
        perfil_prof2.turmas.add(turma_12ea, turma_12id)
        self.stdout.write(f'   ✅ Professor: Ana Martins (Matemática) - Turmas: 12ª EA, 12ª ID')
        
        # Professor 3 - Ricardo Almeida (múltiplos cargos)
        prof3, created = Usuario.objects.get_or_create(
            username='professor.ricardo',
            defaults={
                'first_name': 'Ricardo', 'last_name': 'Almeida',
                'email': 'ricardo.almeida@caf.ao',
                'password': make_password('multi123'),
                'tipo': 'professor',
                'is_professor': True,
                'is_coordenador': True
            }
        )
        perfil_prof3, _ = PerfilProfessor.objects.get_or_create(
            usuario=prof3,
            defaults={'disciplina': disciplina_fisica}
        )
        perfil_prof3.turmas.add(turma_12ea)
        self.stdout.write(f'   ✅ Professor+Coordenador: Ricardo Almeida (Física)')

        # =========================================================
        # 5. COORDENADOR
        # =========================================================
        self.stdout.write('\n👔 Criando coordenador...')
        
        coord, created = Usuario.objects.get_or_create(
            username='coordenador.ana',
            defaults={
                'first_name': 'Ana', 'last_name': 'Paula',
                'email': 'coordenador@caf.ao',
                'password': make_password('coord123'),
                'tipo': 'coordenador', 'is_coordenador': True
            }
        )
        PerfilCoordenador.objects.get_or_create(
            usuario=coord,
            defaults={'departamento': 'Actividades Extra-Curriculares'}
        )
        self.stdout.write(f'   ✅ Coordenador: Ana Paula')

        # =========================================================
        # 6. DIRETOR DE TURMA
        # =========================================================
        self.stdout.write('\n👑 Criando diretor de turma...')
        
        diretor, created = Usuario.objects.get_or_create(
            username='diretor.joao',
            defaults={
                'first_name': 'João', 'last_name': 'Zinga',
                'email': 'diretor@caf.ao',
                'password': make_password('diretor123'),
                'tipo': 'diretor_turma', 'is_diretor_turma': True,
                'turma_vinculada': turma_12ea
            }
        )
        self.stdout.write(f'   ✅ Diretor: João Zinga (Turma: 12ª EA)')

        # =========================================================
        # RESUMO FINAL
        # =========================================================
        self.stdout.write(self.style.SUCCESS('\n✅ PASSO 2 CONCLUÍDO COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS(f'   - Alunos: {PerfilAluno.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Professores: {PerfilProfessor.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Coordenador: 1'))
        self.stdout.write(self.style.SUCCESS(f'   - Diretor: 1'))