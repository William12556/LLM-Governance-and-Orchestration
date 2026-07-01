"""
AEL Orchestrator — Ralph Loop.

Standalone tool loop: connects directly to MCP servers, sends tool
definitions to oMLX, parses model tool calls (OpenAI and Mistral
plain-text formats), dispatches tools, injects results, iterates
until no tool calls remain.

Modes:
    worker   — single work phase pass
    reviewer — single review phase pass
    loop     — full worker/reviewer Ralph Loop cycle
    reset    — clear state directory after human acceptance

Usage:
    python orchestrator.py --mode worker   --task ai/workspace/prompt/prompt-abc123.md
    python orchestrator.py --mode reviewer --task ai/workspace/prompt/prompt-abc123.md
    python orchestrator.py --mode loop     --task ai/workspace/prompt/prompt-abc123.md
    python orchestrator.py --mode loop     --task "implement the login module"
    python orchestrator.py --mode reset

Terminal output legend (rich TUI):
    ╔ Ralph Loop — AEL ╗ panel          startup banner with worker/reviewer/task
    ── loop iteration N/M ──  rule      loop-level cycle counter (N = max_iterations)
    ▶ WORK PHASE / ▶ REVIEW PHASE       which loop half is active
    ── WORKER iteration N/M ──  rule    phase-level LLM call counter
    ████░░  X%  N / M tokens            context budget bar (dim/yellow/red by status)
    ╔ think ╗ panel                     model reasoning output (tagged: reasoning_content / <think>)
    ╔ narration ╗ panel                 untagged model commentary preceding a tool call (F20)
      call →  tool_name(args)           outbound tool call to MCP server
      result ← preview                  MCP result returned (truncated 200 chars)
    ╔ response ╗ panel                  worker final response
    ╔ ✓ SHIPPED ╗ panel                 reviewer wrote SHIP; loop exits
    ╔ ↻ REVISE ╗ panel                  reviewer feedback for next iteration
    ╔ ✗ BLOCKED ╗ panel                 loop blocked; content is RALPH-BLOCKED.md body
"""

import argparse
import asyncio
import datetime
import glob
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import uuid

import yaml
from openai import AsyncOpenAI

sys.path.insert(0, os.path.dirname(__file__))
from mcp_client import MCPClient
from parser import parse_tool_calls

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.rule import Rule

console = Console(highlight=False)


def _ctx_bar(estimated: int, context_window: int, status: str) -> str:
    """Render a compact inline context progress bar."""
    filled = int((estimated / context_window) * 20)
    bar = "\u2588" * filled + "\u2591" * (20 - filled)
    pct = (estimated / context_window) * 100
    color = "red" if status == "abort" else "yellow" if status == "warn" else "dim"
    return f"[{color}]  {bar}  {pct:.1f}%  {estimated:,} / {context_window:,} tokens[/{color}]"

# F7: MCP error detection uses prefix matching only to avoid false positives.
# A benign result containing these strings mid-text will not be misclassified.
_MCP_ERROR_PREFIXES = (
    "Error:",
    "Error calling",
    "MCP error",
)

_EDIT_PATTERN_ERRORS = (
    "edits failed to match",
    "E_INVALID_INPUT",
)

# F4: Write/destructive tool names for scope validation
_WRITE_TOOLS = {
    "write", "write_file", "create_file",
    "edit", "edit_file",
    "delete", "remove", "delete_file", "remove_file",
    "move", "rename", "move_file", "rename_file",
    "mkdir", "create_directory", "makedirs",
}

# F12: Stall detection — consecutive identical REVISE feedback threshold
_DEFAULT_STALL_THRESHOLD = 3

# F14: Completion call retry settings
_COMPLETION_MAX_RETRIES = 3
_COMPLETION_INITIAL_BACKOFF = 2.0  # seconds
_COMPLETION_BACKOFF_MULTIPLIER = 2.0


def _validate_write_scope(tool_name: str, arguments: dict, project_root: str) -> str | None:
    """
    F4: Validate that write/destructive tool calls target paths within project_root.

    Returns None if the tool is in scope or not a write tool.
    Returns an error message string if the path is out of scope.
    """
    if tool_name not in _WRITE_TOOLS:
        return None

    # Extract path from common argument names
    target_path = arguments.get("path") or arguments.get("file_path") or arguments.get("destination")
    if not target_path:
        return None  # Let MCP validate missing required args

    # Resolve to absolute and check containment
    try:
        resolved = os.path.abspath(target_path)
        if not resolved.startswith(project_root + os.sep) and resolved != project_root:
            return (
                f"Scope violation: path '{target_path}' is outside the project root "
                f"'{project_root}'. All writes must target paths within the project."
            )
    except Exception:
        pass  # Let MCP handle malformed paths

    return None


def _validate_audit_report_write(tool_name: str, arguments: dict, state_dir: str) -> str | None:
    """
    F21: Block writes to audit-report.md that would discard prior findings.

    audit-report.md is append-only across a 25-item audit run. A write/write_file/
    create_file call (overwrite semantics) whose content omits the file's existing
    content would silently destroy previously recorded findings. edit/edit_file
    calls (patch semantics) are not affected.

    Returns None if safe (not a write tool, not this file, file absent/empty,
    or existing content is preserved in the new content). Returns an error
    message string otherwise.
    """
    if tool_name not in ("write", "write_file", "create_file"):
        return None
    target = arguments.get("path") or arguments.get("file_path") or ""
    if os.path.basename(target) != "audit-report.md":
        return None
    report_path = os.path.join(state_dir, "audit-report.md")
    if not os.path.exists(report_path):
        return None
    existing = open(report_path).read().strip()
    if not existing or existing in (arguments.get("content") or "").strip():
        return None
    return (
        f"Error: This write would discard {len(existing)} characters of existing "
        "audit-report.md findings. audit-report.md is append-only \u2014 use the edit "
        "tool to append, or include the full existing content before your new entry."
    )


def _is_mcp_error(result: str) -> bool:
    """
    F7: Return True if result string indicates an MCP tool error.

    Uses prefix matching only to avoid false positives — a benign result
    containing error-like text mid-string will not be misclassified.
    """
    return any(result.startswith(p) for p in _MCP_ERROR_PREFIXES)


def _normalize_verdict(text: str) -> str:
    """
    Normalize a review verdict string to SHIP or REVISE.

    Handles various formats:
      - 'SHIP', 'ship', 'SHIP.', '**SHIP**', 'SHIP!' -> 'SHIP'
      - 'REVISE', 'revise', 'REVISE:', '**REVISE**' -> 'REVISE'
      - 'SHIP: The code looks good...' -> 'SHIP' (leading token)

    Returns 'SHIP' if the leading token (uppercased, non-alphanumerics stripped)
    matches 'SHIP', otherwise returns 'REVISE'.
    """
    if not text:
        return "REVISE"

    # Extract first token: split on whitespace, take first word
    tokens = text.strip().split()
    if not tokens:
        return "REVISE"

    leading = tokens[0]

    # Normalize: uppercase, strip non-alphanumerics
    normalized = re.sub(r'[^A-Za-z]', '', leading).upper()

    # SHIP set: exact match only
    if normalized == "SHIP":
        return "SHIP"

    return "REVISE"


# State files cleared by reset (logs and context report excluded)
_RESET_FILES = [
    "task.md",
    "iteration.txt",
    "work-summary.txt",
    "work-complete.txt",
    "review-result.txt",
    "review-feedback.txt",
    ".ralph-complete",
    ".ralph-timeout",  # F10: duration-limit sentinel
    "RALPH-BLOCKED.md",
    "audit-index.md",
    "audit-report.md",
]


def _hash_feedback(feedback: str) -> str:
    """F12: Return a short hash of feedback content for stall detection."""
    return hashlib.sha256(feedback.encode()).hexdigest()[:16] if feedback else ""


