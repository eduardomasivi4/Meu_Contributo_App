from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import A4
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
    PerfilProfessor, PerfilDiretorTurma, PerfilCoordenador,
    CriterioAtividade, RegistroAtividadeAluno, GrupoAtividade
)
from .forms import AtividadeComCriteriosForm, DistribuicaoPontosForm, GrupoFormSet


# ==================== FUNÇÕES AUXILIARES ====================

def is_diretor_turma(user):
    return user.is_authenticated and user.is_diretor_turma and user.turma_vinculada is not None

def is_coordenador_cultural(user):
    return user.is_authenticated and user.is_coordenador_cultural

def is_coordenador_ciencia(user):
    return user.is_authenticated and user.is_coordenador_ciencia

def is_professor(user):
    return user.is_authenticated and user.is_professor


# ==================== PÁGINA INICIAL ====================

def index(request):
    return render(request, 'core/index.html')


# ==================== ALUNO ====================

def login_aluno(request):
    return render(request, 'core/login_aluno.html')


@csrf_exempt
def verificar_processo(request):
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


@csrf_exempt
def validar_senha(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            processo = data.get('processo')
            senha = data.get('senha')
            aluno = PerfilAluno.objects.get(numero_processo=processo)
            user = aluno.usuario
            if user.check_password(senha):
                auth_login(request, user)
                return JsonResponse({'success': True, 'redirect': reverse('dashboard_aluno')})
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
        'resgates_count': perfil.resgates.count(),
        'total_pontos': perfil.transacoes.filter(quantidade__gt=0).aggregate(total=Sum('quantidade'))['total'] or 0,
        'ultimas_transacoes': perfil.transacoes.all().order_by('-data')[:5],
    }
    return render(request, 'core/dashboard_aluno.html', context)


@login_required
def atividades(request):
    if request.user.tipo != 'aluno':
        return redirect('index')
    
    atividades_curriculares = Atividade.objects.filter(
        disciplina__isnull=False
    ).exclude(disciplina=None).order_by('disciplina__nome', 'data_inicio')
    
    atividades_extra = Atividade.objects.filter(
        disciplina__isnull=True
    ).exclude(tipo_atividade=None).order_by('-created_at')
    
    disciplinas = Disciplina.objects.filter(
        atividades__isnull=False
    ).distinct().order_by('nome')
    
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
                aluno=aluno, beneficio=beneficio,
                pontos_gastos=beneficio.custo_pontos, status='confirmado'
            )
            Transacao.objects.create(
                aluno=aluno, quantidade=-beneficio.custo_pontos,
                tipo='resgate', descricao=f'Resgate de {beneficio.nome}'
            )
            return JsonResponse({'success': True, 'novo_saldo': aluno.saldo_pontos})
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
        'curso': perfil.turma.get_curso_display() if perfil.turma else 'Não definido',
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '')
            senha = data.get('senha', '')
            
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                try:
                    usuario = Usuario.objects.get(username=email)
                except Usuario.DoesNotExist:
                    return JsonResponse({'success': False, 'erro': 'Email/nome de usuário não encontrado'})
            
            user = authenticate(request, username=usuario.username, password=senha)
            if not user:
                return JsonResponse({'success': False, 'erro': 'Senha incorreta'})
            
            if not (user.is_professor or user.is_coordenador_cultural or user.is_coordenador_ciencia or user.is_diretor_turma):
                return JsonResponse({'success': False, 'erro': 'Usuário não tem permissão para esta área'})
            
            auth_login(request, user)
            
            cargos = []
            if user.is_professor:
                cargos.append('professor')
            if user.is_coordenador_cultural:
                cargos.append('coordenador_cultural')
            if user.is_coordenador_ciencia:
                cargos.append('coordenador_ciencia')
            if user.is_diretor_turma:
                cargos.append('diretor_turma')
            
            if len(cargos) == 1:
                if cargos[0] == 'professor':
                    return JsonResponse({'success': True, 'redirect': reverse('dashboard_professor')})
                elif cargos[0] == 'coordenador_cultural':
                    return JsonResponse({'success': True, 'redirect': reverse('coordenador_cultural_dashboard')})
                elif cargos[0] == 'coordenador_ciencia':
                    return JsonResponse({'success': True, 'redirect': reverse('coordenador_ciencia_dashboard')})
                elif cargos[0] == 'diretor_turma':
                    return JsonResponse({'success': True, 'redirect': reverse('diretor_dashboard')})
            
            request.session['cargos_disponiveis'] = cargos
            request.session['tem_multiplos_cargos'] = len(cargos) > 1
            return JsonResponse({'success': True, 'redirect': reverse('selecionar_perfil')})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'erro': 'Dados inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'erro': f'Erro: {str(e)}'}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


