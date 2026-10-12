from pathlib import Path

from depcheck.scanners.js_imports import JsImportsScanner


def test_es_import(tmp_path: Path):
  (tmp_path / "a.js").write_text("import lodash from 'lodash';\n")
  assert "lodash" in JsImportsScanner().scan(tmp_path)


def test_require(tmp_path: Path):
  (tmp_path / "a.js").write_text("const x = require('express');\n")
  assert "express" in JsImportsScanner().scan(tmp_path)


def test_scoped_package(tmp_path: Path):
  (tmp_path / "a.js").write_text("import x from '@types/node';\n")
  assert "@types/node" in JsImportsScanner().scan(tmp_path)


def test_subpath_collapses(tmp_path: Path):
  (tmp_path / "a.js").write_text("import get from 'lodash/get';\n")
  found = JsImportsScanner().scan(tmp_path)
  assert "lodash" in found


def test_skips_relative(tmp_path: Path):
  (tmp_path / "a.js").write_text("import x from './local';\n")
  assert JsImportsScanner().scan(tmp_path) == set()