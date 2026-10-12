"""Fetch latest versions from PyPI and npm."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

PYPI_URL = "https://pypi.org/pypi/{name}/json"
NPM_URL = "https://registry.npmjs.org/{name}"
TIMEOUT = 10


def _get_json(url: str) -> dict | None:
  try:
    req = urllib.request.Request(url, headers={"User-Agent": "depcheck/0.1"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
      return json.loads(resp.read().decode("utf-8"))
  except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
      TimeoutError, OSError):
    return None


def latest_pypi(name: str) -> str | None:
  """Return latest version string from PyPI, or None."""
  data = _get_json(PYPI_URL.format(name=name))
  if not data:
    return None
  return (data.get("info") or {}).get("version")


def latest_npm(name: str) -> str | None:
  """Return latest version string from npm, or None."""
  data = _get_json(NPM_URL.format(name=name))
  if not data:
    return None
  return ((data.get("dist-tags") or {}).get("latest"))