from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
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
from django.utils import timezone
from .models import (
    Usuario, PerfilAluno, Turma, Disciplina, DisciplinaTurma,
    Atividade, Beneficio, Transacao, ResgateBeneficio,
    PerfilProfessor, PerfilDiretorTurma, PerfilCoordenador
)

def index(request):
    return render(request, 'core/index.html')


# ==================== ALUNO ====================

def login_aluno(request):
    return render(request, 'core/login_aluno.html')

def verificar_processo(request):
    """API para verificar se o número de processo existe"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            processo = data.get('processo')
            
            aluno = PerfilAluno.objects.get(numero_processo=processo)
            return JsonResponse({
                'existe': True,
                'nome': aluno.usuario.get_full_name() or aluno.usuario.username,
                'processo': aluno.numero_processo
            })
        except PerfilAluno.DoesNotExist:
            return JsonResponse({'existe': False, 'erro': 'Número de processo não encontrado'})
        except json.JSONDecodeError:
            return JsonResponse({'existe': False, 'erro': 'Requisição inválida'}, status=400)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def validar_senha(request):
    """API para validar a senha do aluno"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            processo = data.get('processo')
            senha = data.get('senha')
            
            aluno = PerfilAluno.objects.get(numero_processo=processo)
            user = aluno.usuario
            if user.check_password(senha):
                auth_login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect': reverse('dashboard_aluno')
                })
            else:
                return JsonResponse({'success': False, 'erro': 'Senha incorreta'})
        except PerfilAluno.DoesNotExist:
            return JsonResponse({'success': False, 'erro': 'Aluno não encontrado'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'erro': 'Requisição inválida'}, status=400)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

@login_required
def dashboard_aluno(request):
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    perfil = request.user.perfil_aluno
    context = {
        'aluno': perfil,
        'nome': request.user.get_full_name() or request.user.username,
        'processo': perfil.numero_processo,
        'saldo': perfil.saldo_pontos,
        'turma': perfil.get_turma_nome(),
    }
    return render(request, 'core/dashboard_aluno.html', context)

@login_required
def atividades(request):
    """Exibe lista de atividades (curriculares e extra-curriculares) com filtros"""
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    print("DEBUG: Entrou na view atividades")  # Debug
    
    # Buscar atividades curriculares (com disciplina associada)
    atividades_curriculares = Atividade.objects.filter(
        disciplina__isnull=False
    ).exclude(disciplina=None).order_by('disciplina__nome', 'data_inicio')
    
    print(f"DEBUG: Atividades curriculares encontradas: {atividades_curriculares.count()}")  # Debug
    
    # Buscar atividades extra-curriculares
    atividades_extra = Atividade.objects.filter(
        disciplina__isnull=True
    ).exclude(tipo_atividade=None).order_by('-created_at')
    
    print(f"DEBUG: Atividades extra encontradas: {atividades_extra.count()}")  # Debug
    
    # Buscar disciplinas distintas
    disciplinas = Disciplina.objects.filter(
        atividades__isnull=False
    ).distinct().order_by('nome')
    
    print(f"DEBUG: Disciplinas encontradas: {disciplinas.count()}")  # Debug
    
    context = {
        'atividades_curriculares': atividades_curriculares,
        'atividades_extra': atividades_extra,
        'disciplinas': disciplinas,
        'nome': request.user.get_full_name() or request.user.username,
        'processo': request.user.perfil_aluno.numero_processo,
        'turma': request.user.perfil_aluno.get_turma_nome(),
        'saldo': request.user.perfil_aluno.saldo_pontos,
    }
    return render(request, 'core/atividades.html', context)

@login_required
def loja(request):
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    beneficios_list = Beneficio.objects.filter(disponivel=True)
    context = {
        'beneficios': beneficios_list,
        'saldo': request.user.perfil_aluno.saldo_pontos,
        'nome': request.user.get_full_name() or request.user.username,
        'processo': request.user.perfil_aluno.numero_processo,
        'turma': request.user.perfil_aluno.get_turma_nome(),
    }
    return render(request, 'core/loja.html', context)

@csrf_exempt
@login_required
def api_resgatar_beneficio(request, beneficio_id):
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
    perfil = request.user.perfil_aluno
    
    context = {
        'transacoes': transacoes,
        'nome': request.user.get_full_name() or request.user.username,
        'processo': perfil.numero_processo,
        'turma': perfil.get_turma_nome(),
        'curso': perfil.get_curso_display(),
        'saldo': perfil.saldo_pontos,
    }
    return render(request, 'core/historico.html', context)

