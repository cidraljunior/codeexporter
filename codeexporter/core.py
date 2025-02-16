"""Core export functionality and business logic."""

from pathlib import Path
import json
import zipfile
import ast
from tqdm import tqdm

from .utils import is_binary_file, should_ignore, detect_encoding
from .errors import ExportError, UnreadableFileError


class CodeAnalyzer(ast.NodeVisitor):
    """AST visitor for Python code structure analysis.

    Collects:
        - Functions with signatures
        - Classes and methods
        - Imports
        - Docstrings
    """

    def __init__(self):
        self.structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "docstrings": [],
        }

    def visit_FunctionDef(self, node):
        func_info = {
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "returns": ast.unparse(node.returns) if node.returns else None,
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node),
        }
        self.structure["functions"].append(func_info)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        class_info = {
            "name": node.name,
            "methods": [],
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node),
        }
        self.structure["classes"].append(class_info)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.structure["imports"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module if node.module else ""
        for alias in node.names:
            self.structure["imports"].append(f"{module}.{alias.name}")
        self.generic_visit(node)


def analyze_code_structure(content):
    """Analyze Python source code using AST parsing.

    Args:
        content (str): Python source code

    Returns:
        dict: Analysis results or error message
    """

    try:
        tree = ast.parse(content)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        return analyzer.structure
    except SyntaxError as e:
        return {"error": f"SyntaxError: {e.msg} at line {e.lineno}"}
    except Exception as e:
        return {"error": str(e)}


class ProjectExporter:
    """Main exporter class handling file processing and output generation.

    Args:
        config (Config): Loaded configuration
        verbose (int): Verbosity level

    Methods:
        export: Execute full export process
        _process_files: Walk directory tree
        _should_skip: Filter decision logic
        _read_file: File reading with encoding detection
        _write_output: Format-specific output handling
    """

    def __init__(self, config, verbose=0):
        self.config = config
        self.verbose = verbose
        self.stats = {"processed": 0, "skipped": 0, "errors": 0}
        self.project_dir = None

    def export(self, project_dir, output_path, output_format):
        self.project_dir = project_dir
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == "zip":
            with zipfile.ZipFile(output_path, "w") as zipf:
                self._process_files(project_dir, zip_handler=zipf)
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                self._process_files(project_dir, text_handler=f)

        if self.verbose:
            print(f"Export complete. Stats: {json.dumps(self.stats, indent=2)}")

    def _process_files(self, project_dir, text_handler=None, zip_handler=None):
        file_iter = tqdm(
            list(project_dir.rglob("*")),
            desc="Processing files",
            disable=not self.verbose,
        )

        for file_path in file_iter:
            if self._should_skip(file_path):
                continue

            try:
                content, metadata = self._read_file(file_path)
                self._write_output(
                    file_path, content, metadata, text_handler, zip_handler
                )
                self.stats["processed"] += 1
            except ExportError as e:
                self.stats["errors"] += 1
                if self.verbose > 1:
                    tqdm.write(f"Error processing {file_path}: {str(e)}")

    def _should_skip(self, file_path):
        if not file_path.is_file():
            return True
        if should_ignore(file_path, self.config):
            self.stats["skipped"] += 1
            return True
        if (
            self.config.max_size
            and file_path.stat().st_size > self.config.max_size * 1024**2
        ):
            self.stats["skipped"] += 1
            return True
        if is_binary_file(file_path):
            self.stats["skipped"] += 1
            return True
        return False

    def _read_file(self, file_path):

        try:
            encoding = detect_encoding(file_path)
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                content = f.read()
        except UnicodeDecodeError as e:
            raise UnreadableFileError(file_path, "Encoding error") from e
        except IOError as e:
            raise UnreadableFileError(file_path, str(e)) from e

        metadata = {
            "path": str(file_path.relative_to(self.project_dir)),
            "size": file_path.stat().st_size,
            "encoding": encoding,
            "modified": file_path.stat().st_mtime,
        }

        if file_path.suffix == ".py":
            metadata["ast_info"] = analyze_code_structure(content)

        return content, metadata

    def _write_output(self, file_path, content, metadata, text_handler, zip_handler):
        if zip_handler:
            zip_handler.writestr(str(metadata["path"]), content)
        else:
            text_handler.write(f"## {metadata['path']} ##\n")
            if self.config.with_metadata:
                text_handler.write(f"/* Metadata: {json.dumps(metadata)} */\n")
            text_handler.write(f"{content}\n\n")


def export_project(project_dir, output_path, output_format, config, verbose):
    exporter = ProjectExporter(config, verbose)
    exporter.export(project_dir, output_path, output_format)
