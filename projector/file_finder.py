from pathlib import Path

DEPTH = 3
TARGET_PATH = Path.home() / ".config" / "projector" / "paths"


def get_prj_roots() -> tuple[Path, ...]:
    if TARGET_PATH.exists() == False:
        return (
            Path.home() / "Projects",
            Path.home() / "Documents",
        )

    buff: list[Path] = []
    with open(TARGET_PATH, encoding="utf-8") as f:
        for line in f:
            raw_path = line.strip()

            if not raw_path:
                continue

            path = Path(raw_path).expanduser()

            if not path.is_dir():
                raise ValueError(
                    f"Cannot load path: {raw_path!r}. Expected an existing directory."
                )

            buff.append(path)

    return tuple(buff)


PROJECT_ROOTS = get_prj_roots()


def find_projects() -> list[Path]:
    """
    Find project directories beneath configured roots.

    A directory is considered a project when it contains at least one file
    directly. Directories are searched no deeper than DEPTH levels beneath
    each configured root.
    """

    projects: list[Path] = []

    def dig(current_root: Path, depth: int) -> list[Path]:
        try:
            entries = list(current_root.iterdir())
        except (OSError, PermissionError):
            return []

        visible_entries = [entry for entry in entries if not entry.name.startswith(".")]

        # A file directly inside this directory marks it as a project.
        if any(entry.is_file() for entry in visible_entries):
            return [current_root]

        # Do not descend beyond the configured depth.
        if depth >= DEPTH:
            return []

        discovered_projects: list[Path] = []

        for entry in visible_entries:
            if entry.is_dir():
                discovered_projects.extend(dig(entry, depth + 1))

        return discovered_projects

    for root in PROJECT_ROOTS:
        if not root.is_dir():
            continue

        # Treat each child of the configured root as depth 1.
        for child in root.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                projects.extend(dig(child, depth=1))

    return sorted(
        set(projects),
        key=lambda path: (
            path.name.casefold(),
            str(path.parent).casefold(),
        ),
    )
