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

# llm_with_tools = load_llm().bind_tools([write_generated_file])
llm_fast = load_fast_llm()
llm_power = load_powerful_llm()

def research(state: State, config: RunnableConfig):
    thread_id = config["configurable"]["thread_id"]
    print(f"🧵 thread_id: {thread_id}")
    print("🔎 [RESEARCH] Iniciando...")
    run = config["configurable"]["run_research"]

    print(f"🔧 run_research: {run}")

    if state.get("research") and not run:
        print("♻️ [RESEARCH] Usando estado salvo")

        return {
            "research": state["research"]
        }

    print("🤖 [RESEARCH] Executando LLM...")

    # response = llm.invoke([
    #     SystemMessage(content=RESEARCH_PROMPT),
    #     HumanMessage(content=str(state["requirements"])),
    # ])

    return {
        "research": {
            "result": "response.content"
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

    # response = llm.invoke([
    #     SystemMessage(content=DESIGN_PROMPT),
    #     HumanMessage(content=str(research)),
    # ])

    return {
        "design": {
            "result": "response.content"
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

    # response = llm.invoke([
    #     SystemMessage(content=CONTENT_PROMPT),
    #     HumanMessage(
    #         content=f"""
    #         RESEARCH:
    #         {research}

    #         DESIGN:
    #         {design}
    #         """
    #     ),
    # ])

    print("✅ [CONTENT] Finalizado")

    return {
        "content": {
            "result": "response.content"
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

    requirements = state["requirements"]
    research = state["research"]["result"]
    design = state["design"]["result"]
    content = state["content"]["result"]

    print("🤖 [CODE] Executando LLM...")

    # response = llm.invoke([
    #     SystemMessage(content=CODE_PROMPT),
    #     HumanMessage(
    #         content=f"""
    #         REQUIREMENTS:
    #         {requirements}

    #         RESEARCH:
    #         {research}

    #         DESIGN:
    #         {design}

    #         CONTENT:
    #         {content}
    #         """
    #     ),
    # ])

    return {
        "code": {
            "result": "response.content"
        }
    }

def review(state: State, config: RunnableConfig):
    print("🔍 [REVIEW] Iniciando...")
    print("💻 [REVIEW] Iniciando...")
    run = config["configurable"]["run_review"]

    print(f"🔧 run_review: {run}")

    if state.get("review") and not run:
        print("♻️ [REVIEW] Usando estado salvo")

        return {
            "review": state["review"]
        }
    
    # response = llm.invoke([
    #     SystemMessage(content=REVIEW_PROMPT),
    #     HumanMessage(
    #         content=f"""
    #         Requirements:
    #         {state["requirements"]}

    #         Research:
    #         {state["research"]["result"]}

    #         Design:
    #         {state["design"]["result"]}

    #         Content:
    #         {state["content"]["result"]}

    #         Code:
    #         {state["code"]["result"]}
    #         """
    #             ),
    #         ])

    return {
        "review": {
            "result": "response.content"
        }
    }

def tool_node(state: State):
    call = state["messages"][-1].tool_calls[0]

    result = write_generated_file.invoke(call["args"])

    return {
        "messages": [
            ToolMessage(
                content=str(result),
                tool_call_id=call["id"],
            )
        ]
    }

def should_continue(state: State):
    messages = state.get("messages", [])

    if not messages:
        return END

    if messages[-1].tool_calls:
        return "tools"

    return END

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
