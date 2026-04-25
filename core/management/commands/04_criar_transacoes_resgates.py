from django.core.management.base import BaseCommand
from core.models import (
    Atividade, PerfilAluno, Transacao, ResgateBeneficio,
    Beneficio, RegistroAtividadeAluno, CriterioAtividade,
    Usuario
)


class Command(BaseCommand):
    help = 'PASSO 4: Criar Transações e Resgates'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n🚀 PASSO 4: CRIANDO TRANSAÇÕES E RESGATES\n'))

        # =========================================================
        # 1. BUSCAR DEPENDÊNCIAS
        # =========================================================
        try:
            prof1 = Usuario.objects.get(username='professor.carlos')
            prof2 = Usuario.objects.get(username='professor.ana')
            
            atividade_cultural1 = Atividade.objects.get(nome='Feira de Ciências 2024')
            atividade_fisica = Atividade.objects.get(nome='Prova Trimestral de Física')
            atividade_matematica = Atividade.objects.get(nome='Trabalho de Estatística')
            atividade_ciencia2 = Atividade.objects.get(nome='Hackathon de Programação')
            
            # Buscar critérios
            criterio_fisica1 = CriterioAtividade.objects.get(atividade=atividade_fisica, nome='Resolução de Problemas')
            criterio_fisica2 = CriterioAtividade.objects.get(atividade=atividade_fisica, nome='Justificação Científica')
            
            # Buscar alunos
            alunos_12ea = PerfilAluno.objects.filter(turma__nome='12ª EA')
            alunos_12id = PerfilAluno.objects.filter(turma__nome='12ª ID')
            
            alunos_12ea_dict = {aluno.usuario.first_name: aluno for aluno in alunos_12ea}
            alunos_12id_dict = {aluno.usuario.first_name: aluno for aluno in alunos_12id}
            
            self.stdout.write('   ✅ Dependências encontradas')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ ERRO: {e}'))
            return

        # =========================================================
        # 2. TRANSAÇÕES DA FEIRA DE CIÊNCIAS
        # =========================================================
        self.stdout.write('\n💰 Criando transações da Feira de Ciências...')
        
        feira_pontos = [
            ('João', 80), ('Maria', 60), ('Pedro', 70), ('Ana', 90),
            ('Carlos', 85), ('Sofia', 75), ('Lucas', 65), ('Beatriz', 95),
        ]
        
        for nome, pontos in feira_pontos:
            aluno = alunos_12ea_dict.get(nome) or alunos_12id_dict.get(nome)
            if aluno:
                Transacao.objects.create(
                    aluno=aluno,
                    quantidade=pontos,
                    tipo='distribuicao',
                    descricao=f'Distribuição de pontos da actividade: Feira de Ciências 2024',
                    professor=prof1,
                    atividade=atividade_cultural1
                )
                aluno.saldo_pontos += pontos
                aluno.save()
                self.stdout.write(f'   ✅ {nome}: +{pontos} pts')
        
        self.stdout.write(f'   ✅ Total: {Transacao.objects.filter(atividade=atividade_cultural1).count()} transações')

        # =========================================================
        # 3. TRANSAÇÕES DA PROVA DE FÍSICA
        # =========================================================
        self.stdout.write('\n💰 Criando transações da Prova de Física...')
        
        fisica_pontos = [('João', 85), ('Maria', 90), ('Pedro', 70), ('Ana', 95)]
        
        for nome, pontos in fisica_pontos:
            aluno = alunos_12ea_dict.get(nome)
            if aluno:
                Transacao.objects.create(
                    aluno=aluno,
                    quantidade=pontos,
                    tipo='distribuicao',
                    descricao=f'Distribuição de pontos da actividade: Prova Trimestral de Física',
                    professor=prof1,
                    atividade=atividade_fisica
                )
                aluno.saldo_pontos += pontos
                aluno.save()
                self.stdout.write(f'   ✅ {nome}: +{pontos} pts')
        
        self.stdout.write(f'   ✅ Total: {Transacao.objects.filter(atividade=atividade_fisica).count()} transações')

        # =========================================================
        # 4. TRANSAÇÕES DO TRABALHO DE ESTATÍSTICA (com penalização)
        # =========================================================
        self.stdout.write('\n💰 Criando transações do Trabalho de Estatística...')
        
        matematica_registos = [
            ('Carlos', 'Recolha de Dados', 30),
            ('Carlos', 'Análise Estatística', 50),
            ('Sofia', 'Recolha de Dados', 30),
            ('Sofia', 'Análise Estatística', 50),
            ('Sofia', 'Apresentação', 20),
            ('Lucas', 'Recolha de Dados', 30),
            ('Lucas', 'Análise Estatística', 45),
            ('Lucas', 'Atraso na Entrega', -15),
            ('Beatriz', 'Recolha de Dados', 30),
            ('Beatriz', 'Análise Estatística', 50),
            ('Beatriz', 'Apresentação', 20),
        ]
        
        for nome, criterio_nome, pontos in matematica_registos:
            aluno = alunos_12id_dict.get(nome)
            if aluno:
                Transacao.objects.create(
                    aluno=aluno,
                    quantidade=pontos,
                    tipo='distribuicao',
                    descricao=f'Aplicação do critério "{criterio_nome}" na actividade: Trabalho de Estatística',
                    professor=prof2,
                    atividade=atividade_matematica
                )
                aluno.saldo_pontos += pontos
                aluno.save()
                self.stdout.write(f'   ✅ {nome}: {criterio_nome} ({pontos:+d} pts)')
        
        self.stdout.write(f'   ✅ Total: {Transacao.objects.filter(atividade=atividade_matematica).count()} transações')

        # =========================================================
        # 5. TRANSAÇÕES DO HACKATHON (distribuição parcial)
        # =========================================================
        self.stdout.write('\n💰 Criando transações do Hackathon...')
        
        hackathon_pontos = [('Carlos', 60), ('Sofia', 50), ('Lucas', 45), ('Beatriz', 45)]
        
        for nome, pontos in hackathon_pontos:
            aluno = alunos_12id_dict.get(nome)
            if aluno:
                Transacao.objects.create(
                    aluno=aluno,
                    quantidade=pontos,
                    tipo='distribuicao',
                    descricao=f'Distribuição parcial de pontos: Hackathon de Programação',
                    professor=prof1,
                    atividade=atividade_ciencia2
                )
                aluno.saldo_pontos += pontos
                aluno.save()
                self.stdout.write(f'   ✅ {nome}: +{pontos} pts')
        
        self.stdout.write(f'   ✅ Total: {Transacao.objects.filter(atividade=atividade_ciencia2).count()} transações')

        # =========================================================
        # 6. RESGATES DE BENEFÍCIOS
        # =========================================================
        self.stdout.write('\n🛒 Criando resgates de benefícios...')
        
        resgates = [
            ('João', 'Internet 7 dias', 300),
            ('Beatriz', 'Certificado de Mérito', 150),
            ('Carlos', 'Dia sem Uniforme', 80),
        ]
        
        for nome, beneficio_nome, custo in resgates:
            aluno = alunos_12ea_dict.get(nome) or alunos_12id_dict.get(nome)
            beneficio = Beneficio.objects.get(nome=beneficio_nome)
            
            if aluno and aluno.saldo_pontos >= custo:
                aluno.saldo_pontos -= custo
                aluno.save()
                ResgateBeneficio.objects.create(
                    aluno=aluno,
                    beneficio=beneficio,
                    pontos_gastos=custo,
                    status='confirmado'
                )
                Transacao.objects.create(
                    aluno=aluno,
                    quantidade=-custo,
                    tipo='resgate',
                    descricao=f'Resgate de {beneficio_nome}'
                )
                self.stdout.write(f'   ✅ {nome}: Resgatou {beneficio_nome} (-{custo} pts)')
        
        self.stdout.write(f'   ✅ Total: {ResgateBeneficio.objects.count()} resgates')

        # =========================================================
        # RESUMO FINAL
        # =========================================================
        self.stdout.write(self.style.SUCCESS('\n✅ PASSO 4 CONCLUÍDO COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS(f'   - Transações: {Transacao.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Resgates: {ResgateBeneficio.objects.count()}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 POPULAÇÃO COMPLETA!'))