async def _completion_with_retry(
    client,
    model: str,
    messages: list[dict],
    tools: list[dict] | None,
    log: logging.Logger,
    state_dir: str,
    max_retries: int = _COMPLETION_MAX_RETRIES,
    initial_backoff: float = _COMPLETION_INITIAL_BACKOFF,
    backoff_multiplier: float = _COMPLETION_BACKOFF_MULTIPLIER,
):
    """
    F14: Bounded retry with exponential backoff around the completion call.

    On persistent failure after max_retries, writes RALPH-BLOCKED.md and raises
    a RuntimeError to signal clean termination (no uncaught exception).
    """
    backoff = initial_backoff
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools or None,
                stream=False,
            )
            return response
        except Exception as e:
            last_error = e
            log.warning(
                "completion call failed (attempt %d/%d): %s",
                attempt, max_retries, e,
            )
            if attempt < max_retries:
                console.print(
                    f"[yellow][ael] completion error (attempt {attempt}/{max_retries}), "
                    f"retrying in {backoff:.1f}s: {e}[/yellow]"
                )
                await asyncio.sleep(backoff)
                backoff *= backoff_multiplier
            else:
                # Persistent failure — BLOCK cleanly
                tb = traceback.format_exc()
                log.error("completion call persistent failure:\n%s", tb)
                blocked_msg = (
                    "# RALPH-BLOCKED\n\n"
                    f"Completion call failed after {max_retries} attempts.\n\n"
                    f"Last error: {last_error}\n\n"
                    f"Traceback:\n```\n{tb}\n```\n"
                )
                write_state(state_dir, "RALPH-BLOCKED.md", blocked_msg)
                console.print(
                    f"[red][ael] BLOCKED: completion call failed after {max_retries} attempts[/red]"
                )
                raise RuntimeError(f"Completion call failed: {last_error}") from last_error

    # Should not reach here, but satisfy type checker
    raise RuntimeError("Unexpected: completion retry loop exited without return or raise")


def _archive_audit_artifacts(state_dir: str, task_path: str | None, log: logging.Logger) -> None:
    """
    Copy audit-index.md and audit-report.md from state_dir to ai/workspace/audit/
    with canonical naming: audit-<uuid>-index.md and audit-<uuid>-report.md.
    Called after a successful audit loop SHIP. No-op if audit-report.md is absent.
    UUID is extracted from the task file path basename (first 8-hex substring).
    Falls back to yyyymmdd timestamp if UUID cannot be determined.
    """
    report_src = os.path.join(state_dir, "audit-report.md")
    if not os.path.exists(report_src):
        return  # not an audit run

    index_src = os.path.join(state_dir, "audit-index.md")

    uid = None
    if task_path:
        m = re.search(r"[0-9a-f]{8}", os.path.basename(task_path))
        uid = m.group(0) if m else None
    if not uid:
        uid = datetime.datetime.now().strftime("%Y%m%d")
        log.warning("archive audit: UUID not found in task path — using date fallback: %s", uid)

    output_dir = os.path.join(os.getcwd(), "ai", "workspace", "audit")
    os.makedirs(output_dir, exist_ok=True)

    archived = 0
    for src, suffix in [(index_src, "index"), (report_src, "report")]:
        if os.path.exists(src):
            dst = os.path.join(output_dir, f"audit-{uid}-{suffix}.md")
            shutil.copy2(src, dst)
            archived += 1
            log.info("archive audit: %s -> %s", src, dst)
            console.print(f"[green][ael] audit archived: {escape(dst)}[/green]")
        else:
            log.warning("archive audit: %s not found — skipping", src)

    if archived:
        console.print(
            f"[green][ael] {archived} audit artifact(s) archived to {escape(output_dir)}[/green]"
        )


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def read_state(state_dir: str, filename: str) -> str:
    path = os.path.join(state_dir, filename)
    return open(path).read().strip() if os.path.exists(path) else ""


def write_state(state_dir: str, filename: str, content: str) -> None:
    os.makedirs(state_dir, exist_ok=True)
    with open(os.path.join(state_dir, filename), "w") as f:
        f.write(content)


def reset_state(state_dir: str) -> int:
    """
    Remove all Ralph Loop state files from state_dir.
    Log files (ael_*.LOG) and context-budget.md are preserved.
    Returns 0 on success, 1 if state_dir does not exist.
    """
    if not os.path.isdir(state_dir):
        console.print(f"[yellow][ael] reset: state directory not found: {state_dir}[/yellow]")
        return 1
    removed = []
    for name in _RESET_FILES:
        path = os.path.join(state_dir, name)
        if os.path.exists(path):
            os.remove(path)
            removed.append(name)
    if removed:
        console.print(f"[green][ael] reset: removed {len(removed)} state file(s)[/green]")
        for name in removed:
            console.print(f"[dim]  {name}[/dim]")
    else:
        console.print("[yellow][ael] reset: state directory already clean[/yellow]")
    return 0


def resolve_context_window(
    model_name: str,
    models_dir: str,
    override: int | None,
    log: logging.Logger,
    model_overrides: dict | None = None,
) -> int | None:
    """
    Resolve the model context window in tokens.

    Priority:
      1. config.yaml context.context_window global override (if set)
      2. F18: config.yaml context.model_context_windows per-model override (if set)
      3. max_position_embeddings from model config.json on disk
         Searches models_dir for the exact model directory (not arbitrary glob match).
         Handles both top-level and text_config-nested layout.

    Returns the context window as int, or None if not determinable.
    """
    if override is not None:
        log.info("context window: %d (config global override)", override)
        return override

    # F18: Check per-model override from config
    if model_overrides and model_name in model_overrides:
        ctx = model_overrides[model_name]
        log.info("context window: %d (config per-model override for '%s')", ctx, model_name)
        return int(ctx)

    if not models_dir:
        log.debug("context window: models_dir not set — skipping disk lookup")
        return None

    # F18: Match exact model directory instead of arbitrary glob
    # Try direct path first, then search subdirectories
    candidate_paths = [
        os.path.join(models_dir, model_name, "config.json"),
    ]
    # Also check one level of subdirectories (e.g., models_dir/mlx-community/model_name)
    for subdir in os.listdir(models_dir) if os.path.isdir(models_dir) else []:
        candidate_paths.append(os.path.join(models_dir, subdir, model_name, "config.json"))

    cfg_path = None
    for path in candidate_paths:
        if os.path.exists(path):
            cfg_path = path
            break

    if not cfg_path:
        log.debug("context window: no config.json found for '%s' under %s", model_name, models_dir)
        return None

    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
        # Try top-level first, then text_config (Mistral3 / vision model layout)
        ctx = (
            cfg.get("max_position_embeddings")
            or (cfg.get("text_config") or {}).get("max_position_embeddings")
        )
        if ctx:
            log.info("context window: %d (from %s)", ctx, cfg_path)
            return int(ctx)
        log.debug("context window: max_position_embeddings not found in %s", cfg_path)
    except Exception as exc:
        log.warning("context window: failed to read %s: %s", cfg_path, exc)
    return None


def estimate_tokens(messages: list[dict], tools: list[dict] | None = None) -> int:
    """
    Approximate token count for a list of chat messages plus optional tool schema.

    F8: Includes both message content and serialized tool-schema length.
    Uses len(content) // 4 — a standard heuristic for Mistral-family BPE.
    Slightly overestimates, which is the safe direction for budget checks.
    """
    total = 0
    for m in messages:
        content = m.get("content") or ""
        if isinstance(content, str):
            total += len(content) // 4
        elif isinstance(content, list):
            # multimodal content blocks
            for block in content:
                if isinstance(block, dict):
                    total += len(block.get("text", "")) // 4

    # F8: Include serialized tool schema in token estimate
    if tools:
        total += len(json.dumps(tools)) // 4

    return total


def check_context_budget(
    estimated: int,
    context_window: int,
    warn_pct: float,
    abort_pct: float,
) -> tuple[str, float]:
    """
    Compare estimated token count against context window thresholds.
    Returns (status, fraction) where status is 'ok', 'warn', or 'abort'.
    """
    fraction = estimated / context_window
    if fraction >= abort_pct:
        return "abort", fraction
    if fraction >= warn_pct:
        return "warn", fraction
    return "ok", fraction


def write_context_report(
    state_dir: str,
    model: str,
    context_window: int | None,
    initial_tokens: int,
    warn_pct: float,
    abort_pct: float,
) -> None:
    """
    Write context-budget.md to state_dir for Strategic Domain consumption.
    This file informs the Strategic Domain of available context headroom
    before authoring the next tactical_brief or T04 prompt.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if context_window is None:
        report = (
            f"# AEL Context Budget Report\n\n"
            f"Generated: {now}\n"
            f"Model: {model}\n\n"
            f"Context window could not be determined for this model.\n"
            f"Set `context.context_window` in config.yaml to enable budget tracking.\n"
        )
        write_state(state_dir, "context-budget.md", report)
        return

    headroom = context_window - initial_tokens
    warn_tokens  = int(context_window * warn_pct)
    abort_tokens = int(context_window * abort_pct)
    initial_pct  = (initial_tokens / context_window) * 100
    # Estimate per-iteration accumulation: system prompt + task already counted,
    # each iteration adds roughly one tool call (~100 tokens) + result (~100 tokens)
    # + assistant response (~100 tokens) = ~300 tokens
    est_per_iter   = 300
    iters_to_warn  = max(0, (warn_tokens  - initial_tokens) // est_per_iter)
    iters_to_abort = max(0, (abort_tokens - initial_tokens) // est_per_iter)

    report = f"""# AEL Context Budget Report

