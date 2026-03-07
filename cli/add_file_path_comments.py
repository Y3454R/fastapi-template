#!/usr/bin/env python3
"""
Add file path comments to Python files.

Usage:
    python add_file_path_comments.py <path>

Examples:

# Process entire project directory
python add_file_path_comments.py .

# Process a specific subdirectory
python add_file_path_comments.py app/

# Process a single Python file
python add_file_path_comments.py app/main.py

# Preview changes without modifying files (dry-run)
python add_file_path_comments.py app/main.py --dry-run

# Exclude directories (can specify multiple)
python add_file_path_comments.py . --exclude-dir migrations --exclude-dir tests

# Exclude files (can specify multiple)
python add_file_path_comments.py . --exclude-file settings.py --exclude-file config.py

# Combine exclusions with dry-run
python add_file_path_comments.py . \
    --exclude-dir migrations \
    --exclude-dir tests \
    --exclude-file settings.py \
    --dry-run

# Combine single file processing with dry-run
python add_file_path_comments.py app/main.py --dry-run

# Run on multiple paths individually (repeat command per file or dir)
python add_file_path_comments.py app/api/routes/user.py
python add_file_path_comments.py app/api/routes/item.py

# Undo previously added comments
python add_file_path_comments.py . --undo --dry-run  # Preview undo changes
python add_file_path_comments.py . --undo  # Actually remove comments
"""

import argparse
from pathlib import Path


DEFAULT_EXCLUDED_DIRS = {
    "venv",
    ".venv",
    "env",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
}


def should_exclude(path: Path, excluded_dirs: set, excluded_files: set) -> bool:
    for part in path.parts:
        if part.startswith("."):
            return True
        if part in excluded_dirs:
            return True

    if path.name in excluded_files:
        return True

    return False


def process_file(py_file: Path, project_root: Path, dry_run: bool):
    relative_path = py_file.relative_to(project_root)

    with py_file.open("r", encoding="utf-8") as f:
        content = f.readlines()

    if not content:
        return

    if content[0].startswith("# File:"):
        print(f"[SKIP] Already processed: {relative_path}")
        return

    file_comment = f"# File: {relative_path}\n"

    if content[0].startswith("#!"):
        new_content = [content[0], file_comment] + content[1:]
    else:
        new_content = [file_comment] + content

    if dry_run:
        print(f"[DRY-RUN] Would update: {relative_path}")
    else:
        with py_file.open("w", encoding="utf-8") as f:
            f.writelines(new_content)
        print(f"[UPDATED] {relative_path}")


def undo_file_comment(py_file: Path, dry_run: bool):
    with py_file.open("r", encoding="utf-8") as f:
        content = f.readlines()

    if not content:
        return

    start_index = 0
    if content[0].startswith("#!"):
        start_index = 1

    if start_index < len(content) and content[start_index].startswith("# File:"):
        new_content = (
            [content[0]] + content[start_index + 1 :]
            if start_index == 1
            else content[start_index + 1 :]
        )
        if dry_run:
            print(f"[DRY-RUN] Would remove comment from: {py_file}")
        else:
            with py_file.open("w", encoding="utf-8") as f:
                f.writelines(new_content)
            print(f"[UNDO] Removed comment from: {py_file}")
    else:
        print(f"[SKIP] No comment found in: {py_file}")


def process_path(
    input_path: Path,
    excluded_dirs: set,
    excluded_files: set,
    dry_run: bool,
    undo: bool = False,
):
    if input_path.is_file():
        if input_path.suffix != ".py":
            print("Error: Provided file is not a Python file.")
            return

        if should_exclude(input_path, excluded_dirs, excluded_files):
            print("Skipped due to exclusion rules.")
            return

        project_root = input_path.parent
        if undo:
            undo_file_comment(input_path, dry_run)
        else:
            process_file(input_path, project_root, dry_run)

    elif input_path.is_dir():
        project_root = input_path.resolve()

        for py_file in project_root.rglob("*.py"):
            if should_exclude(py_file, excluded_dirs, excluded_files):
                continue
            if undo:
                undo_file_comment(py_file, dry_run)
            else:
                process_file(py_file, project_root, dry_run)

    else:
        print("Error: Path does not exist.")


def main():
    parser = argparse.ArgumentParser(
        description="Add or remove file path comments in Python files."
    )

    parser.add_argument(
        "path",
        type=str,
        help="Path to a Python file or project directory",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )

    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to exclude (can be used multiple times)",
    )

    parser.add_argument(
        "--exclude-file",
        action="append",
        default=[],
        help="File name to exclude (can be used multiple times)",
    )

    parser.add_argument(
        "--undo",
        action="store_true",
        help="Remove previously added file path comments",
    )

    args = parser.parse_args()

    input_path = Path(args.path).resolve()

    excluded_dirs = DEFAULT_EXCLUDED_DIRS.union(set(args.exclude_dir))
    excluded_files = set(args.exclude_file)

    process_path(
        input_path,
        excluded_dirs=excluded_dirs,
        excluded_files=excluded_files,
        dry_run=args.dry_run,
        undo=args.undo,
    )


if __name__ == "__main__":
    main()
