from django.core.management.base import BaseCommand
from core.models import Turma, Disciplina, DisciplinaTurma


class Command(BaseCommand):
    help = 'PASSO 1: Criar Turmas e Disciplinas'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n🚀 PASSO 1: CRIANDO TURMAS E DISCIPLINAS\n'))

        # =========================================================
        # 1. TURMAS
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
            turma, created = Turma.objects.get_or_create(nome=nome, defaults={'curso': curso, 'ano': ano})
            turmas[nome] = turma
            if created:
                self.stdout.write(f'   ✅ Criada turma: {nome}')
            else:
                self.stdout.write(f'   ⚠️ Turma já existia: {nome}')
        
        self.stdout.write(self.style.SUCCESS(f'   ✅ Total: {len(turmas)} turmas\n'))

        # =========================================================
        # 2. DISCIPLINAS
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
            return disc

        def associar_disciplina_comum(nome, anos):
            disc, _ = Disciplina.objects.get_or_create(nome=nome)
            for ano in anos:
                for turma in turmas.values():
                    if turma.ano == ano:
                        DisciplinaTurma.objects.get_or_create(disciplina=disc, turma=turma)
            return disc

        for nome, anos in disc_informatica.items():
            associar_disciplina(nome, 'informatica', anos)
            self.stdout.write(f'   ✅ Disciplina Informática: {nome}')
        
        for nome, anos in disc_eletronica.items():
            associar_disciplina(nome, 'eletronica', anos)
            self.stdout.write(f'   ✅ Disciplina Eletrónica: {nome}')
        
        for nome, anos in disc_comuns.items():
            associar_disciplina_comum(nome, anos)
            self.stdout.write(f'   ✅ Disciplina Comum: {nome}')
        
        self.stdout.write(self.style.SUCCESS(f'\n   ✅ Total: {Disciplina.objects.count()} disciplinas\n'))
        
        self.stdout.write(self.style.SUCCESS('✅ PASSO 1 CONCLUÍDO COM SUCESSO!\n'))