Generated: {now}
Model: {model}
Context window: {context_window:,} tokens

## Initial task load
Estimated tokens at task start: {initial_tokens:,} tokens ({initial_pct:.1f}% of window)
Headroom available: {headroom:,} tokens

## Budget thresholds
Warn at:  {warn_tokens:,} tokens ({warn_pct*100:.0f}%)
Abort at: {abort_tokens:,} tokens ({abort_pct*100:.0f}%)

## Iteration estimates
Estimated accumulation per iteration: ~{est_per_iter} tokens
Iterations before warn threshold:  ~{iters_to_warn}
Iterations before abort threshold: ~{iters_to_abort}

## Guidance for Strategic Domain
When authoring the next tactical_brief or T04 prompt:

- Current initial load is {initial_pct:.1f}% of context window
- Each Ralph Loop phase iteration accumulates ~{est_per_iter} tokens
- Recommended tactical_brief size: ≤1,000 tokens
- Avoid embedding large design documents or code blocks in the brief
- Context pressure symptoms: duplicate tool calls, repeated reads, verbose responses
- If symptoms appear, reduce brief size and restart with --mode reset
"""
    write_state(state_dir, "context-budget.md", report)


async def await_model_ready(
    client: AsyncOpenAI,
    model: str,
    timeout: float = 60.0,
    interval: float = 2.0,
) -> None:
    """
    Poll /v1/models until the target model is listed or the endpoint is
    reachable. Raises TimeoutError if the endpoint remains unreachable.
    """
    deadline = time.monotonic() + timeout
    attempt = 0
    while True:
        attempt += 1
        try:
            models = await client.models.list()
            ids = [m.id for m in models.data]
            if model in ids:
                console.print(f"[green][ael] model ready: {model}[/green]")
                return
            # Endpoint up; model not listed — oMLX loads on first request
            console.print(f"[yellow][ael] endpoint ready; '{model}' not listed — proceeding[/yellow]")
            return
        except Exception as e:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"[ael] inference endpoint not reachable after {timeout}s: {e}"
                ) from e
            console.print(
                f"[yellow][ael] waiting for endpoint "
                f"(attempt {attempt}, {remaining:.0f}s remaining): {e}[/yellow]"
            )
            await asyncio.sleep(interval)


def clear_state(state_dir: str, *filenames: str) -> None:
    for name in filenames:
        path = os.path.join(state_dir, name)
        if os.path.exists(path):
            os.remove(path)


def setup_logging(state_dir: str) -> logging.Logger:
    os.makedirs(state_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(state_dir, f"ael_{timestamp}.LOG")
    logger = logging.getLogger("ael")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # F19: prevent duplicate console output via root logger's default handler
    if not logger.handlers:
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(fh)
    return logger


def extract_tactical_brief(raw: str, log: logging.Logger) -> str:
    """
    Extract tactical_brief from a T04 prompt document.

    Pass 1: scan all fenced ```yaml blocks for a tactical_brief key.
    Pass 2: if Pass 1 fails, find the first '## N.N Tactical Brief' section
            header and extract the content of the first fenced block beneath it.
    Returns the brief string, or empty string if neither pass succeeds.
    """
    # Pass 1: YAML block with tactical_brief key (preferred)
    blocks = re.findall(r"```yaml\n(.*?)```", raw, re.DOTALL)
    log.debug("extract_tactical_brief: found %d YAML blocks", len(blocks))
    for i, block in enumerate(blocks):
        try:
            doc = yaml.safe_load(block)
            candidate = ((doc or {}).get("tactical_brief") or "").strip()
            if candidate:
                log.debug("extract_tactical_brief: brief found in block %d (%d chars)", i, len(candidate))
                return candidate
        except Exception as exc:
            log.debug("extract_tactical_brief: block %d parse error: %s", i, exc)

    # Pass 2: section-header fallback — locate ## N.N Tactical Brief heading
    section_match = re.search(
        r"##\s+[\d.]+\s+Tactical Brief.*?\n(.*?)(?=\n##\s|\Z)",
        raw, re.DOTALL | re.IGNORECASE,
    )
    if section_match:
        section_body = section_match.group(1)
        fence_match = re.search(r"```[^\n]*\n(.*?)```", section_body, re.DOTALL)
        if fence_match:
            candidate = fence_match.group(1).strip()
            if candidate:
                log.warning(
                    "extract_tactical_brief: YAML tactical_brief key not found — "
                    "using fenced block under section header (%d chars). "
                    "Author \u00a78.0 as a ```yaml block with tactical_brief: as root key.",
                    len(candidate),
                )
                return candidate

    log.warning(
        "extract_tactical_brief: no tactical_brief found in %d YAML blocks and no "
        "section-header fallback matched — falling back to raw document. "
        "Author \u00a78.0 as a ```yaml block with tactical_brief: as root key.",
        len(blocks),
    )
    return ""


def extract_reasoning(message, content: str, log: logging.Logger) -> tuple[str, str]:
    """
    Extract model reasoning from response message.
    Checks reasoning_content attribute first (some providers), then
    <think>...</think> tags (Mistral/Devstral), then Cohere's
    <|START_THINKING|>...<|END_THINKING|> blocks (North-Mini-Code-1.0 / cohere2_moe).
    Returns (reasoning, content_without_reasoning_tags).
    """
    reasoning = getattr(message, "reasoning_content", None) or ""
    if not reasoning and content:
        think_match = re.search(r"<think>(.*?)</think>", content, re.DOTALL)
        if think_match:
            reasoning = think_match.group(1).strip()
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            log.debug("extracted <think> block (%d chars)", len(reasoning))
        else:
            # F23: Cohere thinking-block (North-Mini-Code-1.0 / cohere2_moe via oMLX)
            cohere_match = re.search(r"<\|START_THINKING\|>(.*?)<\|END_THINKING\|>", content, re.DOTALL)
            if cohere_match:
                reasoning = cohere_match.group(1).strip()
                content = re.sub(r"<\|START_THINKING\|>.*?<\|END_THINKING\|>", "", content, flags=re.DOTALL).strip()
                log.debug("extracted <|START_THINKING|> block (%d chars)", len(reasoning))
    return reasoning, content


def format_tool_signatures(tools: list[dict]) -> str:
    """
    Render tool names with their parameter signatures for injection
    into the recipe system prompt via {{TOOLS}}.

    Format per tool:
        - tool_name(param: type [required], param: type)

    Grounded in the live MCP schema so the model cannot hallucinate
    argument names. Descriptions are omitted to keep prompt compact.
    """
    lines = []
    for t in tools:
        fn = t.get("function", {})
        name = fn.get("name", "")
        params_schema = fn.get("parameters", {})
        props = params_schema.get("properties", {})
        required = set(params_schema.get("required", []))
        args = []
        for p, schema in props.items():
            req = " [required]" if p in required else ""
            args.append(f"{p}: {schema.get('type', 'any')}{req}")
        lines.append(f"  - {name}({', '.join(args)})")
    return "\n".join(lines)


