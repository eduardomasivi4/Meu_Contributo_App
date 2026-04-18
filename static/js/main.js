// Elementos
const btnEntrar = document.getElementById('btnEntrar');
const tipoModal = document.getElementById('tipoModal');
const btnAluno = document.getElementById('btnAluno');
const btnProfessor = document.getElementById('btnProfessor');
const closeTipoModal = document.getElementById('closeTipoModal');
const subtitleElement = document.getElementById('typingSubtitle');
const originalText = "Sistema de Gestão de Mérito Estudantil";

// Animação de digitação
function typeWriterAnimation() {
  if (!subtitleElement) return;
  subtitleElement.textContent = '';
  let i = 0;
  function type() {
    if (i < originalText.length) {
      subtitleElement.textContent += originalText.charAt(i);
      i++;
      setTimeout(type, 40);
    }
  }
  type();
}

function showModal() {
  tipoModal.classList.add('active');
  const modalContainer = tipoModal.querySelector('.modal-container');
  modalContainer.style.animation = 'none';
  modalContainer.offsetHeight;
  modalContainer.style.animation = 'fadeInForm 0.3s ease';
}

function hideModal() {
  tipoModal.classList.remove('active');
}

// Eventos
btnEntrar.addEventListener('click', () => {
  btnEntrar.style.transform = 'scale(0.98)';
  setTimeout(() => {
    btnEntrar.style.transform = '';
  }, 150);
  showModal();
});

btnAluno.addEventListener('click', () => {
  btnAluno.style.transform = 'scale(0.95)';
  setTimeout(() => {
    btnAluno.style.transform = '';
  }, 150);
  hideModal();
  window.location.href = '/aluno/login/';
});

btnProfessor.addEventListener('click', () => {
  btnProfessor.style.transform = 'scale(0.95)';
  setTimeout(() => {
    btnProfessor.style.transform = '';
  }, 150);
  hideModal();
  window.location.href = '/professor/login/';
});

closeTipoModal.addEventListener('click', hideModal);
tipoModal.addEventListener('click', (e) => {
  if (e.target === tipoModal) hideModal();
});

// Iniciar animação
setTimeout(typeWriterAnimation, 500);