@login_required
def gerar_comprovativo(request, transacao_id):
    try:
        transacao = Transacao.objects.get(id=transacao_id, aluno=request.user.perfil_aluno)
    except Transacao.DoesNotExist:
        return HttpResponse('Transação não encontrada', status=404)
    
    aluno = request.user.perfil_aluno
    turma = aluno.turma
    curso_nome = turma.get_curso_display() if turma else 'Não definido'
    turma_nome = turma.nome if turma else 'Não definido'
    
    dados_comprovativo = (
        f"O responsável pelo Meu Contributo App do CAF, João Zinga, "
        f"confirma que o(a) estudante {request.user.get_full_name() or request.user.username}, "
        f"estudante do curso de {curso_nome}, turma {turma_nome}, "
        f"converteu {abs(transacao.quantidade)} pontos para obter o benefício {transacao.descricao}."
    )
    
    pdf_url = f"http://{REDE_IP}:{PORTA}{reverse('gerar_comprovativo', args=[transacao.id])}"
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comprovativo_{transacao.id}.pdf"'
    
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    castanho = HexColor('#5C3A21')
    verde = HexColor('#2B7A4B')
    
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo-caf.png')
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        pdf.drawImage(logo, (width - 60) / 2, height - 80, width=50, height=50, preserveAspectRatio=True)
    
    pdf.setFont('Helvetica-Bold', 18)
    pdf.setFillColor(castanho)
    pdf.drawCentredString(width / 2, height - 120, "COLÉGIO ÁRVORE DA FELICIDADE")
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawCentredString(width / 2, height - 150, "COMPROVATIVO DE CONVERSÃO DE PONTOS")
    pdf.setStrokeColor(verde)
    pdf.setLineWidth(2)
    pdf.line(50, height - 170, width - 50, height - 170)
    
    pdf.setFont('Helvetica', 12)
    pdf.setFillColor(castanho)
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
    
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(50, y - 20, f"Data da transação: {transacao.data.strftime('%d/%m/%Y %H:%M')}")
    pdf.drawString(50, y - 45, f"Pontos convertidos: {abs(transacao.quantidade)}")
    pdf.drawString(50, y - 70, f"Benefício: {transacao.descricao}")
    
    y_assinatura = y - 130
    pdf.setFont('Helvetica', 10)
    pdf.drawString(50, y_assinatura, "_________________________________")
    pdf.drawString(80, y_assinatura - 10, "João Zinga")
    pdf.drawString(60, y_assinatura - 25, "Responsável pelo Meu Contributo App")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(pdf_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#5C3A21", back_color="white")
    
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)
    
    qr_size = 80
    pdf.drawImage(qr_reader, width - qr_size - 50, y_assinatura - 100, width=qr_size, height=qr_size)
    pdf.setFont('Helvetica', 8)
    pdf.drawString(width - qr_size - 45, y_assinatura - 110, "QR Code para download")
    pdf.drawString(width - qr_size - 55, y_assinatura - 120, "do comprovativo")
    
    pdf.save()
    return response



# ==================== PROFESSOR ====================

def login_professor(request):
    return render(request, 'core/login_professor.html')

