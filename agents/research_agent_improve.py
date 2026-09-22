from langchain_core.messages import  SystemMessage, HumanMessage
from prompt.research import RESEARCH_PROMPT

class ResearchAgentImprove:
    def __init__(self, llm):
        self.llm = llm

    def execute(self, requirements: dict, source_files: dict) -> str:
        response = self.llm.invoke([
            SystemMessage(content=RESEARCH_PROMPT),
            HumanMessage(content=str(
            f"""
            REQUIREMENTS:
            {requirements}

            SOURCE_FILES:
            {source_files}
            """
                )),
        ])

        return response.content