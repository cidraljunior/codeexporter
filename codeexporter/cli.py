"""Command-line interface definition and handling."""

import click
from pathlib import Path

from .core import export_project
from .config import load_configuration
from .errors import ExportError


@click.command()
@click.argument("project_dir", default=str(Path.cwd()), type=click.Path(exists=True))
@click.option(
    "-o", "--output", default="code_export", help="Output file/directory name"
)
@click.option(
    "--format",
    type=click.Choice(["text", "json", "zip"], case_sensitive=False),
    default="text",
)
@click.option("--ignore-dirs", multiple=True, help="Directories to ignore")
@click.option("--ignore-files", multiple=True, help="Files to ignore")
@click.option("--ignore-ext", multiple=True, help="File extensions to ignore")
@click.option("--max-size", type=int, help="Maximum file size in MB")
@click.option(
    "--include-hidden/--exclude-hidden", default=False, help="Include hidden files"
)
@click.option(
    "--with-metadata/--no-metadata", default=False, help="Include file metadata"
)
@click.option(
    "--use-gitignore/--no-gitignore", default=True, help="Respect .gitignore rules"
)
@click.option("-v", "--verbose", count=True, help="Verbosity level")
def main(
    project_dir,
    output,
    format,
    ignore_dirs,
    ignore_files,
    ignore_ext,
    max_size,
    include_hidden,
    with_metadata,
    use_gitignore,
    verbose,
):
    """Main entry point for codeexport CLI.

    Args:
        project_dir (Path): Root directory to export
        output (str): Output file path
        format (str): Output format (text/zip)
        ignore_dirs (tuple): Directories to exclude
        ignore_files (tuple): Files to exclude
        ignore_ext (tuple): Extensions to exclude
        max_size (int): Max file size in MB
        include_hidden (bool): Include hidden files
        with_metadata (bool): Add metadata comments
        use_gitignore (bool): Respect .gitignore
        verbose (int): Verbosity level (0-2)
    """

    cli_args = {
        "ignore_dirs": ignore_dirs,
        "ignore_files": ignore_files,
        "ignore_ext": ignore_ext,
        "max_size": max_size,
        "include_hidden": include_hidden,
        "with_metadata": with_metadata,
        "use_gitignore": use_gitignore,
    }
    config = load_configuration(Path(project_dir), cli_args=cli_args)

    try:
        export_project(
            project_dir=Path(project_dir),
            output_path=Path(output),
            output_format=format,
            config=config,
            verbose=verbose,
        )
    except ExportError as e:
        click.secho(f"Error: {str(e)}", fg="red")
        raise click.Abort()


if __name__ == "__main__":
    main()
