"""The ShellBench release that ShellForm is pinned to.

ShellForm never copies a ShellBench value (docs/data_contract.md, section 1).
It imports ShellBench, installed in editable mode from a local clone that is
checked out at the tag below. Every result names this tag.

Move the pin only when a new ShellBench tag lands (floor-r1, floor-r2,
floor-r3, v0.3), and record the move in LOG.md.

The check reads the installed distribution version (from ShellBench's
pyproject.toml). It does not read shellbench.__version__, because that string
still says 0.0.1 at tag v0.1.0 and cannot tell the two tags apart.
"""

from importlib import metadata

SHELLBENCH_TAG = "v0.1.0"
SHELLBENCH_VERSION = "0.1.0"


def installed_shellbench_version() -> str:
    """Return the distribution version of the installed shellbench package.

    Raises:
        ImportError: If shellbench is not installed in this environment.
    """
    try:
        return metadata.version("shellbench")
    except metadata.PackageNotFoundError as err:
        raise ImportError("shellbench is not installed") from err


def check_pin() -> str:
    """Check that the installed shellbench matches the pinned release.

    Returns:
        The pinned tag, for writing into result files.

    Raises:
        RuntimeError: If the installed version differs from the pin.
    """
    found = installed_shellbench_version()
    if found != SHELLBENCH_VERSION:
        raise RuntimeError(
            f"shellbench {found} is installed, but ShellForm is pinned to "
            f"{SHELLBENCH_TAG} ({SHELLBENCH_VERSION}). Run "
            f"'git checkout {SHELLBENCH_TAG}' in the ShellBench clone, then "
            f"'pip install -e . --no-deps' there."
        )
    return SHELLBENCH_TAG
