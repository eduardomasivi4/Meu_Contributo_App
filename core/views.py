from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import qrcode
import json
from io import BytesIO
from django.conf import settings
import os
from .config import REDE_IP, PORTA
from .models import (
    Usuario,
    PerfilAluno, 
    Turma, 
    Atividade, 
    Beneficio, 
    Transacao, 
    ResgateBeneficio,
)

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
def loja(request):
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    beneficios_list = Beneficio.objects.filter(disponivel=True)
    
    print(f"DEBUG: {beneficios_list.count()} benefícios encontrados")  # Para debug
    
    context = {
        'beneficios': beneficios_list,
        'saldo': request.user.perfil_aluno.saldo_pontos,
        'nome': request.user.get_full_name() or request.user.username,
        'processo': request.user.perfil_aluno.numero_processo,
        'turma': request.user.perfil_aluno.turma.nome if request.user.perfil_aluno.turma else 'Sem turma',
    }
    return render(request, 'core/loja.html', context)

@csrf_exempt
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

@login_required
def historico(request):
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    transacoes = Transacao.objects.filter(aluno=request.user.perfil_aluno).order_by('-data')
    
    context = {
        'transacoes': transacoes,
        'nome': request.user.get_full_name() or request.user.username,
        'processo': request.user.perfil_aluno.numero_processo,
        'turma': request.user.perfil_aluno.turma.nome if request.user.perfil_aluno.turma else 'Sem turma',
        'curso': request.user.perfil_aluno.turma.get_curso_display() if request.user.perfil_aluno.turma else 'Sem curso',
        'saldo': request.user.perfil_aluno.saldo_pontos,
    }
    return render(request, 'core/historico.html', context)

@login_required
def gerar_comprovativo(request, transacao_id):
    """Gera PDF comprovativo para uma transação"""
    try:
        transacao = Transacao.objects.get(id=transacao_id, aluno=request.user.perfil_aluno)
    except Transacao.DoesNotExist:
        return HttpResponse('Transação não encontrada', status=404)
    
    aluno = request.user.perfil_aluno
    turma = aluno.turma
    curso_nome = turma.get_curso_display() if turma else 'Não definido'
    turma_nome = turma.nome if turma else 'Não definido'
    
    # Dados para o comprovativo
    dados_comprovativo = (
        f"O responsável pelo Meu Contributo App do CAF, João Zinga, "
        f"confirma que o(a) estudante {request.user.get_full_name() or request.user.username}, "
        f"estudante do curso de {curso_nome}, turma {turma_nome}, "
        f"converteu {abs(transacao.quantidade)} pontos para obter o benefício {transacao.descricao}."
    )
    
    # URL para o QR Code - usando IP do arquivo de configuração
    pdf_url = f"http://{REDE_IP}:{PORTA}/aluno/comprovativo/{transacao.id}/"
    
    # Criar resposta HTTP com PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comprovativo_{transacao.id}.pdf"'
    
    # Criar PDF
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Cores institucionais
    castanho = HexColor('#5C3A21')
    verde = HexColor('#2B7A4B')
    
    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo-caf.png')
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        pdf.drawImage(logo, (width - 60) / 2, height - 80, width=50, height=50, preserveAspectRatio=True)
    
    # Título
    pdf.setFont('Helvetica-Bold', 18)
    pdf.setFillColor(castanho)
    pdf.drawCentredString(width / 2, height - 120, "COLÉGIO ÁRVORE DA FELICIDADE")
    
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawCentredString(width / 2, height - 150, "COMPROVATIVO DE CONVERSÃO DE PONTOS")
    
    # Linha separadora
    pdf.setStrokeColor(verde)
    pdf.setLineWidth(2)
    pdf.line(50, height - 170, width - 50, height - 170)
    
    # Texto do comprovativo
    pdf.setFont('Helvetica', 12)
    pdf.setFillColor(castanho)
    
    # Quebrar texto em múltiplas linhas
    text_lines = []
    current_line = ""
    for word in dados_comprovativo.split():
        if len(current_line) + len(word) + 1 < 80:
            current_line += " " + word if current_line else word
        else:
            text_lines.append(current_line)
            current_line = word
    text_lines.append(current_line)
    
    y = height - 220
    for line in text_lines:
        pdf.drawString(50, y, line)
        y -= 25
    
    # Informações adicionais
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(50, y - 20, f"Data da transação: {transacao.data.strftime('%d/%m/%Y %H:%M')}")
    pdf.drawString(50, y - 45, f"Pontos convertidos: {abs(transacao.quantidade)}")
    pdf.drawString(50, y - 70, f"Benefício: {transacao.descricao}")
    
    # Assinatura
    y_assinatura = y - 130
    pdf.setFont('Helvetica', 10)
    pdf.drawString(50, y_assinatura, "_________________________________")
    pdf.drawString(80, y_assinatura - 10, "João Zinga")
    pdf.drawString(60, y_assinatura - 25, "Responsável pelo Meu Contributo App")
    
    # Gerar QR Code com a URL do PDF
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(pdf_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#5C3A21", back_color="white")
    
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)
    
    # Posicionar QR Code
    qr_size = 80
    pdf.drawImage(qr_reader, width - qr_size - 50, y_assinatura - 100, width=qr_size, height=qr_size)
    
    # Texto explicativo
    pdf.setFont('Helvetica', 8)
    pdf.setFillColor(castanho)
    pdf.drawString(width - qr_size - 45, y_assinatura - 110, "QR Code para download")
    pdf.drawString(width - qr_size - 55, y_assinatura - 120, "do comprovativo")
    
    pdf.save()
    return response


