# Pinned by digest (audit-final §1.13 / 2.F.2). The digest below resolves
# python:3.12-slim as published on Docker Hub on 2026-05-05; refresh by
# running:
#   docker pull python:3.12-slim
#   docker inspect --format='{{index .RepoDigests 0}}' python:3.12-slim
# (or, without docker, query the registry API at
#  https://registry-1.docker.io/v2/library/python/manifests/3.12-slim and
#  read the `docker-content-digest` response header).
FROM python:3.12-slim@sha256:46cb7cc2877e60fbd5e21a9ae6115c30ace7a077b9f8772da879e4590c18c2e3

WORKDIR /app

# Determinism: pin hash seed so Holm/BH tie-breaks on (p, hid) tuples are
# byte-identical across runs (audit-final A8/C5 / opus_reaudit).
ENV PYTHONHASHSEED=0
# Determinism: pin SOURCE_DATE_EPOCH so any artifact writer routed through
# main._bundle_analysis.generated_at_utc() emits a fixed UTC timestamp
# (final_opus_audit.md §1.12). The value is the Reproducible Builds
# convention's "neutral" canonical epoch (2023-11-14T22:13:20Z) and matches
# the value documented in the Makefile.
ENV SOURCE_DATE_EPOCH=1700000000

# System deps. ``git`` is pinned at build time via apt's pin-priority on the
# Debian base; if a future base image bumps the package version, update the
# version constraint here too.
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies from hash-pinned lockfiles BEFORE the editable
# install so the editable install only resolves intra-repo packages.
COPY requirements-stage1.lock.txt requirements-stage2-cpu.lock.txt /app/
RUN pip install --no-cache-dir --require-hashes -r /app/requirements-stage1.lock.txt && \
    pip install --no-cache-dir --require-hashes -r /app/requirements-stage2-cpu.lock.txt

# Copy packaged source
COPY packages/ /app/packages/
COPY main/ /app/main/
COPY README.md /app/README.md

# Install both packages without resolving dependencies (already pinned above).
RUN pip install --no-cache-dir --no-deps -e /app/packages/evaluator && \
    pip install --no-cache-dir --no-deps -e /app/packages/runner

# Run tests on build to validate
RUN python -m pytest /app/packages/evaluator/tests -q && \
    python -m pytest /app/packages/runner/tests -q

# Default: run evaluation on mounted bundle
ENTRYPOINT ["automechinterp-evaluator"]
CMD ["evaluate", "--bundle", "/bundle"]
