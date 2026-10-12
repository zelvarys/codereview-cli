from pathlib import Path

from depaudit.scanners.js_imports import JsImportsScanner


def modules(tmp_path: Path) -> set[str]:
  return {i.module for i in JsImportsScanner().scan(tmp_path)}


def test_es_import(tmp_path: Path):
  (tmp_path / "a.js").write_text("import lodash from 'lodash';\n")
  assert "lodash" in modules(tmp_path)


def test_require(tmp_path: Path):
  (tmp_path / "a.js").write_text("const x = require('express');\n")
  assert "express" in modules(tmp_path)


def test_scoped_package(tmp_path: Path):
  (tmp_path / "a.js").write_text("import x from '@types/node';\n")
  assert "@types/node" in modules(tmp_path)


def test_subpath_collapses(tmp_path: Path):
  (tmp_path / "a.js").write_text("import get from 'lodash/get';\n")
  assert "lodash" in modules(tmp_path)


def test_skips_relative(tmp_path: Path):
  (tmp_path / "a.js").write_text("import x from './local';\n")
  assert modules(tmp_path) == set()


def test_records_line(tmp_path: Path):
  (tmp_path / "a.js").write_text("\n\nimport lodash from 'lodash';\n")
  imports = JsImportsScanner().scan(tmp_path)
  assert len(imports) == 1
  assert imports[0].line == 3