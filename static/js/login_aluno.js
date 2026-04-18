// Elementos
const backBtn = document.getElementById('backBtn');
const loginForm = document.getElementById('loginForm');
const btnLogin = document.getElementById('btnLogin');
const forgotLink = document.getElementById('forgotLink');
const professorLink = document.getElementById('professorLink');
const modal = document.getElementById('infoModal');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const modalCloseBtn = document.getElementById('modalCloseBtn');

// Função para mostrar modal
function showModal(title, message, isSuccess = true) {
  modalTitle.textContent = title;
  modalMessage.textContent = message;
  const modalIcon = modal.querySelector('.modal-icon');
  
  if (isSuccess) {
    modalIcon.style.background = 'linear-gradient(135deg, #2B7A4B, #1E5A38)';
    modalIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
  } else {
    modalIcon.style.background = 'linear-gradient(135deg, #D4A373, #B5835A)';
    modalIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
  }
  
  modal.classList.add('active');
}

function hideModal() {
  modal.classList.remove('active');
}

// Voltar para tela inicial
backBtn.addEventListener('click', () => {
  backBtn.style.transform = 'scale(0.95)';
  setTimeout(() => {
    backBtn.style.transform = '';
    window.location.href = '/';
  }, 150);
});

// Login
btnLogin.addEventListener('click', (e) => {
  e.preventDefault();
  
  const processo = document.getElementById('processoInput').value.trim();
  const senha = document.getElementById('senhaInput').value;
  
  if (!processo || !senha) {
    showModal('⚠️ Atenção', 'Por favor, preencha o Número de Processo e a Senha.', false);
    return;
  }
  
  btnLogin.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Processando...';
  btnLogin.disabled = true;
  
  setTimeout(() => {
    btnLogin.innerHTML = '<i class="fas fa-arrow-right-to-bracket"></i> ENTRAR NO SISTEMA';
    btnLogin.disabled = false;
    showModal('✅ Sucesso!', 'Login realizado com sucesso!\nBem-vindo ao sistema de mérito.');
    
    // Redirecionar após 2 segundos
    setTimeout(() => {
      window.location.href = '/aluno/dashboard/';
    }, 2000);
  }, 1500);
});

// Esqueci a senha
forgotLink.addEventListener('click', (e) => {
  e.preventDefault();
  showModal('🔐 Recuperar Senha', 'Entre em contato com a secretaria acadêmica para recuperar seu acesso.\n\nEmail: secretaria@colegioarvore.ao', false);
});

// Acessar área do professor
professorLink.addEventListener('click', (e) => {
  e.preventDefault();
  professorLink.style.opacity = '0.7';
  setTimeout(() => {
    professorLink.style.opacity = '';
    window.location.href = '/professor/login/';
  }, 200);
});

// Fechar modal
modalCloseBtn.addEventListener('click', hideModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) hideModal();
});