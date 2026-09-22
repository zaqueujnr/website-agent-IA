import os
from langgraph.checkpoint.postgres import PostgresSaver

from workflows.registry import build_workflow
from utils.utils import clear_messages


def main():
    workflow_name = os.getenv(
        "WORKFLOW",
        "create",
    )

    db_uri = os.getenv("DATABASE_URL")

    config_improve = {
        "configurable": {
            "thread_id": "jebitte-maquinas",

            "run_research": False,
            "run_audit": False,
            "run_design": True,
            "run_content": False,
            "run_code": True,
            "run_review": True,
        }
    }

    with PostgresSaver.from_conn_string(
        db_uri
    ) as checkpointer:

        checkpointer.setup()

        graph = build_workflow(
            workflow_name=workflow_name,
            checkpointer=checkpointer,
        )

        clear_messages(graph, config_improve)

        result = graph.invoke(
            {
                "project": {
                    "name": "Jebitte máquinas",
                    "source_path": "/app/data/source",
                },
                "requirements": {
                    "description": """
                    Melhorar o design e a experiência do usuário
                    do site existente da Jebitte Máquinas.

                    Modernizar a interface, aprimorar a responsividade
                    e adicionar animações profissionais.

                    Preservar as funcionalidades e informações existentes.
                    """
                }
            },
            config=config_improve,
        )

        print(result)


if __name__ == "__main__":
    main()