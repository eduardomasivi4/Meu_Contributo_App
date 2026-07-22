# Primeiro, resetar o banco
rm -f db.sqlite3
find core/migrations -name "*.py" -not -name "__init__.py" -delete

# Recriar migrations
python manage.py makemigrations core
python manage.py migrate

# Popular dados (versão com credenciais reduzidas + Diretor Pedagógico)
python manage.py popular_dados



## 🔑 LISTA COMPLETA DE TODAS AS CREDENCIAIS DO SISTEMA (VERSÃO REDUZIDA + DIRETOR PEDAGÓGICO)

Aqui estão **TODAS** as credenciais geradas pelo script `popular_dados.py` (versão reduzida com Diretor Pedagógico):

---

### 👨‍🎓 ALUNOS (12 alunos – 1 por turma)

| Nome do Aluno | Nº Processo | Username | Email | Senha | Saldo | Turma |
|---------------|-------------|----------|-------|-------|-------|-------|
| Ricardo Oliveira | 20240001 | ricardo.oliveira | ricardo.oliveira@aluno.caf.ao | `aluno123` | 1250 | 10ª ID |
| Lucas Almeida | 20240003 | lucas.almeida | lucas.almeida@aluno.caf.ao | `aluno123` | 2100 | 10ª IB |
| Rafael Lima | 20240005 | rafael.lima | rafael.lima@aluno.caf.ao | `aluno123` | 3420 | 11ª ID |
| Gabriel Souza | 20240007 | gabriel.souza | gabriel.souza@aluno.caf.ao | `aluno123` | 1560 | 11ª IB |
| André Rodrigues | 20240009 | andre.rodrigues | andre.rodrigues@aluno.caf.ao | `aluno123` | 4100 | 12ª ID |
| Thiago Mendes | 20240011 | thiago.mendes | thiago.mendes@aluno.caf.ao | `aluno123` | 2950 | 12ª IB |
| Pedro Henrique | 20240013 | pedro.henrique | pedro.henrique@aluno.caf.ao | `aluno123` | 890 | 10ª EA |
| Bruno Cardoso | 20240015 | bruno.cardoso | bruno.cardoso@aluno.caf.ao | `aluno123` | 1670 | 10ª EE |
| Felipe Augusto | 20240017 | felipe.augusto | felipe.augusto@aluno.caf.ao | `aluno123` | 2780 | 11ª EA |
| Vinícius Pereira | 20240019 | vinicius.pereira | vinicius.pereira@aluno.caf.ao | `aluno123` | 1890 | 11ª EE |
| Eduardo Martins | 20240021 | eduardo.martins | eduardo.martins@aluno.caf.ao | `aluno123` | 5230 | 12ª EA |
| Guilherme Castro | 20240023 | guilherme.castro | guilherme.castro@aluno.caf.ao | `aluno123` | 3670 | 12ª EE |

---

### 👨‍🏫 PROFESSORES (1 por disciplina)

Cada disciplina do sistema possui um professor vinculado. A tabela abaixo lista todos os professores gerados (exemplo para algumas disciplinas; o padrão é `prof.<disciplina>`).

| Nome | Username | Email | Senha | Disciplina |
|------|----------|-------|-------|------------|
| Prof_Eletrotécnica Default | prof.eletrotecnica | prof.eletrotecnica@caf.ao | `prof123` | Eletrotécnica |
| Prof_SEAC Default | prof.seac | prof.seac@caf.ao | `prof123` | SEAC |
| Prof_TIC Default | prof.tic | prof.tic@caf.ao | `prof123` | TIC |
| Prof_TLP Default | prof.tlp | prof.tlp@caf.ao | `prof123` | TLP |
| Prof_TREI Default | prof.trei | prof.trei@caf.ao | `prof123` | TREI |
| Prof_Eletrónica Default | prof.eletronica | prof.eletronica@caf.ao | `prof123` | Eletrónica |
| Prof_Informática Default | prof.informatica | prof.informatica@caf.ao | `prof123` | Informática |
| Prof_POL Default | prof.pol | prof.pol@caf.ao | `prof123` | POL |
| Prof_S.D.T Default | prof.s.d.t | prof.s.d.t@caf.ao | `prof123` | S.D.T |
| Prof_T.T Default | prof.t.t | prof.t.t@caf.ao | `prof123` | T.T |
| Prof_Telecomunicações Default | prof.telecomunicacoes | prof.telecomunicacoes@caf.ao | `prof123` | Telecomunicações |
| Prof_D.T Default | prof.d.t | prof.d.t@caf.ao | `prof123` | D.T |
| Prof_Empreendedorismo Default | prof.empreendedorismo | prof.empreendedorismo@caf.ao | `prof123` | Empreendedorismo |
| Prof_FAI Default | prof.fai | prof.fai@caf.ao | `prof123` | FAI |
| Prof_Física Default | prof.fisica | prof.fisica@caf.ao | `prof123` | Física |
| Prof_Gestão de Projetos Default | prof.gestao_de_projetos | prof.gestao_de_projetos@caf.ao | `prof123` | Gestão de Projetos |
| Prof_Inglês Default | prof.ingles | prof.ingles@caf.ao | `prof123` | Inglês |
| Prof_Língua Portuguesa Default | prof.lingua_portuguesa | prof.lingua_portuguesa@caf.ao | `prof123` | Língua Portuguesa |
| Prof_Matemática Default | prof.matematica | prof.matematica@caf.ao | `prof123` | Matemática |
| Prof_OGI Default | prof.ogi | prof.ogi@caf.ao | `prof123` | OGI |
| Prof_Química Default | prof.quimica | prof.quimica@caf.ao | `prof123` | Química |

