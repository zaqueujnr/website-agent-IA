from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    BaseMessage,
)

from prompt.code import CODE_PROMPT


class CodeAgent:
    def __init__(self, llm):
        self.llm = llm

    def execute(
        self,
        project: dict,
        requirements: dict,
        design: str,
        content: str,
    ) -> BaseMessage:

        response = self.llm.invoke([
            SystemMessage(content=CODE_PROMPT),

            HumanMessage(
            content=f"""
            PROJECT:
            {project}

            REQUIREMENTS:
            {requirements}

            DESIGN:
            {design}

            CONTENT:
            {content}
            """
            ),
        ])

        return response

    def continue_execution(
        self,
        history: list[BaseMessage],
    ) -> BaseMessage:

        response = self.llm.invoke([
            SystemMessage(content=CODE_PROMPT),
            *history,
        ])

        return response
    
    