@csrf_exempt
def verificar_credenciais_professor(request):
    """API para verificar credenciais de professores, coordenadores e diretores"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '')
            senha = data.get('senha', '')
            
            print(f"🔍 DEBUG: Tentativa login - Email: {email}")
            
            # Buscar usuário pelo email primeiro
            try:
                usuario = Usuario.objects.get(email=email)
                print(f"🔍 DEBUG: Usuário encontrado: {usuario.username}")
            except Usuario.DoesNotExist:
                print(f"🔍 DEBUG: Email não encontrado: {email}")
                return JsonResponse({'success': False, 'erro': 'Email não encontrado'})
            
            # Autenticar com o username encontrado
            user = authenticate(request, username=usuario.username, password=senha)
            
            if not user:
                print(f"🔍 DEBUG: Senha incorreta para {usuario.username}")
                return JsonResponse({'success': False, 'erro': 'Senha incorreta'})
            
            # Verificar permissões
            if not (user.is_professor or user.is_coordenador or user.is_diretor_turma):
                print(f"🔍 DEBUG: {user.username} não tem permissões")
                return JsonResponse({'success': False, 'erro': 'Usuário não tem permissão para esta área'})
            
            # Fazer login
            auth_login(request, user)
            print(f"✅ DEBUG: Login bem-sucedido para {user.username}")
            
            # Determinar cargos
            cargos = []
            if user.is_professor:
                cargos.append('professor')
            if user.is_coordenador:
                cargos.append('coordenador')
            if user.is_diretor_turma:
                cargos.append('diretor_turma')
            
            print(f"🔍 DEBUG: Cargos: {cargos}")
            
            # Redirecionar baseado nos cargos
            if len(cargos) == 1:
                if cargos[0] == 'professor':
                    return JsonResponse({'success': True, 'redirect': reverse('dashboard_professor')})
                elif cargos[0] == 'coordenador':
                    return JsonResponse({'success': True, 'redirect': reverse('coordenador_dashboard')})
                elif cargos[0] == 'diretor_turma':
                    return JsonResponse({'success': True, 'redirect': reverse('diretor_dashboard')})
            
            # Múltiplos cargos
            # No final da view, quando o usuário tem múltiplos cargos
            request.session['cargos_disponiveis'] = cargos
            request.session['tem_multiplos_cargos'] = len(cargos) > 1
            return JsonResponse({'success': True, 'redirect': reverse('selecionar_perfil')})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'erro': 'Requisição inválida'}, status=400)
        except Exception as e:
            print(f"❌ DEBUG: Erro: {e}")
            return JsonResponse({'success': False, 'erro': f'Erro: {str(e)}'}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

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
        try:
            data = json.loads(request.body)
            perfil = data.get('perfil')
        except json.JSONDecodeError:
            return JsonResponse({'erro': 'Requisição inválida'}, status=400)
        
        if perfil == 'professor':
            return JsonResponse({'redirect': reverse('dashboard_professor')})
        elif perfil == 'coordenador':
            return JsonResponse({'redirect': reverse('coordenador_dashboard')})
        elif perfil == 'diretor_turma':
            return JsonResponse({'redirect': reverse('diretor_dashboard')})  # ← Nome correto
        else:
            return JsonResponse({'erro': 'Perfil inválido'}, status=400)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

@login_required
def dashboard_professor(request):
    if not request.user.is_professor:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('index')
    
    # Inicializar estrutura para agrupar disciplinas por curso
    disciplinas_por_curso = {
        'eletronica': {'nome': 'Eletrónica e Telecomunicações', 'disciplinas': []},
        'informatica': {'nome': 'Informática', 'disciplinas': []},
        'comum': {'nome': 'Comum (Ambos os Cursos)', 'disciplinas': []},
    }
    
    # CORREÇÃO 6: Buscar todas as disciplinas com suas turmas associadas
    todas_disciplinas = Disciplina.objects.all()
    
    for disciplina in todas_disciplinas:
        # Buscar todos os cursos que esta disciplina atende
        turmas_da_disciplina = Turma.objects.filter(disciplinas_relacionadas__disciplina=disciplina)
        cursos_presentes = set(turmas_da_disciplina.values_list('curso', flat=True))
        
        # Verificar se a disciplina pertence a ambos os cursos
        tem_eletronica = 'eletronica' in cursos_presentes
        tem_informatica = 'informatica' in cursos_presentes
        
        if tem_eletronica and tem_informatica:
            # Disciplina comum a ambos os cursos
            if disciplina not in disciplinas_por_curso['comum']['disciplinas']:
                disciplinas_por_curso['comum']['disciplinas'].append(disciplina)
        elif tem_eletronica:
            # Disciplina apenas de Eletrónica
            if disciplina not in disciplinas_por_curso['eletronica']['disciplinas']:
                disciplinas_por_curso['eletronica']['disciplinas'].append(disciplina)
        elif tem_informatica:
            # Disciplina apenas de Informática
            if disciplina not in disciplinas_por_curso['informatica']['disciplinas']:
                disciplinas_por_curso['informatica']['disciplinas'].append(disciplina)
        else:
            # Disciplina sem turmas associadas (fallback para comum)
            if disciplina not in disciplinas_por_curso['comum']['disciplinas']:
                disciplinas_por_curso['comum']['disciplinas'].append(disciplina)
    
    # Remover cursos que não têm disciplinas (opcional)
    context = {
        'disciplinas_por_curso': disciplinas_por_curso,
        'tem_multiplos_cargos': request.session.get('tem_multiplos_cargos', False),
    }
    return render(request, 'core/dashboard_professor.html', context)

@login_required
@csrf_exempt
def get_turmas_por_disciplina(request, disciplina_id):
    if not (request.user.is_professor or request.user.is_coordenador or request.user.is_diretor_turma):
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    turmas = Turma.objects.filter(disciplinas_relacionadas__disciplina=disciplina).distinct()
    data = [{'id': t.id, 'nome': t.nome, 'curso': t.get_curso_display()} for t in turmas]
    return JsonResponse({'turmas': data})

@login_required
def turma_detail(request, turma_id):
    if not (request.user.is_professor or request.user.is_diretor_turma):
        return redirect('index')
    
    turma = get_object_or_404(Turma, id=turma_id)
    disciplina_id = request.GET.get('disciplina_id')
    
    if not disciplina_id:
        messages.error(request, 'Nenhuma disciplina selecionada.')
        return redirect('dashboard_professor')
    
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    
    alunos = turma.alunos.all().order_by('usuario__first_name')
    atividades = Atividade.objects.filter(disciplina=disciplina, turmas=turma).order_by('-created_at')
    
    from django.utils import timezone
    agora = timezone.now()
    hoje = agora.date()
    hora_atual = agora.time()
    
    for atividade in atividades:
        # CORREÇÃO: Data OU Hora de fim
        pode = False
        if atividade.data_fim and atividade.hora_fim:
            # Se a data de fim já passou
            if atividade.data_fim < hoje:
                pode = True
            # Se é hoje e a hora atual já passou da hora de fim
            elif atividade.data_fim == hoje and atividade.hora_fim <= hora_atual:
                pode = True
        atividade.pode_distribuir = pode
    
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
        messages.error(request, 'Acesso não autorizado.')
        return redirect('index')
    
    turma = get_object_or_404(Turma, id=turma_id)
    disciplina_id = request.GET.get('disciplina_id')
    
    if not disciplina_id:
        messages.error(request, 'Nenhuma disciplina selecionada.')
        return redirect('turma_detail', turma_id=turma.id)
    
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    
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
        
        messages.success(request, f'Atividade "{nome}" criada com sucesso!')
        # Redirecionar com o mesmo disciplina_id
        return redirect(f'{reverse("turma_detail", args=[turma.id])}?disciplina_id={disciplina.id}')
    
    todas_turmas = Turma.objects.all().order_by('curso', 'nome')
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'todas_turmas': todas_turmas,
    }
    return render(request, 'core/criar_atividade.html', context)

@login_required
def distribuir_pontos(request, atividade_id):
    if not request.user.is_professor:
        return redirect('index')
    
    atividade = get_object_or_404(Atividade, id=atividade_id)
    turma_id = request.GET.get('turma_id')
    
    if not turma_id:
        messages.error(request, 'Nenhuma turma selecionada.')
        return redirect('dashboard_professor')
    
    turma = get_object_or_404(Turma, id=turma_id)
    
    if not atividade.turmas.filter(id=turma.id).exists():
        messages.error(request, 'Esta atividade não está associada a esta turma.')
        return redirect('turma_detail', turma_id=turma.id)
    
    from django.utils import timezone
    agora = timezone.now()
    hoje = agora.date()
    hora_atual = agora.time()
    
    # CORREÇÃO: Data OU Hora de fim
    pode_distribuir = False
    if atividade.data_fim and atividade.hora_fim:
        if atividade.data_fim < hoje:
            pode_distribuir = True
        elif atividade.data_fim == hoje and atividade.hora_fim <= hora_atual:
            pode_distribuir = True
    
    alunos = turma.alunos.all().order_by('usuario__first_name', 'usuario__username')
    
    if request.method == 'POST':
        if not pode_distribuir:
            messages.error(request, 'Esta atividade ainda não terminou. Não é possível distribuir pontos.')
            return redirect('turma_detail', turma_id=turma.id)
        
        pontos_distribuidos = 0
        for aluno in alunos:
            pontos_str = request.POST.get(f'pontos_{aluno.id}')
            if pontos_str and pontos_str.strip():
                pontos = int(pontos_str)
                if pontos > 0 and pontos <= atividade.max_pontos_por_aluno:
                    aluno.saldo_pontos += pontos
                    aluno.save()
                    Transacao.objects.create(
                        aluno=aluno,
                        quantidade=pontos,
                        tipo='distribuicao',
                        descricao=f'Distribuição de pontos da atividade: {atividade.nome}',
                        professor=request.user,
                        atividade=atividade
                    )
                    pontos_distribuidos += 1
        
        if pontos_distribuidos > 0:
            messages.success(request, f'Pontos distribuídos com sucesso para {pontos_distribuidos} aluno(s)!')
        else:
            messages.warning(request, 'Nenhum ponto foi distribuído.')
        
        return redirect('turma_detail', turma_id=turma.id)
    
    context = {
        'atividade': atividade,
        'turma': turma,
        'alunos': alunos,
        'max_pontos': atividade.max_pontos_por_aluno,
        'pode_distribuir': pode_distribuir,
    }
    return render(request, 'core/distribuir_pontos.html', context)



# ==================== DIRETOR DE TURMA ====================

def is_diretor_turma(user):
    return user.is_authenticated and user.is_diretor_turma and user.turma_vinculada is not None

@login_required
@user_passes_test(is_diretor_turma)
def diretor_dashboard(request):
    """Dashboard do diretor de turma - mostra apenas atividades do coordenador"""
    turma = request.user.turma_vinculada
    
    if not turma:
        messages.error(request, 'Você não está vinculado a nenhuma turma.')
        return redirect('index')
    
    # Alunos da turma em ordem alfabética
    alunos = turma.alunos.all().order_by('usuario__first_name', 'usuario__username')
    
    # CORREÇÃO: Mostrar apenas atividades do coordenador (sem disciplina)
    # Atividades que NÃO têm disciplina (criadas pelo coordenador)
    hoje = timezone.now().date()
    hora_atual = timezone.now().time()
    
    atividades = Atividade.objects.filter(
        turmas=turma,
        disciplina__isnull=True  # ← Apenas atividades do coordenador
    ).order_by('-created_at')
    
    print(f"DEBUG Diretor: Turma {turma.nome} - Atividades do coordenador: {atividades.count()}")  # Debug
    
    for atividade in atividades:
        # Verificar se pode distribuir pontos
        if atividade.data_fim and atividade.hora_fim:
            if atividade.data_fim < hoje:
                atividade.pode_distribuir = True
            elif atividade.data_fim == hoje and atividade.hora_fim <= hora_atual:
                atividade.pode_distribuir = True
            else:
                atividade.pode_distribuir = False
        else:
            atividade.pode_distribuir = False
        
        # Verificar se já foi distribuído (usando session)
        session_key = f'atividade_{atividade.id}_turma_{turma.id}_distribuida'
        atividade.ja_distribuida = request.session.get(session_key, False)
    
    context = {
        'turma': turma,
        'alunos': alunos,
        'atividades': atividades,
        'nome': request.user.get_full_name() or request.user.username,
        'tem_multiplos_cargos': request.session.get('tem_multiplos_cargos', False),
    }
    return render(request, 'core/diretor_dashboard.html', context)

@login_required
@user_passes_test(is_diretor_turma)
def diretor_adicionar_pontos(request, aluno_id):
    """Adicionar pontos a um aluno específico (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'erro': 'Método não permitido'})
    
    try:
        data = json.loads(request.body)
        pontos = int(data.get('pontos', 0))
        motivo = data.get('motivo', 'Adição de pontos pelo diretor de turma')
        
        # Verificar se o aluno pertence à turma do diretor
        aluno = get_object_or_404(
            PerfilAluno, 
            id=aluno_id, 
            turma=request.user.turma_vinculada
        )
        
        if pontos <= 0:
            return JsonResponse({'success': False, 'erro': 'Os pontos devem ser maiores que zero.'})
        
        # Adicionar pontos
        aluno.saldo_pontos += pontos
        aluno.save()
        
        # Registrar transação
        Transacao.objects.create(
            aluno=aluno,
            quantidade=pontos,
            tipo='adicao',
            descricao=motivo,
            professor=request.user
        )
        
        return JsonResponse({
            'success': True,
            'novo_saldo': aluno.saldo_pontos,
            'mensagem': f'{pontos} pontos adicionados com sucesso!'
        })
        
    except PerfilAluno.DoesNotExist:
        return JsonResponse({'success': False, 'erro': 'Aluno não encontrado'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'erro': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'erro': str(e)})