def selecionar_perfil(request):
    cargos = request.session.get('cargos_disponiveis', [])
    context = {
        'tem_professor': 'professor' in cargos,
        'tem_coordenador_cultural': 'coordenador_cultural' in cargos,
        'tem_coordenador_ciencia': 'coordenador_ciencia' in cargos,
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
        elif perfil == 'coordenador_cultural':
            return JsonResponse({'redirect': reverse('coordenador_cultural_dashboard')})
        elif perfil == 'coordenador_ciencia':
            return JsonResponse({'redirect': reverse('coordenador_ciencia_dashboard')})
        elif perfil == 'diretor_turma':
            return JsonResponse({'redirect': reverse('diretor_dashboard')})
        return JsonResponse({'erro': 'Perfil inválido'}, status=400)
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def dashboard_professor(request):
    if not request.user.is_professor:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('index')
    
    perfil_prof = get_object_or_404(PerfilProfessor, usuario=request.user)
    disciplina_do_professor = perfil_prof.disciplina
    
    if not disciplina_do_professor:
        messages.warning(request, 'Nenhuma disciplina associada ao seu perfil.')
        return redirect('index')
    
    turmas_do_professor = perfil_prof.turmas.all()
    
    turmas_por_curso = {
        'eletronica': {'nome': 'Eletrónica e Telecomunicações', 'turmas': []},
        'informatica': {'nome': 'Informática', 'turmas': []},
        'comum': {'nome': 'Disciplinas Comuns', 'turmas': []},
    }
    
    for turma in turmas_do_professor:
        curso_key = turma.curso
        if curso_key in turmas_por_curso:
            turmas_por_curso[curso_key]['turmas'].append(turma)
    
    context = {
        'disciplina': disciplina_do_professor,
        'turmas_por_curso': turmas_por_curso,
        'tem_multiplos_cargos': request.session.get('tem_multiplos_cargos', False),
    }
    return render(request, 'core/dashboard_professor.html', context)


@login_required
@csrf_exempt
def get_turmas_por_disciplina(request, disciplina_id):
    if not (request.user.is_professor or request.user.is_diretor_turma):
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
    atividades = Atividade.objects.filter(disciplina=disciplina, turmas=turma).order_by('-created_at')
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'atividades': atividades,
    }
    return render(request, 'core/turma_detail.html', context)


# ==================== PROFESSOR - CRIAÇÃO E GESTÃO ====================

