# CodeExporter

A powerful CLI tool to export project code with metadata for AI analysis.

## Features

- Export code in text or zip formats
- File metadata inclusion (size, encoding, modification time)
- AST analysis for Python files
- Configurable ignore patterns
- .gitignore support
- Multi-source configuration

## Installation

```bash
# Install from PyPI
pip install codeexporter

# Install from source
git clone https://github.com/cidraljunior/codeexporter
cd codeexporter
pip install .
```

## Usage

### Basic Command
```bash
codeexport /path/to/project -o output.txt
```

### Common Options
```bash
# Export as zip with metadata
codeexport . --format zip -o project.zip --with-metadata

# Custom ignore patterns
codeexport . --ignore-dirs test --ignore-ext .log --max-size 2
```

### Configuration Guide

**1. CLI Arguments**  
All options can be passed as command-line arguments.

**2. Project Config**  
Create `.codeexportrc` in your project root:
```yaml
ignore_dirs: [node_modules, dist]
ignore_ext: [.map, .log]
max_size: 3
```

**3. User Config**  
`~/.config/codeexport/config.yaml`:
```yaml
include_hidden: false
with_metadata: true
ignore_files: [thumbs.db]
```

**Precedence Order**: CLI > Project Config > User Config

## Contribution

### Reporting Issues
Create GitHub issues with:
- Error logs
- Reproduction steps
- Expected vs actual behavior

### Development Setup
```bash
git clone https://github.com/cidraljunior/codeexporter
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Testing
```bash
pytest tests/ --cov=codeexporter --cov-report=term-missing
```

### Coding Standards
- Follow PEP8 with Black formatting
- Type hints for all public functions
- Document new features in README
- Add tests for new functionality

## License
MIT License - See [LICENSE](LICENSE)