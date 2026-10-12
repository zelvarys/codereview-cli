from pathlib import Path

from depcheck.scanners.py_imports import PyImportsScanner


def test_simple_imports(tmp_path: Path):
  (tmp_path / "a.py").write_text("import requests\nimport numpy as np\n")
  found = PyImportsScanner().scan(tmp_path)
  assert "requests" in found
  assert "numpy" in found


def test_from_import(tmp_path: Path):
  (tmp_path / "a.py").write_text("from flask import Flask\n")
  assert "flask" in PyImportsScanner().scan(tmp_path)


def test_skips_relative_imports(tmp_path: Path):
  (tmp_path / "a.py").write_text("from .local import thing\n")
  assert "local" not in PyImportsScanner().scan(tmp_path)


def test_skips_junk_dirs(tmp_path: Path):
  junk = tmp_path / "node_modules"
  junk.mkdir()
  (junk / "x.py").write_text("import fake\n")
  assert "fake" not in PyImportsScanner().scan(tmp_path)