@login_required
@user_passes_test(lambda u: u.is_professor)
def criar_atividade_com_criterios(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    disciplina_id = request.GET.get('disciplina_id')
    disciplina = get_object_or_404(Disciplina, id=disciplina_id) if disciplina_id else None
    
    if request.method == 'POST':
        form = AtividadeComCriteriosForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.disciplina = disciplina
            atividade.criado_por = request.user
            atividade.save()
            
            # Salvar turmas
            turmas_ids = request.POST.getlist('turmas')
            if turmas_ids:
                atividade.turmas.set(turmas_ids)
            else:
                atividade.turmas.add(turma)
            
            # Salvar critérios
            nomes = request.POST.getlist('criterio_nome[]')
            pontos = request.POST.getlist('criterio_pontos[]')
            for n, p in zip(nomes, pontos):
                if n and p:
                    CriterioAtividade.objects.create(atividade=atividade, nome=n, pontos=int(p))
            
            # Salvar grupos
            grupo_nomes = request.POST.getlist('grupo_nome[]')
            for idx, grupo_nome in enumerate(grupo_nomes):
                if grupo_nome and grupo_nome.strip():
                    grupo = GrupoAtividade.objects.create(
                        atividade=atividade,
                        nome=grupo_nome.strip()
                    )
                    alunos_ids = request.POST.getlist(f'grupo_alunos_{idx}[]')
                    if alunos_ids:
                        grupo.alunos.set(alunos_ids)
            
            messages.success(request, f'Actividade "{atividade.nome}" criada com sucesso!')
            # REDIRECIONAR PARA O DASHBOARD DO PROFESSOR
            return redirect('dashboard_professor')
        else:
            messages.error(request, 'Erro ao criar actividade. Verifique os dados.')
            print(form.errors)
    else:
        form = AtividadeComCriteriosForm(initial={'turmas': [turma.id]})
    
    if disciplina:
        form.fields['turmas'].queryset = Turma.objects.filter(
            disciplinas_relacionadas__disciplina=disciplina
        ).distinct()
    
    context = {
        'form': form,
        'turma': turma,
        'disciplina': disciplina,
    }
    return render(request, 'core/criar_atividade_criterios.html', context)

@login_required
@user_passes_test(lambda u: u.is_professor)
def editar_atividade_professor(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id, disciplina__isnull=False)
    
    if atividade.finalizada:
        messages.error(request, 'Não é possível editar uma atividade já finalizada.')
        return redirect('dashboard_professor')
    
    if request.method == 'POST':
        form = AtividadeComCriteriosForm(request.POST, instance=atividade)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.save()
            atividade.turmas.set(request.POST.getlist('turmas'))
            
            # Atualizar critérios
            atividade.criterios.all().delete()
            nomes = request.POST.getlist('criterio_nome[]')
            pontos = request.POST.getlist('criterio_pontos[]')
            for n, p in zip(nomes, pontos):
                if n and p:
                    CriterioAtividade.objects.create(atividade=atividade, nome=n, pontos=int(p))
            
            # Atualizar grupos
            atividade.grupos.all().delete()
            grupo_nomes = request.POST.getlist('grupo_nome[]')
            for idx, grupo_nome in enumerate(grupo_nomes):
                if grupo_nome and grupo_nome.strip():
                    grupo = GrupoAtividade.objects.create(
                        atividade=atividade,
                        nome=grupo_nome.strip()
                    )
                    alunos_ids = request.POST.getlist(f'grupo_alunos_{idx}[]')
                    if alunos_ids:
                        grupo.alunos.set(alunos_ids)
            
            messages.success(request, f'Actividade "{atividade.nome}" actualizada com sucesso!')
            # REDIRECIONAR PARA O DASHBOARD DO PROFESSOR
            return redirect('dashboard_professor')
    else:
        form = AtividadeComCriteriosForm(instance=atividade)
        form.fields['turmas'].initial = [t.id for t in atividade.turmas.all()]
    
    context = {
        'form': form,
        'atividade': atividade,
        'turma': atividade.turmas.first(),
        'disciplina': atividade.disciplina,
        'is_edit': True,
    }
    return render(request, 'core/criar_atividade_criterios.html', context)

@login_required
@user_passes_test(lambda u: u.is_professor)
def eliminar_atividade_professor(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id, disciplina__isnull=False)
    
    if atividade.finalizada:
        messages.error(request, 'Não é possível eliminar uma atividade já finalizada.')
        return redirect('dashboard_professor')
    
    if request.method == 'POST':
        nome = atividade.nome
        atividade.delete()
        messages.success(request, f'Atividade "{nome}" eliminada com sucesso!')
        # REDIRECIONAR PARA O DASHBOARD DO PROFESSOR
        return redirect('dashboard_professor')
    
    context = {'atividade': atividade}
    return render(request, 'core/professor_confirmar_delete.html', context)

@login_required
@user_passes_test(lambda u: u.is_professor)
def criar_grupos_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id, disciplina__isnull=False)
    
    if atividade.finalizada:
        messages.error(request, 'Não é possível editar grupos de uma atividade já finalizada.')
        turma_id = atividade.turmas.first().id if atividade.turmas.exists() else None
        if turma_id:
            return redirect('turma_detail', turma_id=turma_id)
        return redirect('dashboard_professor')
    
    turma = atividade.turmas.first()
    if not turma:
        messages.error(request, 'Atividade sem turma associada.')
        return redirect('dashboard_professor')
    
    if request.method == 'POST':
        formset = GrupoFormSet(request.POST, queryset=atividade.grupos.all(), form_kwargs={'turma': turma})
        if formset.is_valid():
            instances = formset.save(commit=False)
            for grupo in instances:
                grupo.atividade = atividade
                grupo.save()
                formset.save_m2m()
            for deleted in formset.deleted_objects:
                deleted.delete()
            messages.success(request, f'Grupos da atividade "{atividade.nome}" atualizados!')
            return redirect(f'/turma/{turma.id}/?disciplina_id={atividade.disciplina.id}')
        else:
            messages.error(request, 'Erro ao salvar grupos. Verifique se há alunos duplicados.')
    else:
        formset = GrupoFormSet(queryset=atividade.grupos.all(), form_kwargs={'turma': turma})
    
    alunos_em_grupos = [aluno for grupo in atividade.grupos.all() for aluno in grupo.alunos.all()]
    alunos_sem_grupo = PerfilAluno.objects.filter(turma=turma).exclude(id__in=[a.id for a in alunos_em_grupos])
    
    context = {
        'atividade': atividade,
        'turma': turma,
        'formset': formset,
        'alunos_sem_grupo': alunos_sem_grupo,
    }
    return render(request, 'core/criar_grupos_atividade.html', context)


