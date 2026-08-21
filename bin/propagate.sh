#!/usr/bin/env bash
# propagate.sh — Push ai/ to a downstream project ai/ directory.
#
# PREREQUISITE: The LLM-Governance-and-Orchestration repository must be
# cloned locally. This script must be run from the repository root.
# Clone: https://github.com/William12556/LLM-Governance-and-Orchestration
#
# Usage:
#   bin/propagate.sh <project-root>
#
# Example:
#   bin/propagate.sh ~/Documents/GitHub/<project name>
#
# The script pushes ai/ into <project-root>/ai/.
# Project-specific files are never overwritten (see Excludes below).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AI_SRC="${REPO_ROOT}/ai"

# --- Argument validation ---------------------------------------------------

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <project-root>" >&2
    exit 1
fi

PROJECT_ROOT="$(cd "$1" && pwd)"
PROJECT_AI="${PROJECT_ROOT}/ai"

if [[ ! -d "${AI_SRC}" ]]; then
    echo "Error: ai/ not found at ${AI_SRC}" >&2
    exit 1
fi

if [[ ! -d "${PROJECT_AI}" ]]; then
    echo "Error: target ai/ directory not found at ${PROJECT_AI}" >&2
    exit 1
fi

# --- Excludes --------------------------------------------------------------
# Project-specific files that must never be overwritten in the target.

# Path-specific excludes are anchored with a leading '/' (relative to the
# transfer root, ai/) so each matches only its intended file. Unanchored, a
# basename pattern matches at any depth: 'workspace/' would also exclude a
# downstream ai/doc/workspace/, and 'config.yaml' any config.yaml anywhere
# under ai/. Only the genuinely depth-independent patterns below — editor and
# interpreter droppings — remain unanchored.

EXCLUDES=(
    --exclude='/ael/config.yaml'    # project-specific AEL configuration
    --exclude='/context.md'         # project-specific conventions/stack; seeded below when absent
    --exclude='/task.md'            # project-specific open-work register; seeded below when absent
    --exclude='/workspace/'         # project-local governance documents
    --exclude='/state/'             # AEL runtime state (post-2026-06-16 path; was ael/state/)
    --exclude='/dashboard-alerts.md' # govwatch write target
    --exclude='.DS_Store'
    --exclude='__pycache__/'
    --exclude='*.pyc'
    --exclude='*.pyo'
)

# --- Preview ---------------------------------------------------------------
# --itemize-changes lines beginning with '>f' indicate files that would
# actually be transferred. Directories and unchanged files are excluded.

echo "=== Preview: ai -> ${PROJECT_AI} ==="
echo ""

# context.md is excluded from the transfer, so it is invisible to CHANGES. A
# target differing from the source only by a missing context.md therefore
# reported "up to date" and exited before reaching the seeding pass below —
# making that pass unreachable in precisely the case it exists to serve, the
# new project. The seed condition is evaluated here, before the early exit,
# and admitted as work to be done.

if [[ -f "${PROJECT_AI}/context.md" ]]; then
    NEEDS_SEED_CONTEXT="false"
else
    NEEDS_SEED_CONTEXT="true"
fi

if [[ -f "${PROJECT_AI}/task.md" ]]; then
    NEEDS_SEED_TASK="false"
else
    NEEDS_SEED_TASK="true"
fi

CHANGES=$(rsync --dry-run -av --itemize-changes "${EXCLUDES[@]}" \
    "${AI_SRC}/" "${PROJECT_AI}/" | grep '^>f' || true)

if [[ -z "${CHANGES}" && "${NEEDS_SEED_CONTEXT}" == "false" && "${NEEDS_SEED_TASK}" == "false" ]]; then
    echo "Target is up to date. No changes to apply."
    exit 0
fi

if [[ -n "${CHANGES}" ]]; then
    echo "${CHANGES}"
else
    echo "(no framework files differ)"
fi

if [[ "${NEEDS_SEED_CONTEXT}" == "true" ]]; then
    echo "seed         context.md (absent in target)"
fi

if [[ "${NEEDS_SEED_TASK}" == "true" ]]; then
    echo "seed         task.md (absent in target)"
fi

echo ""

# --- Confirmation ----------------------------------------------------------

read -r -p "Apply changes? [y/N] " CONFIRM
if [[ "${CONFIRM}" != "y" && "${CONFIRM}" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# --- Propagate -------------------------------------------------------------

rsync -av "${EXCLUDES[@]}" \
    "${AI_SRC}/" "${PROJECT_AI}/"

# --- Seed project-specific context ----------------------------------------
# context.md is excluded from the transfer above so an existing downstream copy
# is never overwritten. New projects still need the template, so seed it here.
# NEEDS_SEED was evaluated before the preview's early exit; --ignore-existing is
# not used, as the absence of the file is already established by that test.

if [[ "${NEEDS_SEED_CONTEXT}" == "true" ]]; then
    rsync -a "${AI_SRC}/context.md" "${PROJECT_AI}/"
    echo ""
    echo "context.md: template seeded (new project). Fill it in before the first AEL run."
else
    echo ""
    echo "context.md: existing project copy preserved."
fi

if [[ "${NEEDS_SEED_TASK}" == "true" ]]; then
    rsync -a "${AI_SRC}/task.md" "${PROJECT_AI}/"
    echo ""
    echo "task.md: template seeded (new project)."
else
    echo ""
    echo "task.md: existing project copy preserved."
fi

echo ""
echo "Done. Review changes and commit manually."
