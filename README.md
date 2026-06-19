# 🎓 JARVIS Acadêmico

O JARVIS (Journaling & Academic Retrieval Virtual Intelligent System) é um **assistente acadêmico pessoal** que opera via linguagem natural. Ele combina a potência de modelos de linguagem (LLMs) com um banco de dados operacional e um sistema de RAG (Retrieval-Augmented Generation) para ser o cérebro da sua vida universitária.

---

## 📁 Estrutura do Projeto

```
jarvis-academico/
├── main.py                          # Ponto de entrada (Terminal)
├── interface.py                     # Interface Web (Streamlit)
├── data/                            # PDFs do dataset acadêmico
├── db/
│   ├── agenda.db                    # Banco de dados SQLite
│   ├── faiss.index                  # Índice vetorial persistido
│   └── chunks_meta.pkl              # Metadados do RAG
├── logs/
│   └── app.log                      # Logs da aplicação
└── src/
    ├── config/
    │   └── setting.py               # Configurações e variáveis de ambiente
    ├── database/
    │   ├── db_utils.py              # CRUD e lógica de acesso ao banco
    │   ├── init_db.py               # Inicialização do schema
    │   └── seed_db.py               # Dados de exemplo
    ├── llm/
    │   ├── Agente.py                # Orquestrador (Memória + Tools + LLM)
    │   ├── memory.py                # Gestão de memória de curto prazo
    │   └── SYSTEM_PROMPT.py         # Catálogo de ferramentas e regras do agente
    ├── rag/
    │   ├── chunker.py               # Processamento de texto em fragmentos
    │   ├── context_builder.py       # Seleção e ranking de contexto
    │   ├── loader.py                # Extração de texto de PDFs
    │   └── VetorStore.py            # Busca vetorial e persistência FAISS
    ├── tools/
    │   ├── study_planner.py         # Serviço de geração de planos de estudo
    │   ├── tool_manager.py          # Roteador de execução das ferramentas
    │   └── tools.py                 # Implementação das funções de ferramenta
    └── utils/
        └── logger.py                # Sistema de logging centralizado
```

---

## 🚀 Como Executar

### 1. Instalação

```bash
git clone https://github.com/seu-usuario/jarvis-academico.git
cd jarvis-academico
pip install -r requirements.txt
```

### 2. Configuração (.env)

Crie um arquivo `.env` na raiz do projeto:

```env
API_KEY=sua_chave_aqui
BASE_URL=https://openrouter.ai/api/v1
MODEL=google/gemini-pro-1.5           # Recomendado para melhor raciocínio
```

### 3. Inicialização

```bash
# Inicializar banco e dados de exemplo
python -m src.database.init_db
python -m src.database.seed_db

# Opcional: O sistema indexa os PDFs automaticamente na primeira execução
```

### 4. Escolha sua Interface

**Terminal (CLI):**
```bash
python main.py
```

**Web (Streamlit):**
```bash
streamlit run interface.py
```

---

## 🧠 Funcionalidades Principais

### 1. RAG Acadêmico
O JARVIS "lê" seus materiais didáticos (PDFs na pasta `/data`) e responde perguntas técnicas baseadas estritamente no conteúdo fornecido, citando fontes.

### 2. Gestão de Agenda e Tarefas
Integração total com banco de dados para gerenciar aulas, provas, trabalhos e tarefas pendentes através de linguagem natural.

### 3. Modo Quiz (Active Recall) 🆕
Diga *"Me faça um quiz sobre [tópico]"* e o JARVIS entrará em modo de teste interativo. Ele formulará perguntas baseadas no seu material, avaliará suas respostas e identificará lacunas de conhecimento.

### 4. Planejador de Estudos Inteligente
Ao pedir um plano de estudos, o JARVIS cruza seus dados de agenda (prazos próximos) com o conteúdo técnico dos PDFs para criar um cronograma priorizado e focado no que realmente importa.

---

## 🛠️ Catálogo de Ferramentas (26 Tools)

O JARVIS utiliza **Multi-Tool Calling**, podendo acionar várias ferramentas para uma única frase do usuário.

| Categoria | Principais Ferramentas |
|---|---|
| **Consulta** | `consultar_agenda`, `consultar_semana`, `listar_materias`, `obter_resumo_academico` |
| **Escrita** | `adicionar_na_agenda`, `adicionar_tarefa`, `adicionar_materia` |
| **Edição** | `alterar_tarefa`, `alterar_prova`, `alterar_trabalho`, `alterar_materia`, `alterar_horario` |
| **Remoção** | `remover_tarefa`, `remover_prova`, `remover_trabalho`, `remover_horario`, `sair_da_materia` |
| **Conhecimento** | `buscar_material_rag`, `planejar_estudos` |
| **Interação** | `iniciar_quiz`, `encerrar_quiz`, `concluir_tarefa` |

---

## 🧪 Testes

```bash
pytest
```

---

## 🏗️ Arquitetura

O JARVIS utiliza um fluxo de **Raciocínio → Ação → Observação → Síntese**:

1.  **Decisão:** O `Agente` analisa a query com o `SYSTEM_PROMPT` e decide quais ferramentas (em ordem sequencial) devem ser usadas.
2.  **Execução:** O `tool_manager` orquestra as chamadas para as funções em `tools.py` ou serviços especializados como o `StudyPlannerService`.
3.  **Contextualização:** Se necessário, o `VetorStore` recupera chunks de texto relevantes dos materiais didáticos.
4.  **Geração:** Um gerador de resposta especializado (Normal, Quiz ou Plano de Estudo) sintetiza os dados em uma resposta amigável e formatada em Markdown.

---

## 🔮 Possíveis Melhorias

- [x] Interface Web (Streamlit)
- [x] Persistência do Vector Store em disco
- [ ] Suporte a OCR para PDFs escaneados
- [ ] Memória de longo prazo (histórico salvo em DB)
- [ ] Integração com Google Calendar / Notion
- [ ] Sistema de notificações via Telegram/WhatsApp

---

## 📝 Documentação do Dataset
*Consulte o final do README original para detalhes sobre as obras de Cormen, Kurose e Szwarcfiter incluídas no projeto.*