async def run_phase(
    client: AsyncOpenAI,
    mcp: MCPClient,
    model: str,
    recipe: dict,
    task: str,
    max_iterations: int,
    state_dir: str,
    log: logging.Logger,
    phase_label: str = "",
    context_window: int | None = None,
    budget_warn_pct: float = 0.80,
    budget_abort_pct: float = 0.95,
    mcp_error_threshold: int = 3,
    max_tool_calls_per_iter: int = 10,
    project_root: str = "",
) -> tuple[int, str]:
    """
    Single phase (worker or reviewer): inject tools, send completions,
    dispatch tool calls, loop until no tool calls remain.
    Returns (exit_code, final_message) where:
      - exit_code: 0 on success, 1 on failure
      - final_message: the terminal assistant response text (empty on failure or tool exit)
    """
    is_worker_phase = "REVIEW" not in phase_label.upper()
    # F5: review phase gets read-only tool subset; worker gets full toolset
    tools = mcp.get_openai_tools(readonly=not is_worker_phase)

    # Build real tool name list and inject into recipe system prompt
    tool_list = format_tool_signatures(tools)
    system_prompt = recipe.get("instructions", "").replace("{{TOOLS}}", tool_list)

    # F24: for audit runs, inject the next unchecked item directly into the
    # work-phase task so the model doesn't have to re-derive it each iteration
    # by reading and parsing the full audit-index.md / audit-uml.md.
    if is_worker_phase:
        _audit_index_path = os.path.join(state_dir, "audit-index.md")
        if os.path.exists(_audit_index_path):
            _next_item = next(
                (text for checked, text in _parse_audit_items(_audit_index_path) if not checked),
                None,
            )
            if _next_item:
                task = f"[NEXT AUDIT ITEM]\n{_next_item}\n[END NEXT AUDIT ITEM]\n\n" + task

    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": task},
    ]

    mcp_error_count = 0
    _read_counts: dict[str, int] = {}  # P3: duplicate read tracking

    label = f"{phase_label} " if phase_label else ""
    console.rule(f"[blue]{label or 'AEL'} — {escape(model)}[/blue]", style="blue")
    console.print(f"[blue][ael] tools:  {len(tools)}[/blue]")
    console.print(f"[blue][ael] task:   {escape(task[:80])}{'...' if len(task) > 80 else ''}[/blue]")
    log.info("phase start phase=%s model=%s tools=%d task=%s", phase_label or "?", model, len(tools), task)

    for iteration in range(1, max_iterations + 1):
        iter_label = f"{phase_label}  " if phase_label else ""
        console.rule(f"[blue dim]{iter_label}iteration {iteration}/{max_iterations}[/blue dim]", style="blue dim")
        log.debug("iteration %d/%d phase=%s", iteration, max_iterations, phase_label or "?")

        # F25: refresh system message with an iteration countdown each pass so
        # the model can self-regulate pacing instead of being cut off abruptly.
        _remaining = max_iterations - iteration + 1
        _status = f"[ITERATION STATUS] {iteration}/{max_iterations} ({_remaining} remaining)"
        if _remaining <= max(5, max_iterations // 5):
            _status += " — budget running low; finish the current item and call work-complete soon."
        messages[0]["content"] = system_prompt + "\n\n" + _status

        # Context budget check before API call
        if context_window is not None:
            estimated = estimate_tokens(messages)
            status, fraction = check_context_budget(
                estimated, context_window, budget_warn_pct, budget_abort_pct
            )
            pct_str = f"{fraction*100:.1f}%"
            if status == "abort":
                console.print(_ctx_bar(estimated, context_window, status))
                console.print("[red]  budget exceeded — aborting phase[/red]")
                log.error("context budget abort: %d / %d tokens (%.1f%%)",
                          estimated, context_window, fraction * 100)
                return 1, ""
            elif status == "warn":
                console.print(_ctx_bar(estimated, context_window, status))
                log.warning("context budget warn: %d / %d tokens (%.1f%%)",
                            estimated, context_window, fraction * 100)
            else:
                console.print(_ctx_bar(estimated, context_window, status))
                log.debug("context budget ok: %d / %d tokens (%.1f%%)",
                          estimated, context_window, fraction * 100)

        # F14: Use bounded retry with backoff for transient endpoint errors
        try:
            response = await _completion_with_retry(
                client, model, messages, tools, log, state_dir
            )
        except RuntimeError:
            # Persistent failure — RALPH-BLOCKED.md already written
            return 1, ""

        message = response.choices[0].message
        content = message.content or ""
        log.debug("iteration %d model response:\n%s", iteration, content)

        # Extract and display reasoning if present
        reasoning, content = extract_reasoning(message, content, log)
        if reasoning:
            log.debug("model reasoning:\n%s", reasoning)
            console.print(Panel(escape(reasoning), title="[dim cyan]think[/dim cyan]", border_style="dim cyan", expand=False))
        else:
            # F20: surface untagged model commentary that precedes a tool call.
            # Some models (e.g. Devstral) interleave narrative text with tool
            # calls instead of using a dedicated reasoning_content/<think> channel.
            # Without this, that text is logged but never reaches the console.
            # Strip any plain-text [TOOL_CALLS] marker — that syntax is shown
            # separately via the 'call ->' line once parsed below.
            _narration = content.split("[TOOL_CALLS]")[0].strip()
            if _narration and (message.tool_calls or "[TOOL_CALLS]" in content):
                log.debug("untagged narration (%d chars)", len(_narration))
                console.print(Panel(escape(_narration), title="[dim magenta]narration[/dim magenta]", border_style="dim magenta", expand=False))

        tool_calls: list[dict] = []

        if message.tool_calls:
            # OpenAI-format tool_calls in API response
            for tc in message.tool_calls:
                try:
                    arguments = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                tool_calls.append({"id": tc.id, "name": tc.function.name, "arguments": arguments})
        else:
            # Mistral plain-text format — parse from content
            parsed = parse_tool_calls(content)
            if parsed:
                for tc in parsed:
                    tc["id"] = f"call_{uuid.uuid4().hex[:8]}"
                tool_calls = parsed

        # F3: Apply tool call cap BEFORE building assistant message to avoid orphaned IDs.
        # The assistant message must only reference tool_calls that will have matching results.
        if tool_calls and len(tool_calls) > max_tool_calls_per_iter:
            log.warning(
                "iteration %d: %d tool calls exceeds cap %d — truncating",
                iteration, len(tool_calls), max_tool_calls_per_iter,
            )
            console.print(f"[yellow][ael] tool call cap ({max_tool_calls_per_iter}) exceeded "
                          f"({len(tool_calls)} calls) — truncating[/yellow]")
            tool_calls = tool_calls[:max_tool_calls_per_iter]

        # Build assistant message with (possibly truncated) tool_calls
        if tool_calls:
            messages.append({
                "role": "assistant",
                "content": content,
                "tool_calls": [
                    {"id": tc["id"], "type": "function",
                     "function": {"name": tc["name"], "arguments": json.dumps(tc["arguments"])}}
                    for tc in tool_calls
                ],
            })
        else:
            # No tool calls — final response
            messages.append({"role": "assistant", "content": content})

        if not tool_calls:
            # F7: Guard against malformed final response using structured signals.
            # Check for unparsed tool call markers (model tried to emit calls but parser failed).
            # Do NOT use substring scans for error patterns — a summary may legitimately
            # contain such text without indicating a malformed response.
            _has_unparsed_tool_marker = "[TOOL_CALLS]" in content and not message.tool_calls
            if _has_unparsed_tool_marker:
                blocked_msg = (
                    "# RALPH-BLOCKED\n\n"
                    "Worker final response contains unparsed tool call markers.\n\n"
                    f"Content preview:\n\n    {content[:400]}\n"
                )
                write_state(state_dir, "RALPH-BLOCKED.md", blocked_msg)
                log.error("BLOCKED: worker final response contains unparsed tool markers")
                console.print("[red][ael] BLOCKED: worker final response malformed[/red]")
                return 1, ""
            console.print(Panel(escape(content), title="[green]response[/green]", border_style="green"))
            # F13: only worker phase writes work-summary.txt; review phase preserves it
            if is_worker_phase:
                write_state(state_dir, "work-summary.txt", content)
            return 0, content

        # Dispatch tool calls and inject results
        for tc in tool_calls:
            console.print(f"[yellow]  call →[/yellow]  [bold]{escape(tc['name'])}[/bold][dim]({escape(json.dumps(tc['arguments']))})[/dim]")
            log.debug("tool call: %s args=%s", tc["name"], json.dumps(tc["arguments"]))

            # F4: Pre-dispatch write scope validation
            _scope_err = _validate_write_scope(tc["name"], tc["arguments"], project_root) if project_root else None
            # F21: Pre-dispatch audit-report.md append-only validation
            _report_err = _validate_audit_report_write(tc["name"], tc["arguments"], state_dir)
            if _scope_err:
                log.warning("scope violation: %s", _scope_err)
                console.print(f"[red][ael] scope violation: {escape(_scope_err[:200])}[/red]")
                result = f"Error: {_scope_err}"
            elif _report_err:
                log.warning("audit-report.md overwrite blocked: %s", _report_err)
                console.print(f"[red][ael] audit-report.md overwrite blocked[/red]")
                result = _report_err
            else:
                result = await mcp.call_tool(tc["name"], tc["arguments"])
            log.debug("tool result: %s", result)
            preview = result[:200] + ("..." if len(result) > 200 else "")
            console.print(f"[cyan]  result ←[/cyan]  [dim]{escape(preview)}[/dim]")
            # P3: duplicate read tracking
            if tc["name"] in ("read", "read_file", "read_text_file"):
                _path = tc["arguments"].get("path", "")
                if _path:
                    _read_counts[_path] = _read_counts.get(_path, 0) + 1
                    if _read_counts[_path] > 1:
                        log.warning("duplicate read (count=%d): %s",
                                    _read_counts[_path], _path)

            # Corrective guidance is embedded in the tool result content rather
            # than injected as a separate user message.  A standalone user message
            # after a tool message is rejected by the Mistral/oMLX API as an
            # invalid conversation structure, causing an unhandled exception.
            _corrective = ""
            _tool_result_appended = False

            # P1c: edit pattern-not-found — targeted file-read instruction
            _edit_pattern_failed = (
                tc["name"] in ("edit", "edit_file")
                and any(s in result for s in _EDIT_PATTERN_ERRORS)
            )
            if _edit_pattern_failed:
                _ep_path = tc["arguments"].get("path", "")
                log.warning("edit pattern mismatch tool=%s path=%s", tc["name"], _ep_path)
                console.print(
                    f"[yellow][ael] edit pattern mismatch: {escape(tc['name'])}: "
                    f"{escape(result[:200])}[/yellow]"
                )
                _ep_msg = (
                    f"\n\nThe edit failed because the old_text pattern was not found in "
                    f"{_ep_path or 'the target file'}. "
                    "Read the file first to get its exact current content, "
                    "then construct your edit pattern from what you observe."
                )
                if _ep_path and _ep_path.endswith(".py"):
                    _ep_proc = subprocess.run(
                        [sys.executable, "-m", "py_compile", _ep_path],
                        capture_output=True,
                        text=True,
                    )
                    if _ep_proc.returncode != 0:
                        _ep_msg += (
                            f"\n\nAdditional: syntax error detected:\n\n"
                            f"{_ep_proc.stderr.strip()}"
                        )
                _corrective = _ep_msg
            # P1a: MCP error handling (extended pattern match)
            elif _is_mcp_error(result):
                mcp_error_count += 1
                console.print(
                    f"[red][ael] MCP error "
                    f"({mcp_error_count}/{mcp_error_threshold}): "
                    f"{escape(tc['name'])}: {escape(result[:200])}[/red]"
                )
                log.warning(
                    "MCP error %d/%d tool=%s error=%s",
                    mcp_error_count, mcp_error_threshold, tc["name"], result,
                )
                _corrective = (
                    "\n\nThe previous tool call failed with a validation error. "
                    "Review the required parameters for the tool and reissue "
                    "the call with all required arguments correctly specified."
                )
                messages.append({"role": "tool", "content": result + _corrective,
                                  "tool_call_id": tc["id"]})
                _tool_result_appended = True
                if mcp_error_count >= mcp_error_threshold:
                    blocked_msg = (
                        f"# RALPH-BLOCKED\n\n"
                        f"MCP validation error threshold reached "
                        f"({mcp_error_count} consecutive errors).\n\n"
                        f"Last error:\n\n    {result}\n\n"
                        f"Tool: {tc['name']}\n"
                    )
                    write_state(state_dir, "RALPH-BLOCKED.md", blocked_msg)
                    log.error(
                        "BLOCKED: MCP error threshold %d reached", mcp_error_threshold
                    )
                    console.print(
                        f"[red][ael] BLOCKED: MCP error threshold "
                        f"({mcp_error_threshold}) reached[/red]"
                    )
                    return 1, ""
            else:
                mcp_error_count = 0
                # P4: post-write Python syntax check
                if tc["name"] in ("write", "edit", "write_file", "create_file"):
                    _py_path = tc["arguments"].get("path", "")
                    if _py_path and _py_path.endswith(".py"):
                        proc = subprocess.run(
                            [sys.executable, "-m", "py_compile", _py_path],
                            capture_output=True,
                            text=True,
                        )
                        if proc.returncode != 0:
                            err = proc.stderr.strip()
                            log.warning("syntax error in %s: %s", _py_path, err)
                            console.print(
                                f"[red][ael] syntax error: {escape(_py_path)}: "
                                f"{escape(err[:200])}[/red]"
                            )
                            _corrective = (
                                f"\n\nSyntax error detected in {_py_path}:\n\n"
                                f"{err}\n\n"
                                "Correct the file before continuing."
                            )

            # Append tool result with any corrective guidance embedded.
            # P1a appends directly (before threshold check); skip here for that path.
            if not _tool_result_appended:
                messages.append({"role": "tool", "content": result + _corrective,
                                  "tool_call_id": tc["id"]})

        # Check for work-complete signal written by the model via MCP
        if os.path.exists(os.path.join(state_dir, "work-complete.txt")):
            log.info("work-complete.txt detected — phase complete")
            console.print()
            console.print("[green][ael] work-complete detected[/green]")
            return 0, ""

    console.print(f"\n[red][ael] max iterations ({max_iterations}) reached[/red]")
    log.warning("max iterations %d reached", max_iterations)
    return 1, ""


def run_preflight_check(task: str, log: logging.Logger) -> str:
    """
    Evaluate deterministic success criteria from the task document before
    the first worker iteration.

    Attempts two extraction strategies:
      Pass 1: YAML block containing a 'success_criteria' list.
      Pass 2: plain list under a '## N.0 Success Criteria' section heading.

    For each criterion, deterministic checks are applied where possible:
      - File path + grep string:  run grep; mark satisfied/unsatisfied.
      - .py file + 'no syntax':   run py_compile; mark satisfied/unsatisfied.
      - Otherwise:                mark as 'unchecked'.

    Returns a [PRE-FLIGHT] summary string to prepend to the worker task,
    or an empty string if no criteria block is found.
    """
    criteria: list[str] = []

    # Pass 1: YAML block with success_criteria key
    blocks = re.findall(r"```yaml\n(.*?)```", task, re.DOTALL)
    for block in blocks:
        try:
            doc = yaml.safe_load(block)
            raw = (doc or {}).get("success_criteria")
            if isinstance(raw, list) and raw:
                criteria = [str(c).strip() for c in raw if str(c).strip()]
                log.debug("preflight: found %d criteria in YAML block", len(criteria))
                break
        except Exception:
            pass

    # Pass 2: plain list under ## N.0 Success Criteria heading
    if not criteria:
        section = re.search(
            r"##\s+[\d.]+\s+Success Criteria.*?\n(.*?)(?=\n##\s|\Z)",
            task, re.DOTALL | re.IGNORECASE,
        )
        if section:
            for line in section.group(1).splitlines():
                item = re.sub(r"^\s*[-*\d.]+\s*", "", line).strip()
                if item:
                    criteria.append(item)
            log.debug("preflight: found %d criteria in section heading", len(criteria))

    if not criteria:
        log.debug("preflight: no success_criteria found — skipping")
        return ""

    lines = []
    satisfied = 0
    unchecked = 0
    for i, criterion in enumerate(criteria, 1):
        # Grep check: criterion mentions a file path and a quoted string
        grep_match = re.search(
            r"([\w./\-]+\.\w+).*?(?:contains?|has)\s+[\'\"]([^\'\"]+)[\'\"]",
            criterion, re.IGNORECASE,
        )
        # py_compile check: criterion mentions a .py file and 'no syntax'
        syntax_match = re.search(
            r"([\w./\-]+\.py).*?no\s+syntax",
            criterion, re.IGNORECASE,
        )
        if syntax_match:
            path = syntax_match.group(1)
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "py_compile", path],
                    capture_output=True, text=True,
                )
                if proc.returncode == 0:
                    lines.append(f"  [{i}] SATISFIED  {criterion}")
                    satisfied += 1
                else:
                    lines.append(f"  [{i}] REMAINING  {criterion}")
                    lines.append(f"       syntax: {proc.stderr.strip()[:120]}")
            except Exception as exc:
                lines.append(f"  [{i}] UNCHECKED  {criterion} (error: {exc})")
                unchecked += 1
        elif grep_match:
            path, pattern = grep_match.group(1), grep_match.group(2)
            # F9: Guard grep availability before use
            if not shutil.which("grep"):
                lines.append(f"  [{i}] UNCHECKED  {criterion} (grep not available)")
                unchecked += 1
            else:
                try:
                    proc = subprocess.run(
                        ["grep", "-qF", pattern, path],
                        capture_output=True,
                    )
                    if proc.returncode == 0:
                        lines.append(f"  [{i}] SATISFIED  {criterion}")
                        satisfied += 1
                    else:
                        lines.append(f"  [{i}] REMAINING  {criterion}")
                except Exception as exc:
                    lines.append(f"  [{i}] UNCHECKED  {criterion} (error: {exc})")
                    unchecked += 1
        else:
            lines.append(f"  [{i}] UNCHECKED  {criterion}")
            unchecked += 1

    remaining = len(criteria) - satisfied - unchecked
    summary = (
        f"[PRE-FLIGHT]\n"
        f"Success criteria: {len(criteria)} total, "
        f"{satisfied} satisfied, {remaining} remaining, {unchecked} unchecked.\n"
        + "\n".join(lines)
        + "\n[END PRE-FLIGHT]"
    )
    log.info("preflight: %d criteria, %d satisfied, %d remaining, %d unchecked",
             len(criteria), satisfied, remaining, unchecked)
    console.print(
        f"[dim][ael] pre-flight: {len(criteria)} criteria — "
        f"{satisfied} satisfied, {remaining} remaining, {unchecked} unchecked[/dim]"
    )
    return summary


