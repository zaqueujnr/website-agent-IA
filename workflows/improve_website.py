from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from state.state import State

from agents.research_agent_improve import ResearchAgentImprove
from agents.audit_agent import AuditAgent
from agents.design_agent_improve import DesignAgentImprove
from agents.content_agent_improve import ContentAgentImprove
from agents.code_agent_improve import CodeAgent
from agents.tools import tool_node, should_continue
from langchain_core.runnables.config import RunnableConfig
from tools.write_generated_file import write_generated_file
from utils.utils import load_fast_llm, load_powerful_llm
from utils.source_reader import read_project_files

llm_fast = load_fast_llm()
llm_power_with_tools = load_powerful_llm().bind_tools(
    [write_generated_file]
)

research_agent = ResearchAgentImprove(llm_fast)
audit_agent = AuditAgent(llm_fast)
design_agent = DesignAgentImprove(llm_fast)
content_agent = ContentAgentImprove(llm_fast)
code_agent = CodeAgent(llm_power_with_tools)

def read_source(
    state: State,
):
    print("📂 [READ_SOURCE] Lendo arquivos...")

    source_path = state["project"]["source_path"]

    source_files = read_project_files(source_path)

    print(
        f"✅ [READ_SOURCE] "
        f"{len(source_files)} arquivos lidos"
    )

    return {
        "source_files": source_files
    }

def research(state: State, config: RunnableConfig):
    print("🔎 [RESEARCH] Iniciando...")
    run = config["configurable"]["run_research"]
    print(f"🔧 run_research: {run}")


    if state.get("research") and not run:
        print("♻️ [RESEARCH] Usando estado salvo")

        return {
            "research": state["research"]
        }

    print("🤖 [RESEARCH] Executando LLM...")

    requirements = state["requirements"]
    source_files = state["source_files"]
    
    result = research_agent.execute(
           requirements, source_files
       )
    
    return {
        "research": {
            "result": result
        }
    }

def design(state: State, config: RunnableConfig):
    print("🎨 [DESIGN] Iniciando...")

    run = config["configurable"]["run_design"]

    print(f"🔧 run_design: {run}")

    if state.get("design") and not run:
        print("♻️ [DESIGN] Usando estado salvo")

        return {
            "design": state["design"]
        }

    print("🤖 [DESIGN] Executando LLM...")

    research = state["research"]["result"]


    result = design_agent.execute(
           research
       )

    return {
        "design": {
            "result": result
        }
    }

def content(state: State, config: RunnableConfig):
    print("✍️ [CONTENT] Iniciando...")

    run = config["configurable"]["run_content"]

    print(f"🔧 run_content: {run}")

    if state.get("content") and not run:
        print("♻️ [CONTENT] Usando estado salvo")

        return {
            "content": state["content"]
        }

    print("🤖 [CONTENT] Executando LLM...")

    research = state["research"]["result"]
    design = state["design"]["result"]
    source_files = state["source_files"]

    result = content_agent.execute(
           research, design, source_files
       )

    print("✅ [CONTENT] Finalizado")

    return {
        "content": {
            "result": result
        }
    }

def code(state: State, config: RunnableConfig):
    print("💻 [CODE] Iniciando...")

    run = config["configurable"].get("run_code", True)

    print(f"🔧 run_code: {run}")

    # Reutiliza o código salvo quando run_code=False
    if state.get("code") and not run:
        print("♻️ [CODE] Usando estado salvo")

        return {
            "code": state["code"]
        }

    project = state["project"]
    requirements = state["requirements"]
    research = state["research"]["result"]
    design = state["design"]["result"]
    content = state["content"]["result"]
    source_files = state.get("source_files", {})

    history = state.get("messages", [])

    # Primeira execução do CODE
    if not history:
        print("🆕 [CODE] Iniciando conversa...")

        response = code_agent.execute(
            project=project,
            requirements=requirements,
            design=design,
            content=content,
            research=research
        )

    # Execuções seguintes após tool calls
    else:
        print("🔄 [CODE] Continuando conversa com histórico...")

        response = code_agent.continue_execution(
            history=history
        )

    print("🤖 CONTENT:", repr(response.content))
    print("🔧 TOOL CALLS:", response.tool_calls)

    return {
        "messages": [response],
        "code": {
            "result": response.content
        }
    }

def build_improve_graph(
    checkpointer,
) -> CompiledStateGraph:

    builder = StateGraph(State)

    # Nodes
    builder.add_node("read_source", read_source)
    builder.add_node("research", research)
    builder.add_node("design", design)
    builder.add_node("content", content)
    builder.add_node("code", code)
    builder.add_node("tools", tool_node)

    # Entry point
    builder.add_edge(START, "read_source")

    # Workflow sequence
    builder.add_edge("read_source", "research")
    builder.add_edge("research", "design")
    builder.add_edge("design", "content")
    builder.add_edge("content", "code")

    # Tool execution
    builder.add_conditional_edges(
        "code",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    builder.add_edge("tools", "code")

    # Compile
    return builder.compile(
        checkpointer=checkpointer
    )