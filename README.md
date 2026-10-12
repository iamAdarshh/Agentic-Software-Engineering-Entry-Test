# Agentic Software Engineering – Entry Test

## Task 1: Checking what the agent wants to install

`check_requirements.py` checks every line of a `requirements.txt` against the
[PyPI JSON API](https://docs.pypi.org/api/json/) before you `pip install` it,
to catch hallucinated package names and versions.

It reports:

1. **Dependencies checked** – number of dependency lines in the file
2. **Packages not on PyPI** – `https://pypi.org/pypi/<name>/json` returns 404
3. **Versions not on PyPI** – package exists, but `https://pypi.org/pypi/<name>/<version>/json` returns 404
4. **Oldest pinned release** – among existing package/version pairs, the oldest by the
   `upload_time` of the first file under `urls`, printed as `name==version (year)`

Uses only the Python standard library (`urllib`, `json`, `re`).

### Usage

```bash
python3 check_requirements.py requirements.txt
```

Without an argument it reads `requirements.txt` from the current directory.

### Examples

`requirements.txt`:

```
Dependencies checked: 5
Packages not on PyPI: 1
Versions not on PyPI: 1
Oldest pinned release: numpy==1.16.0 (2019)
```

`requirements2.txt`:

```
Dependencies checked: 8
Packages not on PyPI: 2
Versions not on PyPI: 3
Oldest pinned release: python-dateutil==2.2 (2013)
```

### Notes

- Blank lines and `#` comments are not counted as dependencies.
- Extras (`pkg[extra]==1.0`) and environment markers (`; python_version<"3"`) are stripped.
- A single `=` (e.g. `pkg=1.0`, a common typo) is treated as a pin.
- Lines without an exact pin are only checked for package existence.
- Network errors other than 404 abort the script rather than being miscounted.
