# Primeiro, resetar o banco
rm -f db.sqlite3
find core/migrations -name "*.py" -not -name "__init__.py" -delete

# Recriar migrations
python manage.py makemigrations core
python manage.py migrate

# Popular dados
python manage.py popular_dados



## 🔑 LISTA COMPLETA DE TODAS AS CREDENCIAIS DO SISTEMA (DADOS FIXOS)

Aqui estão **TODAS** as credenciais geradas pelo script `popular_dados_fixos.py`:

---

### 👨‍🎓 ALUNOS (24 alunos)

| Nome do Aluno | Nº Processo | Username | Email | Senha | Saldo | Turma |
|---------------|-------------|----------|-------|-------|-------|-------|
| Ricardo Oliveira | 20240001 | ricardo.oliveira | ricardo.oliveira@aluno.caf.ao | `aluno123` | 1250 | 10ª ID |
| Fernanda Santos | 20240002 | fernanda.santos | fernanda.santos@aluno.caf.ao | `aluno123` | 980 | 10ª ID |
| Lucas Almeida | 20240003 | lucas.almeida | lucas.almeida@aluno.caf.ao | `aluno123` | 2100 | 10ª IB |
| Beatriz Costa | 20240004 | beatriz.costa | beatriz.costa@aluno.caf.ao | `aluno123` | 1850 | 10ª IB |
| Rafael Lima | 20240005 | rafael.lima | rafael.lima@aluno.caf.ao | `aluno123` | 3420 | 11ª ID |
| Juliana Ferreira | 20240006 | juliana.ferreira | juliana.ferreira@aluno.caf.ao | `aluno123` | 2980 | 11ª ID |
| Gabriel Souza | 20240007 | gabriel.souza | gabriel.souza@aluno.caf.ao | `aluno123` | 1560 | 11ª IB |
| Mariana Silva | 20240008 | mariana.silva | mariana.silva@aluno.caf.ao | `aluno123` | 2230 | 11ª IB |
| André Rodrigues | 20240009 | andre.rodrigues | andre.rodrigues@aluno.caf.ao | `aluno123` | 4100 | 12ª ID |
| Camila Nunes | 20240010 | camila.nunes | camila.nunes@aluno.caf.ao | `aluno123` | 3870 | 12ª ID |
| Thiago Mendes | 20240011 | thiago.mendes | thiago.mendes@aluno.caf.ao | `aluno123` | 2950 | 12ª IB |
| Larissa Rocha | 20240012 | larissa.rocha | larissa.rocha@aluno.caf.ao | `aluno123` | 3120 | 12ª IB |
| Pedro Henrique | 20240013 | pedro.henrique | pedro.henrique@aluno.caf.ao | `aluno123` | 890 | 10ª EA |
| Amanda Lima | 20240014 | amanda.lima | amanda.lima@aluno.caf.ao | `aluno123` | 1340 | 10ª EA |
| Bruno Cardoso | 20240015 | bruno.cardoso | bruno.cardoso@aluno.caf.ao | `aluno123` | 1670 | 10ª EE |
| Tatiane Oliveira | 20240016 | tatiane.oliveira | tatiane.oliveira@aluno.caf.ao | `aluno123` | 1430 | 10ª EE |
| Felipe Augusto | 20240017 | felipe.augusto | felipe.augusto@aluno.caf.ao | `aluno123` | 2780 | 11ª EA |
| Natália Souza | 20240018 | natalia.souza | natalia.souza@aluno.caf.ao | `aluno123` | 2450 | 11ª EA |
| Vinícius Pereira | 20240019 | vinicius.pereira | vinicius.pereira@aluno.caf.ao | `aluno123` | 1890 | 11ª EE |
| Patrícia Lima | 20240020 | patricia.lima | patricia.lima@aluno.caf.ao | `aluno123` | 2120 | 11ª EE |
| Eduardo Martins | 20240021 | eduardo.martins | eduardo.martins@aluno.caf.ao | `aluno123` | 5230 | 12ª EA |
| Carolina Ribeiro | 20240022 | carolina.ribeiro | carolina.ribeiro@aluno.caf.ao | `aluno123` | 4980 | 12ª EA |
| Guilherme Castro | 20240023 | guilherme.castro | guilherme.castro@aluno.caf.ao | `aluno123` | 3670 | 12ª EE |
| Vanessa Alves | 20240024 | vanessa.alves | vanessa.alves@aluno.caf.ao | `aluno123` | 3890 | 12ª EE |

