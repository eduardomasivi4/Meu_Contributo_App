from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

# ==================== ALUNO ====================
def login_aluno(request):
    return render(request, 'core/login_aluno.html')

def dashboard_aluno(request):
    return render(request, 'core/dashboard_aluno.html')

def atividades(request):
    return render(request, 'core/atividades.html')

def loja(request):
    return render(request, 'core/loja.html')

# ==================== PROFESSOR ====================
def login_professor(request):
    return render(request, 'core/login_professor.html')

def selecionar_perfil(request):
    return render(request, 'core/selecionar_perfil.html')

def dashboard_professor(request):
    return render(request, 'core/dashboard_professor.html')

# ==================== DIRETOR DE TURMA ====================
def diretor_turma(request):
    return render(request, 'core/diretor_turma.html')

# ==================== COORDENADOR ====================
def coordenador_atividades(request):
    return render(request, 'core/coordenador_atividades.html')