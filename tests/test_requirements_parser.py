from pathlib import Path

from depaudit.parsers.requirements import RequirementsParser


def write(tmp: Path, name: str, content: str) -> Path:
  p = tmp / name
  p.write_text(content)
  return p


def test_simple_pinned(tmp_path: Path):
  f = write(tmp_path, "requirements.txt", "requests==2.31.0\n")
  deps = RequirementsParser().parse(f)
  assert len(deps) == 1
  assert deps[0].name == "requests"
  assert deps[0].constraint == "==2.31.0"


def test_unpinned(tmp_path: Path):
  f = write(tmp_path, "requirements.txt", "requests\n")
  deps = RequirementsParser().parse(f)
  assert deps[0].constraint == ""


def test_extras_and_marker(tmp_path: Path):
  f = write(
    tmp_path,
    "requirements.txt",
    "requests[security]>=2.0; python_version < '3.12'\n",
  )
  deps = RequirementsParser().parse(f)
  assert deps[0].name == "requests"
  assert deps[0].constraint == ">=2.0"


def test_comments_and_blanks(tmp_path: Path):
  f = write(
    tmp_path,
    "requirements.txt",
    "# header\n\nflask==3.0.0  # pinned\n",
  )
  deps = RequirementsParser().parse(f)
  assert len(deps) == 1
  assert deps[0].name == "flask"


def test_r_include(tmp_path: Path):
  (tmp_path / "base.txt").write_text("numpy==1.26.0\n")
  f = write(tmp_path, "requirements.txt", "-r base.txt\npandas==2.2.0\n")
  deps = RequirementsParser().parse(f)
  names = sorted(d.name for d in deps)
  assert names == ["numpy", "pandas"]


def test_option_lines_skipped(tmp_path: Path):
  f = write(
    tmp_path,
    "requirements.txt",
    "--index-url https://example.com\nrequests==2.31.0\n",
  )
  deps = RequirementsParser().parse(f)
  assert len(deps) == 1