@login_required
@user_passes_test(lambda u: u.is_professor)
def iniciar_atividade_professor_v2(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id, disciplina__isnull=False)
    if atividade.finalizada:
        messages.error(request, 'Actividade já finalizada.')
        return redirect('dashboard_professor')
    
    turma_id = request.GET.get('turma_id')
    turma = get_object_or_404(Turma, id=turma_id)
    grupos = atividade.grupos.all()
    
    alunos_por_grupo = {}
    for grupo in grupos:
        alunos_por_grupo[grupo.id] = {
            'nome': grupo.nome,
            'alunos': list(grupo.alunos.all().order_by('usuario__first_name')),
            'total_alunos': grupo.alunos.count()
        }
    
    alunos_sem_grupo_ids = [a.id for g in grupos for a in g.alunos.all()]
    alunos_sem_grupo = turma.alunos.exclude(id__in=alunos_sem_grupo_ids).order_by('usuario__first_name')
    
    context = {
        'atividade': atividade,
        'turma': turma,
        'grupos': grupos,
        'alunos_por_grupo': alunos_por_grupo,
        'alunos_sem_grupo': alunos_sem_grupo,
        'criterios': atividade.criterios.all(),
        'tem_grupos': grupos.exists(),
    }
    return render(request, 'core/iniciar_atividade_professor_v2.html', context)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def terminar_atividade_professor(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    if atividade.finalizada:
        return JsonResponse({'success': False, 'erro': 'Actividade já finalizada'})
    
    data = json.loads(request.body)
    registos = data.get('registos', [])
    if not registos:
        return JsonResponse({'success': False, 'erro': 'Nenhum registo para guardar'})
    
    for reg in registos:
        aluno = PerfilAluno.objects.get(id=reg['aluno_id'])
        criterio = CriterioAtividade.objects.get(id=reg['criterio_id'])
        pontos = reg['pontos']
        
        RegistroAtividadeAluno.objects.create(
            atividade=atividade, aluno=aluno, criterio=criterio, pontos_atribuidos=pontos
        )
        Transacao.objects.create(
            aluno=aluno, quantidade=pontos,
            tipo='distribuicao' if pontos >= 0 else 'remocao',
            descricao=f'Critério "{criterio.nome}" na actividade {atividade.nome}',
            professor=request.user, atividade=atividade
        )
        aluno.saldo_pontos += pontos
        aluno.save()
    
    atividade.finalizada = True
    atividade.save()
    return JsonResponse({'success': True})


@login_required
def ver_registros_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    if not atividade.finalizada:
        messages.warning(request, 'Actividade ainda não finalizada.')
        return redirect('dashboard_professor')
    
    registos = atividade.registros_alunos.all().select_related('aluno', 'criterio')
    alunos_data = {}
    for r in registos:
        aid = r.aluno.id
        if aid not in alunos_data:
            alunos_data[aid] = {'aluno': r.aluno, 'total': 0, 'pos': 0, 'neg': 0, 'registos': []}
        alunos_data[aid]['total'] += r.pontos_atribuidos
        if r.pontos_atribuidos >= 0:
            alunos_data[aid]['pos'] += r.pontos_atribuidos
        else:
            alunos_data[aid]['neg'] += abs(r.pontos_atribuidos)
        alunos_data[aid]['registos'].append(r)
    
    context = {'atividade': atividade, 'alunos_data': alunos_data.values()}
    return render(request, 'core/ver_registros_atividade.html', context)


@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_professor)
def api_aplicar_criterio_grupo(request, grupo_id, criterio_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'erro': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        grupo = get_object_or_404(GrupoAtividade, id=grupo_id)
        criterio = get_object_or_404(CriterioAtividade, id=criterio_id)
        tipo = data.get('tipo', 'adicao')
        
        if grupo.atividade.disciplina is None:
            return JsonResponse({'success': False, 'erro': 'Grupo pertence a atividade extra-curricular'})
        
        alunos = grupo.alunos.all()
        registros = []
        for aluno in alunos:
            registros.append({
                'aluno_id': aluno.id,
                'criterio_id': criterio.id,
                'criterio_nome': criterio.nome,
                'pontos': criterio.pontos if tipo == 'adicao' else -criterio.pontos,
                'tipo': tipo
            })
        
        return JsonResponse({
            'success': True,
            'mensagem': f'Critério "{criterio.nome}" aplicado ao grupo "{grupo.nome}" ({alunos.count()} alunos)',
            'registros': registros,
            'total_pontos': sum(r['pontos'] for r in registros)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'erro': str(e)})


# ==================== DIRETOR DE TURMA ====================

@login_required
@user_passes_test(is_diretor_turma)
def diretor_dashboard(request):
    turma = request.user.turma_vinculada
    if not turma:
        messages.error(request, 'Você não está vinculado a nenhuma turma.')
        return redirect('index')
    
    alunos = turma.alunos.all().order_by('usuario__first_name', 'usuario__username')
    
    atividades = Atividade.objects.filter(
        turmas=turma, disciplina__isnull=True
    ).order_by('-created_at')
    
    for atividade in atividades:
        if atividade.pontos_turma > 0 and not atividade.distribuida:
            atividade.tem_pontos_para_distribuir = True
        else:
            atividade.tem_pontos_para_distribuir = False
    
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
def diretor_distribuir_pontos_limite(request, atividade_id):
    turma = request.user.turma_vinculada
    if not turma:
        messages.error(request, 'Você não está vinculado a nenhuma turma.')
        return redirect('diretor_dashboard')
    
    atividade = get_object_or_404(Atividade, id=atividade_id, turmas=turma, disciplina__isnull=True)
    
    if atividade.distribuida:
        messages.warning(request, 'Os pontos desta atividade já foram completamente distribuídos.')
        return redirect('diretor_dashboard')
    
    if not atividade.finalizada:
        messages.error(request, 'Esta atividade ainda não foi finalizada pelo coordenador.')
        return redirect('diretor_dashboard')
    
    if atividade.pontos_turma <= 0:
        messages.error(request, 'Não há pontos disponíveis para distribuir.')
        return redirect('diretor_dashboard')
    
    alunos = turma.alunos.all().order_by('usuario__first_name', 'usuario__last_name')
    session_key = f'distribuicao_atividade_{atividade_id}_turma_{turma.id}'
    distribuicao_salva = request.session.get(session_key, {})
    
    if request.method == 'POST':
        if 'salvar_progresso' in request.POST:
            pontos_por_aluno = {}
            for aluno in alunos:
                pontos = int(request.POST.get(f'pontos_aluno_{aluno.id}', 0))
                if pontos > 0:
                    pontos_por_aluno[str(aluno.id)] = pontos
            request.session[session_key] = pontos_por_aluno
            messages.success(request, 'Progresso salvo com sucesso!')
            return redirect('diretor_dashboard')
        
        elif 'finalizar' in request.POST:
            total_distribuido = 0
            for aluno in alunos:
                pontos = int(request.POST.get(f'pontos_aluno_{aluno.id}', 0))
                total_distribuido += pontos
            
            if total_distribuido != atividade.pontos_turma:
                messages.warning(request, f'Faltam {atividade.pontos_turma - total_distribuido} pontos para completar a distribuição.')
                return redirect('diretor_distribuir_pontos_limite', atividade_id=atividade_id)
            
            for aluno in alunos:
                pontos = int(request.POST.get(f'pontos_aluno_{aluno.id}', 0))
                if pontos > 0:
                    aluno.saldo_pontos += pontos
                    aluno.save()
                    Transacao.objects.create(
                        aluno=aluno, quantidade=pontos, tipo='distribuicao',
                        descricao=f'Distribuição de pontos: {atividade.nome}',
                        professor=request.user, atividade=atividade
                    )
            
            atividade.distribuida = True
            atividade.pontos_ja_distribuidos = atividade.pontos_turma
            atividade.save()
            
            if session_key in request.session:
                del request.session[session_key]
            
            messages.success(request, f'Pontos distribuídos! Total: {total_distribuido} pontos.')
            return redirect('diretor_dashboard')
    
    valores_iniciais = {}
    for aluno in alunos:
        valores_iniciais[f'pontos_aluno_{aluno.id}'] = distribuicao_salva.get(str(aluno.id), 0)
    
    context = {
        'atividade': atividade,
        'turma': turma,
        'alunos': alunos,
        'total_disponivel': atividade.pontos_restantes,
        'pontos_ja_distribuidos': atividade.pontos_ja_distribuidos,
        'total_geral': atividade.pontos_turma,
        'distribuicao_salva': bool(distribuicao_salva),
        'initial_values': valores_iniciais,
        'valores_iniciais': valores_iniciais,  # <-- ADICIONE ESTA LINHA
    }
    return render(request, 'core/diretor_distribuir_pontos_limite.html', context)


@login_required
@user_passes_test(is_diretor_turma)
def diretor_limpar_distribuicao(request, atividade_id):
    if request.method == 'POST':
        turma = request.user.turma_vinculada
        session_key = f'distribuicao_atividade_{atividade_id}_turma_{turma.id}'
        if session_key in request.session:
            del request.session[session_key]
            messages.success(request, 'Progresso de distribuição cancelado.')
        return redirect('diretor_dashboard')
    return redirect('diretor_dashboard')


@login_required
@user_passes_test(is_diretor_turma)
def diretor_ver_distribuicao(request, atividade_id):
    turma = request.user.turma_vinculada
    if not turma:
        messages.error(request, 'Você não está vinculado a nenhuma turma.')
        return redirect('diretor_dashboard')
    
    atividade = get_object_or_404(Atividade, id=atividade_id, turmas=turma, disciplina__isnull=True)
    
    if not atividade.distribuida:
        messages.warning(request, 'Esta atividade ainda não foi distribuída.')
        return redirect('diretor_dashboard')
    
    transacoes = Transacao.objects.filter(
        atividade=atividade, aluno__turma=turma, tipo='distribuicao'
    ).select_related('aluno')
    
    alunos_data = []
    total_distribuido = 0
    
    for aluno in turma.alunos.all().order_by('usuario__first_name'):
        pontos_aluno = sum(t.quantidade for t in transacoes if t.aluno.id == aluno.id)
        total_distribuido += pontos_aluno
        alunos_data.append({'aluno': aluno, 'pontos': pontos_aluno})
    
    context = {
        'atividade': atividade,
        'turma': turma,
        'alunos_data': alunos_data,
        'total_distribuido': total_distribuido,
        'total_original': atividade.pontos_turma,
    }
    return render(request, 'core/diretor_ver_distribuicao.html', context)


# ==================== COORDENADORES ====================

@login_required
@user_passes_test(is_coordenador_cultural)
def coordenador_cultural_dashboard(request):
    atividades = Atividade.objects.filter(
        disciplina__isnull=True, 
        tipo_atividade='cultural'
    ).order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    if search_query:
        atividades = atividades.filter(
            Q(nome__icontains=search_query) | Q(descricao__icontains=search_query)
        )
    
    paginator = Paginator(atividades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'atividades': page_obj,
        'search_query': search_query,
        'total_count': atividades.count(),
        'tipo': 'cultural',
    }
    return render(request, 'core/coordenador_dashboard_unico.html', context)


@login_required
@user_passes_test(is_coordenador_ciencia)
def coordenador_ciencia_dashboard(request):
    atividades = Atividade.objects.filter(
        disciplina__isnull=True, 
        tipo_atividade='ciencia_tecnologia'
    ).order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    if search_query:
        atividades = atividades.filter(
            Q(nome__icontains=search_query) | Q(descricao__icontains=search_query)
        )
    
    paginator = Paginator(atividades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'atividades': page_obj,
        'search_query': search_query,
        'total_count': atividades.count(),
        'tipo': 'ciencia',
    }
    return render(request, 'core/coordenador_dashboard_unico.html', context)

@login_required
def coordenador_criar_atividade_separado(request):
    tipo_atividade = request.GET.get('tipo', 'cultural')
    
    if tipo_atividade == 'cultural' and not request.user.is_coordenador_cultural:
        messages.error(request, 'Não tem permissão para criar actividades culturais.')
        return redirect('coordenador_cultural_dashboard')
    if tipo_atividade == 'ciencia_tecnologia' and not request.user.is_coordenador_ciencia:
        messages.error(request, 'Não tem permissão para criar actividades de ciência.')
        return redirect('coordenador_ciencia_dashboard')
    
    # Buscar todas as turmas para seleção
    turmas = Turma.objects.all().order_by('curso', 'nome')
    
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao', '')
            selecao_turmas = request.POST.get('selecao_turmas', 'todas')
            curso_selecionado = request.POST.get('curso_selecionado', '')
            turmas_selecionadas_ids = request.POST.getlist('turmas_selecionadas')
            
            # Criar atividade
            atividade = Atividade.objects.create(
                tipo_atividade=tipo_atividade,
                nome=nome,
                descricao=descricao,
                finalizada=False,
                criterios_avaliacao='',
                max_pontos_por_aluno=0,  # Extra-curricular não tem max por aluno
            )
            
            # Salvar critérios
            criterios_nomes = request.POST.getlist('criterio_nome[]')
            criterios_pontos = request.POST.getlist('criterio_pontos[]')
            for nome_criterio, pontos in zip(criterios_nomes, criterios_pontos):
                if nome_criterio and pontos:
                    CriterioAtividade.objects.create(
                        atividade=atividade, nome=nome_criterio, pontos=int(pontos)
                    )
            
            # Selecionar turmas baseado na escolha
            turmas_a_adicionar = []
            if selecao_turmas == 'todas':
                turmas_a_adicionar = Turma.objects.all()
            elif selecao_turmas == 'por_curso' and curso_selecionado:
                turmas_a_adicionar = Turma.objects.filter(curso=curso_selecionado)
            elif selecao_turmas == 'especificas' and turmas_selecionadas_ids:
                turmas_a_adicionar = Turma.objects.filter(id__in=turmas_selecionadas_ids)
            
            atividade.turmas.set(turmas_a_adicionar)
            
            messages.success(request, f'Actividade "{nome}" criada com sucesso!')
            
            if tipo_atividade == 'cultural':
                return redirect('coordenador_cultural_dashboard')
            else:
                return redirect('coordenador_ciencia_dashboard')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar atividade: {str(e)}')
    
    context = {
        'turmas': turmas,
        'is_edit': False,
        'tipo': tipo_atividade,
    }
    return render(request, 'core/coordenador_criar_atividade_separado.html', context)


@login_required
@user_passes_test(lambda u: u.is_coordenador_cultural or u.is_coordenador_ciencia)
def coordenador_editar_atividade(request, pk):
    atividade = get_object_or_404(Atividade, id=pk, disciplina__isnull=True)
    tipo_atividade = atividade.tipo_atividade
    
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao', '')
            selecao_cursos = request.POST.get('selecao_cursos')
            curso_selecionado = request.POST.get('curso_selecionado')
            
            atividade.nome = nome
            atividade.descricao = descricao
            
            atividade.criterios.all().delete()
            criterios_nomes = request.POST.getlist('criterio_nome[]')
            criterios_pontos = request.POST.getlist('criterio_pontos[]')
            for nome_criterio, pontos in zip(criterios_nomes, criterios_pontos):
                if nome_criterio and pontos:
                    CriterioAtividade.objects.create(
                        atividade=atividade, nome=nome_criterio, pontos=int(pontos)
                    )
            
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
            messages.success(request, f'Actividade "{nome}" actualizada com sucesso!')
            
            if tipo_atividade == 'cultural':
                return redirect('coordenador_cultural_dashboard')
            else:
                return redirect('coordenador_ciencia_dashboard')
            
        except Exception as e:
            messages.error(request, f'Erro ao actualizar atividade: {str(e)}')
    
    cursos = Turma.CURSO_CHOICES
    selecao_atual = 'ambos' if atividade.todos_cursos else 'um_curso'
    context = {
        'atividade': atividade,
        'cursos': cursos,
        'selecao_atual': selecao_atual,
        'is_edit': True,
        'tipo': tipo_atividade,
    }
    return render(request, 'core/coordenador_criar_atividade_separado.html', context)


@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_coordenador_cultural or u.is_coordenador_ciencia)
def coordenador_eliminar_atividade(request, pk):
    atividade = get_object_or_404(Atividade, id=pk, disciplina__isnull=True)
    
    if request.method == 'POST':
        nome = atividade.nome
        atividade.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Actividade "{nome}" eliminada!'})
        
        messages.success(request, f'Actividade "{nome}" eliminada com sucesso!')
        
        if atividade.tipo_atividade == 'cultural':
            return redirect('coordenador_cultural_dashboard')
        else:
            return redirect('coordenador_ciencia_dashboard')
    
    return render(request, 'core/coordenador_confirmar_delete.html', {'atividade': atividade})


