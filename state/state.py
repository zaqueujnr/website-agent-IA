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

    force_research: bool
    force_design: bool
    force_content: bool
    force_code: bool
    force_review: bool