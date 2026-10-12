from pathlib import Path

from depcheck.scanners.py_imports import PyImportsScanner


def modules(tmp_path: Path) -> set[str]:
    return {i.module for i in PyImportsScanner().scan(tmp_path)}


def test_simple_imports(tmp_path: Path):
    (tmp_path / "a.py").write_text("import requests\nimport numpy as np\n")
    found = modules(tmp_path)
    assert "requests" in found
    assert "numpy" in found


def test_from_import(tmp_path: Path):
    (tmp_path / "a.py").write_text("from flask import Flask\n")
    assert "flask" in modules(tmp_path)


def test_skips_relative_imports(tmp_path: Path):
    (tmp_path / "a.py").write_text("from .local import thing\n")
    assert "local" not in modules(tmp_path)


def test_skips_junk_dirs(tmp_path: Path):
    junk = tmp_path / "node_modules"
    junk.mkdir()
    (junk / "x.py").write_text("import fake\n")
    assert "fake" not in modules(tmp_path)


def test_records_line_and_source(tmp_path: Path):
    f = tmp_path / "a.py"
    f.write_text("\n\nimport requests\n")
    imports = PyImportsScanner().scan(tmp_path)
    assert len(imports) == 1
    assert imports[0].line == 3
    assert imports[0].source.endswith("a.py")