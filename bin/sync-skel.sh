#!/usr/bin/env bash
# sync-skel.sh — OBSOLETE.
#
# The framework/ai/ -> skel/ai/ two-step propagation chain has been removed.
# ai/ is now the single canonical source for downstream propagation.
#
# Use bin/propagate.sh <project-root> to push ai/ to a downstream project.

echo "sync-skel.sh is obsolete. Use bin/propagate.sh <project-root> instead." >&2
exit 1
