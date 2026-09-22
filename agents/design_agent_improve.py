
from langchain_core.messages import SystemMessage, HumanMessage
from prompt.design import DESIGN_PROMPT
class DesignAgentImprove:
    def __init__(self, llm):
        self.llm = llm

    def execute(self, research: dict) -> str:
        response = self.llm.invoke([
            SystemMessage(content=DESIGN_PROMPT),
            HumanMessage(content=str(research)
            ),
        ])

        return response.content