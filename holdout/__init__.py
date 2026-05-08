"""Blinded holdout package boundary marker.

Audit-final §2.E.2: the ``holdout`` directory is a Python package and is
imported as such by the Custodian tooling; making the package boundary
explicit prevents accidental shadowing by sibling top-level modules and
ensures attestation/preflight imports resolve consistently across machines.
"""
