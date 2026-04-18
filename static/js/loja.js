// Dados dos benefícios
const beneficios = [
  {
    id: 1,
    nome: "Boletim de Notas Oficial",
    categoria: "academico",
    descricao: "Impressão colorida do boletim de notas oficial com selo do colégio.",
    pontos: 200,
    icone: "fa-file-alt",
    validade: "30 dias"
  },
  {
    id: 2,
    nome: "Folhas para Provas (Professor)",
    categoria: "academico",
    descricao: "10 folhas pautadas para provas do professor, com identificação oficial.",
    pontos: 30,
    icone: "fa-copy",
    validade: "Uso imediato",
    precoOriginal: 50,
    reduzido: true
  },
  {
    id: 3,
    nome: "Folhas para Provas Trimestrais",
    categoria: "academico",
    descricao: "20 folhas pautadas para as provas trimestrais oficiais.",
    pontos: 60,
    icone: "fa-scroll",
    validade: "Uso imediato",
    precoOriginal: 100,
    reduzido: true
  },
  {
    id: 4,
    nome: "Internet Grátis (7 dias)",
    categoria: "tecnologia",
    descricao: "Acesso Wi-Fi de alta velocidade em todo o campus por 7 dias consecutivos.",
    pontos: 300,
    icone: "fa-wifi",
    validade: "Ativação imediata"
  },
  {
    id: 5,
    nome: "Internet Grátis (30 dias)",
    categoria: "tecnologia",
    descricao: "Acesso Wi-Fi de alta velocidade em todo o campus por um mês inteiro.",
    pontos: 1000,
    icone: "fa-wifi",
    validade: "Ativação imediata"
  }
];

// Elementos
const beneficiosGrid = document.getElementById('beneficiosGrid');
const saldoValor = document.getElementById('saldoValor');
const logoutBtn = document.getElementById('logoutBtn');
const modal = document.getElementById('infoModal');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const categoryBtns = document.querySelectorAll('.category-btn');

let saldoAtual = 2450;
let categoriaAtiva = 'todos';

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

function atualizarSaldoDisplay() {
  saldoValor.textContent = saldoAtual.toLocaleString();
}

function renderBeneficios() {
  let filtered = [...beneficios];
  
  if (categoriaAtiva !== 'todos') {
    filtered = beneficios.filter(b => b.categoria === categoriaAtiva);
  }
  
  if (filtered.length === 0) {
    beneficiosGrid.innerHTML = `
      <div class="sem-atividades">
        <i class="fas fa-box-open"></i>
        <h3>Nenhum benefício encontrado</h3>
        <p>Não há benefícios disponíveis nesta categoria no momento.</p>
      </div>
    `;
    return;
  }
  
  beneficiosGrid.innerHTML = filtered.map(b => {
    const categoriaNome = b.categoria === 'academico' ? 'Acadêmico' : 'Tecnologia';
    const categoriaIcon = b.categoria === 'academico' ? '📚' : '💻';
    const isReduzido = b.reduzido === true;
    
    return `
      <div class="atividade-card">
        <div class="atividade-header ciencia">
          <div class="atividade-categoria">
            ${categoriaIcon} ${categoriaNome}
          </div>
          <h3>${b.nome}</h3>
        </div>
        <div class="atividade-body">
          <p style="color: #8B694C; font-size: 14px; margin-bottom: 16px;">${b.descricao}</p>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div class="atividade-pontos" style="${isReduzido ? 'background: #FEF3C7; color: #D4A373;' : ''}">
              <i class="fas fa-star"></i> ${b.pontos} pts
              ${isReduzido ? `<span style="font-size: 11px; margin-left: 6px; text-decoration: line-through;">${b.precoOriginal} pts</span>` : ''}
            </div>
            <div class="info-text">
              <i class="fas fa-clock"></i> ${b.validade}
            </div>
          </div>
          ${isReduzido ? `
            <div style="background: #FEF3C7; padding: 4px 10px; border-radius: 20px; font-size: 11px; color: #D4A373; margin-bottom: 12px; display: inline-block;">
              <i class="fas fa-tag"></i> Preço reduzido!
            </div>
          ` : ''}
          <button class="btn-resgatar-beneficio" data-id="${b.id}" data-nome="${b.nome}" data-pontos="${b.pontos}">
            <i class="fas fa-exchange-alt"></i> Resgatar
          </button>
        </div>
      </div>
    `;
  }).join('');
  
  // Adicionar eventos aos botões
  document.querySelectorAll('.btn-resgatar-beneficio').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = parseInt(btn.dataset.id);
      const nome = btn.dataset.nome;
      const pontos = parseInt(btn.dataset.pontos);
      
      if (saldoAtual >= pontos) {
        saldoAtual -= pontos;
        atualizarSaldoDisplay();
        
        btn.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Processando';
        btn.disabled = true;
        
        setTimeout(() => {
          btn.innerHTML = '<i class="fas fa-exchange-alt"></i> Resgatar';
          btn.disabled = false;
          showModal('🎉 Resgate Confirmado!', `Você resgatou "${nome}" por ${pontos} pontos.\n\nDirija-se à secretaria para retirar o benefício.`);
          renderBeneficios();
        }, 500);
      } else {
        showModal('❌ Saldo Insuficiente', `Você precisa de ${pontos} pontos para resgatar "${nome}".\nSeu saldo atual é ${saldoAtual} pontos.`, false);
      }
    });
  });
}

// Categorias
categoryBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    categoryBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    categoriaAtiva = btn.dataset.categoria;
    renderBeneficios();
  });
});

// Logout
if (logoutBtn) {
  logoutBtn.addEventListener('click', () => {
    window.location.href = '/';
  });
}

// Fechar modal
modalCloseBtn.addEventListener('click', hideModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) hideModal();
});

// Inicializar
atualizarSaldoDisplay();
renderBeneficios();