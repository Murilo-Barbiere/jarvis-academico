# 🎓 JARVIS Acadêmico

Um assistente inteligente para organização universitária que combina **RAG (Retrieval-Augmented Generation)** com **tool calling** para responder dúvidas acadêmicas, gerenciar tarefas, provas e horários.

---

## 📁 Estrutura do Projeto

```
jarvis-academico/
├── main.py                          # Ponto de entrada da aplicação
├── data/                            # PDFs do dataset acadêmico (10 arquivos)
├── db/
│   └── agenda.db                    # Banco de dados SQLite
├── logs/
│   └── app.log                      # Logs da aplicação
└── src/
    ├── config/
    │   └── setting.py               # Configurações e variáveis de ambiente
    ├── database/
    │   ├── db_utils.py              # Funções de acesso ao banco de dados
    │   ├── init_db.py               # Inicialização do schema do banco
    │   └── seed_db.py               # Dados de exemplo para o banco
    ├── llm/
    │   ├── GammaAgente.py           # Cliente LLM (perguntar + decidir tool)
    │   └── SYSTEM_PROMPT.py         # Prompt do sistema com definição das tools
    ├── rag/
    │   ├── chunker.py               # Divisão e limpeza de textos em chunks
    │   ├── context_builder.py       # Montagem do contexto para o LLM
    │   ├── loader.py                # Leitura e extração de texto dos PDFs
    │   └── VetorStore.py            # Indexação e busca vetorial com FAISS
    ├── tools/
    │   ├── tool_manager.py          # Roteador de execução das tools
    │   └── tools.py                 # Implementação de cada ferramenta
    └── utils/
        └── logger.py                # Configuração de logging
```

---

## 🚀 Como Executar

### 1. Pré-requisitos

- Python 3.10+
- Dependências instaladas (veja abaixo)
- Uma chave de API compatível com OpenAI (ex: OpenRouter, Groq, etc.)

### 2. Instalação

```bash
git clone https://github.com/seu-usuario/jarvis-academico.git
cd jarvis-academico
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
API_KEY=sua_chave_aqui
BASE_URL=https://openrouter.ai/api/v1   # ou outra base compatível
MODEL=mistralai/mistral-7b-instruct     # ou outro modelo de sua preferência
```

### 4. Inicializar o Banco de Dados

```bash
python -m src.database.init_db
python -m src.database.seed_db   # opcional: carrega dados de exemplo
```

### 5. Executar

```bash
python main.py
```

---

## 💬 Como Usar

Após iniciar, o sistema entra em loop de perguntas. Digite sua pergunta em linguagem natural:

```
Pergunta: Quais aulas tenho hoje?
Pergunta: Adiciona uma prova de Redes para amanhã
Pergunta: Qual a diferença entre LSTM e GRU?
Pergunta: Lista minhas tarefas pendentes
Pergunta: sair
```

Digite `sair` para encerrar.

---

## 🛠️ Ferramentas Disponíveis

| Ferramenta | Descrição |
|---|---|
| `consultar_agenda` | Aulas de hoje + provas nos próximos 7 dias |
| `consultar_semana` | Grade completa da semana (seg–sex) |
| `adicionar_na_agenda` | Adiciona provas, tarefas ou horários recorrentes |
| `listar_tarefas` | Lista tarefas pendentes |
| `adicionar_tarefa` | Atalho rápido para criar tarefas |
| `concluir_tarefa` | Marca uma tarefa como concluída |
| `buscar_material_rag` | Busca semântica nos PDFs indexados |
| `adicionar_materia` | Cadastra uma nova disciplina |
| `sair_da_materia` | Remove uma disciplina (e seus horários/provas) |
| `listar_materias` | Lista todas as disciplinas cadastradas |

---

## 🧠 Arquitetura

```
Usuário
   │
   ▼
main.py
   │
   ├─── GammaAgente.decidir_tool()   ←── SYSTEM_PROMPT (tool calling via JSON)
   │         │
   │    Tool chamada?
   │         │
   │    Sim ─┴─ Não
   │    │         │
   │    ▼         ▼
   │ tool_manager  VetorStore.buscar()
   │    │               │
   │    ▼               ▼
   │  tools.py     context_builder
   │    │               │
   └────┴───────────────┘
              │
              ▼
   GammaAgente.perguntar_llm()
              │
              ▼
           Resposta
```

O fluxo principal funciona em duas etapas:

1. **Decisão de tool:** O LLM analisa a pergunta e retorna um JSON indicando qual ferramenta usar (ou nenhuma).
2. **Resposta final:** Com o contexto (resultado da tool ou chunks do RAG), o LLM gera a resposta em linguagem natural.

---

## 🗄️ Banco de Dados

O SQLite (`db/agenda.db`) contém 4 tabelas:

- **disciplinas** — nome, professor, sala
- **horarios** — dia da semana, hora início/fim, vínculo com disciplina
- **provas** — data, descrição, vínculo com disciplina
- **tarefas** — título, descrição, data de entrega, status, prioridade

---

## 📦 Principais Dependências

| Pacote | Uso |
|---|---|
| `openai` | Cliente para APIs compatíveis com OpenAI |
| `sentence-transformers` | Geração de embeddings (`all-MiniLM-L6-v2`) |
| `faiss-cpu` | Indexação e busca vetorial |
| `langchain-text-splitters` | Divisão de textos em chunks |
| `pymupdf` (`fitz`) | Extração de texto de PDFs |
| `python-dotenv` | Carregamento de variáveis de ambiente |

---

## ⚙️ Configurações (`setting.py`)

| Variável | Padrão | Descrição |
|---|---|---|
| `PDF_PATH` | `data` | Pasta com os PDFs do dataset |
| `DB_PATH` | `db/agenda.db` | Caminho do banco SQLite |
| `CHUNK_SIZE` | `500` | Tamanho dos chunks de texto |
| `CHUNK_OVERLAP` | `100` | Sobreposição entre chunks |
| `MODEL_NAME` | `all-MiniLM-L6-v2` | Modelo de embeddings |

---

## 📝 Logs

Todas as operações são registradas em `logs/app.log`:

- Queries recebidas
- Tools chamadas e seus argumentos/resultados
- Chunks recuperados pelo RAG
- Erros e avisos

---

## 🔮 Possíveis Melhorias

- [ ] Interface web (Streamlit / FastAPI)
- [ ] Suporte a OCR para PDFs escaneados
- [ ] Memória de conversação entre sessões
- [ ] Persistência do Vector Store em disco
- [ ] Notificações de provas e tarefas próximas
- [ ] Autenticação multi-usuário