@login_required
@user_passes_test(lambda u: u.is_coordenador_cultural or u.is_coordenador_ciencia)
def coordenador_ver_registos(request, pk):
    atividade = get_object_or_404(Atividade, id=pk, disciplina__isnull=True)
    
    if not atividade.finalizada:
        messages.warning(request, 'Esta actividade ainda não foi finalizada.')
        
        if atividade.tipo_atividade == 'cultural':
            return redirect('coordenador_cultural_dashboard')
        else:
            return redirect('coordenador_ciencia_dashboard')
    
    registos_por_turma = {}
    for turma in atividade.turmas.all():
        pontos_aplicados = atividade.criterios.all().aggregate(total=Sum('pontos'))['total'] or 0
        
        registos_por_turma[turma.id] = {
            'turma': turma,
            'total_pontos': pontos_aplicados,
            'distribuida': atividade.distribuida,
            'criterios': atividade.criterios.all()
        }
    
    context = {
        'atividade': atividade,
        'registos_por_turma': registos_por_turma.values(),
    }
    return render(request, 'core/coordenador_ver_registos.html', context)


@login_required
@user_passes_test(lambda u: u.is_coordenador_cultural or u.is_coordenador_ciencia)
def coordenador_iniciar_atividade(request, pk):
    atividade = get_object_or_404(Atividade, id=pk, disciplina__isnull=True)
    
    if atividade.finalizada:
        messages.error(request, 'Esta atividade já foi finalizada.')
        if atividade.tipo_atividade == 'cultural':
            return redirect('coordenador_cultural_dashboard')
        else:
            return redirect('coordenador_ciencia_dashboard')
    
    turmas = atividade.turmas.all().order_by('curso', 'nome')
    criterios = atividade.criterios.all()
    
    context = {
        'atividade': atividade,
        'turmas': turmas,
        'criterios': criterios,
        'tipo': atividade.tipo_atividade,
    }
    return render(request, 'core/coordenador_iniciar_atividade.html', context)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def coordenador_terminar_atividade(request, pk):
    atividade = get_object_or_404(Atividade, id=pk, disciplina__isnull=True)
    
    if atividade.finalizada:
        return JsonResponse({'success': False, 'erro': 'Atividade já finalizada'})
    
    try:
        data = json.loads(request.body)
        registos = data.get('registos', [])
        
        if not registos:
            return JsonResponse({'success': False, 'erro': 'Nenhum registo para guardar'})
        
        pontos_por_turma = {}
        for reg in registos:
            turma_id = reg['turma_id']
            pontos = reg['pontos']
            if turma_id not in pontos_por_turma:
                pontos_por_turma[turma_id] = 0
            pontos_por_turma[turma_id] += pontos
        
        total_pontos = sum(pontos_por_turma.values())
        
        for turma_id, pontos in pontos_por_turma.items():
            turma = Turma.objects.get(id=turma_id)
            atividade.pontos_turma = pontos
            atividade.save()
        
        atividade.finalizada = True
        atividade.save()
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'erro': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'erro': str(e)})


