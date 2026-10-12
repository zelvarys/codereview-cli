from depcheck.checks.outdated import OutdatedCheck, _extract_pinned, _version_tuple
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


def test_extract_pinned_range_returns_none():
    assert _extract_pinned(">=1.0") is None
    assert _extract_pinned("") is None


def test_version_tuple():
    assert _version_tuple("1.2.3") == (1, 2, 3)
    assert _version_tuple("v2.0") == (2, 0)


def test_outdated_flags_older():
    p = make_project([dep("requests", "==2.0.0")])
    check = OutdatedCheck(lambda d: "2.31.0")
    findings = check.run(p)
    assert len(findings) == 1
    assert "2.31.0" in findings[0].message


def test_outdated_skips_current():
    p = make_project([dep("requests", "==2.31.0")])
    check = OutdatedCheck(lambda d: "2.31.0")
    assert check.run(p) == []


def test_outdated_skips_newer_pinned():
    p = make_project([dep("requests", "==3.0.0")])
    check = OutdatedCheck(lambda d: "2.31.0")
    assert check.run(p) == []


def test_outdated_skips_unpinned():
    p = make_project([dep("requests", "")])
    check = OutdatedCheck(lambda d: "2.31.0")
    assert check.run(p) == []


def test_outdated_skips_lookup_failure():
    p = make_project([dep("requests", "==2.0.0")])
    check = OutdatedCheck(lambda d: None)
    assert check.run(p) == []