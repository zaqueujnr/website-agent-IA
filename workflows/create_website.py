from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from state.state import State

from agents.research_agent import ResearchAgent
from agents.design_agent import DesignAgent
from agents.content_agent import ContentAgent
from agents.code_agent import CodeAgent
from agents.tools import tool_node, should_continue
from langchain_core.runnables.config import RunnableConfig
from tools.write_generated_file import write_generated_file
from utils.utils import load_fast_llm, load_powerful_llm

llm_fast = load_fast_llm()
llm_power_with_tools = load_powerful_llm().bind_tools(
    [write_generated_file]
)

research_agent = ResearchAgent(llm_fast)
design_agent = DesignAgent(llm_fast)
content_agent = ContentAgent(llm_fast)
code_agent = CodeAgent(llm_power_with_tools)


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

    response = research_agent.execute(requirements)

    return {
        "research": {
            "result": response.content
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

    requirements = state["requirements"]
    research = state["research"]["result"]

    response = design_agent.execute(requirements, research)

    return {
        "design": {
            "result": response.content
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

    response = content_agent.execute(research, design)

    print("✅ [CONTENT] Finalizado")

    return {
        "content": {
            "result": response.content
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
    design = state["design"]["result"]
    content = state["content"]["result"]

    history = state.get("messages", [])

    # Primeira execução do CODE
    if not history:
        print("🆕 [CODE] Iniciando conversa...")

        response = code_agent.execute(
            project=project,
            requirements=requirements,
            design=design,
            content=content,
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

def build_create_graph(checkpointer) -> CompiledStateGraph[State, None, State, State]:
    builder = StateGraph(State)

    builder.add_node("research", research)
    builder.add_node("design", design)
    builder.add_node("content", content)
    builder.add_node("code", code)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "research")

    builder.add_edge("research", "design")
    builder.add_edge("design", "content")
    builder.add_edge("content", "code")

    builder.add_conditional_edges(
        "code",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    builder.add_edge("tools", "code")

    return builder.compile(
        checkpointer=checkpointer
    )
