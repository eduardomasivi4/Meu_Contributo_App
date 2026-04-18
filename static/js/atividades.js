// Dados das atividades
const atividades = [
  {
    id: 1,
    nome: "Workshop de Robótica com Arduino",
    categoria: "ciencia",
    descricao: "Aprenda a programar microcontroladores e construir robôs autônomos.",
    requisitos: [
      "Conhecimentos básicos de lógica de programação",
      "Disponibilidade para 4 sessões de 3 horas",
      "Trazer computador portátil (opcional)",
      "Trabalho em equipe para projeto final"
    ],
    pontos: 200,
    status: "disponivel",
    data: "Novembro 2023"
  },
  {
    id: 2,
    nome: "Feira de Ciências: Sustentabilidade",
    categoria: "ciencia",
    descricao: "Apresentação de projetos sobre energias renováveis e conservação ambiental.",
    requisitos: [
      "Desenvolver um protótipo ou pesquisa científica",
      "Apresentação oral de 10 minutos",
      "Relatório escrito do projeto",
      "Participação em todas as sessões de orientação"
    ],
    pontos: 300,
    status: "disponivel",
    data: "Dezembro 2023"
  },
  {
    id: 3,
    nome: "Oficina de Teatro e Expressão Artística",
    categoria: "cultura",
    descricao: "Desenvolva habilidades de atuação, expressão corporal e improvisação.",
    requisitos: [
      "Disponibilidade para ensaios semanais",
      "Participar da apresentação final",
      "Criar uma pequena cena em grupo",
      "Trazer roupa preta para o ensaio geral"
    ],
    pontos: 180,
    status: "disponivel",
    data: "Novembro 2023"
  },
  {
    id: 4,
    nome: "Concurso de Fotografia Artística",
    categoria: "cultura",
    descricao: "Registre momentos únicos e concorra a prêmios com sua criatividade.",
    requisitos: [
      "Enviar 3 fotografias originais",
      "Tema: 'A beleza do quotidiano'",
      "Participar da exposição final no auditório",
      "As fotos devem ser tiradas durante o período do concurso"
    ],
    pontos: 150,
    status: "disponivel",
    data: "Janeiro 2024"
  },
  {
    id: 5,
    nome: "Olimpíada de Matemática",
    categoria: "ciencia",
    descricao: "Competição de resolução de problemas matemáticos desafiadores.",
    requisitos: [
      "Inscrição prévia com o professor de matemática",
      "Realizar prova escrita de 2 horas",
      "Participar de 2 sessões de treino",
      "Classificação mínima de 60% na fase eliminatória"
    ],
    pontos: 250,
    status: "andamento",
    data: "Em andamento"
  },
  {
    id: 6,
    nome: "Clube de Leitura e Debate Literário",
    categoria: "cultura",
    descricao: "Encontros semanais para discutir obras clássicas e contemporâneas.",
    requisitos: [
      "Ler o livro proposto antes de cada encontro",
      "Participar ativamente dos debates",
      "Apresentar uma análise crítica de uma obra",
      "Frequência mínima de 75%"
    ],
    pontos: 160,
    status: "andamento",
    data: "Em andamento"
  }
];

// Elementos
const atividadesGrid = document.getElementById('atividadesGrid');
const categoryBtns = document.querySelectorAll('.category-btn');
const modal = document.getElementById('infoModal');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const modalCloseBtn = document.getElementById('modalCloseBtn');

let categoriaAtiva = 'todas';

function showModal(title, message) {
  modalTitle.textContent = title;
  modalMessage.textContent = message;
  modal.classList.add('active');
}

function hideModal() {
  modal.classList.remove('active');
}

function getStatusInfo(status) {
  if (status === 'disponivel') {
    return { text: 'Disponível', class: 'status-disponivel', icon: 'fa-calendar-check' };
  }
  return { text: 'Em Andamento', class: 'status-andamento', icon: 'fa-spinner' };
}

function renderAtividades() {
  let filtered = [...atividades];
  
  if (categoriaAtiva !== 'todas') {
    filtered = atividades.filter(a => a.categoria === categoriaAtiva);
  }
  
  if (filtered.length === 0) {
    atividadesGrid.innerHTML = `
      <div class="sem-atividades">
        <i class="fas fa-calendar-times"></i>
        <h3>Nenhuma atividade encontrada</h3>
        <p>Não há atividades disponíveis nesta categoria no momento.</p>
      </div>
    `;
    return;
  }
  
  atividadesGrid.innerHTML = filtered.map(a => {
    const statusInfo = getStatusInfo(a.status);
    const headerClass = a.categoria === 'ciencia' ? 'ciencia' : 'cultura';
    const categoriaNome = a.categoria === 'ciencia' ? 'Ciência e Tecnologia' : 'Culturais';
    const categoriaIcon = a.categoria === 'ciencia' ? '🔬' : '🎭';
    
    return `
      <div class="atividade-card" data-id="${a.id}">
        <div class="atividade-header ${headerClass}">
          <div class="atividade-categoria">
            ${categoriaIcon} ${categoriaNome}
          </div>
          <h3>${a.nome}</h3>
        </div>
        <div class="atividade-body">
          <div class="requisitos-section">
            <div class="requisitos-title">
              <i class="fas fa-clipboard-list"></i> Critérios de Avaliação
            </div>
            <ul class="requisitos-lista">
              ${a.requisitos.map(r => `<li><i class="fas fa-check-circle"></i> ${r}</li>`).join('')}
            </ul>
          </div>
          <div class="atividade-pontos">
            <i class="fas fa-star"></i> ${a.pontos} pontos
          </div>
          <div class="atividade-footer">
            <span class="status-badge ${statusInfo.class}">
              <i class="fas ${statusInfo.icon}"></i> ${statusInfo.text}
            </span>
            <span class="info-text">
              <i class="fas fa-calendar"></i> ${a.data}
            </span>
          </div>
        </div>
      </div>
    `;
  }).join('');
  
  // Adicionar evento de clique nos cards
  document.querySelectorAll('.atividade-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = parseInt(card.dataset.id);
      const atividade = atividades.find(a => a.id === id);
      if (atividade) {
        showModal(
          `📋 ${atividade.nome}`,
          `Pontuação: ${atividade.pontos} pontos\n\nRequisitos:\n${atividade.requisitos.map(r => `• ${r}`).join('\n')}`
        );
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
    renderAtividades();
  });
});

// Logout
document.getElementById('logoutBtn')?.addEventListener('click', () => {
  window.location.href = '/';
});

// Fechar modal
modalCloseBtn.addEventListener('click', hideModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) hideModal();
});

// Inicializar
renderAtividades();