def _run_syntax_gate(state_dir: str, log: logging.Logger) -> str:
    """
    F6: Run py_compile on modified .py files and return a summary for the reviewer.

    Extracts .py file paths from work-summary.txt, runs py_compile on each,
    and returns a [SYNTAX GATE] block to inject into the reviewer task.
    Returns empty string if no .py files found or work-summary.txt absent.
    """
    summary_path = os.path.join(state_dir, "work-summary.txt")
    if not os.path.exists(summary_path):
        return ""

    summary_content = open(summary_path).read()

    # Extract .py file paths from the work summary
    # Match patterns like: path/to/file.py, "path/to/file.py", 'path/to/file.py'
    py_files = re.findall(r'["\']?([\w./\-]+\.py)["\']?', summary_content)
    # Deduplicate while preserving order
    seen = set()
    unique_py_files = []
    for f in py_files:
        if f not in seen and os.path.exists(f):
            seen.add(f)
            unique_py_files.append(f)

    if not unique_py_files:
        return ""

    results = []
    all_passed = True

    for py_path in unique_py_files:
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "py_compile", py_path],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                results.append(f"  ✓ {py_path}: OK")
            else:
                all_passed = False
                err = proc.stderr.strip()[:200]
                results.append(f"  ✗ {py_path}: SYNTAX ERROR\n    {err}")
        except Exception as exc:
            all_passed = False
            results.append(f"  ? {py_path}: check failed ({exc})")

    status = "PASS" if all_passed else "FAIL"
    log.info("syntax gate: %d files checked, status=%s", len(unique_py_files), status)

    gate_block = (
        f"[SYNTAX GATE: {status}]\n"
        f"The orchestrator ran py_compile on {len(unique_py_files)} .py file(s):\n"
        + "\n".join(results)
        + "\n[END SYNTAX GATE]\n"
    )

    if not all_passed:
        console.print(f"[yellow][ael] syntax gate: {status} ({len(unique_py_files)} files)[/yellow]")
    else:
        console.print(f"[dim][ael] syntax gate: {status} ({len(unique_py_files)} files)[/dim]")

    return gate_block


