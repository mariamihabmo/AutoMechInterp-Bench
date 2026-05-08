#!/usr/bin/env python3
"""Compatibility wrapper for audit helpers.

The current implementation lives in `_bundle_analysis.py`. This module exists
so older references to `main/audit_utils.py` still resolve.
"""

from _bundle_analysis import *  # noqa: F401,F403
