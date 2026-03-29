#!/usr/bin/env bash
# sync-skel.sh — Sync framework/ai/ into skel/ai/.
#
# PREREQUISITE: Run from the repository root.
# Repository: https://github.com/William12556/LLM-Governance-and-Orchestration
#
# Usage:
#   bin/sync-skel.sh
#
# Propagates core governance files from framework/ai/ to skel/ai/.
# Excludes framework-only directories (doc/, knowledge/) and ephemeral files.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRAMEWORK_SRC="${REPO_ROOT}/framework/ai"
SKEL_DST="${REPO_ROOT}/skel/ai"

# --- Validation ------------------------------------------------------------

if [[ ! -d "${FRAMEWORK_SRC}" ]]; then
    echo "Error: framework/ai not found at ${FRAMEWORK_SRC}" >&2
    exit 1
fi

if [[ ! -d "${SKEL_DST}" ]]; then
    echo "Error: skel/ai not found at ${SKEL_DST}" >&2
    exit 1
fi

# --- Excludes --------------------------------------------------------------
# doc/ and knowledge/ are framework-only development artefacts.
# They must not propagate to skel/ or downstream projects.

EXCLUDES=(
    --exclude='doc/'
    --exclude='knowledge/'
    --exclude='.DS_Store'
    --exclude='__pycache__/'
    --exclude='*.pyc'
    --exclude='*.pyo'
)

# --- Preview ---------------------------------------------------------------

echo "=== Preview: framework/ai -> skel/ai ==="
echo ""

CHANGES=$(rsync --dry-run -av --itemize-changes "${EXCLUDES[@]}" \
    "${FRAMEWORK_SRC}/" "${SKEL_DST}/" | grep '^>f' || true)

if [[ -z "${CHANGES}" ]]; then
    echo "skel/ai is up to date. No changes to apply."
    exit 0
fi

echo "${CHANGES}"
echo ""

# --- Confirmation ----------------------------------------------------------

read -r -p "Apply changes? [y/N] " CONFIRM
if [[ "${CONFIRM}" != "y" && "${CONFIRM}" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# --- Sync ------------------------------------------------------------------

rsync -av "${EXCLUDES[@]}" \
    "${FRAMEWORK_SRC}/" "${SKEL_DST}/"

echo ""
echo "Done. Review changes and commit manually."
echo "Next: run bin/propagate.sh <project-root> for each downstream project."