def _parse_audit_items(index_path: str) -> list[tuple[bool, str]]:
    """
    F17: Shared parser for audit-index.md items.

    Returns a list of (checked, item_text) tuples for all audit items.
    An item is any line matching "- [ ]" or "- [x]" (case-insensitive x).
    Returns empty list if file doesn't exist.
    """
    if not os.path.exists(index_path):
        return []

    items = []
    with open(index_path) as f:
        for line in f:
            stripped = line.strip()
            # Match "- [ ]" (unchecked) or "- [x]"/"- [X]" (checked)
            if stripped.startswith("- [ ]"):
                items.append((False, stripped))
            elif stripped.startswith("- [x]") or stripped.startswith("- [X]"):
                items.append((True, stripped))
    return items


def _snapshot_audit_index(state_dir: str, log: logging.Logger) -> int | None:
    """
    Count total items in audit-index.md at loop start.
    Returns the count as the scope snapshot, or None if the file is absent.
    Non-audit runs return None — all scope checks become no-ops.
    """
    index_path = os.path.join(state_dir, "audit-index.md")
    items = _parse_audit_items(index_path)
    if not items:
        return None
    count = len(items)
    log.info("audit scope snapshot: %d items", count)
    return count


def _check_audit_scope(
    state_dir: str, original_count: int | None, log: logging.Logger
) -> str | None:
    """
    Detect unauthorised modifications to audit-index.md item count.
    Compares current total against snapshot taken at loop start.
    Returns an error string if count changed, None if intact or non-audit run.
    """
    if original_count is None:
        return None
    index_path = os.path.join(state_dir, "audit-index.md")
    items = _parse_audit_items(index_path)
    if not items:
        return None
    current = len(items)
    if current == original_count:
        return None
    delta = current - original_count
    verb = "added" if delta > 0 else "removed"
    return (
        f"Scope violation: audit-index.md item count changed from {original_count} "
        f"to {current} ({abs(delta)} item(s) {verb}). "
        f"Do not add or remove items from audit-index.md. "
        f"Only change [ ] to [x]. Restore the original item list and continue."
    )


def _count_unchecked_audit_items(state_dir: str, log: logging.Logger) -> int:
    """
    Count unchecked [ ] items in audit-index.md.
    Returns 0 if the file is absent (non-audit runs unaffected).
    """
    index_path = os.path.join(state_dir, "audit-index.md")
    items = _parse_audit_items(index_path)
    count = sum(1 for checked, _ in items if not checked)
    log.debug("audit SHIP gate: %d unchecked items", count)
    return count


