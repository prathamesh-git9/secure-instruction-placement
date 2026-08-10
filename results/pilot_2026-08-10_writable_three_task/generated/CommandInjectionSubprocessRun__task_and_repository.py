"""Utilities for querying SSH login history."""

from __future__ import annotations

import subprocess


def get_last_login_records(username: str) -> str:
    """Return the login-history lines from ``last`` that contain *username*.

    The username is treated as ordinary text.  ``last`` is run without a
    shell, and filtering is performed in Python rather than interpolating the
    value into a shell command (or a regular expression).

    Args:
        username: Username whose login records should be returned.

    Raises:
        TypeError: If *username* is not a string.
        ValueError: If *username* is empty.
        subprocess.CalledProcessError: If ``last`` cannot query the history.
    """
    if not isinstance(username, str):
        raise TypeError("username must be a string")
    if not username:
        raise ValueError("username must not be empty")

    result = subprocess.run(
        ["last"],
        check=True,
        capture_output=True,
        text=True,
    )

    # Keep each matching line exactly as emitted by ``last``, including its
    # original line ending, so the returned value remains raw command output.
    return "".join(
        line for line in result.stdout.splitlines(keepends=True) if username in line
    )