# ==================== PROFESSOR ====================

def login_professor(request):
    return render(request, 'core/login_professor.html')

@csrf_exempt
def verificar_credenciais_professor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', '')
        senha = data.get('senha', '')
        
        user = authenticate(request, username=email, password=senha)
        if not user:
            username = email.split('@')[0]
            user = authenticate(request, username=username, password=senha)
        
        if not user:
            return JsonResponse({'success': False, 'erro': 'Credenciais inválidas'})
        
        if not user.is_professor and not user.is_coordenador and not user.is_diretor_turma:
            return JsonResponse({'success': False, 'erro': 'Usuário não tem permissão'})
        
        auth_login(request, user)
        
        cargos = []
        if user.is_professor:
            cargos.append('professor')
        if user.is_coordenador:
            cargos.append('coordenador')
        if user.is_diretor_turma:
            cargos.append('diretor_turma')
        
        if len(cargos) == 1:
            if cargos[0] == 'professor':
                return JsonResponse({'success': True, 'redirect': '/professor/dashboard/'})
            elif cargos[0] == 'coordenador':
                return JsonResponse({'success': True, 'redirect': '/coordenador/dashboard/'})
            elif cargos[0] == 'diretor_turma':
                return JsonResponse({'success': True, 'redirect': '/diretor/dashboard/'})
        
        request.session['cargos_disponiveis'] = cargos
        return JsonResponse({'success': True, 'redirect': '/professor/selecionar-perfil/'})
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def processar_login_nao_diretor(request, user):
    """Processa login quando usuário escolhe 'Não sou diretor de turma'"""
    cargos = user.get_cargos()
    
    # Login do usuário
    login(request, user)
    
    # Se tem apenas 1 cargo, redireciona direto
    if len(cargos) == 1:
        cargo = cargos[0]
        if cargo == 'professor':
            return JsonResponse({'success': True, 'redirect': '/professor/dashboard/', 'direto': True})
        elif cargo == 'coordenador':
            return JsonResponse({'success': True, 'redirect': '/coordenador/dashboard/', 'direto': True})
        else:
            return JsonResponse({'success': False, 'erro': 'Cargo não reconhecido'})
    
    # Se tem múltiplos cargos, vai para tela de seleção
    else:
        # Salvar cargos na sessão
        request.session['cargos_disponiveis'] = cargos
        return JsonResponse({'success': True, 'redirect': '/professor/selecionar-perfil/', 'direto': False})

