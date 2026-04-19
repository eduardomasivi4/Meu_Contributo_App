from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import PerfilAluno, Atividade, Inscricao, Beneficio, ResgateBeneficio, Transacao


def index(request):
    return render(request, 'core/index.html')


# ==================== ALUNO ====================

def login_aluno(request):
    return render(request, 'core/login_aluno.html')

def verificar_processo(request):
    """API para verificar se o número de processo existe"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        processo = data.get('processo')
        
        try:
            aluno = PerfilAluno.objects.get(numero_processo=processo)
            return JsonResponse({
                'existe': True,
                'nome': aluno.usuario.get_full_name() or aluno.usuario.username,
                'processo': aluno.numero_processo
            })
        except PerfilAluno.DoesNotExist:
            return JsonResponse({'existe': False, 'erro': 'Número de processo não encontrado'})
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def validar_senha(request):
    """API para validar a senha do aluno"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        processo = data.get('processo')
        senha = data.get('senha')
        
        try:
            aluno = PerfilAluno.objects.get(numero_processo=processo)
            user = aluno.usuario
            if user.check_password(senha):
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect': '/aluno/dashboard/'
                })
            else:
                return JsonResponse({'success': False, 'erro': 'Senha incorreta'})
        except PerfilAluno.DoesNotExist:
            return JsonResponse({'success': False, 'erro': 'Aluno não encontrado'})
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

@login_required
def dashboard_aluno(request):
    # Verificar se o usuário é do tipo aluno
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    perfil = request.user.perfil_aluno
    context = {
        'aluno': perfil,
        'nome': request.user.get_full_name() or request.user.username,
        'processo': perfil.numero_processo,
        'saldo': perfil.saldo_pontos,
        'turma': perfil.turma.nome if perfil.turma else 'Sem turma',
    }
    return render(request, 'core/dashboard_aluno.html', context)

@login_required
def atividades(request):
    # Verificar se o usuário é do tipo aluno
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    # Buscar todas as atividades
    atividades_list = Atividade.objects.all().order_by('data', 'hora_inicio')
    
    context = {
        'atividades': atividades_list,
    }
    return render(request, 'core/atividades.html', context)

@login_required
def loja(request):
    # Verificar se o usuário é do tipo aluno
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    beneficios_list = Beneficio.objects.filter(disponivel=True)
    context = {
        'beneficios': beneficios_list,
        'saldo': request.user.perfil_aluno.saldo_pontos
    }
    return render(request, 'core/loja.html', context)

@login_required
def api_inscrever_atividade(request, atividade_id):
    """API para inscrever aluno em atividade"""
    if request.user.tipo != 'aluno':
        return JsonResponse({'success': False, 'erro': 'Acesso não autorizado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    try:
        atividade = Atividade.objects.get(id=atividade_id)
        aluno = request.user.perfil_aluno
        
        if Inscricao.objects.filter(aluno=aluno, atividade=atividade).exists():
            return JsonResponse({'success': False, 'erro': 'Já inscrito nesta atividade'})
        
        Inscricao.objects.create(
            aluno=aluno,
            atividade=atividade,
            status='confirmada'
        )
        
        return JsonResponse({'success': True, 'mensagem': 'Inscrição realizada com sucesso!'})
    except Atividade.DoesNotExist:
        return JsonResponse({'success': False, 'erro': 'Atividade não encontrada'})

@login_required
def api_resgatar_beneficio(request, beneficio_id):
    """API para resgatar benefício"""
    if request.user.tipo != 'aluno':
        return JsonResponse({'success': False, 'erro': 'Acesso não autorizado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    try:
        beneficio = Beneficio.objects.get(id=beneficio_id)
        aluno = request.user.perfil_aluno
        
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
            
            return JsonResponse({'success': True, 'novo_saldo': aluno.saldo_pontos})
        else:
            return JsonResponse({'success': False, 'erro': 'Saldo insuficiente'})
    except Beneficio.DoesNotExist:
        return JsonResponse({'success': False, 'erro': 'Benefício não encontrado'})


# ==================== PROFESSOR (placeholder) ====================

def login_professor(request):
    return render(request, 'core/login_professor.html')

def selecionar_perfil(request):
    return render(request, 'core/selecionar_perfil.html')

def dashboard_professor(request):
    return render(request, 'core/dashboard_professor.html')

def diretor_turma(request):
    return render(request, 'core/diretor_turma.html')

def coordenador_atividades(request):
    return render(request, 'core/coordenador_atividades.html')
    return render(request, 'core/coordenador_atividades.html')