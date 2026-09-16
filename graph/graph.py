from langchain_core.runnables.config import RunnableConfig
from langgraph.constants import START,END
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

from prompt.research import RESEARCH_PROMPT
from prompt.design import DESIGN_PROMPT
from prompt.content import CONTENT_PROMPT
from prompt.code import CODE_PROMPT
from prompt.review import REVIEW_PROMPT
from state.state import State
from tools.write_generated_file import write_generated_file
from utils.utils import load_fast_llm, load_powerful_llm

llm_fast = load_fast_llm()
llm_power_with_tools = load_powerful_llm().bind_tools([write_generated_file])

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

    response = llm_fast.invoke([
        SystemMessage(content=RESEARCH_PROMPT),
        HumanMessage(content=str(state["requirements"])),
    ])

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

    response = llm_fast.invoke([
        SystemMessage(content=DESIGN_PROMPT),
            HumanMessage(
            content=f"""
            REQUIREMENTS:
            {requirements}

            RESEARCH:
            {research}

            """
        ),
    ])

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

    response = llm_fast.invoke([
        SystemMessage(content=CONTENT_PROMPT),
        HumanMessage(
            content=f"""
            RESEARCH:
            {research}

            DESIGN:
            {design}
            """
        ),
    ])

    print("✅ [CONTENT] Finalizado")

    return {
        "content": {
            "result": response.content
        }
    }

def code(state: State, config: RunnableConfig):
    print("💻 [CODE] Iniciando...")

    run = config["configurable"]["run_code"]

    print(f"🔧 run_code: {run}")

    if state.get("code") and not run:
        print("♻️ [CODE] Usando estado salvo")

        return {
            "code": state["code"]
        }

    project = state["project"]
    design = state["design"]["result"]
    content = state["content"]["result"]

    history = state.get("messages", [])

    # Primeira execução do CODE
    if not history:
        print("🆕 [CODE] Iniciando conversa...")

        user_message = HumanMessage(
            content=f"""
            PROJECT:
            {project}

            DESIGN:
            {design}

            CONTENT:
            {content}
            """
        )

        response = llm_power_with_tools.invoke([
            SystemMessage(content=CODE_PROMPT),
            user_message
        ])

        print("🤖 CONTENT:", repr(response.content))
        print("🔧 TOOL CALLS:", response.tool_calls)

        return {
            "messages": [
                user_message,
                response
            ],
            "code": {
                "result": response.content
            }
        }

    # Execuções seguintes após uma tool call
    print("🔄 [CODE] Continuando conversa com histórico...")
    
    response = llm_power_with_tools.invoke([
        SystemMessage(content=CODE_PROMPT),
        *history
    ])

    print("🤖 CONTENT:", repr(response.content))
    print("🔧 TOOL CALLS:", response.tool_calls)

    return {
        "messages": [response],
        "code": {
            "result": response.content
        }
    }

def should_continue(state: State):
    messages = state.get("messages", [])

    if not messages:
        return END

    if messages[-1].tool_calls:
        return "tools"

    return END


def tool_node(state: State):
    message = state["messages"][-1]

    tool_messages = []

    for call in message.tool_calls:
        result = write_generated_file.invoke(call["args"])

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=call["id"],
            )
        )

    return {
        "messages": tool_messages
    }



def build_graph(checkpointer) -> CompiledStateGraph[State, None, State, State]:
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
