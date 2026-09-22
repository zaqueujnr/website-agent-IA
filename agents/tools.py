from langgraph.constants import END
from langchain_core.messages import ToolMessage
from state.state import State
from tools.write_generated_file import write_generated_file


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