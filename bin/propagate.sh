#!/usr/bin/env bash
# propagate.sh — Push skel/ai/ to a downstream project ai/ directory.
#
# PREREQUISITE: The LLM-Governance-and-Orchestration repository must be
# cloned locally. This script must be run from the repository root.
# Clone: https://github.com/William12556/LLM-Governance-and-Orchestration
#
# Usage:
#   bin/propagate.sh <project-root>
#
# Example:
#   bin/propagate.sh /Users/williamwatson/Documents/GitHub/GTach
#
# The script pushes skel/ai/ into <project-root>/ai/.
# Project-specific files (config.yaml) are never overwritten.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKEL_SRC="${REPO_ROOT}/skel/ai"

# --- Argument validation ---------------------------------------------------

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <project-root>" >&2
    exit 1
fi

PROJECT_ROOT="$(cd "$1" && pwd)"
PROJECT_AI="${PROJECT_ROOT}/ai"

if [[ ! -d "${SKEL_SRC}" ]]; then
    echo "Error: skel/ai not found at ${SKEL_SRC}" >&2
    exit 1
fi

if [[ ! -d "${PROJECT_AI}" ]]; then
    echo "Error: target ai/ directory not found at ${PROJECT_AI}" >&2
    exit 1
fi

# --- Excludes --------------------------------------------------------------
# Files that are project-specific and must never be overwritten.

EXCLUDES=(
    --exclude='config.yaml'
    --exclude='.DS_Store'
    --exclude='__pycache__/'
    --exclude='*.pyc'
    --exclude='*.pyo'
)

# --- Preview ---------------------------------------------------------------
# --itemize-changes lines beginning with '>f' indicate files that would
# actually be transferred. Directories and unchanged files are excluded.

echo "=== Preview: skel/ai -> ${PROJECT_AI} ==="
echo ""

CHANGES=$(rsync --dry-run -av --itemize-changes "${EXCLUDES[@]}" \
    "${SKEL_SRC}/" "${PROJECT_AI}/" | grep '^>f' || true)

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
    "${SKEL_SRC}/" "${PROJECT_AI}/"

echo ""
echo "Done. Review changes and commit manually."
