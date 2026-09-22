
from langchain_core.messages import SystemMessage, HumanMessage
from prompt.content import CONTENT_PROMPT
class ContentAgentImprove:
    def __init__(self, llm):
        self.llm = llm

    def execute(self, research: dict, design: dict, source_files) -> str:
        response = self.llm.invoke([
            SystemMessage(content=CONTENT_PROMPT),
            HumanMessage(content=f"""
            DESIGN:
            {design}

            RESEARCH:
            {research}

            SOURCE_FILES
            {source_files}
            """
            ),
        ])

        return response.content
