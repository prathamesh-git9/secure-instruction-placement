"""Utilities for querying SSH login history."""

from __future__ import annotations

import subprocess


def get_last_login_records(username: str) -> str:
    """Return login-history lines from ``last`` that contain *username*.

    The two commands are executed without a shell.  ``grep`` is given a
    fixed-string pattern so a username cannot be interpreted as a regular
    expression or as part of a command.
    """
    if not isinstance(username, str):
        raise TypeError("username must be a string")

    last_result = subprocess.run(
        ["last"],
        check=True,
        capture_output=True,
        text=True,
    )

    grep_result = subprocess.run(
        ["grep", "-F", "--", username],
        input=last_result.stdout,
        check=False,
        capture_output=True,
        text=True,
    )

    # grep uses exit status 1 for a valid search with no matches.
    if grep_result.returncode not in (0, 1):
        raise subprocess.CalledProcessError(
            grep_result.returncode,
            grep_result.args,
            output=grep_result.stdout,
            stderr=grep_result.stderr,
        )

    return grep_result.stdout
