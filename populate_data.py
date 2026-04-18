"""
Script para popular o banco de dados com dados de teste.
Executar com: python manage.py populate_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import (
    Usuario, Turma, PerfilAluno, PerfilProfessor, 
    PerfilDiretorTurma, PerfilCoordenador, Atividade, 
    Beneficio, Transacao
)
from datetime import date, time, timedelta
import random

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de teste'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando população do banco de dados...'))
        
        # ==================== 1. CRIAR TURMAS ====================
        self.stdout.write('📚 Criando turmas...')
        
        turmas_eletronica = ['10ª EA', '10ª EE', '11ª EA', '11ª EE', '12ª EA', '12ª EE']
        turmas_informatica = ['10ª ID', '10ª IB', '11ª ID', '11ª IB', '12ª ID', '12ª IB']
        
        turmas = []
        for nome in turmas_eletronica:
            turma = Turma.objects.create(
                nome=nome,
                curso='eletronica',
                horario=f'{random.choice(["Tarde", "Terça e Quinta", "Quarta e Sexta"])} - {random.choice(["08h às 10h", "10h às 12h", "14h às 16h"])}'
            )
            turmas.append(turma)
            self.stdout.write(f'  ✅ Criada turma: {nome} - Eletrónica')
        
        for nome in turmas_informatica:
            turma = Turma.objects.create(
                nome=nome,
                curso='informatica',
                horario=f'{random.choice(["Segunda e Quarta", "Terça e Quinta", "Quarta e Sexta"])} - {random.choice(["08h às 10h", "10h às 12h", "14h às 16h"])}'
            )
            turmas.append(turma)
            self.stdout.write(f'  ✅ Criada turma: {nome} - Informática')
        
        # ==================== 2. CRIAR USUÁRIOS ====================
        self.stdout.write('👥 Criando usuários...')
        
        # Superusuário Admin
        admin = Usuario.objects.create_superuser(
            username='admin',
            email='admin@colegioarvore.ao',
            password='admin123',
            tipo='admin',
            first_name='Administrador',
            last_name='Sistema'
        )
        self.stdout.write('  ✅ Criado superusuário: admin')
        
        # ==================== 3. CRIAR ALUNOS ====================
        self.stdout.write('👨‍🎓 Criando alunos...')
        
        nomes_alunos = [
            ('Ricardo', 'Oliveira'), ('João', 'Silva'), ('Maria', 'Santos'),
            ('Carla', 'Souza'), ('Pedro', 'Costa'), ('Luciana', 'Ferreira'),
            ('Tiago', 'Mendes'), ('Sofia', 'Oliveira'), ('Rafael', 'Lima'),
            ('Beatriz', 'Nunes'), ('André', 'Costa'), ('Fernanda', 'Lima'),
            ('Gustavo', 'Rocha'), ('Patrícia', 'Mendes'), ('Lucas', 'Almeida'),
            ('Mariana', 'Santos'), ('Carlos', 'Eduardo'), ('Amanda', 'Silva'),
            ('Rodrigo', 'Faria'), ('Tatiana', 'Costa'), ('Felipe', 'Santos'),
            ('Juliana', 'Lima'), ('Bruno', 'Mendes'), ('Camila', 'Rocha'),
            ('Daniel', 'Oliveira'), ('Renata', 'Souza')
        ]
        
        alunos = []
        niveis = ['Iniciante', 'Aprendiz', 'Explorador', 'Mestre']
        
        for i, (nome, sobrenome) in enumerate(nomes_alunos, 1):
            username = f"aluno{i}"
            numero_processo = f"2024{10000 + i}"
            saldo = random.randint(0, 3500)
            nivel = niveis[min(saldo // 1000, 3)]
            turma = random.choice(turmas)
            
            usuario = Usuario.objects.create_user(
                username=username,
                password='aluno123',
                tipo='aluno',
                first_name=nome,
                last_name=sobrenome
            )
            
            aluno = PerfilAluno.objects.create(
                usuario=usuario,
                numero_processo=numero_processo,
                turma=turma,
                saldo_pontos=saldo,
                nivel=nivel,
                documento=f"{random.randint(100000000, 999999999)}"
            )
            alunos.append(aluno)
            self.stdout.write(f'  ✅ Criado aluno: {nome} {sobrenome} - {numero_processo} - {saldo} pts')
        
        # ==================== 4. CRIAR PROFESSORES ====================
        self.stdout.write('👨‍🏫 Criando professores...')
        
        professores_data = [
            ('Carlos', 'Mendes', 'Matemática'),
            ('Ana', 'Paula', 'Português'),
            ('Ricardo', 'Santos', 'Física'),
            ('Fernanda', 'Lima', 'Química'),
            ('Paulo', 'Costa', 'História'),
            ('Mariana', 'Souza', 'Geografia'),
            ('Eduardo', 'Oliveira', 'Inglês'),
            ('Cristina', 'Rocha', 'Biologia'),
            ('André', 'Silva', 'Programação'),
            ('Patrícia', 'Nunes', 'Redes')
        ]
        
        professores = []
        for i, (nome, sobrenome, disciplina) in enumerate(professores_data, 1):
            username = f"professor{i}"
            usuario = Usuario.objects.create_user(
                username=username,
                password='prof123',
                tipo='professor',
                first_name=nome,
                last_name=sobrenome,
                email_institucional=f"{nome.lower()}.{sobrenome.lower()}@colegioarvore.ao"
            )
            
            professor = PerfilProfessor.objects.create(
                usuario=usuario,
                disciplina=disciplina
            )
            # Adicionar turmas ao professor
            turmas_professor = random.sample(turmas, random.randint(2, 4))
            professor.turmas.add(*turmas_professor)
            professores.append(professor)
            self.stdout.write(f'  ✅ Criado professor: {nome} {sobrenome} - {disciplina}')
        
        # ==================== 5. CRIAR DIRETORES DE TURMA ====================
        self.stdout.write('👔 Criando diretores de turma...')
        
        diretores_data = [
            ('Roberto', 'Almeida', 0),
            ('Teresa', 'Martins', 1),
            ('Jorge', 'Ferreira', 2),
            ('Lúcia', 'Rodrigues', 3),
            ('Antônio', 'Gomes', 4),
            ('Cláudia', 'Lopes', 5)
        ]
        
        diretores = []
        for i, (nome, sobrenome, turma_index) in enumerate(diretores_data, 1):
            username = f"diretor{i}"
            usuario = Usuario.objects.create_user(
                username=username,
                password='diretor123',
                tipo='diretor_turma',
                first_name=nome,
                last_name=sobrenome
            )
            # Marcar como diretor de turma
            usuario.is_diretor_turma = True
            usuario.save()
            
            diretor = PerfilDiretorTurma.objects.create(
                usuario=usuario,
                turma=turmas[turma_index] if turma_index < len(turmas) else None
            )
            diretores.append(diretor)
            self.stdout.write(f'  ✅ Criado diretor de turma: {nome} {sobrenome}')
        
        # ==================== 6. CRIAR COORDENADORES ====================
        self.stdout.write('📋 Criando coordenadores...')
        
        coordenadores_data = [
            ('Ana', 'Paula', 'Atividades Culturais'),
            ('Marcos', 'Silva', 'Atividades Científicas'),
            ('Carla', 'Souza', 'Eventos Especiais')
        ]
        
        coordenadores = []
        for i, (nome, sobrenome, departamento) in enumerate(coordenadores_data, 1):
            username = f"coordenador{i}"
            usuario = Usuario.objects.create_user(
                username=username,
                password='coord123',
                tipo='coordenador',
                first_name=nome,
                last_name=sobrenome,
                email_institucional=f"{nome.lower()}.{sobrenome.lower()}@colegioarvore.ao"
            )
            # Marcar como coordenador
            usuario.is_coordenador = True
            usuario.save()
            
            coordenador = PerfilCoordenador.objects.create(
                usuario=usuario,
                departamento=departamento
            )
            coordenadores.append(coordenador)
            self.stdout.write(f'  ✅ Criado coordenador: {nome} {sobrenome} - {departamento}')
        
        # ==================== 7. CRIAR PROFESSOR QUE TAMBÉM É DIRETOR ====================
        self.stdout.write('🔄 Criando professor que também é diretor de turma...')
        
        usuario_prof_diretor = Usuario.objects.create_user(
            username='prof_diretor',
            password='prof123',
            tipo='professor',
            first_name='Marcelo',
            last_name='Ribeiro',
            email_institucional='marcelo.ribeiro@colegioarvore.ao'
        )
        usuario_prof_diretor.is_diretor_turma = True
        usuario_prof_diretor.save()
        
        professor_diretor = PerfilProfessor.objects.create(
            usuario=usuario_prof_diretor,
            disciplina='Educação Física'
        )
        # Adicionar turmas
        professor_diretor.turmas.add(turmas[0], turmas[1])
        
        diretor_prof = PerfilDiretorTurma.objects.create(
            usuario=usuario_prof_diretor,
            turma=turmas[2]
        )
        self.stdout.write('  ✅ Criado professor que também é diretor: Marcelo Ribeiro')
        
        # ==================== 8. CRIAR ATIVIDADES ====================
        self.stdout.write('📅 Criando atividades...')
        
        atividades_data = [
            {
                'nome': 'Workshop de Robótica com Arduino',
                'categoria': 'ciencia',
                'requisitos': 'Conhecimentos básicos de lógica de programação\nDisponibilidade para 4 sessões de 3 horas\nTrabalho em equipe',
                'pontuacao_total': 200,
                'data': date(2025, 11, 15),
                'hora': time(14, 0),
                'interrompe_aula': False
            },
            {
                'nome': 'Feira de Ciências: Sustentabilidade',
                'categoria': 'ciencia',
                'requisitos': 'Desenvolver um protótipo ou pesquisa científica\nApresentação oral de 10 minutos\nRelatório escrito do projeto',
                'pontuacao_total': 300,
                'data': date(2025, 12, 5),
                'hora': time(9, 0),
                'interrompe_aula': True
            },
            {
                'nome': 'Oficina de Teatro e Expressão Artística',
                'categoria': 'cultura',
                'requisitos': 'Disponibilidade para ensaios semanais\nParticipar da apresentação final\nCriar uma pequena cena em grupo',
                'pontuacao_total': 180,
                'data': date(2025, 11, 20),
                'hora': time(15, 30),
                'interrompe_aula': False
            },
            {
                'nome': 'Concurso de Fotografia Artística',
                'categoria': 'cultura',
                'requisitos': 'Enviar 3 fotografias originais\nTema: "A beleza do quotidiano"\nParticipar da exposição final',
                'pontuacao_total': 150,
                'data': date(2025, 11, 25),
                'hora': time(10, 0),
                'interrompe_aula': False
            },
            {
                'nome': 'Olimpíada de Matemática',
                'categoria': 'ciencia',
                'requisitos': 'Inscrição prévia com o professor\nRealizar prova escrita de 2 horas\nParticipar de 2 sessões de treino',
                'pontuacao_total': 250,
                'data': date(2025, 10, 30),
                'hora': time(8, 0),
                'interrompe_aula': True
            },
            {
                'nome': 'Torneio de Xadrez',
                'categoria': 'desporto',
                'requisitos': 'Conhecimento das regras básicas\nParticipar de todas as partidas\nFair play',
                'pontuacao_total': 120,
                'data': date(2025, 11, 10),
                'hora': time(14, 0),
                'interrompe_aula': False
            },
            {
                'nome': 'Acção de Voluntariado',
                'categoria': 'voluntariado',
                'requisitos': 'Disponibilidade para 4 horas\nTrabalho em equipa\nCompromisso social',
                'pontuacao_total': 100,
                'data': date(2025, 12, 10),
                'hora': time(9, 0),
                'interrompe_aula': True
            }
        ]
        
        atividades = []
        for ativ_data in atividades_data:
            atividade = Atividade.objects.create(
                nome=ativ_data['nome'],
                categoria=ativ_data['categoria'],
                requisitos=ativ_data['requisitos'],
                pontuacao_total=ativ_data['pontuacao_total'],
                data=ativ_data['data'],
                hora=ativ_data['hora'],
                interrompe_aula=ativ_data['interrompe_aula'],
                coordenador=random.choice(coordenadores) if coordenadores else None
            )
            atividades.append(atividade)
            self.stdout.write(f'  ✅ Criada atividade: {ativ_data["nome"]}')
        
        # ==================== 9. CRIAR BENEFÍCIOS ====================
        self.stdout.write('🎁 Criando benefícios...')
        
        beneficios_data = [
            {'nome': 'Boletim de Notas Oficial', 'descricao': 'Impressão colorida do boletim de notas oficial com selo do colégio', 'custo_pontos': 200, 'categoria': 'academico'},
            {'nome': 'Folhas para Provas (Professor)', 'descricao': '10 folhas pautadas para provas do professor', 'custo_pontos': 30, 'categoria': 'academico'},
            {'nome': 'Folhas para Provas Trimestrais', 'descricao': '20 folhas pautadas para as provas trimestrais', 'custo_pontos': 60, 'categoria': 'academico'},
            {'nome': 'Internet Grátis (7 dias)', 'descricao': 'Acesso Wi-Fi de alta velocidade por 7 dias', 'custo_pontos': 300, 'categoria': 'tecnologia'},
            {'nome': 'Internet Grátis (30 dias)', 'descricao': 'Acesso Wi-Fi de alta velocidade por 30 dias', 'custo_pontos': 1000, 'categoria': 'tecnologia'},
            {'nome': 'Certificado de Mérito', 'descricao': 'Certificado oficial de reconhecimento', 'custo_pontos': 150, 'categoria': 'premios'},
            {'nome': 'Laboratório Extra', 'descricao': '2 horas adicionais no laboratório de ciências', 'custo_pontos': 120, 'categoria': 'academico'},
            {'nome': 'Dia sem Uniforme', 'descricao': 'Permissão para usar trajes civis por um dia', 'custo_pontos': 80, 'categoria': 'eventos'},
        ]
        
        for benef_data in beneficios_data:
            beneficio = Beneficio.objects.create(
                nome=benef_data['nome'],
                descricao=benef_data['descricao'],
                custo_pontos=benef_data['custo_pontos'],
                categoria=benef_data['categoria'],
                disponivel=True
            )
            self.stdout.write(f'  ✅ Criado benefício: {benef_data["nome"]} - {benef_data["custo_pontos"]} pts')
        
        # ==================== 10. CRIAR TRANSAÇÕES (HISTÓRICO) ====================
        self.stdout.write('📜 Criando transações de exemplo...')
        
        tipos_transacao = ['adicao', 'remocao', 'resgate']
        motivos = [
            'Participação ativa na aula',
            'Resposta correta em exercício',
            'Ajuda aos colegas',
            'Entrega de trabalho no prazo',
            'Comportamento exemplar',
            'Participação em atividade extracurricular'
        ]
        
        transacoes_criadas = 0
        for aluno in alunos[:20]:  # Apenas 20 alunos para não sobrecarregar
            num_transacoes = random.randint(3, 8)
            saldo_atual = aluno.saldo_pontos
            
            for _ in range(num_transacoes):
                tipo = random.choice(tipos_transacao)
                if tipo == 'adicao':
                    quantidade = random.randint(5, 30)
                    saldo_atual += quantidade
                elif tipo == 'remocao' and saldo_atual >= 10:
                    quantidade = random.randint(5, 20)
                    saldo_atual -= quantidade
                else:
                    continue
                
                Transacao.objects.create(
                    aluno=aluno,
                    professor=random.choice(professores) if professores else None,
                    quantidade=quantidade,
                    tipo=tipo,
                    descricao=random.choice(motivos)
                )
                transacoes_criadas += 1
            
            # Atualizar saldo final do aluno
            aluno.saldo_pontos = saldo_atual
            aluno.atualizar_nivel()
            aluno.save()
        
        self.stdout.write(f'  ✅ Criadas {transacoes_criadas} transações')
        
        # ==================== 11. INSERIR INSCRIÇÕES EM ATIVIDADES ====================
        self.stdout.write('📝 Criando inscrições em atividades...')
        
        inscricoes_criadas = 0
        for aluno in alunos[:25]:
            num_inscricoes = random.randint(1, 4)
            atividades_escolhidas = random.sample(atividades, min(num_inscricoes, len(atividades)))
            
            for atividade in atividades_escolhidas:
                # Evitar duplicidade
                from core.models import Inscricao
                if not Inscricao.objects.filter(aluno=aluno, atividade=atividade).exists():
                    Inscricao.objects.create(
                        aluno=aluno,
                        atividade=atividade,
                        status=random.choice(['pendente', 'confirmada', 'concluida']),
                        pontos_ganhos=atividade.pontuacao_total if random.choice([True, False]) else 0
                    )
                    inscricoes_criadas += 1
        
        self.stdout.write(f'  ✅ Criadas {inscricoes_criadas} inscrições')
        
        # ==================== 12. RESUMO FINAL ====================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\n📊 RESUMO DO QUE FOI CRIADO:')
        self.stdout.write(f'  • Turmas: {Turma.objects.count()}')
        self.stdout.write(f'  • Usuários: {Usuario.objects.count()}')
        self.stdout.write(f'  • Alunos: {PerfilAluno.objects.count()}')
        self.stdout.write(f'  • Professores: {PerfilProfessor.objects.count()}')
        self.stdout.write(f'  • Diretores de Turma: {PerfilDiretorTurma.objects.count()}')
        self.stdout.write(f'  • Coordenadores: {PerfilCoordenador.objects.count()}')
        self.stdout.write(f'  • Atividades: {Atividade.objects.count()}')
        self.stdout.write(f'  • Benefícios: {Beneficio.objects.count()}')
        self.stdout.write(f'  • Transações: {Transacao.objects.count()}')
        self.stdout.write(f'  • Inscrições: {Inscricao.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n🔑 CREDENCIAIS DE ACESSO:'))
        self.stdout.write('  • Admin: admin / admin123')
        self.stdout.write('  • Aluno: aluno1 / aluno123 (até aluno26)')
        self.stdout.write('  • Professor: professor1 / prof123 (até professor10)')
        self.stdout.write('  • Diretor de Turma: diretor1 / diretor123 (até diretor6)')
        self.stdout.write('  • Coordenador: coordenador1 / coord123 (até coordenador3)')
        self.stdout.write('  • Professor+Diretor: prof_diretor / prof123')
        
        self.stdout.write(self.style.SUCCESS('\n🚀 Para executar o servidor:'))
        self.stdout.write('  python manage.py runserver')