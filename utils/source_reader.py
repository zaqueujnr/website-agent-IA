from pathlib import Path


ALLOWED_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".json",
}


def read_project_files(
    source_path: str,
) -> dict[str, str]:
    root = Path(source_path)

    files = {}
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix not in ALLOWED_EXTENSIONS:
            continue

        relative_path = file_path.relative_to(root)
        print(relative_path)

        files[str(relative_path)] = file_path.read_text(
            encoding="utf-8"
        )

    return files