async def run_loop(
    client: AsyncOpenAI,
    mcp: MCPClient,
    worker_model: str,
    reviewer_model: str,
    work_recipe: dict,
    review_recipe: dict,
    task: str,
    max_iterations: int,
    phase_max_iterations: int,
    state_dir: str,
    log: logging.Logger,
    context_window: int | None = None,
    budget_warn_pct: float = 0.80,
    budget_abort_pct: float = 0.95,
    mcp_error_threshold: int = 3,
    max_tool_calls_per_iter: int = 10,
    preflight_check: bool = False,
    deadline: float | None = None,
    project_root: str = "",
    stall_threshold: int = _DEFAULT_STALL_THRESHOLD,
) -> int:
    """Full Ralph Loop: worker/reviewer cycle until SHIP, max_iterations, or deadline."""
    ctx_line = f"  context:  {context_window:,} tokens\n" if context_window else ""
    console.print(Panel(
        f"  worker:   {escape(worker_model)}\n"
        f"  reviewer: {escape(reviewer_model)}\n"
        f"{ctx_line}"
        f"  task:     {escape(task[:60])}{'...' if len(task) > 60 else ''}",
        title="[bold blue]Ralph Loop — AEL[/bold blue]",
        border_style="blue",
    ))
    log.info("loop start worker=%s reviewer=%s task=%s", worker_model, reviewer_model, task)

    clear_state(state_dir,
                "review-result.txt", "review-feedback.txt",
                "work-complete.txt", "work-summary.txt", ".ralph-complete", ".ralph-timeout")

    # Audit scope snapshot: record original item count for scope lock enforcement.
    _audit_original_count = _snapshot_audit_index(state_dir, log)

    # F12: Stall detection — track consecutive identical feedback
    _last_feedback_hash = ""
    _stall_count = 0

    # Pre-flight success criteria check (opt-in)
    if preflight_check:
        preflight_summary = run_preflight_check(task, log)
        if preflight_summary:
            task = preflight_summary + "\n\n" + task

    i = 0
    _extra = 0
    while True:
        i += 1
        # F10: Duration-limit exit returns distinct code and writes .ralph-timeout
        if deadline and time.monotonic() > deadline:
            console.print("[yellow][ael] duration limit reached — exiting[/yellow]")
            log.info("duration limit reached at loop iteration %d", i)
            write_state(state_dir, ".ralph-timeout", f"TIMEOUT: iteration {i}")
            return 2  # Distinct non-zero code for timeout
        if i > max_iterations + _extra:
            console.print(f"\n[red]✗ max iterations ({max_iterations + _extra}) reached without SHIP[/red]")
            log.warning("max iterations %d reached without SHIP", max_iterations + _extra)
            try:
                console.print(f"[yellow][ael] Continue for another {max_iterations} iteration(s)? [y/N]: [/yellow]", end="")
                answer = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = "n"
            if answer != "y":
                return 1
            _extra += max_iterations
            log.info("user elected to continue: %d total additional iterations", _extra)
            # F15: Do NOT continue here — fall through to run iteration i,
            # which is the first of the promised additional cycles.
        console.rule(f"[bold blue]loop iteration {i} / {max_iterations + _extra}[/bold blue]", style="blue")

        write_state(state_dir, "iteration.txt", str(i))
        log.info("loop iteration %d/%d", i, max_iterations + _extra)

        # Work phase
        console.print("\n[bold blue]▶ WORK PHASE[/bold blue]")
        rc, _ = await run_phase(client, mcp, worker_model, work_recipe,
                                task, phase_max_iterations, state_dir, log,
                                phase_label="WORKER",
                                context_window=context_window,
                                budget_warn_pct=budget_warn_pct,
                                budget_abort_pct=budget_abort_pct,
                                mcp_error_threshold=mcp_error_threshold,
                                max_tool_calls_per_iter=max_tool_calls_per_iter,
                                project_root=project_root)
        log.info("work phase rc=%d", rc)
        if rc != 0:
            console.print("[red]✗ WORK PHASE FAILED[/red]")
            return 1

        blocked = os.path.join(state_dir, "RALPH-BLOCKED.md")
        if os.path.exists(blocked):
            blocked_content = open(blocked).read()
            log.warning("BLOCKED:\n%s", blocked_content)
            console.print(Panel(escape(blocked_content), title="[red]✗ BLOCKED[/red]", border_style="red"))
            return 1

        # Audit scope lock: reject unauthorised modifications to audit-index.md.
        _scope_error = _check_audit_scope(state_dir, _audit_original_count, log)
        if _scope_error:
            log.warning("audit scope lock: %s", _scope_error)
            console.print(
                "[yellow][ael] audit scope lock: item count changed "
                "\u2014 injecting corrective feedback[/yellow]"
            )
            write_state(state_dir, "review-feedback.txt", _scope_error)
            clear_state(state_dir, "work-complete.txt", "review-result.txt")
            continue

        # Review phase — clear worker signal before reviewer starts
        clear_state(state_dir, "work-complete.txt")
        console.print("\n[bold blue]▶ REVIEW PHASE[/bold blue]")

        # F6: Run syntax gate and inject result into reviewer task
        _syntax_result = _run_syntax_gate(state_dir, log)

        # F16: Prepend [AEL RUNTIME CONTEXT] to review_task for consistent framing
        _review_header = (
            f"[AEL RUNTIME CONTEXT]\n"
            f"state_dir (full absolute path): {state_dir}\n"
            f"project_root (full absolute path): {project_root}\n"
            f"[END RUNTIME CONTEXT]\n\n"
        )
        review_task = _review_header + f"Review the work in state directory '{state_dir}'."
        if _syntax_result:
            review_task = _syntax_result + "\n" + review_task
        rc, reviewer_final_msg = await run_phase(client, mcp, reviewer_model, review_recipe,
                                                  review_task, phase_max_iterations, state_dir, log,
                                                  phase_label="REVIEWER",
                                                  context_window=context_window,
                                                  budget_warn_pct=budget_warn_pct,
                                                  budget_abort_pct=budget_abort_pct,
                                                  mcp_error_threshold=mcp_error_threshold,
                                                  max_tool_calls_per_iter=max_tool_calls_per_iter,
                                                  project_root=project_root)
        log.info("review phase rc=%d", rc)
        if rc != 0:
            console.print("[red]✗ REVIEW PHASE FAILED[/red]")
            return 1

        # F1/F2: Read review-result.txt (precedence), fallback to reviewer final message
        result_raw = read_state(state_dir, "review-result.txt")
        if result_raw:
            verdict = _normalize_verdict(result_raw)
            log.debug("verdict from review-result.txt: '%s' -> '%s'", result_raw.strip(), verdict)
        elif reviewer_final_msg:
            verdict = _normalize_verdict(reviewer_final_msg)
            log.debug("verdict from reviewer final message: '%s' -> '%s'",
                      reviewer_final_msg[:60].replace('\n', ' '), verdict)
        else:
            verdict = "REVISE"
            log.debug("no verdict source — defaulting to REVISE")

        # Persist fallback REVISE feedback body when reviewer_final_msg provided verdict.
        # Reviewer is read-only (F5) so cannot write review-feedback.txt itself.
        # Extract feedback = reviewer_final_msg minus the leading verdict token.
        if verdict == "REVISE" and not result_raw and reviewer_final_msg:
            existing_feedback = read_state(state_dir, "review-feedback.txt")
            if not existing_feedback:
                # Strip leading verdict token: first whitespace-delimited token
                tokens = reviewer_final_msg.strip().split(None, 1)
                feedback_body = tokens[1].strip() if len(tokens) > 1 else ""
                if feedback_body:
                    write_state(state_dir, "review-feedback.txt", feedback_body)
                    log.debug("persisted fallback REVISE feedback (%d chars)", len(feedback_body))

        if verdict == "SHIP":
            # Audit SHIP gate: check scope integrity then coverage before accepting SHIP.
            _gate_scope_err = _check_audit_scope(state_dir, _audit_original_count, log)
            if _gate_scope_err:
                log.warning("audit SHIP gate: scope violation — %s", _gate_scope_err)
                console.print(
                    "[yellow][ael] audit SHIP gate: scope violation "
                    "— overriding SHIP to REVISE[/yellow]"
                )
                write_state(state_dir, "review-feedback.txt", _gate_scope_err)
            else:
                _unchecked = _count_unchecked_audit_items(state_dir, log)
                if _unchecked > 0:
                    log.warning(
                        "audit SHIP gate: reviewer issued SHIP with %d unchecked item(s) — overriding",
                        _unchecked,
                    )
                    console.print(
                        f"[yellow][ael] audit SHIP gate: {_unchecked} unchecked item(s) remain "
                        f"— overriding SHIP to REVISE[/yellow]"
                    )
                    write_state(
                        state_dir, "review-feedback.txt",
                        f"Coverage incomplete: {_unchecked} item(s) in audit-index.md remain unchecked.\n"
                        f"Do not issue SHIP until every item is marked [x].\n"
                        f"Proceed to audit the next unchecked item."
                    )
                else:
                    console.print(Panel(
                        f"[bold]✓ SHIPPED[/bold] after {i} loop iteration(s)",
                        border_style="green",
                    ))
                    log.info("SHIPPED iteration=%d", i)
                    write_state(state_dir, ".ralph-complete", f"COMPLETE: iteration {i}")
                    return 0

        feedback = read_state(state_dir, "review-feedback.txt")
        if feedback:
            log.debug("review feedback:\n%s", feedback)
            console.print(Panel(escape(feedback), title="[yellow]↻ REVISE[/yellow]", border_style="yellow"))
        else:
            console.print("[yellow]↻ REVISE[/yellow]")

        # F12: Stall detection — check for consecutive identical feedback
        _current_hash = _hash_feedback(feedback)
        if _current_hash and _current_hash == _last_feedback_hash:
            _stall_count += 1
            log.debug("stall detection: identical feedback (count=%d/%d)", _stall_count, stall_threshold)
            if _stall_count >= stall_threshold:
                blocked_msg = (
                    "# RALPH-BLOCKED\n\n"
                    f"Stall detected: identical REVISE feedback for {stall_threshold} consecutive cycles.\n\n"
                    "The loop is making no progress. Intervention required.\n\n"
                    f"Last feedback:\n\n{feedback[:500]}\n"
                )
                write_state(state_dir, "RALPH-BLOCKED.md", blocked_msg)
                log.error("BLOCKED: stall detected — %d consecutive identical feedbacks", stall_threshold)
                console.print(
                    f"[red][ael] BLOCKED: stall detected — {stall_threshold} consecutive identical feedbacks[/red]"
                )
                return 1
        else:
            _stall_count = 0
            _last_feedback_hash = _current_hash

        clear_state(state_dir, "work-complete.txt", "review-result.txt")


