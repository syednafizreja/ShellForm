"""The ShellBench release that ShellForm is pinned to.

ShellForm never copies a ShellBench value (docs/data_contract.md, section 1).
It imports ShellBench, installed in editable mode from a local clone that is
checked out at the tag below. Every result names this tag.

Move the pin only when a new ShellBench tag lands (floor-r1, floor-r2,
floor-r3, v0.3), and record the move in LOG.md.

The pin is checked against the git tag of the clone when git can see it, and
against the version string otherwise. (ShellBench v0.1.0 still reported
"0.0.1"; v0.2.0 and v0.3.0 both report "0.2.0". Pin moved v0.1.0 -> v0.2.0
on 7 Nov 2026, LOG.md Day 10; v0.2.0 -> v0.3.0 on 8 Nov 2026, LOG.md Day 11.)
"""

import subprocess
from pathlib import Path

SHELLBENCH_TAG = "v0.3.0"
SHELLBENCH_VERSION = "0.2.0"  # as reported by shellbench.__version__ at v0.2.0 and v0.3.0


def installed_shellbench_version() -> str:
    """Return the version string of the installed shellbench package.

    Raises:
        ImportError: If shellbench is not installed in this environment.
    """
    import shellbench

    return shellbench.__version__


def installed_shellbench_tag():
    """Return the git tag the installed shellbench clone is checked out at.

    Returns:
        The exact tag at HEAD, or None if git is missing, the install is not a
        git clone, or HEAD is not exactly at a tag.
    """
    import shellbench

    src = Path(shellbench.__file__).resolve().parent
    try:
        out = subprocess.run(["git", "describe", "--tags", "--exact-match"], cwd=src,
                             capture_output=True, text=True, check=False)
    except OSError:
        return None
    return out.stdout.strip() or None


def check_pin() -> str:
    """Check that the installed shellbench matches the pinned release.

    Returns:
        The pinned tag, for writing into result files.

    Raises:
        RuntimeError: If the installed clone is at another tag, is not at any
            tag while git can see it, or reports another version.
    """
    tag = installed_shellbench_tag()
    found = installed_shellbench_version()
    if tag is not None and tag != SHELLBENCH_TAG:
        raise RuntimeError(f"shellbench clone is at {tag}, but ShellForm is pinned to "
                           f"{SHELLBENCH_TAG}. Run 'git checkout {SHELLBENCH_TAG}' in the clone.")
    if found != SHELLBENCH_VERSION:
        raise RuntimeError(f"shellbench {found} is installed, but ShellForm is pinned to "
                           f"{SHELLBENCH_TAG} ({SHELLBENCH_VERSION}). Run "
                           f"'git checkout {SHELLBENCH_TAG}' in the ShellBench clone.")
    return SHELLBENCH_TAG
