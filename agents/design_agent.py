from langchain_core.messages import SystemMessage, HumanMessage
from prompt.audit import DESIGN_PROMPT
class DesignAgent:
    def __init__(self, llm):
        self.llm = llm

    def execute(self, requirements: dict, research: dict) -> str:
        response = self.llm.invoke([
            SystemMessage(content=DESIGN_PROMPT),
            HumanMessage(content=f"""
            REQUIREMENTS:
            {requirements}

            RESEARCH:
            {research}
            """
            ),
        ])

        return response.content