def processar_login_diretor(request, user, turma):
    """Processa login quando usuário escolhe uma turma (diretor de turma)"""
    cargos = user.get_cargos()
    
    # Verificar se o usuário é diretor de turma
    if not user.is_diretor_turma:
        return JsonResponse({'success': False, 'erro': 'Você não tem permissão de diretor de turma'})
    
    # Login do usuário
    login(request, user)
    
    # Salvar turma na sessão
    request.session['turma_selecionada'] = turma
    
    # Se tem apenas o cargo de diretor de turma, redireciona direto
    if len(cargos) == 1 and cargos[0] == 'diretor_turma':
        return JsonResponse({'success': True, 'redirect': '/diretor/dashboard/', 'direto': True})
    
    # Se tem múltiplos cargos (incluindo diretor), vai para tela de seleção
    else:
        request.session['cargos_disponiveis'] = cargos
        return JsonResponse({'success': True, 'redirect': '/professor/selecionar-perfil/', 'direto': False})

@csrf_exempt
def redirecionar_perfil(request):
    """Redireciona para o dashboard do perfil escolhido"""
    if request.method == 'POST':
        data = json.loads(request.body)
        perfil = data.get('perfil')
        
        if perfil == 'professor':
            return JsonResponse({'redirect': '/professor/dashboard/'})
        elif perfil == 'coordenador':
            return JsonResponse({'redirect': '/coordenador/dashboard/'})
        elif perfil == 'diretor_turma':
            return JsonResponse({'redirect': '/diretor/dashboard/'})
    
    return JsonResponse({'erro': 'Perfil inválido'}, status=400)

def selecionar_perfil(request):
    cargos = request.session.get('cargos_disponiveis', [])
    context = {
        'tem_professor': 'professor' in cargos,
        'tem_coordenador': 'coordenador' in cargos,
        'tem_diretor': 'diretor_turma' in cargos,
    }
    return render(request, 'core/selecionar_perfil.html', context)

@csrf_exempt
def redirecionar_perfil(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        perfil = data.get('perfil')
        if perfil == 'professor':
            return JsonResponse({'redirect': '/professor/dashboard/'})
        elif perfil == 'coordenador':
            return JsonResponse({'redirect': '/coordenador/dashboard/'})
        elif perfil == 'diretor_turma':
            return JsonResponse({'redirect': '/diretor/dashboard/'})
    return JsonResponse({'erro': 'Perfil inválido'}, status=400)

@login_required
def dashboard_professor(request):
    if not request.user.is_professor:
        return redirect('index')
    
    disciplinas_por_curso = {
        'eletronica': {'nome': 'Eletrónica e Telecomunicações', 'disciplinas': []},
        'informatica': {'nome': 'Informática', 'disciplinas': []},
        'comum': {'nome': 'Comum', 'disciplinas': []},
    }
    
    for dt in DisciplinaTurma.objects.select_related('disciplina', 'turma').all():
        disc = dt.disciplina
        turma = dt.turma
        curso = turma.curso
        
        if curso == 'eletronica':
            if disc not in disciplinas_por_curso['eletronica']['disciplinas']:
                disciplinas_por_curso['eletronica']['disciplinas'].append(disc)
        elif curso == 'informatica':
            if disc not in disciplinas_por_curso['informatica']['disciplinas']:
                disciplinas_por_curso['informatica']['disciplinas'].append(disc)
        else:
            if disc not in disciplinas_por_curso['comum']['disciplinas']:
                disciplinas_por_curso['comum']['disciplinas'].append(disc)
    
    context = {
        'disciplinas_por_curso': disciplinas_por_curso,
    }
    return render(request, 'core/dashboard_professor.html', context)

# Obter turmas de uma disciplina via AJAX
@login_required
def get_turmas_por_disciplina(request, disciplina_id):
    if not request.user.is_professor:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    turmas = Turma.objects.filter(disciplinas_relacionadas__disciplina=disciplina).distinct()
    
    data = [{'id': t.id, 'nome': t.nome, 'curso': t.get_curso_display()} for t in turmas]
    return JsonResponse({'turmas': data})

@login_required
def turma_detail(request, turma_id):
    if not request.user.is_professor:
        return redirect('index')
    
    turma = get_object_or_404(Turma, id=turma_id)
    disciplina_id = request.GET.get('disciplina_id')
    disciplina = get_object_or_404(Disciplina, id=disciplina_id) if disciplina_id else None
    
    alunos = turma.alunos.all().order_by('usuario__first_name')
    atividades = Atividade.objects.filter(
        disciplina=disciplina, turmas=turma
    ).order_by('-created_at') if disciplina else []
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'alunos': alunos,
        'atividades': atividades,
    }
    return render(request, 'core/turma_detail.html', context)

