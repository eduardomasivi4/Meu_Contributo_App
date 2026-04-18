// Elementos
const saldoElement = document.getElementById('saldoValor');
const saldoGrande = document.getElementById('saldoGrande');
const logoutBtn = document.getElementById('logoutBtn');
const modal = document.getElementById('infoModal');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const modalCloseBtn = document.getElementById('modalCloseBtn');

let saldoAtual = 2450;

function atualizarSaldoDisplay() {
  saldoElement.textContent = saldoAtual.toLocaleString();
  saldoGrande.textContent = saldoAtual.toLocaleString();
}

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

// Participar de atividades
document.querySelectorAll('.btn-participar').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.innerHTML = '⏳';
    setTimeout(() => {
      btn.innerHTML = 'Inscrito!';
      btn.style.background = '#D4A373';
      showModal('✅ Inscrição Realizada!', 'Você se inscreveu na atividade. Ao concluir, receberá os pontos.');
      setTimeout(() => {
        btn.innerHTML = 'Inscrever';
        btn.style.background = '';
      }, 2000);
    }, 500);
  });
});

// Resgatar benefícios
document.querySelectorAll('.btn-resgatar').forEach(btn => {
  btn.addEventListener('click', () => {
    const custo = parseInt(btn.closest('.beneficio-item')?.querySelector('.beneficio-custo')?.innerText.split(' ')[0] || 200);
    
    if (saldoAtual >= custo) {
      saldoAtual -= custo;
      atualizarSaldoDisplay();
      
      btn.innerHTML = '⏳';
      setTimeout(() => {
        btn.innerHTML = 'Resgatado!';
        btn.style.background = '#A58E6F';
        showModal('🎉 Resgate Confirmado!', 'Benefício resgatado. Dirija-se à secretaria.');
        setTimeout(() => {
          btn.innerHTML = 'Resgatar';
          btn.style.background = '';
        }, 2000);
      }, 500);
    } else {
      showModal('❌ Saldo Insuficiente', `Você precisa de ${custo} pontos. Seu saldo é ${saldoAtual}.`, false);
    }
  });
});

// Logout
logoutBtn.addEventListener('click', () => {
  logoutBtn.innerHTML = '⏳';
  setTimeout(() => {
    logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Sair';
    window.location.href = '/';
  }, 500);
});

// Fechar modal
modalCloseBtn.addEventListener('click', hideModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) hideModal();
});