> **Nota**: Além destes, existe um professor genérico (`professor.generico@caf.ao` / `prof123`) utilizado para transações que não estão vinculadas a uma disciplina específica.

---

### 👨‍🏫 DIRETORES DE TURMA (1 por turma)

Cada turma tem um diretor de turma. A tabela abaixo lista todos os diretores criados (padrão: `diretor.<turma>`).

| Nome | Username | Email | Senha | Turma Vinculada |
|------|----------|-------|-------|-----------------|
| Diretor_10ª ID Turma | diretor.10a_id | diretor.10a_id@caf.ao | `diretor123` | 10ª ID |
| Diretor_10ª IB Turma | diretor.10a_ib | diretor.10a_ib@caf.ao | `diretor123` | 10ª IB |
| Diretor_11ª ID Turma | diretor.11a_id | diretor.11a_id@caf.ao | `diretor123` | 11ª ID |
| Diretor_11ª IB Turma | diretor.11a_ib | diretor.11a_ib@caf.ao | `diretor123` | 11ª IB |
| Diretor_12ª ID Turma | diretor.12a_id | diretor.12a_id@caf.ao | `diretor123` | 12ª ID |
| Diretor_12ª IB Turma | diretor.12a_ib | diretor.12a_ib@caf.ao | `diretor123` | 12ª IB |
| Diretor_10ª EA Turma | diretor.10a_ea | diretor.10a_ea@caf.ao | `diretor123` | 10ª EA |
| Diretor_10ª EE Turma | diretor.10a_ee | diretor.10a_ee@caf.ao | `diretor123` | 10ª EE |
| Diretor_11ª EA Turma | diretor.11a_ea | diretor.11a_ea@caf.ao | `diretor123` | 11ª EA |
| Diretor_11ª EE Turma | diretor.11a_ee | diretor.11a_ee@caf.ao | `diretor123` | 11ª EE |
| Diretor_12ª EA Turma | diretor.12a_ea | diretor.12a_ea@caf.ao | `diretor123` | 12ª EA |
| Diretor_12ª EE Turma | diretor.12a_ee | diretor.12a_ee@caf.ao | `diretor123` | 12ª EE |

---

### 📋 COORDENADORES (1 por curso)

| Nome | Username | Email | Senha | Curso |
|------|----------|-------|-------|-------|
| Coordenador_Informatica Curso | coordenador.informatica | coordenador.informatica@caf.ao | `coord123` | Informática |
| Coordenador_Eletronica Curso | coordenador.eletronica | coordenador.eletronica@caf.ao | `coord123` | Eletrónica |

---

### 🎓 DIRETOR PEDAGÓGICO (1 único usuário)

| Nome | Username | Email | Senha | Cargos |
|------|----------|-------|-------|--------|
| Manuel Costa | diretor.pedagogico | `pedagogico@caf.ao` | `pedagogico123` | Diretor Pedagógico |

---

## 📋 TABELA RESUMO (TODAS CREDENCIAIS)

| Tipo | Identificador | Senha |
|------|---------------|-------|
| **Aluno** | Nº Processo (20240001, 20240003, ... 20240023) | `aluno123` |
| **Aluno** | Username (ricardo.oliveira, lucas.almeida, ...) | `aluno123` |
| **Aluno** | Email (@aluno.caf.ao) | `aluno123` |
| **Professor** | `prof.<disciplina>@caf.ao` (ex: prof.matematica@caf.ao) | `prof123` |
| **Professor (genérico)** | `prof.generico@caf.ao` | `prof123` |
| **Diretor de Turma** | `diretor.<turma>@caf.ao` (ex: diretor.10a_id@caf.ao) | `diretor123` |
| **Coordenador** (Informática) | `coordenador.informatica@caf.ao` | `coord123` |
| **Coordenador** (Eletrónica) | `coordenador.eletronica@caf.ao` | `coord123` |
| **Diretor Pedagógico** | `pedagogico@caf.ao` | `pedagogico123` |

---

## 🌐 URLs DE LOGIN

| Perfil | URL para Login |
|--------|----------------|
| Aluno | `http://127.0.0.1:8000/aluno/login/` |
| Professor / Diretor de Turma / Coordenador / Diretor Pedagógico | `http://127.0.0.1:8000/professor/login/` |

---

## 📊 ALUNOS POR TURMA (1 por turma)

| Turma | Aluno (Nº Processo) |
|-------|---------------------|
| 10ª ID | 20240001 (Ricardo Oliveira) |
| 10ª IB | 20240003 (Lucas Almeida) |
| 11ª ID | 20240005 (Rafael Lima) |
| 11ª IB | 20240007 (Gabriel Souza) |
| 12ª ID | 20240009 (André Rodrigues) |
| 12ª IB | 20240011 (Thiago Mendes) |
| 10ª EA | 20240013 (Pedro Henrique) |
| 10ª EE | 20240015 (Bruno Cardoso) |
| 11ª EA | 20240017 (Felipe Augusto) |
| 11ª EE | 20240019 (Vinícius Pereira) |
| 12ª EA | 20240021 (Eduardo Martins) |
| 12ª EE | 20240023 (Guilherme Castro) |

---

**✅ Lista completa de todas as credenciais fixas do sistema (versão reduzida + Diretor Pedagógico)!** 🚀