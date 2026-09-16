from graph.graph import build_graph
import uuid
import os
from langgraph.checkpoint.postgres import PostgresSaver

thread_id = "a67c79ee-a1c9-4caf-9ef5-42d92f32215c"
DB_URI = os.getenv("DATABASE_URL")

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()

    graph = build_graph(checkpointer)

    config = {
        "configurable": {
            "thread_id": thread_id,
            "run_research": False,
            "run_design": False,
            "run_content": False,
            "run_code": False,
            "run_review": False,
        }
    }

    # Recupera o estado salvo
    state = graph.get_state(config)

    # Limpa somente as mensagens antigas
    if state.values.get("messages"):
        graph.update_state(
            config,
            {
                "messages": [
                    RemoveMessage(id=message.id)
                    for message in state.values["messages"]
                ]
            }
        )

    result = graph.invoke(
        {
        "requirements": {
             "Crie um site profissional para uma empresa de telhas."
        }
    }, config=config)

    state = graph.get_state(
    {
        "configurable": {
            "thread_id": "a67c79ee-a1c9-4caf-9ef5-42d92f32215c"
        }
    }
    )

