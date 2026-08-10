"""Utilities for querying SSH login history."""

from __future__ import annotations

import re
import subprocess


_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def get_last_login_records(username: str) -> str:
    """Return recent login records for *username*.

    The system's ``last`` command is invoked without a shell.  Filtering is
    performed in Python so that the username cannot become shell syntax.

    Raises:
        TypeError: If ``username`` is not a string.
        ValueError: If ``username`` is empty or contains unsupported
            characters.
        FileNotFoundError: If the host does not provide ``last``.
        subprocess.CalledProcessError: If ``last`` fails.
    """
    if not isinstance(username, str):
        raise TypeError("username must be a string")
    if not _USERNAME_PATTERN.fullmatch(username):
        raise ValueError("username contains unsupported characters")

    result = subprocess.run(
        ["last"],
        check=True,
        capture_output=True,
        text=True,
    )

    records = []
    for line in result.stdout.splitlines(keepends=True):
        fields = line.split(maxsplit=1)
        if fields and fields[0] == username:
            records.append(line)
    return "".join(records)
