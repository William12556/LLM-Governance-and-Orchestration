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

EXCLUDES=(
    --exclude='config.yaml'        # project-specific AEL configuration
    --exclude='workspace/'         # project-local governance documents
    --exclude='ael/state/'         # ephemeral AEL state
    --exclude='dashboard-alerts.md' # govwatch write target
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

CHANGES=$(rsync --dry-run -av --itemize-changes "${EXCLUDES[@]}" \
    "${AI_SRC}/" "${PROJECT_AI}/" | grep '^>f' || true)

if [[ -z "${CHANGES}" ]]; then
    echo "Target is up to date. No changes to apply."
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

# --- Propagate -------------------------------------------------------------

rsync -av "${EXCLUDES[@]}" \
    "${AI_SRC}/" "${PROJECT_AI}/"

echo ""
echo "Done. Review changes and commit manually."
