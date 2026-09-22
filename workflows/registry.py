from workflows.create_website import (
    build_create_graph,
)

from workflows.improve_website import (
    build_improve_graph,
)

WORKFLOWS = {
    "create": build_create_graph,
    "improve": build_improve_graph,
}


def build_workflow(
    workflow_name: str,
    checkpointer,
):
    workflow_builder = WORKFLOWS.get(
        workflow_name
    )

    if workflow_builder is None:
        raise ValueError(
            f"Workflow inválido: {workflow_name}"
        )

    return workflow_builder(checkpointer)