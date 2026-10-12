import json
from pathlib import Path

from depcheck.cli import main


def test_clean_project_exit_zero(tmp_path: Path, capsys):
  (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")
  (tmp_path / "app.py").write_text("import requests\n")
  rc = main([str(tmp_path), "--no-color"])
  out = capsys.readouterr().out
  assert rc == 0
  assert "No issues found" in out


def test_unpinned_exit_one(tmp_path: Path, capsys):
  (tmp_path / "requirements.txt").write_text("requests\n")
  (tmp_path / "app.py").write_text("import requests\n")
  rc = main([str(tmp_path), "--no-color"])
  assert rc == 1
  assert "unpinned" in capsys.readouterr().out


def test_json_output(tmp_path: Path, capsys):
  (tmp_path / "requirements.txt").write_text("requests\n")
  (tmp_path / "app.py").write_text("import requests\n")
  rc = main([str(tmp_path), "--json"])
  out = capsys.readouterr().out
  assert rc == 1
  data = json.loads(out)
  assert isinstance(data, list)
  assert any(item["check"] == "unpinned" for item in data)


def test_missing_path(capsys):
  rc = main(["/nonexistent/path/xyz"])
  assert rc == 2