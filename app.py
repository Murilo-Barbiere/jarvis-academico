"""
app.py — JARVIS Acadêmico · Interface Streamlit
────────────────────────────────────────────────
Execute com : streamlit run app.py
CLI (sem UI): python main.py
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import sys
from datetime import datetime

import streamlit as st

# ── garante que a raiz do projeto esteja no path ────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.setting import (
    JARVIS_QUERY_REWRITER_ENABLED,
    MODEL_NAME,
    PDF_PATH,
    VECTOR_STORE_PATH,
)
from src.llm.GammaAgente import JarvisAgent
from src.llm.query_rewriter import QueryRewriterService
from src.rag.VetorStore import VetorStore
from src.rag.chunker import preparar_documentos
from src.rag.loader import ler_pdfs
from src.tools.tool_manager import executar_tool
from src.utils.logger import configurar_logger

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="JARVIS Acadêmico",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**JARVIS Acadêmico**  \n"
            "Assistente universitário inteligente com RAG + Tool Calling.  \n\n"
            "- Interface web: `streamlit run app.py`  \n"
            "- Terminal: `python main.py`"
        )
    },
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <style>
    /* Remove padding excessivo no topo */
    .block-container { padding-top: 1.2rem; padding-bottom: 0; }

    /* Bordinha sutil nos expanders de tool */
    [data-testid="stExpander"] {
        border: 1px solid rgba(74, 158, 255, 0.25);
        border-radius: 6px;
        margin-top: 0.35rem;
        margin-bottom: 0.1rem;
    }

    /* Caption da query reescrita */
    .rewritten-query {
        color: #7eb8f7;
        font-size: 0.82rem;
        font-style: italic;
        margin-bottom: 4px;
    }

    /* Caixa de boas-vindas */
    .welcome-box {
        border: 1px solid rgba(74, 158, 255, 0.3);
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        background: rgba(74, 158, 255, 0.05);
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════════
# RECURSOS CACHEADOS  (compartilhados entre todas as abas/sessões)
# ═══════════════════════════════════════════════════════════════════════════════


@st.cache_resource(show_spinner=False)
def _carregar_vetor_store() -> "VetorStore | None":
    """
    Carrega o índice FAISS do disco ou o reconstrói a partir dos PDFs.
    Resultado é compartilhado entre todas as sessões (operação de leitura).
    """
    logger = configurar_logger()
    vs = VetorStore(MODEL_NAME)

    if vs.carregar(VECTOR_STORE_PATH):
        logger.info(f"[UI] Vector Store carregado — {len(vs.chunks)} chunks")
        return vs

    logger.info("[UI] Reconstruindo Vector Store a partir dos PDFs…")
    docs = ler_pdfs(PDF_PATH)
    if not docs:
        logger.warning("[UI] Nenhum PDF encontrado — RAG desabilitado.")
        return None

    chunks, meta = preparar_documentos(docs)
    vs.adicionar_documentos(chunks, meta)
    vs.salvar(VECTOR_STORE_PATH)
    logger.info(f"[UI] Vector Store criado — {len(chunks)} chunks")
    return vs


@st.cache_resource(show_spinner=False)
def _carregar_rewriter() -> QueryRewriterService:
    """Instancia o Query Rewriter (stateless, pode ser compartilhado)."""
    return QueryRewriterService()


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO DA SESSÃO
# ═══════════════════════════════════════════════════════════════════════════════


def _init_state() -> None:
    """Inicializa variáveis de session_state ausentes."""
    if "jarvis" not in st.session_state:
        # Cada aba/sessão tem seu próprio agente com memória independente
        st.session_state.jarvis = JarvisAgent()
    if "messages" not in st.session_state:
        # Cada item: {role, content, tool_info?, query_reescrita?}
        st.session_state.messages = []


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES DE UI
# ═══════════════════════════════════════════════════════════════════════════════

_TOOL_ICONS: dict[str, str] = {
    "consultar_agenda": "📅",
    "consultar_semana": "🗓️",
    "adicionar_na_agenda": "➕",
    "listar_tarefas": "📋",
    "listar_tarefas_concluidas": "☑️",
    "listar_trabalhos": "📁",
    "listar_provas": "📝",
    "listar_materias": "🏫",
    "adicionar_tarefa": "✅",
    "concluir_tarefa": "✔️",
    "remover_tarefa": "🗑️",
    "alterar_tarefa": "✏️",
    "buscar_material_rag": "🔍",
    "obter_resumo_academico": "📊",
    "planejar_estudos": "🗺️",
    "adicionar_materia": "🏫",
    "sair_da_materia": "🚪",
    "alterar_materia": "✏️",
    "remover_prova": "🗑️",
    "remover_trabalho": "🗑️",
    "alterar_prova": "✏️",
    "alterar_trabalho": "✏️",
    "remover_horario": "🗑️",
    "alterar_horario": "✏️",
}

_ACOES_RAPIDAS: list[tuple[str, str]] = [
    ("📅  Agenda de Hoje",   "O que tenho na agenda hoje? Mostre aulas, provas e trabalhos dos próximos 7 dias."),
    ("🗓️  Grade da Semana",   "Mostre minha grade de horários da semana completa, de segunda a sexta."),
    ("📋  Tarefas Pendentes", "Liste todas as minhas tarefas pendentes."),
    ("📝  Provas",            "Liste todas as minhas provas cadastradas."),
    ("📁  Trabalhos",         "Liste todos os meus trabalhos cadastrados."),
    ("🏫  Disciplinas",       "Liste todas as minhas disciplinas cadastradas com professor e sala."),
    ("📊  Resumo Acadêmico",  "Como está minha situação acadêmica? Quais são as prioridades mais urgentes?"),
    ("🗺️  Planejar Estudos",  "Monte um plano de estudos personalizado e detalhado para mim."),
]

_EXEMPLOS: list[str] = [
    "Quais aulas tenho hoje?",
    "Adiciona uma prova de Redes para amanhã às 19h",
    "O que é uma árvore binária de busca?",
    "Como funciona o protocolo DNS?",
    "Cria a tarefa 'Estudar para P1' para sexta-feira",
    "Conclui a tarefa 'Revisar SQL'",
    "Muda a prova de IA para 2026-07-15",
    "Qual a diferença entre LSTM e GRU?",
    "Adiciona a disciplina Computação em Nuvem",
    "Remove o horário de Redes na segunda-feira às 20:50",
]

_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
_DIAS_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira",
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo",
]

# ═══════════════════════════════════════════════════════════════════════════════
# LÓGICA DE PROCESSAMENTO
# ═══════════════════════════════════════════════════════════════════════════════


def _processar_mensagem(
    query: str,
    vetor_store: "VetorStore | None",
    rewriter: QueryRewriterService,
    use_rewriter: bool,
) -> dict:
    """
    Pipeline: Query Rewriting → Tool Decision → Tool Execution → Response.

    Returns
    -------
    dict com chaves:
        resposta        : str
        tool_info       : dict | None
        query_reescrita : str | None   (None se igual à original)
    """
    # 1 ── Query Rewriting ─────────────────────────────────────────────────────
    query_agente = rewriter.rewrite(query) if use_rewriter else query

    # 2 ── Decisão de Tool ─────────────────────────────────────────────────────
    plano = st.session_state.jarvis.decidir_tool(query_agente)
    nome_tool = plano.get("tool") if plano else "nenhuma"

    tool_info = None
    contexto = ""

    # 3 ── Execução da Tool ────────────────────────────────────────────────────
    if nome_tool and nome_tool != "nenhuma":
        argumentos = plano.get("arguments", {})

        # Verifica se RAG está disponível antes de chamar busca semântica
        if nome_tool == "buscar_material_rag" and vetor_store is None:
            contexto = (
                "O módulo de busca em PDFs está indisponível: "
                "nenhum arquivo PDF foi encontrado na pasta configurada."
            )
            tool_info = {
                "tool": nome_tool,
                "arguments": argumentos,
                "result": {"aviso": "RAG indisponível — sem PDFs indexados."},
            }
        else:
            try:
                resultado = executar_tool(nome_tool, argumentos, vetor_store)
                contexto = json.dumps(resultado, ensure_ascii=False, default=str)
                tool_info = {
                    "tool": nome_tool,
                    "arguments": argumentos,
                    "result": resultado,
                }
            except Exception as exc:
                contexto = f"Erro ao executar a ferramenta '{nome_tool}': {exc}"
                tool_info = {
                    "tool": nome_tool,
                    "arguments": argumentos,
                    "result": {"erro": str(exc)},
                }
    else:
        contexto = "Nenhuma informação extra necessária além do histórico da conversa."

    # 4 ── Geração da Resposta ─────────────────────────────────────────────────
    if nome_tool == "planejar_estudos":
        resposta = st.session_state.jarvis.gerar_plano_estudos(query, contexto)
    else:
        resposta = st.session_state.jarvis.gerar_resposta_final(query, contexto)

    return {
        "resposta": resposta,
        "tool_info": tool_info,
        "query_reescrita": query_agente if query_agente != query else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# COMPONENTES DE UI
# ═══════════════════════════════════════════════════════════════════════════════


def _ui_tool_expander(tool_info: dict) -> None:
    """Expander colapsável com detalhes da ferramenta utilizada."""
    nome = tool_info["tool"]
    icon = _TOOL_ICONS.get(nome, "🔧")

    with st.expander(f"{icon} Ferramenta: **{nome}**", expanded=False):
        col_a, col_b = st.columns(2, gap="medium")

        with col_a:
            st.caption("📤 **Parâmetros enviados**")
            args = tool_info.get("arguments") or {}
            if args:
                st.json(args)
            else:
                st.caption("*(nenhum parâmetro)*")

        with col_b:
            st.caption("📥 **Resultado**")
            result = tool_info.get("result")
            if result is None:
                st.caption("*(sem resultado)*")
            elif isinstance(result, (dict, list)):
                st.json(result)
            else:
                st.code(str(result), language=None)


def _ui_render_messages() -> None:
    """Itera sobre o histórico e renderiza cada mensagem."""
    for msg in st.session_state.messages:
        avatar = "🎓" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            # Metadados do assistente (aparecem antes do texto)
            if msg["role"] == "assistant":
                if msg.get("query_reescrita"):
                    st.caption(f'🔄 *Query otimizada: "{msg["query_reescrita"]}"*')
                if msg.get("tool_info"):
                    _ui_tool_expander(msg["tool_info"])
            st.markdown(msg["content"])


def _ui_sidebar(vetor_store: "VetorStore | None", rewriter_default: bool) -> tuple:
    """
    Renderiza a barra lateral.

    Returns
    -------
    (prompt_rapido: str | None, use_rewriter: bool)
    """
    prompt_rapido: str | None = None

    with st.sidebar:
        # ── Identidade ─────────────────────────────────────
        st.markdown("## 🎓 JARVIS\n*Acadêmico*")
        st.caption("Assistente universitário inteligente")
        st.divider()

        # ── Status ─────────────────────────────────────────
        if vetor_store is not None:
            n = len(vetor_store.chunks)
            st.success(f"✅ RAG ativo — **{n:,}** chunks")
        else:
            st.warning("⚠️ RAG desativado\n*(sem PDFs indexados)*")

        n_msgs = len(st.session_state.messages)
        if n_msgs:
            st.info(f"💬 **{n_msgs}** mensagem(s) no histórico")

        st.divider()

        # ── Ações Rápidas ──────────────────────────────────
        st.subheader("⚡ Ações Rápidas")
        for label, prompt in _ACOES_RAPIDAS:
            if st.button(label, use_container_width=True):
                prompt_rapido = prompt

        st.divider()

        # ── Configurações ──────────────────────────────────
        st.subheader("⚙️ Configurações")
        use_rewriter = st.toggle(
            "Query Rewriter",
            value=rewriter_default,
            help=(
                "Quando ativo, o JARVIS reformula automaticamente "
                "sua pergunta antes de processar, melhorando a precisão "
                "das buscas no RAG e a seleção das ferramentas."
            ),
        )

        st.divider()

        # ── Limpar Histórico ───────────────────────────────
        if st.button(
            "🗑️ Limpar Histórico",
            use_container_width=True,
            type="secondary",
            disabled=(n_msgs == 0),
        ):
            st.session_state.messages = []
            st.session_state.jarvis.memory.clear()
            st.rerun()

        st.divider()

        # ── Exemplos de Perguntas ──────────────────────────
        with st.expander("💡 Exemplos de perguntas", expanded=False):
            for ex in _EXEMPLOS:
                st.caption(f"• *{ex}*")

    return prompt_rapido, use_rewriter


def _ui_welcome() -> None:
    """Exibe mensagem de boas-vindas quando o histórico está vazio."""
    st.markdown(
        """
        <div class="welcome-box">
        <h4>👋 Olá! Sou o <strong>JARVIS Acadêmico</strong>.</h4>
        <p>Posso te ajudar com:</p>
        <ul>
          <li>📅 Consultar agenda, horários e próximas provas</li>
          <li>✅ Gerenciar tarefas, trabalhos e disciplinas</li>
          <li>🔍 Responder dúvidas com base nos seus PDFs</li>
          <li>🗺️ Criar planos de estudo personalizados</li>
        </ul>
        <p style="margin-bottom:0; font-size: 0.88rem; color: #8899aa;">
          Use os botões de <strong>Ações Rápidas</strong> na barra lateral ou
          digite sua pergunta abaixo.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _ui_header() -> None:
    """Renderiza o cabeçalho com título e data atual."""
    agora = datetime.now()
    col_title, col_date = st.columns([3, 1])

    with col_title:
        st.title("💬 JARVIS Acadêmico")
        st.caption(
            "Pergunte sobre aulas, provas e tarefas — "
            "ou tire dúvidas sobre o conteúdo dos PDFs."
        )

    with col_date:
        st.markdown(
            f"""
            <div style="text-align:right; padding-top:0.6rem; line-height:1.4">
              <span style="font-size:1.5rem">📆</span><br>
              <strong>{_DIAS_SEMANA[agora.weekday()]}</strong><br>
              <span style="color:#8899aa; font-size:0.85rem">
                {agora.day} de {_MESES[agora.month-1]} de {agora.year}
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    _init_state()

    # Carrega recursos pesados (cacheados — rápido a partir da 2ª execução)
    with st.spinner("🔄 Inicializando JARVIS…"):
        vetor_store = _carregar_vetor_store()
        rewriter = _carregar_rewriter()

    # Sidebar — retorna prompt rápido e configuração do rewriter
    prompt_rapido, use_rewriter = _ui_sidebar(vetor_store, JARVIS_QUERY_REWRITER_ENABLED)

    # Cabeçalho
    _ui_header()
    st.divider()

    # Boas-vindas (somente sem histórico)
    if not st.session_state.messages:
        _ui_welcome()

    # Histórico de mensagens
    _ui_render_messages()

    # ── Determina o Prompt ─────────────────────────────────────────────────
    prompt: str | None = prompt_rapido  # ação rápida tem prioridade

    chat_input = st.chat_input("💬 Pergunte ao JARVIS…")
    if chat_input:
        prompt = chat_input

    # ── Processamento ──────────────────────────────────────────────────────
    if prompt:
        # 1. Exibe mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # 2. Processa e exibe resposta do JARVIS
        resposta = ""
        tool_info = None
        query_reescrita = None

        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("JARVIS está pensando…"):
                try:
                    resultado = _processar_mensagem(
                        query=prompt,
                        vetor_store=vetor_store,
                        rewriter=rewriter,
                        use_rewriter=use_rewriter,
                    )
                    resposta = resultado["resposta"]
                    tool_info = resultado["tool_info"]
                    query_reescrita = resultado["query_reescrita"]

                    # Metadados antes da resposta
                    if query_reescrita:
                        st.caption(f'🔄 *Query otimizada: "{query_reescrita}"*')
                    if tool_info:
                        _ui_tool_expander(tool_info)

                    st.markdown(resposta)

                except Exception as exc:
                    resposta = f"❌ Ocorreu um erro inesperado: `{exc}`"
                    st.error(resposta)

        # 3. Salva no histórico para próximas reruns
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": resposta,
                "tool_info": tool_info,
                "query_reescrita": query_reescrita,
            }
        )


if __name__ == "__main__":
    main()