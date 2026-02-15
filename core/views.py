from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

#   USER AUTHENTICATIONS:
#       LOGIN
def login_view(request):

    #       RECEBER OS DADOS DO USUÁRIO
    if request.method == 'POST':
        nome_usuario = request.POST.get('username')
        senha = request.POST.get('password')
    
        #       VERIFICAR SE EXISTE UM USUÁRIO COM AS MESMAS CREDENCIAIS INSERIDAS
        user = authenticate(request, username= nome_usuario, password=senha)
        if user is not None:
        
            #       SE JÁ EXISTE, INICIA A SESSÃO E MOSTRA A TELA DASHBOARD
            login(request, user)
            return redirect('dashboard')

            #       SE NÃO, MOSTRE UMA MENSAGEM DE ERRO NA TELA DE LOGIN
        else:
            messages.error(request, 'Usuário inexistente. por favor crie uma conta')
            return redirect ('login')
    
    return render (request, 'core/login.html')

#       CADASTRO
def cadastro(request):
    
    #       RECEBER OS DADOS DO USUARIO
    if request.method == 'POST':
        nome_usuario = request.POST['username']
        email_usuario = request.POST['email']
        senha1 = request.POST['password1']
        senha2 = request.POST['password2']
        
        #       VERIFICAR SE AS SENHAS SÃO DIFERENTES:
        if senha1 != senha2:
            
            #       Se FOREM DIFERENTES, MOSTRE A TELA DE CADASTRO COM UMA MENSAGEM DE ERRO
            messages.error(request, 'As senhas são diferentes.')
            return redirect ('cadastro')

            #       SE NÃO, VERIFIQUE SE O USUÁRIO JÁ EXISTE NO BANCO DE DADOS
        else:
            if User.objects.filter(username=nome_usuario).exists():
            
                #       Se EXISTE, MOSTRE A TELA DE CADASTRO COM UMA MENSAGEM DE ERRO
                messages.error(request, 'Nome de usuario já existe')
                return redirect('cadastro')

                #       SE NÃO, CRIE UM NOVO USUÁRIO E VÁ PARA A DASHBOARD
            else:
                User.objects.create_user(username=nome_usuario, email=email_usuario, password=senha1)
                return redirect('dashboard')

    return render(request, 'core/cadastro.html')

#       ACTIVITY SCREENS
#           DASHBOARD
def dashboard(request):
    return render(request, 'core/dashboard.html')

def atividade(request):
    return render(request, 'core/atividade.html')

def historico(request):
    return render(request, 'core/historico.html')

def credito(request):
    return render(request, 'core/credito.html')

def perfil(request):
    return render(request, 'core/perfil.html')

def logout_view(request):
    pass

def editar_perfil(request):
    pass

def imagem(request):
    pass