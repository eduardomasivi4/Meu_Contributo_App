from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Atividade
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'core/login.html')

@login_required
def dashboard(request):
    total = sum(a.creditos for a in Atividade.objects.filter(usuario=request.user))
    return render(request, 'core/dashboard.html', {'total': total})

@login_required
def atividade(request):
    if request.method == "POST":
        Atividade.objects.create(
            usuario=request.user,
            nome=request.POST['nome'],
            tipo=request.POST['tipo'],
            creditos=request.POST['creditos'],
            data=request.POST['data'],
            descricao=request.POST['descricao']
        )
        return redirect('dashboard')
    return render(request, 'core/atividade.html')

@login_required
def historico(request):
    atividades = Atividade.objects.filter(usuario=request.user)
    return render(request, 'core/historico.html', {'atividades': atividades})

@login_required
def credito(request):
    total = sum(a.creditos for a in Atividade.objects.filter(usuario=request.user))
    return render(request, 'core/credito.html', {'total': total})

@login_required
def perfil(request):
    return render(request, 'core/perfil.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def editar_perfil(request):
    pass

def imagem(request):
    pass

def cadastro(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        senha1 = request.POST['password1']
        senha2 = request.POST['password2']

        if senha1 != senha2:
            messages.error(request, "As senhas não coincidem")
            return redirect('cadastro')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Usuário já existe")
            return redirect('cadastro')

        User.objects.create_user(
            username=username,
            email=email,
            password=senha1
        )

        messages.success(request, "Conta criada com sucesso")
        return redirect('login')

    return render(request, 'core/cadastro.html')