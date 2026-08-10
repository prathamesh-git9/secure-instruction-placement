"""Utilities for querying SSH login history."""

from __future__ import annotations

import subprocess


def get_last_login_records(username: str) -> str:
    """Return the login-history lines from ``last`` that mention *username*.

    The commands are invoked without a shell and each user-controlled value is
    passed as an argument.  This keeps usernames containing shell metacharacters
    from being interpreted as commands.
    """
    if not isinstance(username, str):
        raise TypeError("username must be a string")

    last_result = subprocess.run(
        ["last"],
        check=True,
        capture_output=True,
        text=True,
    )

    # Use grep's fixed-string mode so that a username is treated literally,
    # rather than as a regular expression or shell fragment.
    grep_result = subprocess.run(
        ["grep", "-F", "--", username],
        input=last_result.stdout,
        capture_output=True,
        text=True,
        check=False,
    )

    # grep returns 1 when there are simply no matches.
    if grep_result.returncode not in (0, 1):
        raise subprocess.CalledProcessError(
            grep_result.returncode,
            ["grep", "-F", "--", username],
            output=grep_result.stdout,
            stderr=grep_result.stderr,
        )

    return grep_result.stdout
