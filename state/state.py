from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

    project: dict
    requirements: dict
    research: dict
    design: dict
    content: dict
    code: dict
    review: dict

    current_agent: str
    current_step: str

    source_files: dict
    source_structure: dict