@login_required
@user_passes_test(is_diretor_turma)
def diretor_reduzir_pontos(request, aluno_id):
    """Reduzir pontos de um aluno específico (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'erro': 'Método não permitido'})
    
    try:
        data = json.loads(request.body)
        pontos = int(data.get('pontos', 0))
        motivo = data.get('motivo', 'Redução de pontos pelo diretor de turma')
        
        # Verificar se o aluno pertence à turma do diretor
        aluno = get_object_or_404(
            PerfilAluno, 
            id=aluno_id, 
            turma=request.user.turma_vinculada
        )
        
        if pontos <= 0:
            return JsonResponse({'success': False, 'erro': 'Os pontos devem ser maiores que zero.'})
        
        if aluno.saldo_pontos < pontos:
            return JsonResponse({
                'success': False, 
                'erro': f'Saldo insuficiente. Saldo atual: {aluno.saldo_pontos} pontos.'
            })
        
        # Reduzir pontos
        aluno.saldo_pontos -= pontos
        aluno.save()
        
        # Registrar transação
        Transacao.objects.create(
            aluno=aluno,
            quantidade=-pontos,
            tipo='remocao',
            descricao=motivo,
            professor=request.user
        )
        
        return JsonResponse({
            'success': True,
            'novo_saldo': aluno.saldo_pontos,
            'mensagem': f'{pontos} pontos removidos com sucesso!'
        })
        
    except PerfilAluno.DoesNotExist:
        return JsonResponse({'success': False, 'erro': 'Aluno não encontrado'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'erro': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'erro': str(e)})

@login_required
@user_passes_test(is_diretor_turma)
def diretor_distribuir_pontos(request, atividade_id):
    """Distribuir pontos de uma atividade do coordenador para os alunos da turma"""
    turma = request.user.turma_vinculada
    
    if not turma:
        messages.error(request, 'Você não está vinculado a nenhuma turma.')
        return redirect('diretor_dashboard')
    
    # CORREÇÃO: Verificar se é atividade do coordenador (sem disciplina)
    atividade = get_object_or_404(
        Atividade, 
        id=atividade_id, 
        turmas=turma,
        disciplina__isnull=True  # ← Apenas atividades do coordenador
    )
    
    # Verificar se já foi distribuído
    session_key = f'atividade_{atividade_id}_turma_{turma.id}_distribuida'
    if request.session.get(session_key, False):
        messages.warning(request, 'Os pontos desta atividade já foram distribuídos para esta turma.')
        return redirect('diretor_dashboard')
    
    # Verificar se pode distribuir
    from django.utils import timezone
    agora = timezone.now()
    hoje = agora.date()
    hora_atual = agora.time()
    
    pode_distribuir = False
    if atividade.data_fim and atividade.hora_fim:
        if atividade.data_fim < hoje:
            pode_distribuir = True
        elif atividade.data_fim == hoje and atividade.hora_fim <= hora_atual:
            pode_distribuir = True
    
    if not pode_distribuir:
        messages.error(request, f'Esta atividade ainda não terminou. Data/Hora de fim: {atividade.data_fim} {atividade.hora_fim}')
        return redirect('diretor_dashboard')
    
    alunos = turma.alunos.all().order_by('usuario__first_name', 'usuario__username')
    
    if request.method == 'POST':
        pontos_distribuidos = 0
        
        for aluno in alunos:
            pontos_str = request.POST.get(f'pontos_{aluno.id}')
            if pontos_str and pontos_str.strip():
                pontos = int(pontos_str)
                if pontos > 0 and pontos <= atividade.max_pontos_por_aluno:
                    aluno.saldo_pontos += pontos
                    aluno.save()
                    
                    Transacao.objects.create(
                        aluno=aluno,
                        quantidade=pontos,
                        tipo='distribuicao',
                        descricao=f'Distribuição de pontos da atividade: {atividade.nome}',
                        professor=request.user,
                        atividade=atividade
                    )
                    pontos_distribuidos += 1
        
        if pontos_distribuidos > 0:
            request.session[session_key] = True
            messages.success(request, f'Pontos distribuídos com sucesso para {pontos_distribuidos} aluno(s)!')
        else:
            messages.warning(request, 'Nenhum ponto foi distribuído.')
        
        return redirect('diretor_dashboard')
    
    context = {
        'atividade': atividade,
        'turma': turma,
        'alunos': alunos,
        'max_pontos': atividade.max_pontos_por_aluno,
        'pode_distribuir': pode_distribuir,
    }
    return render(request, 'core/diretor_distribuir_pontos.html', context)

@login_required
@user_passes_test(is_diretor_turma)
def diretor_distribuir_pontos(request, atividade_id):
    """Distribuir pontos de uma atividade para os alunos da turma"""
    turma = request.user.turma_vinculada
    
    if not turma:
        messages.error(request, 'Você não está vinculado a nenhuma turma.')
        return redirect('diretor_dashboard')
    
    atividade = get_object_or_404(Atividade, id=atividade_id, turmas=turma)
    
    # Verificar se pode distribuir
    from django.utils import timezone
    agora = timezone.now()
    hoje = agora.date()
    hora_atual = agora.time()
    
    pode_distribuir = False
    if atividade.data_fim and atividade.hora_fim:
        if atividade.data_fim < hoje:
            pode_distribuir = True
        elif atividade.data_fim == hoje and atividade.hora_fim <= hora_atual:
            pode_distribuir = True
    
    if not pode_distribuir:
        messages.error(request, 'Esta atividade ainda não terminou. Não é possível distribuir pontos.')
        return redirect('diretor_dashboard')
    
    alunos = turma.alunos.all().order_by('usuario__first_name', 'usuario__username')
    
    if request.method == 'POST':
        pontos_distribuidos = 0
        
        for aluno in alunos:
            pontos_str = request.POST.get(f'pontos_{aluno.id}')
            if pontos_str and pontos_str.strip():
                pontos = int(pontos_str)
                if pontos > 0 and pontos <= atividade.max_pontos_por_aluno:
                    aluno.saldo_pontos += pontos
                    aluno.save()
                    Transacao.objects.create(
                        aluno=aluno,
                        quantidade=pontos,
                        tipo='distribuicao',
                        descricao=f'Distribuição de pontos da atividade: {atividade.nome}',
                        professor=request.user,
                        atividade=atividade
                    )
                    pontos_distribuidos += 1
        
        if pontos_distribuidos > 0:
            messages.success(request, f'Pontos distribuídos com sucesso para {pontos_distribuidos} aluno(s)!')
        else:
            messages.warning(request, 'Nenhum ponto foi distribuído.')
        
        return redirect('diretor_dashboard')
    
    context = {
        'atividade': atividade,
        'turma': turma,
        'alunos': alunos,
        'max_pontos': atividade.max_pontos_por_aluno,
        'pode_distribuir': pode_distribuir,
    }
    return render(request, 'core/diretor_distribuir_pontos.html', context)



# ==================== COORDENADOR DE ATIVIDADES ====================

def is_coordenador(user):
    return user.is_authenticated and user.is_coordenador


@login_required
@user_passes_test(is_coordenador)
def coordenador_dashboard(request):
    """Dashboard do coordenador com lista de atividades criadas pelo coordenador"""
    
    # Mostrar apenas atividades SEM disciplina (criadas pelo coordenador)
    atividades = Atividade.objects.filter(
        disciplina__isnull=True
    ).order_by('-created_at')
    
    # Barra de pesquisa
    search_query = request.GET.get('search', '')
    if search_query:
        atividades = atividades.filter(
            Q(nome__icontains=search_query) |
            Q(tipo_atividade__icontains=search_query) |
            Q(descricao__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(atividades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contar total de atividades curriculares
    total_curriculares = Atividade.objects.filter(disciplina__isnull=False).count()
    
    context = {
        'atividades': page_obj,
        'search_query': search_query,
        'total_count': atividades.count(),
        'total_curriculares': total_curriculares,
    }
    return render(request, 'core/coordenador_dashboard.html', context)


@login_required
@user_passes_test(is_coordenador)
def coordenador_criar_atividade(request):
    """Criar nova atividade como coordenador (com interrupção de aula)"""
    if request.method == 'POST':
        try:
            # Dados básicos
            tipo_atividade = request.POST.get('tipo_atividade')
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao', '')
            criterios = request.POST.get('criterios')
            data_inicio = request.POST.get('data_inicio')
            data_fim = request.POST.get('data_fim')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fim = request.POST.get('hora_fim')
            max_pontos = request.POST.get('max_pontos')
            selecao_cursos = request.POST.get('selecao_cursos')
            curso_selecionado = request.POST.get('curso_selecionado')
            
            # NOVO CAMPO: Interrupção de aula
            interrompe_aula = request.POST.get('interrompe_aula') == 'sim'
            
            # Validar datas
            from datetime import datetime
            if data_inicio > data_fim:
                messages.error(request, 'A data de fim não pode ser anterior à data de início.')
                return redirect('coordenador_criar_atividade')
            
            if data_inicio == data_fim and hora_inicio >= hora_fim:
                messages.error(request, 'No mesmo dia, a hora de fim deve ser posterior à hora de início.')
                return redirect('coordenador_criar_atividade')
            
            # Criar atividade
            atividade = Atividade.objects.create(
                tipo_atividade=tipo_atividade,
                nome=nome,
                descricao=descricao,
                criterios_avaliacao=criterios,
                data_inicio=data_inicio,
                data_fim=data_fim,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                max_pontos_por_aluno=max_pontos,
                interrompe_aula=interrompe_aula,  # NOVO CAMPO
            )
            
            # Associar turmas baseado na seleção de cursos
            if selecao_cursos == 'ambos':
                atividade.todos_cursos = True
                turmas = Turma.objects.all()
                atividade.turmas.set(turmas)
            else:
                atividade.cursos_associados = curso_selecionado
                turmas = Turma.objects.filter(curso=curso_selecionado)
                atividade.turmas.set(turmas)
            
            atividade.save()
            messages.success(request, f'Atividade "{nome}" criada com sucesso!')
            return redirect('coordenador_dashboard')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar atividade: {str(e)}')
            return redirect('coordenador_criar_atividade')
    
    # GET - mostrar formulário
    cursos = Turma.CURSO_CHOICES
    context = {
        'cursos': cursos,
        'is_edit': False,
    }
    return render(request, 'core/coordenador_criar_atividade.html', context)


@login_required
@user_passes_test(is_coordenador)
def coordenador_editar_atividade(request, pk):
    """Editar atividade existente (com interrupção de aula)"""
    atividade = get_object_or_404(Atividade, id=pk)
    
    # Verificar se é atividade do coordenador (sem disciplina)
    if atividade.disciplina is not None:
        messages.error(request, 'Esta atividade é curricular e não pode ser editada aqui.')
        return redirect('coordenador_dashboard')
    
    if request.method == 'POST':
        try:
            # Dados básicos
            tipo_atividade = request.POST.get('tipo_atividade')
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao', '')
            criterios = request.POST.get('criterios')
            data_inicio = request.POST.get('data_inicio')
            data_fim = request.POST.get('data_fim')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fim = request.POST.get('hora_fim')
            max_pontos = request.POST.get('max_pontos')
            selecao_cursos = request.POST.get('selecao_cursos')
            curso_selecionado = request.POST.get('curso_selecionado')
            
            # NOVO CAMPO: Interrupção de aula
            interrompe_aula = request.POST.get('interrompe_aula') == 'sim'
            
            # Validar datas
            if data_inicio > data_fim:
                messages.error(request, 'A data de fim não pode ser anterior à data de início.')
                return redirect('coordenador_editar_atividade', pk=pk)
            
            if data_inicio == data_fim and hora_inicio >= hora_fim:
                messages.error(request, 'No mesmo dia, a hora de fim deve ser posterior à hora de início.')
                return redirect('coordenador_editar_atividade', pk=pk)
            
            # Atualizar dados básicos
            atividade.tipo_atividade = tipo_atividade
            atividade.nome = nome
            atividade.descricao = descricao
            atividade.criterios_avaliacao = criterios
            atividade.data_inicio = data_inicio
            atividade.data_fim = data_fim
            atividade.hora_inicio = hora_inicio
            atividade.hora_fim = hora_fim
            atividade.max_pontos_por_aluno = max_pontos
            atividade.interrompe_aula = interrompe_aula  # NOVO CAMPO
            
            # Atualizar associações de turmas
            atividade.turmas.clear()
            if selecao_cursos == 'ambos':
                atividade.todos_cursos = True
                atividade.cursos_associados = None
                turmas = Turma.objects.all()
                atividade.turmas.set(turmas)
            else:
                atividade.todos_cursos = False
                atividade.cursos_associados = curso_selecionado
                turmas = Turma.objects.filter(curso=curso_selecionado)
                atividade.turmas.set(turmas)
            
            atividade.save()
            messages.success(request, f'Atividade "{nome}" atualizada com sucesso!')
            return redirect('coordenador_dashboard')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar atividade: {str(e)}')
            return redirect('coordenador_editar_atividade', pk=pk)
    
    # GET - mostrar formulário preenchido
    cursos = Turma.CURSO_CHOICES
    selecao_atual = 'ambos' if atividade.todos_cursos else 'um_curso'
    context = {
        'atividade': atividade,
        'cursos': cursos,
        'selecao_atual': selecao_atual,
        'is_edit': True,
    }
    return render(request, 'core/coordenador_criar_atividade.html', context)


@csrf_exempt
@login_required
@user_passes_test(is_coordenador)
def coordenador_eliminar_atividade(request, pk):
    """Eliminar atividade (AJAX ou POST)"""
    atividade = get_object_or_404(Atividade, id=pk)
    
    # Verificar se é atividade do coordenador
    if atividade.disciplina is not None:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'erro': 'Não é possível eliminar atividade curricular.'})
        messages.error(request, 'Não é possível eliminar atividade curricular.')
        return redirect('coordenador_dashboard')
    
    if request.method == 'POST':
        nome = atividade.nome
        atividade.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Atividade "{nome}" eliminada!'})
        
        messages.success(request, f'Atividade "{nome}" eliminada com sucesso!')
        return redirect('coordenador_dashboard')
    
    return render(request, 'core/coordenador_confirmar_delete.html', {'atividade': atividade})


@login_required
@user_passes_test(is_coordenador)
def coordenador_atividades_curriculares(request):
    """Lista todas as atividades curriculares (criadas pelos professores)"""
    
    # Buscar apenas atividades COM disciplina (atividades dos professores)
    atividades = Atividade.objects.filter(
        disciplina__isnull=False
    ).order_by('-created_at')
    
    # Barra de pesquisa
    search_query = request.GET.get('search', '')
    if search_query:
        atividades = atividades.filter(
            Q(nome__icontains=search_query) |
            Q(disciplina__nome__icontains=search_query) |
            Q(descricao__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(atividades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'atividades': page_obj,
        'search_query': search_query,
        'total_count': atividades.count(),
    }
    return render(request, 'core/coordenador_atividades_curriculares.html', context)


@login_required
@user_passes_test(is_coordenador)
def api_buscar_atividades(request):
    """API para busca de atividades (AJAX)"""
    search_query = request.GET.get('q', '')
    atividades = Atividade.objects.filter(disciplina__isnull=True).order_by('-created_at')
    
    if search_query:
        atividades = atividades.filter(
            Q(nome__icontains=search_query) |
            Q(tipo_atividade__icontains=search_query)
        )
    
    data = []
    for atv in atividades[:20]:
        data.append({
            'id': atv.id,
            'nome': atv.nome,
            'tipo': atv.get_tipo_atividade_display(),
            'data_inicio': atv.data_inicio.strftime('%d/%m/%Y') if atv.data_inicio else '-',
            'data_fim': atv.data_fim.strftime('%d/%m/%Y') if atv.data_fim else '-',
            'max_pontos': atv.max_pontos_por_aluno,
            'cursos': atv.get_cursos_display,
            'interrompe_aula': atv.interrompe_aula,  # NOVO CAMPO
        })
    
    return JsonResponse({'success': True, 'atividades': data})