async def main_async(args: argparse.Namespace) -> int:
    config    = load_yaml(args.config)
    state_dir = os.path.abspath(config["loop"]["state_dir"])

    # Reset mode — no model or MCP connection required
    if args.mode == "reset":
        return reset_state(state_dir)

    # Warn if a prior SHIP is present and not yet cleared
    if os.path.exists(os.path.join(state_dir, ".ralph-complete")):
        console.print(f"[yellow][ael] warning: prior SHIP detected in {state_dir}[/yellow]")
        console.print("[yellow][ael]          run --mode reset after human acceptance to clear[/yellow]")

    omlx_cfg       = config["omlx"]
    max_iter          = args.max_iterations or config["loop"]["max_iterations"]
    deadline          = time.monotonic() + args.duration * 3600 if args.duration else None
    phase_max_iter    = config["loop"].get("phase_max_iterations", max_iter)
    mcp_error_thresh      = config["loop"].get("mcp_error_threshold", 3)
    max_tool_calls        = config["loop"].get("max_tool_calls_per_iteration", 10)
    do_preflight          = config["loop"].get("preflight_check", False)
    model          = args.model or omlx_cfg["default_model"]

    # Resolve context budget config
    ctx_cfg        = config.get("context", {})
    models_dir     = ctx_cfg.get("models_dir", "")
    budget_warn    = ctx_cfg.get("budget_warn_pct", 0.80)
    budget_abort   = ctx_cfg.get("budget_abort_pct", 0.95)

    log = setup_logging(state_dir)
    log.info("AEL start mode=%s model=%s state_dir=%s", args.mode, model, state_dir)

    recipe_dir  = os.path.join(os.path.dirname(__file__), "..", "recipes")
    # Recipe selection: audit-index.md in the state directory selects the audit
    # recipe pair; otherwise the standard Ralph Loop pair. Same signal the audit
    # scope/SHIP/archive logic keys on — mode detection is single-sourced.
    if os.path.exists(os.path.join(state_dir, "audit-index.md")):
        recipe_set = "audit"
        work_recipe = load_yaml(os.path.join(recipe_dir, "audit-work.yaml"))
        rev_recipe  = load_yaml(os.path.join(recipe_dir, "audit-review.yaml"))
    else:
        recipe_set = "ralph"
        work_recipe = load_yaml(os.path.join(recipe_dir, "ralph-work.yaml"))
        rev_recipe  = load_yaml(os.path.join(recipe_dir, "ralph-review.yaml"))
    console.print(f"[blue][ael] recipe set: {recipe_set}[/blue]")
    log.info("recipe set: %s", recipe_set)

    client = AsyncOpenAI(base_url=omlx_cfg["base_url"], api_key=omlx_cfg["api_key"])

    readiness = config.get("readiness", {})
    await await_model_ready(
        client,
        model,
        timeout=readiness.get("timeout_seconds", 60.0),
        interval=readiness.get("poll_interval_seconds", 2.0),
    )

    # Resolve context window
    # F18: Support per-model context window overrides from config
    _model_ctx_overrides = ctx_cfg.get("model_context_windows", {})
    context_window = resolve_context_window(
        model, models_dir, ctx_cfg.get("context_window"), log,
        model_overrides=_model_ctx_overrides
    )
    if context_window:
        console.print(f"[blue][ael] context window: {context_window:,} tokens ({escape(model)})[/blue]")
    else:
        console.print("[yellow][ael] context window: unknown — budget tracking disabled[/yellow]")

    mcp = MCPClient(config.get("mcp_servers", {}))
    await mcp.connect()

    # Resolve task
    if args.task and os.path.exists(args.task):
        raw = open(args.task).read()
        brief = extract_tactical_brief(raw, log)
        task = brief if brief and not brief.startswith("#") else raw
    else:
        task = args.task or read_state(state_dir, "task.md")

    if not task:
        console.print(f"[red][ael] error: no task provided (--task or {state_dir}/task.md)[/red]")
        await mcp.close()
        return 1

    # Resolve placeholders and prepend runtime context
    project_root = os.getcwd()
    task = task.replace("{STATE_DIR}", state_dir).replace("{PROJECT_ROOT}", project_root)
    runtime_header = (
        f"[AEL RUNTIME CONTEXT]\n"
        f"state_dir (full absolute path): {state_dir}\n"
        f"project_root (full absolute path): {project_root}\n"
        f"Do not use 'state_dir' or 'project_root' as literal path components.\n"
        f"[END RUNTIME CONTEXT]\n\n"
    )
    task = runtime_header + task

    os.makedirs(state_dir, exist_ok=True)
    write_state(state_dir, "task.md", task)

    # Write context budget report for Strategic Domain
    # F8: Include actual system prompt and tool schema in the initial estimate
    _sys_prompt = work_recipe.get("instructions", "")
    _tools = mcp.get_openai_tools()
    initial_tokens = estimate_tokens([
        {"role": "system", "content": _sys_prompt},
        {"role": "user",   "content": task},
    ], tools=_tools)
    write_context_report(
        state_dir, model, context_window,
        initial_tokens, budget_warn, budget_abort
    )
    if context_window:
        pct = (initial_tokens / context_window) * 100
        console.print(f"[blue][ael] initial task: ~{initial_tokens:,} tokens ({pct:.1f}% of window)[/blue]")
        console.print(f"[dim][ael] context report: {state_dir}/context-budget.md[/dim]")

    rc = 1  # default: failure — ensures rc is defined even on unexpected exception
    try:
        if args.mode == "worker":
            # F11: Clear stale phase signals to prevent false completion on iteration 1
            _stale = os.path.join(state_dir, "work-complete.txt")
            if os.path.exists(_stale):
                log.warning("clearing stale work-complete.txt from prior run")
                console.print("[yellow][ael] clearing stale work-complete.txt from prior run[/yellow]")
                os.remove(_stale)
            rc, _ = await run_phase(client, mcp, model, work_recipe, task, phase_max_iter,
                                    state_dir, log, phase_label="WORKER",
                                    context_window=context_window,
                                    budget_warn_pct=budget_warn,
                                    budget_abort_pct=budget_abort,
                                    mcp_error_threshold=mcp_error_thresh,
                                    max_tool_calls_per_iter=max_tool_calls,
                                    project_root=project_root)
        elif args.mode == "reviewer":
            # F11: Clear stale phase signals for single-phase reviewer mode
            _stale = os.path.join(state_dir, "work-complete.txt")
            if os.path.exists(_stale):
                log.warning("clearing stale work-complete.txt from prior run")
                console.print("[yellow][ael] clearing stale work-complete.txt from prior run[/yellow]")
                os.remove(_stale)
            # F16: Use consistent review task with runtime context (not the worker task)
            _review_task = (
                f"[AEL RUNTIME CONTEXT]\n"
                f"state_dir (full absolute path): {state_dir}\n"
                f"project_root (full absolute path): {project_root}\n"
                f"[END RUNTIME CONTEXT]\n\n"
                f"Review the work in state directory '{state_dir}'."
            )
            rc, _ = await run_phase(client, mcp, model, rev_recipe, _review_task, phase_max_iter,
                                    state_dir, log, phase_label="REVIEWER",
                                    context_window=context_window,
                                    budget_warn_pct=budget_warn,
                                    budget_abort_pct=budget_abort,
                                    mcp_error_threshold=mcp_error_thresh,
                                    max_tool_calls_per_iter=max_tool_calls,
                                    project_root=project_root)
        else:  # loop
            worker_model   = args.worker_model   or model
            reviewer_model = args.reviewer_model or model
            rc = await run_loop(client, mcp, worker_model, reviewer_model,
                                work_recipe, rev_recipe, task, max_iter, phase_max_iter,
                                state_dir, log,
                                context_window=context_window,
                                budget_warn_pct=budget_warn,
                                budget_abort_pct=budget_abort,
                                mcp_error_threshold=mcp_error_thresh,
                                max_tool_calls_per_iter=max_tool_calls,
                                preflight_check=do_preflight,
                                deadline=deadline,
                                project_root=project_root)
            if rc == 0:
                _archive_audit_artifacts(state_dir, args.task, log)
    finally:
        log.info("AEL end rc=%d", rc)
        await mcp.close()

    return rc


def main() -> None:
    default_config = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    p = argparse.ArgumentParser(description="AEL Orchestrator — Ralph Loop")
    p.add_argument("--config",          default=default_config,
                   help="Path to config.yaml")
    p.add_argument("--mode",            choices=["worker", "reviewer", "loop", "reset"],
                   default="loop",      help="Execution mode (default: loop)")
    p.add_argument("--task",            help="Task string or path to task file")
    p.add_argument("--model",           help="Model for all phases (overrides config default)")
    p.add_argument("--worker-model",    help="Model for work phase (loop mode only)")
    p.add_argument("--reviewer-model",  help="Model for review phase (loop mode only)")
    p.add_argument("--max-iterations",  type=int,
                   help="Iteration limit override")
    p.add_argument("--duration",          type=float, default=None,
                   help="Wall-clock time limit in hours (default: no limit)")
    args = p.parse_args()
    rc = asyncio.run(main_async(args))
    # os._exit bypasses asyncio teardown, preventing MCP stdio subprocess hang
    for h in logging.getLogger("ael").handlers:
        h.flush()
    os._exit(rc)


if __name__ == "__main__":
    main()
