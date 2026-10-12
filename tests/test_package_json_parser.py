from pathlib import Path

from depcheck.parsers.package_json import PackageJsonParser


def test_deps_and_devdeps(tmp_path: Path):
  (tmp_path / "package.json").write_text(
    """
{
  "name": "x",
  "dependencies": { "lodash": "^4.17.0" },
  "devDependencies": { "jest": "^29.0.0" }
}
"""
  )
  deps = PackageJsonParser().parse(tmp_path / "package.json")
  kinds = {d.name: d.kind for d in deps}
  assert kinds == {"lodash": "runtime", "jest": "dev"}


def test_invalid_json(tmp_path: Path):
  (tmp_path / "package.json").write_text("{not json")
  assert PackageJsonParser().parse(tmp_path / "package.json") == []