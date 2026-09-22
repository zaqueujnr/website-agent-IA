from langchain_core.messages import  SystemMessage, HumanMessage
from prompt.research import RESEARCH_PROMPT

class ResearchAgent:
    def __init__(self, llm):
        self.llm = llm

    def execute(self, requirements: dict) -> str:
        response = self.llm.invoke([
            SystemMessage(content=RESEARCH_PROMPT),
            HumanMessage(content=str(requirements)),
        ])

        return response.content