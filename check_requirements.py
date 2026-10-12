#!/usr/bin/env python3
"""Check every dependency in a requirements file against the PyPI JSON API.

Usage:
    python check_requirements.py [requirements.txt]

For each line it reports whether the package exists on PyPI, whether the
pinned version exists, and which existing pinned release is the oldest
(by the upload_time of the first file listed under "urls").
"""

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

PYPI_URL = "https://pypi.org/pypi"
TIMEOUT = 10

# name, optional [extras], optional "==version" (or "=version")
REQUIREMENT_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*(?:={1,2}\s*(?P<version>\S+))?"
)


def fetch_json(url):
    """Return the parsed JSON at url, or None if PyPI answers 404."""
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise


def parse_line(line):
    """Split a requirement line into (name, version); version is None if unpinned.

    A single "=" (a common typo for "==") is also treated as a pin.
    """
    line = line.split("#", 1)[0].split(";", 1)[0].strip()
    match = REQUIREMENT_RE.match(line)
    if not match:
        return line, None
    return match.group("name"), match.group("version")


def read_requirements(path):
    """Return the dependency lines, skipping blank lines and comments."""
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "requirements.txt"
    lines = read_requirements(path)

    missing_packages = 0
    missing_versions = 0
    oldest = None  # (upload_time, name, version)

    for line in lines:
        name, version = parse_line(line)
        quoted_name = urllib.parse.quote(name)

        if fetch_json(f"{PYPI_URL}/{quoted_name}/json") is None:
            missing_packages += 1
            continue
        if version is None:
            continue

        release = fetch_json(f"{PYPI_URL}/{quoted_name}/{urllib.parse.quote(version)}/json")
        if release is None:
            missing_versions += 1
            continue

        files = release.get("urls") or []
        if not files:
            continue  # release exists but has no uploaded files to date it by
        upload_time = files[0]["upload_time"]
        if oldest is None or upload_time < oldest[0]:
            oldest = (upload_time, name, version)

    print(f"Dependencies checked: {len(lines)}")
    print(f"Packages not on PyPI: {missing_packages}")
    print(f"Versions not on PyPI: {missing_versions}")
    if oldest:
        upload_time, name, version = oldest
        print(f"Oldest pinned release: {name}=={version} ({upload_time[:4]})")
    else:
        print("Oldest pinned release: none")


if __name__ == "__main__":
    main()