---

### 👨‍🏫 PROFESSOR (1 usuário)

| Nome | Username | Email | Senha | Cargos |
|------|----------|-------|-------|--------|
| Carlos Mendes | professor.carlos | `professor@caf.ao` | `prof123` | Professor |

---

### 📋 COORDENADOR (1 usuário)

| Nome | Username | Email | Senha | Cargos |
|------|----------|-------|-------|--------|
| Ana Paula | coordenador.ana | `coordenador@caf.ao` | `coord123` | Coordenador |

---

### 👔 DIRETOR DE TURMA (1 usuário)

| Nome | Username | Email | Senha | Cargos | Turma Vinculada |
|------|----------|-------|-------|--------|-----------------|
| João Zinga | diretor.joao | `diretor@caf.ao` | `diretor123` | Diretor de Turma | 12ª EA |

---

## 📋 TABELA RESUMO (TODAS CREDENCIAIS)

| Tipo | Identificador | Senha |
|------|---------------|-------|
| **Aluno** | Nº Processo (20240001 a 20240024) | `aluno123` |
| **Aluno** | Username (ricardo.oliveira, etc.) | `aluno123` |
| **Aluno** | Email (@aluno.caf.ao) | `aluno123` |
| **Professor** | `professor@caf.ao` | `prof123` |
| **Professor** | Username: `professor.carlos` | `prof123` |
| **Coordenador** | `coordenador@caf.ao` | `coord123` |
| **Coordenador** | Username: `coordenador.ana` | `coord123` |
| **Diretor** | `diretor@caf.ao` | `diretor123` |
| **Diretor** | Username: `diretor.joao` | `diretor123` |

---

## 🌐 URLs DE LOGIN

| Perfil | URL para Login |
|--------|----------------|
| Aluno | `http://127.0.0.1:8000/aluno/login/` |
| Professor / Coordenador / Diretor | `http://127.0.0.1:8000/professor/login/` |

---

## 📊 ALUNOS POR TURMA

| Turma | Alunos (Nº Processo) |
|-------|---------------------|
| 10ª ID | 20240001 (Ricardo Oliveira), 20240002 (Fernanda Santos) |
| 10ª IB | 20240003 (Lucas Almeida), 20240004 (Beatriz Costa) |
| 11ª ID | 20240005 (Rafael Lima), 20240006 (Juliana Ferreira) |
| 11ª IB | 20240007 (Gabriel Souza), 20240008 (Mariana Silva) |
| 12ª ID | 20240009 (André Rodrigues), 20240010 (Camila Nunes) |
| 12ª IB | 20240011 (Thiago Mendes), 20240012 (Larissa Rocha) |
| 10ª EA | 20240013 (Pedro Henrique), 20240014 (Amanda Lima) |
| 10ª EE | 20240015 (Bruno Cardoso), 20240016 (Tatiane Oliveira) |
| 11ª EA | 20240017 (Felipe Augusto), 20240018 (Natália Souza) |
| 11ª EE | 20240019 (Vinícius Pereira), 20240020 (Patrícia Lima) |
| 12ª EA | 20240021 (Eduardo Martins), 20240022 (Carolina Ribeiro) |
| 12ª EE | 20240023 (Guilherme Castro), 20240024 (Vanessa Alves) |

---

**✅ Lista completa de todas as credenciais fixas do sistema!** 🚀