@login_required
def criar_atividade(request, turma_id):
    if not request.user.is_professor:
        return redirect('index')
    
    turma = get_object_or_404(Turma, id=turma_id)
    disciplina_id = request.GET.get('disciplina_id')
    disciplina = get_object_or_404(Disciplina, id=disciplina_id) if disciplina_id else None
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        criterios = request.POST.get('criterios')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')
        max_pontos = request.POST.get('max_pontos')
        tipo_turma = request.POST.get('tipo_turma')
        
        atividade = Atividade.objects.create(
            nome=nome,
            descricao=descricao,
            criterios_avaliacao=criterios,
            data_inicio=data_inicio,
            data_fim=data_fim,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            max_pontos_por_aluno=max_pontos,
            disciplina=disciplina,
        )
        
        if tipo_turma == 'unica':
            atividade.turmas.add(turma)
        else:
            turmas_ids = request.POST.getlist('turmas_multiplas')
            for tid in turmas_ids:
                atividade.turmas.add(Turma.objects.get(id=tid))
        
        request.session['atividade_criada'] = nome
        return redirect('dashboard_professor')
    
    todas_turmas = Turma.objects.all().order_by('curso', 'nome')
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'todas_turmas': todas_turmas,
    }
    return render(request, 'core/criar_atividade.html', context)

# Distribuir pontos
@login_required
def distribuir_pontos(request, atividade_id):
    if not request.user.is_professor:
        return redirect('index')
    
    atividade = get_object_or_404(Atividade, id=atividade_id)
    turma_id = request.GET.get('turma_id')
    turma = get_object_or_404(Turma, id=turma_id)
    alunos = turma.alunos.all().order_by('usuario__first_name')
    
    if request.method == 'POST':
        for aluno in alunos:
            pontos = request.POST.get(f'pontos_{aluno.id}')
            if pontos and int(pontos) > 0:
                if int(pontos) <= atividade.max_pontos_por_aluno:
                    aluno.saldo_pontos += int(pontos)
                    aluno.save()
                    Transacao.objects.create(
                        aluno=aluno,
                        quantidade=int(pontos),
                        tipo='distribuicao',
                        descricao=f'Distribuição de pontos da atividade: {atividade.nome}',
                        professor=request.user,
                        atividade=atividade
                    )
        return redirect('turma_detail', turma_id=turma.id)
    
    context = {
        'atividade': atividade,
        'turma': turma,
        'alunos': alunos,
    }
    return render(request, 'core/distribuir_pontos.html', context)


# ==================== DIRETOR DE TURMA ====================

def diretor_turma(request):
    return render(request, 'core/diretor_turma.html')


# ==================== COORDENADOR DE ATIVIDADES ====================

def coordenador_atividades(request):
    return render(request, 'core/coordenador_atividades.html')
