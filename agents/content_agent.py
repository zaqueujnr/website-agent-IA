
from langchain_core.messages import SystemMessage, HumanMessage
from prompt.content import CONTENT_PROMPT
class ContentAgent:
    def __init__(self, llm):
        self.llm = llm

    def execute(self, research: dict, design: dict) -> str:
        response = self.llm.invoke([
            SystemMessage(content=CONTENT_PROMPT),
            HumanMessage(content=f"""
            RESEARCH:
            {research}
            
            DESIGN:
            {design}

            """
            ),
        ])

        return response.content
