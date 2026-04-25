#!/usr/bin/env python
"""
SIMULAÇÃO DE CENÁRIO REAL - SISTEMA DE MÉRITO ESTUDANTIL
Execute: python simular_cenario_real.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django ANTES de qualquer importação de modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'merito_caf_config.settings')

# Inicializar Django
django.setup()

# Agora sim podemos importar os modelos
from django.contrib.auth.hashers import make_password
from core.models import (
    Usuario, Turma, Disciplina, DisciplinaTurma, PerfilAluno, 
    PerfilProfessor, PerfilDiretorTurma, Beneficio, Atividade, 
    CriterioAtividade, Transacao, ResgateBeneficio, GrupoAtividade,
    RegistroAtividadeAluno
)


def criar_turmas():
    print("\n🏫 CRIANDO TURMAS...")
    turmas = {}
    
    # Turmas do Curso de Eletrónica
    turmas_eletronica = ['ET10A', 'ET10B', 'ET11A', 'ET11B', 'ET12A', 'ET12B']
    for nome in turmas_eletronica:
        turma, _ = Turma.objects.get_or_create(
            nome=nome,
            curso='eletronica',
            defaults={'ano': f'{nome[:4]}ª'}
        )
        turmas[nome] = turma
        print(f"  ✓ {nome} - Eletrónica")
    
    # Turmas do Curso de Informática
    turmas_informatica = ['INF10A', 'INF10B', 'INF11A', 'INF11B', 'INF12A', 'INF12B']
    for nome in turmas_informatica:
        turma, _ = Turma.objects.get_or_create(
            nome=nome,
            curso='informatica',
            defaults={'ano': f'{nome[:4]}ª'}
        )
        turmas[nome] = turma
        print(f"  ✓ {nome} - Informática")
    
    return turmas


def criar_disciplinas():
    print("\n📚 CRIANDO DISCIPLINAS...")
    disciplinas = {}
    
    disciplinas_lista = [
        # Comuns
        'Matemática', 'Português', 'Inglês', 'Educação Física',
        # Eletrónica
        'Física', 'Química', 'Eletrónica Geral', 'Microcontroladores', 'Sistemas Digitais',
        # Informática
        'Programação', 'Redes de Computadores', 'Bases de Dados', 'Desenvolvimento Web'
    ]
    
    for nome in disciplinas_lista:
        disc, _ = Disciplina.objects.get_or_create(nome=nome)
        disciplinas[nome] = disc
        print(f"  ✓ {nome}")
    
    return disciplinas


def associar_disciplinas_turmas(turmas, disciplinas):
    print("\n🔗 ASSOCIANDO DISCIPLINAS ÀS TURMAS...")
    
    # Disciplinas comuns a todas
    comuns = ['Matemática', 'Português', 'Inglês', 'Educação Física']
    
    for turma_nome, turma in turmas.items():
        # Adicionar disciplinas comuns
        for disc in comuns:
            DisciplinaTurma.objects.get_or_create(
                disciplina=disciplinas[disc], turma=turma
            )
        
        # Disciplinas específicas por curso
        if turma.curso == 'eletronica':
            especificas = ['Física', 'Química', 'Eletrónica Geral', 'Microcontroladores', 'Sistemas Digitais']
        else:
            especificas = ['Programação', 'Redes de Computadores', 'Bases de Dados', 'Desenvolvimento Web']
        
        for disc in especificas:
            DisciplinaTurma.objects.get_or_create(
                disciplina=disciplinas[disc], turma=turma
            )
    
    print("  ✓ Associações criadas para todas as turmas")


def criar_usuarios_e_perfis(turmas, disciplinas):
    print("\n👥 CRIANDO USUÁRIOS E PERFIS...")
    
    # 1. ADMIN
    admin, _ = Usuario.objects.get_or_create(
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
    print("  ✓ Admin criado (admin@colegioarvore.ao / admin123)")
    
    # 2. PROFESSORES
    professores = [
        {'nome': 'João', 'sobrenome': 'Silva', 'email': 'joao.silva@colegioarvore.ao', 'disciplina': 'Matemática', 'turmas': ['ET10A', 'ET10B', 'INF10A', 'INF10B']},
        {'nome': 'Maria', 'sobrenome': 'Santos', 'email': 'maria.santos@colegioarvore.ao', 'disciplina': 'Português', 'turmas': ['ET10A', 'ET10B', 'INF10A', 'INF10B']},
        {'nome': 'Carlos', 'sobrenome': 'Pereira', 'email': 'carlos.pereira@colegioarvore.ao', 'disciplina': 'Programação', 'turmas': ['INF10A', 'INF10B', 'INF11A', 'INF11B']},
        {'nome': 'Ana', 'sobrenome': 'Oliveira', 'email': 'ana.oliveira@colegioarvore.ao', 'disciplina': 'Eletrónica Geral', 'turmas': ['ET10A', 'ET10B', 'ET11A', 'ET11B']},
        {'nome': 'Pedro', 'sobrenome': 'Costa', 'email': 'pedro.costa@colegioarvore.ao', 'disciplina': 'Física', 'turmas': ['ET10A', 'ET11A', 'ET12A']},
    ]
    
    for p in professores:
        usuario, created = Usuario.objects.get_or_create(
            username=f"prof_{p['nome'].lower()}",
            defaults={
                'email': p['email'],
                'password': make_password('professor123'),
                'first_name': p['nome'],
                'last_name': p['sobrenome'],
                'tipo': 'professor',
                'is_professor': True
            }
        )
        
        perfil, _ = PerfilProfessor.objects.get_or_create(
            usuario=usuario,
            defaults={'disciplina': disciplinas[p['disciplina']]}
        )
        
        for turma_nome in p['turmas']:
            if turma_nome in turmas:
                perfil.turmas.add(turmas[turma_nome])
        
        print(f"  ✓ Professor {p['nome']} {p['sobrenome']} - {p['disciplina']}")
    
    # 3. DIRETORES DE TURMA
    diretores = [
        {'turma': 'ET10A', 'nome': 'Ricardo', 'sobrenome': 'Almeida'},
        {'turma': 'INF10A', 'nome': 'Patrícia', 'sobrenome': 'Lima'},
        {'turma': 'ET11A', 'nome': 'Fernando', 'sobrenome': 'Rocha'},
        {'turma': 'INF11A', 'nome': 'Cristina', 'sobrenome': 'Mendes'},
    ]
    
    for d in diretores:
        username = f"diretor_{d['turma'].lower()}"
        usuario, created = Usuario.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@colegioarvore.ao",
                'password': make_password('diretor123'),
                'first_name': d['nome'],
                'last_name': d['sobrenome'],
                'tipo': 'diretor_turma',
                'is_diretor_turma': True,
                'turma_vinculada': turmas[d['turma']]
            }
        )
        print(f"  ✓ Diretor {d['nome']} {d['sobrenome']} - Turma {d['turma']}")
    
    # 4. COORDENADORES
    coord_cultural, _ = Usuario.objects.get_or_create(
        username='coord_cultural',
        defaults={
            'email': 'cultural@colegioarvore.ao',
            'password': make_password('coordenador123'),
            'first_name': 'Coordenador',
            'last_name': 'Cultural',
            'tipo': 'coordenador',
            'is_coordenador_cultural': True
        }
    )
    print("  ✓ Coordenador Cultural criado (cultural@colegioarvore.ao / coordenador123)")
    
    coord_ciencia, _ = Usuario.objects.get_or_create(
        username='coord_ciencia',
        defaults={
            'email': 'ciencia@colegioarvore.ao',
            'password': make_password('coordenador123'),
            'first_name': 'Coordenador',
            'last_name': 'Ciência',
            'tipo': 'coordenador',
            'is_coordenador_ciencia': True
        }
    )
    print("  ✓ Coordenador Ciência criado (ciencia@colegioarvore.ao / coordenador123)")


def criar_alunos(turmas):
    print("\n🎓 CRIANDO ALUNOS...")
    
    nomes = ['João', 'Maria', 'Pedro', 'Ana', 'Lucas', 'Beatriz', 'Rafael', 'Camila', 'Gabriel', 'Juliana', 
             'Bruno', 'Fernanda', 'Thiago', 'Larissa', 'Felipe', 'Letícia', 'Gustavo', 'Amanda', 'Daniel', 'Vanessa']
    sobrenomes = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima', 'Gomes',
                  'Ribeiro', 'Martins', 'Carvalho', 'Almeida', 'Costa', 'Nascimento', 'Araújo', 'Moura', 'Castro', 'Ramos']
    
    alunos_por_turma = {
        'ET10A': 8, 'ET10B': 7, 'INF10A': 8, 'INF10B': 7,
        'ET11A': 6, 'ET11B': 6, 'INF11A': 6, 'INF11B': 6,
        'ET12A': 5, 'ET12B': 5, 'INF12A': 5, 'INF12B': 5,
    }
    
    aluno_index = 0
    total_alunos = 0
    
    for turma_nome, quantidade in alunos_por_turma.items():
        turma = turmas.get(turma_nome)
        if not turma:
            continue
        
        for i in range(quantidade):
            nome = nomes[(aluno_index + i) % len(nomes)]
            sobrenome = sobrenomes[(aluno_index + i) % len(sobrenomes)]
            ano = turma_nome[:4]
            numero = f"{ano}{1000 + aluno_index + i}"
            username = f"aluno_{numero}"
            
            usuario, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@aluno.colegioarvore.ao",
                    'password': make_password(numero),
                    'first_name': nome,
                    'last_name': sobrenome,
                    'tipo': 'aluno'
                }
            )
            
            if created:
                saldo_inicial = random.randint(50, 300)
                PerfilAluno.objects.create(
                    usuario=usuario,
                    numero_processo=numero,
                    turma=turma,
                    saldo_pontos=saldo_inicial
                )
                total_alunos += 1
        
        print(f"  ✓ Turma {turma_nome}: {quantidade} alunos")
        aluno_index += quantidade
    
    print(f"\n  📊 Total de alunos criados: {total_alunos}")


def criar_beneficios():
    print("\n🎁 CRIANDO BENEFÍCIOS...")
    
    beneficios = [
        {'nome': 'Café da Manhã Grátis', 'descricao': 'Café da manhã completo no refeitório', 'custo': 50, 'categoria': 'premios'},
        {'nome': 'Desconto 10% na Cantina', 'descricao': '10% de desconto em todas as compras na cantina por 1 semana', 'custo': 100, 'categoria': 'academico'},
        {'nome': 'Acesso Wi-Fi Premium (7 dias)', 'descricao': 'Acesso à internet de alta velocidade', 'custo': 150, 'categoria': 'tecnologia'},
        {'nome': 'Camiseta Oficial do CAF', 'descricao': 'Camiseta exclusiva do colégio', 'custo': 200, 'categoria': 'premios'},
        {'nome': 'Ingresso Cinema', 'descricao': 'Ingresso para sessão de cinema', 'custo': 180, 'categoria': 'eventos'},
        {'nome': 'Kit Material Escolar', 'descricao': 'Cadernos, canetas e lápis', 'custo': 250, 'categoria': 'academico'},
        {'nome': 'Excursão Cultural', 'descricao': 'Participação em excursão com toda a turma', 'custo': 400, 'categoria': 'eventos'},
        {'nome': 'Troféu de Mérito', 'descricao': 'Troféu de reconhecimento', 'custo': 350, 'categoria': 'premios'},
    ]
    
    for b in beneficios:
        beneficio, created = Beneficio.objects.get_or_create(
            nome=b['nome'],
            defaults={
                'descricao': b['descricao'],
                'custo_pontos': b['custo'],
                'categoria': b['categoria'],
                'disponivel': True,
                'estoque': 20
            }
        )
        if created:
            print(f"  ✓ {b['nome']} - {b['custo']} pts")
    
    return Beneficio.objects.all()


def criar_atividades_curriculares(turmas, disciplinas):
    print("\n📝 CRIANDO ATIVIDADES CURRICULARES...")
    
    hoje = datetime.now().date()
    atividades_criadas = []
    
    # Atividade 1: Mini-teste de Matemática
    try:
        prof_joao = Usuario.objects.get(username='prof_joao')
    except Usuario.DoesNotExist:
        prof_joao = Usuario.objects.filter(is_professor=True).first()
    
    disciplina = disciplinas['Matemática']
    
    for turma_nome in ['ET10A', 'ET10B', 'INF10A', 'INF10B']:
        turma = turmas[turma_nome]
        
        atividade = Atividade.objects.create(
            nome='Mini-teste de Matemática',
            descricao='Teste rápido sobre equações do 1º grau',
            criterios_avaliacao='Cálculo correto\nDemonstração dos passos\nOrganização',
            max_pontos_por_aluno=50,
            disciplina=disciplina,
            criado_por=prof_joao,
            finalizada=False
        )
        atividade.turmas.add(turma)
        
        CriterioAtividade.objects.create(atividade=atividade, nome='Resposta correta', pontos=30)
        CriterioAtividade.objects.create(atividade=atividade, nome='Demonstração dos cálculos', pontos=15)
        CriterioAtividade.objects.create(atividade=atividade, nome='Organização', pontos=5)
        
        atividades_criadas.append(atividade)
        print(f"  ✓ Mini-teste de Matemática - Turma {turma_nome}")
    
    # Atividade 2: Trabalho de Programação
    try:
        prof_carlos = Usuario.objects.get(username='prof_carlos')
    except Usuario.DoesNotExist:
        prof_carlos = Usuario.objects.filter(is_professor=True).first()
    
    disciplina = disciplinas['Programação']
    
    for turma_nome in ['INF10A', 'INF10B', 'INF11A', 'INF11B']:
        turma = turmas[turma_nome]
        
        atividade = Atividade.objects.create(
            nome='Projeto: Calculadora em Python',
            descricao='Desenvolver uma calculadora com operações básicas',
            criterios_avaliacao='Funcionalidade completa\nInterface amigável\nCódigo organizado',
            max_pontos_por_aluno=100,
            disciplina=disciplina,
            criado_por=prof_carlos,
            finalizada=False
        )
        atividade.turmas.add(turma)
        
        CriterioAtividade.objects.create(atividade=atividade, nome='Funcionalidades completas', pontos=50)
        CriterioAtividade.objects.create(atividade=atividade, nome='Qualidade do código', pontos=30)
        CriterioAtividade.objects.create(atividade=atividade, nome='Documentação', pontos=20)
        
        atividades_criadas.append(atividade)
        print(f"  ✓ Projeto Python - Turma {turma_nome}")
    
    # Atividade 3: Experiência de Física
    try:
        prof_pedro = Usuario.objects.get(username='prof_pedro')
    except Usuario.DoesNotExist:
        prof_pedro = Usuario.objects.filter(is_professor=True).first()
    
    disciplina = disciplinas['Física']
    
    for turma_nome in ['ET10A', 'ET11A', 'ET12A']:
        turma = turmas[turma_nome]
        
        atividade = Atividade.objects.create(
            nome='Experiência: Movimento Uniforme',
            descricao='Realizar experiência prática sobre movimento retilíneo',
            criterios_avaliacao='Montagem do experimento\nColeta de dados\nAnálise dos resultados',
            max_pontos_por_aluno=80,
            disciplina=disciplina,
            criado_por=prof_pedro,
            finalizada=False
        )
        atividade.turmas.add(turma)
        
        CriterioAtividade.objects.create(atividade=atividade, nome='Montagem correta', pontos=20)
        CriterioAtividade.objects.create(atividade=atividade, nome='Dados precisos', pontos=30)
        CriterioAtividade.objects.create(atividade=atividade, nome='Análise completa', pontos=30)
        
        atividades_criadas.append(atividade)
        print(f"  ✓ Experiência de Física - Turma {turma_nome}")
    
    return atividades_criadas


def criar_atividades_extra_curriculares(turmas):
    print("\n🎨 CRIANDO ATIVIDADES EXTRA-CURRICULARES...")
    
    try:
        coord_cultural = Usuario.objects.get(username='coord_cultural')
    except Usuario.DoesNotExist:
        coord_cultural = Usuario.objects.filter(is_coordenador_cultural=True).first()
    
    try:
        coord_ciencia = Usuario.objects.get(username='coord_ciencia')
    except Usuario.DoesNotExist:
        coord_ciencia = Usuario.objects.filter(is_coordenador_ciencia=True).first()
    
    atividades_criadas = []
    
    # Atividade Cultural - Festival de Talentos
    atividade = Atividade.objects.create(
        nome='Festival de Talentos 2024',
        descricao='Evento cultural com apresentações artísticas',
        criterios_avaliacao='Originalidade\nTécnica\nApresentação',
        max_pontos_por_aluno=200,
        tipo_atividade='cultural',
        criado_por=coord_cultural,
        finalizada=False,
        todos_cursos=True
    )
    for turma in list(turmas.values())[:8]:
        atividade.turmas.add(turma)
    
    CriterioAtividade.objects.create(atividade=atividade, nome='Participação', pontos=50)
    CriterioAtividade.objects.create(atividade=atividade, nome='Qualidade da apresentação', pontos=100)
    CriterioAtividade.objects.create(atividade=atividade, nome='Originalidade', pontos=50)
    atividades_criadas.append(atividade)
    print(f"  ✓ Festival de Talentos 2024 (Cultural)")
    
    # Atividade Cultural - Exposição de Artes
    atividade = Atividade.objects.create(
        nome='Exposição de Artes Plásticas',
        descricao='Exposição de trabalhos artísticos dos alunos',
        criterios_avaliacao='Criatividade\nTécnica\nAcabamento',
        max_pontos_por_aluno=150,
        tipo_atividade='cultural',
        criado_por=coord_cultural,
        finalizada=False,
        todos_cursos=False,
        cursos_associados='eletronica'
    )
    for turma in [t for t in turmas.values() if t.curso == 'eletronica'][:4]:
        atividade.turmas.add(turma)
    
    CriterioAtividade.objects.create(atividade=atividade, nome='Criatividade', pontos=60)
    CriterioAtividade.objects.create(atividade=atividade, nome='Técnica', pontos=50)
    CriterioAtividade.objects.create(atividade=atividade, nome='Apresentação', pontos=40)
    atividades_criadas.append(atividade)
    print(f"  ✓ Exposição de Artes Plásticas (Cultural)")
    
    # Atividade Científica - Feira de Ciências
    atividade = Atividade.objects.create(
        nome='Feira de Ciências e Tecnologia',
        descricao='Apresentação de projetos científicos inovadores',
        criterios_avaliacao='Pesquisa\nInovação\nApresentação',
        max_pontos_por_aluno=250,
        tipo_atividade='ciencia_tecnologia',
        criado_por=coord_ciencia,
        finalizada=False,
        todos_cursos=True
    )
    for turma in list(turmas.values())[:8]:
        atividade.turmas.add(turma)
    
    CriterioAtividade.objects.create(atividade=atividade, nome='Pesquisa', pontos=100)
    CriterioAtividade.objects.create(atividade=atividade, nome='Inovação', pontos=80)
    CriterioAtividade.objects.create(atividade=atividade, nome='Apresentação', pontos=70)
    atividades_criadas.append(atividade)
    print(f"  ✓ Feira de Ciências e Tecnologia (Ciência)")
    
    # Atividade Científica - Workshop de Robótica
    atividade = Atividade.objects.create(
        nome='Workshop de Robótica',
        descricao='Oficina prática de construção de robôs',
        criterios_avaliacao='Participação\nProjeto final\nTrabalho em equipe',
        max_pontos_por_aluno=180,
        tipo_atividade='ciencia_tecnologia',
        criado_por=coord_ciencia,
        finalizada=False,
        todos_cursos=False,
        cursos_associados='informatica'
    )
    for turma in [t for t in turmas.values() if t.curso == 'informatica'][:4]:
        atividade.turmas.add(turma)
    
    CriterioAtividade.objects.create(atividade=atividade, nome='Participação', pontos=50)
    CriterioAtividade.objects.create(atividade=atividade, nome='Projeto final', pontos=80)
    CriterioAtividade.objects.create(atividade=atividade, nome='Trabalho em equipe', pontos=50)
    atividades_criadas.append(atividade)
    print(f"  ✓ Workshop de Robótica (Ciência)")
    
    return atividades_criadas


def simular_resgates_beneficios():
    print("\n💰 SIMULANDO RESGATES DE BENEFÍCIOS...")
    
    alunos = PerfilAluno.objects.all()
    beneficios = Beneficio.objects.all()
    
    resgates_realizados = 0
    
    for aluno in alunos[:30]:
        if aluno.saldo_pontos > 100:
            num_resgates = random.randint(0, 2)
            beneficios_disponiveis = [b for b in beneficios if b.custo_pontos <= aluno.saldo_pontos]
            
            for _ in range(num_resgates):
                if beneficios_disponiveis:
                    beneficio = random.choice(beneficios_disponiveis)
                    
                    if aluno.saldo_pontos >= beneficio.custo_pontos:
                        aluno.saldo_pontos -= beneficio.custo_pontos
                        aluno.save()
                        
                        ResgateBeneficio.objects.create(
                            aluno=aluno,
                            beneficio=beneficio,
                            pontos_gastos=beneficio.custo_pontos,
                            status='confirmado'
                        )
                        
                        Transacao.objects.create(
                            aluno=aluno,
                            quantidade=-beneficio.custo_pontos,
                            tipo='resgate',
                            descricao=f'Resgate de {beneficio.nome}'
                        )
                        resgates_realizados += 1
    
    print(f"  ✓ {resgates_realizados} resgates de benefícios realizados")


def exibir_relatorio_final():
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL DA SIMULAÇÃO")
    print("=" * 70)
    
    print(f"\n🏫 INSTITUIÇÃO:")
    print(f"   Turmas: {Turma.objects.count()}")
    print(f"   Disciplinas: {Disciplina.objects.count()}")
    
    print(f"\n👥 USUÁRIOS:")
    print(f"   Professores: {Usuario.objects.filter(is_professor=True).count()}")
    print(f"   Diretores: {Usuario.objects.filter(is_diretor_turma=True).count()}")
    print(f"   Coordenadores: {Usuario.objects.filter(is_coordenador_cultural=True).count() + Usuario.objects.filter(is_coordenador_ciencia=True).count()}")
    print(f"   Alunos: {PerfilAluno.objects.count()}")
    
    total_pontos = sum(a.saldo_pontos for a in PerfilAluno.objects.all())
    print(f"\n💰 PONTUAÇÃO:")
    print(f"   Total de pontos em circulação: {total_pontos}")
    if PerfilAluno.objects.count() > 0:
        print(f"   Média por aluno: {total_pontos // PerfilAluno.objects.count()}")
    
    print(f"\n🎁 BENEFÍCIOS:")
    print(f"   Benefícios disponíveis: {Beneficio.objects.filter(disponivel=True).count()}")
    print(f"   Resgates realizados: {ResgateBeneficio.objects.count()}")
    
    print(f"\n📝 ATIVIDADES:")
    print(f"   Atividades curriculares: {Atividade.objects.filter(disciplina__isnull=False).count()}")
    print(f"   Atividades extra-curriculares: {Atividade.objects.filter(disciplina__isnull=True).count()}")
    
    print("\n" + "=" * 70)
    print("🔐 CREDENCIAIS DE ACESSO")
    print("=" * 70)
    
    print("\n👑 ADMIN:")
    print("   Email: admin@colegioarvore.ao")
    print("   Senha: admin123")
    
    print("\n👨‍🏫 PROFESSORES:")
    for prof in Usuario.objects.filter(is_professor=True)[:5]:
        print(f"   {prof.email} / professor123")
    
    print("\n👔 DIRETORES:")
    for diretor in Usuario.objects.filter(is_diretor_turma=True):
        print(f"   {diretor.email} / diretor123")
    
    print("\n🎭 COORDENADORES:")
    print("   cultural@colegioarvore.ao / coordenador123")
    print("   ciencia@colegioarvore.ao / coordenador123")
    
    print("\n🎓 ALUNOS (exemplos):")
    for aluno in PerfilAluno.objects.all()[:5]:
        print(f"   {aluno.usuario.email} / {aluno.numero_processo}")
    print("   ... e mais alunos")


def main():
    print("=" * 70)
    print("🚀 INICIANDO SIMULAÇÃO DE CENÁRIO REAL")
    print("=" * 70)
    
    # Limpar dados existentes
    print("\n⚠️  Limpando dados existentes...")
    Transacao.objects.all().delete()
    ResgateBeneficio.objects.all().delete()
    RegistroAtividadeAluno.objects.all().delete()
    GrupoAtividade.objects.all().delete()
    CriterioAtividade.objects.all().delete()
    Atividade.objects.all().delete()
    Beneficio.objects.all().delete()
    PerfilAluno.objects.all().delete()
    PerfilProfessor.objects.all().delete()
    DisciplinaTurma.objects.all().delete()
    Disciplina.objects.all().delete()
    Turma.objects.all().delete()
    Usuario.objects.exclude(is_superuser=True).delete()
    print("  ✓ Dados antigos removidos")
    
    # Executar criação
    turmas = criar_turmas()
    disciplinas = criar_disciplinas()
    associar_disciplinas_turmas(turmas, disciplinas)
    criar_usuarios_e_perfis(turmas, disciplinas)
    criar_alunos(turmas)
    criar_beneficios()
    criar_atividades_curriculares(turmas, disciplinas)
    criar_atividades_extra_curriculares(turmas)
    simular_resgates_beneficios()
    exibir_relatorio_final()
    
    print("\n" + "=" * 70)
    print("✅ SIMULAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print("\nPara iniciar o servidor:")
    print("  python manage.py runserver 0.0.0.0:8000")


if __name__ == '__main__':
    main()