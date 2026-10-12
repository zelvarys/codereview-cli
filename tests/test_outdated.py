from depcheck.checks.outdated import OutdatedCheck, _extract_pinned, _major
from depcheck.models import Dependency, Project


def dep(name, constraint, line=1):
  return Dependency(
    name=name, raw=f"{name}{constraint}", constraint=constraint,
    source="requirements.txt", line=line, kind="runtime",
  )


def make_project(deps):
  return Project(root=".", dependencies=list(deps), imports=[],
           languages={"python"})


def test_extract_pinned_exact():
  assert _extract_pinned("==1.2.3") == "1.2.3"
  assert _extract_pinned("===1.2.3") == "1.2.3"


def test_extract_pinned_bare():
  assert _extract_pinned("1.2.3") == "1.2.3"


def test_extract_pinned_npm_caret():
  assert _extract_pinned("^1.2.3") == "1.2.3"
  assert _extract_pinned("~1.2.3") == "1.2.3"


def test_extract_pinned_range_returns_none():
  assert _extract_pinned(">=1.0") is None
  assert _extract_pinned("") is None


def test_major():
  assert _major("1.2.3") == 1
  assert _major("v2.0") == 2
  assert _major("19.3.0") == 19


def test_flags_one_major_behind():
  p = make_project([dep("requests", "==1.2.0")])
  check = OutdatedCheck(lambda d: "2.0.0")
  findings = check.run(p)
  assert len(findings) == 1
  assert findings[0].severity == "warning"
  assert "1 major" in findings[0].message


def test_flags_multiple_majors_behind():
  p = make_project([dep("typescript", "==5.2.2")])
  check = OutdatedCheck(lambda d: "7.0.2")
  findings = check.run(p)
  assert len(findings) == 1
  assert "2 majors" in findings[0].message


def test_skips_same_major():
  p = make_project([dep("requests", "==2.20.0")])
  check = OutdatedCheck(lambda d: "2.31.0")
  assert check.run(p) == []


def test_skips_patch_behind():
  p = make_project([dep("requests", "==2.31.0")])
  check = OutdatedCheck(lambda d: "2.31.5")
  assert check.run(p) == []


def test_skips_newer_pinned():
  p = make_project([dep("requests", "==3.0.0")])
  check = OutdatedCheck(lambda d: "2.31.0")
  assert check.run(p) == []


def test_skips_unpinned():
  p = make_project([dep("requests", "")])
  check = OutdatedCheck(lambda d: "2.31.0")
  assert check.run(p) == []


def test_skips_lookup_failure():
  p = make_project([dep("requests", "==1.0.0")])
  check = OutdatedCheck(lambda d: None)
  assert check.run(p) == []