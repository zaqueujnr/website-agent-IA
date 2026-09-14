from pathlib import Path
from langchain_core.tools import tool

GENERATED_DIR = Path("generated")


@tool
def write_generated_file(filename: str, content: str) -> str:
    """Cria um arquivo dentro da pasta generated."""

    file_path = GENERATED_DIR / filename

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding="utf-8")

    return f"Arquivo criado: {file_path}"