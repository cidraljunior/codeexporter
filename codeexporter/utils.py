"""Utility functions for file handling and detection."""

import chardet
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern


def is_binary_file(file_path):
    """Check if file appears to be binary.

    Args:
        file_path (Path): File to check

    Returns:
        bool: True if binary file detected
    """

    try:
        with open(file_path, "rb") as f:
            return b"\x00" in f.read(1024)
    except IOError:
        return True


def detect_encoding(file_path):
    """Detect file encoding using chardet.

    Args:
        file_path (Path): File to analyze

    Returns:
        str: Detected encoding (default: utf-8)
    """

    with open(file_path, "rb") as f:
        raw = f.read(1024)
    return chardet.detect(raw).get("encoding", "utf-8")


def should_ignore(path, config):
    """Determine if a path should be excluded from export.

    Args:
        path (Path): File/directory path to check
        config (Config): Current configuration

    Returns:
        bool: True if path should be ignored
    """

    # Check against ignore patterns
    if path.name in config.ignore_files:
        return True
    if path.suffix in config.ignore_ext:
        return True
    if any(part in config.ignore_dirs for part in path.parts):
        return True

    # Check .gitignore if enabled
    if config.use_gitignore:
        try:
            rel_path = path.relative_to(config.project_dir)
        except ValueError:
            return False

        # Find relevant .gitignore files
        gitignore_files = []
        current_dir = path.parent
        while current_dir.is_relative_to(config.project_dir):
            gitignore = current_dir / ".gitignore"
            if gitignore.exists():
                gitignore_files.append(gitignore)
            current_dir = current_dir.parent

        # Parse gitignore patterns
        spec = PathSpec([])
        for gitignore in reversed(gitignore_files):
            with open(gitignore, "r", errors="replace") as f:
                lines = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
                spec += PathSpec.from_lines(GitWildMatchPattern, lines)

        return spec.match_file(rel_path)

    return False
