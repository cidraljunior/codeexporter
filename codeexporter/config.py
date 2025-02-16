"""Configuration loading and management."""

from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "ignore_dirs": [".git", "__pycache__", "venv", ".venv"],
    "ignore_files": [".DS_Store", "thumbs.db"],
    "ignore_ext": [".pyc", ".bin"],
    "max_size": 5,  # MB
    "include_hidden": False,
    "with_metadata": True,
    "use_gitignore": True,
}


def load_configuration(project_dir, cli_args=None):
    """Load and merge configurations from multiple sources.

    Args:
        project_dir (Path): Project root directory
        cli_args (dict): Command-line arguments

    Returns:
        Config: Merged configuration object

    Sources (in precedence order):
        1. CLI arguments
        2. Project .codeexportrc
        3. User config.yaml
        4. Default values
    """

    config = DEFAULT_CONFIG.copy()

    # Load from project config file
    project_config = project_dir / ".codeexportrc"
    if project_config.exists():
        with open(project_config) as f:
            config.update(yaml.safe_load(f))

    # Load from user home directory
    user_config = Path.home() / ".config" / "codeexport" / "config.yaml"
    if user_config.exists():
        with open(user_config) as f:
            config.update(yaml.safe_load(f))

    # Merge CLI arguments
    if cli_args:
        # Handle list-type arguments
        list_fields = ["ignore_dirs", "ignore_files", "ignore_ext"]
        for field in list_fields:
            if cli_args.get(field):
                config[field] = list(set(config.get(field, []) + list(cli_args[field])))

        # Handle scalar arguments
        scalar_fields = ["max_size", "include_hidden", "with_metadata", "use_gitignore"]
        for field in scalar_fields:
            if cli_args.get(field) is not None:
                config[field] = cli_args[field]

    return Config(project_dir=project_dir, **config)


class Config:
    """Central configuration container.

    Attributes:
        ignore_dirs (set): Directories to ignore
        ignore_files (set): Files to ignore
        ignore_ext (set): Extensions to ignore
        max_size (int): Maximum file size (MB)
        include_hidden (bool): Include hidden files
        with_metadata (bool): Include metadata
        use_gitignore (bool): Use .gitignore rules
        project_dir (Path): Base project directory
    """

    def __init__(self, project_dir, **kwargs):
        self.project_dir = Path(project_dir)
        self.ignore_dirs = set(kwargs.get("ignore_dirs", []))
        self.ignore_files = set(kwargs.get("ignore_files", []))
        self.ignore_ext = set(kwargs.get("ignore_ext", []))
        self.max_size = kwargs.get("max_size", 5)
        self.include_hidden = kwargs.get("include_hidden", False)
        self.with_metadata = kwargs.get("with_metadata", True)
        self.use_gitignore = kwargs.get("use_gitignore", True)