@login_required
@user_passes_test(lambda u: u.is_coordenador_cultural or u.is_coordenador_ciencia)
def api_buscar_atividades(request):
    search_query = request.GET.get('q', '')
    tipo_atividade = request.GET.get('tipo', 'cultural')
    
    atividades = Atividade.objects.filter(
        disciplina__isnull=True, tipo_atividade=tipo_atividade
    ).order_by('-created_at')
    
    if search_query:
        atividades = atividades.filter(
            Q(nome__icontains=search_query) | Q(descricao__icontains=search_query)
        )
    
    data = []
    for atv in atividades[:20]:
        data.append({
            'id': atv.id,
            'nome': atv.nome,
            'descricao': atv.descricao,
            'criterios': [{'nome': c.nome, 'pontos': c.pontos} for c in atv.criterios.all()],
            'cursos': atv.get_cursos_display if hasattr(atv, 'get_cursos_display') else 'Não especificado',
            'finalizada': atv.finalizada,
        })
    
    return JsonResponse({'success': True, 'atividades': data})


@login_required
def coordenador_redirecionar_dashboard(request):
    if request.user.is_coordenador_cultural:
        return redirect('coordenador_cultural_dashboard')
    elif request.user.is_coordenador_ciencia:
        return redirect('coordenador_ciencia_dashboard')
    else:
        return redirect('index')


# ==================== ALIAS PARA COMPATIBILIDADE ====================

def iniciar_atividade_professor(request, atividade_id):
    return iniciar_atividade_professor_v2(request, atividade_id)