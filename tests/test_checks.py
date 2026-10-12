from depcheck.checks.duplicate import DuplicateCheck
from depcheck.checks.missing import MissingCheck
from depcheck.checks.stdlib_shadow import StdlibShadowCheck
from depcheck.checks.unpinned import UnpinnedCheck
from depcheck.checks.unused import UnusedCheck
from depcheck.models import Dependency, Project


def make_project(deps=(), imported=(), languages=("python",)):
  return Project(
    root=".",
    dependencies=list(deps),
    imported=set(imported),
    languages=set(languages),
  )


def dep(name, constraint="", kind="runtime", line=1):
  return Dependency(
    name=name, raw=name, constraint=constraint,
    source="requirements.txt", line=line, kind=kind,
  )


def test_unpinned():
  p = make_project(deps=[dep("requests")])
  assert len(UnpinnedCheck().run(p)) == 1


def test_pinned_ok():
  p = make_project(deps=[dep("requests", "==2.31.0")])
  assert UnpinnedCheck().run(p) == []


def test_unused():
  p = make_project(deps=[dep("requests", "==2.31.0")], imported=[])
  assert len(UnusedCheck().run(p)) == 1


def test_used_ok():
  p = make_project(deps=[dep("requests", "==2.31.0")], imported=["requests"])
  assert UnusedCheck().run(p) == []


def test_dev_deps_not_flagged_unused():
  p = make_project(deps=[dep("pytest", "==7", kind="dev")], imported=[])
  assert UnusedCheck().run(p) == []


def test_missing():
  p = make_project(deps=[], imported=["requests"])
  findings = MissingCheck().run(p)
  assert any(f.message.startswith("`requests`") for f in findings)


def test_stdlib_not_missing():
  p = make_project(deps=[], imported=["json", "os"])
  assert MissingCheck().run(p) == []


def test_stdlib_shadow():
  p = make_project(deps=[dep("json", "==1")])
  assert len(StdlibShadowCheck().run(p)) == 1


def test_duplicate_different_constraints():
  p = make_project(deps=[dep("requests", "==2.0"), dep("requests", "==2.1")])
  assert len(DuplicateCheck().run(p)) == 1


def test_duplicate_same_constraint_ok():
  p = make_project(deps=[dep("requests", "==2.0"), dep("requests", "==2.0")])
  assert DuplicateCheck().run(p) == []