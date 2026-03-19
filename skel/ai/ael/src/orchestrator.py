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

Usage:
    python orchestrator.py --mode worker   --task workspace/prompt/prompt-abc123.md
    python orchestrator.py --mode reviewer --task workspace/prompt/prompt-abc123.md
    python orchestrator.py --mode loop     --task workspace/prompt/prompt-abc123.md
    python orchestrator.py --mode loop     --task "implement the login module"
"""

import argparse
import asyncio
import datetime
import json
import logging
import os
import sys
import uuid

import yaml
from openai import AsyncOpenAI

sys.path.insert(0, os.path.dirname(__file__))
from mcp_client import MCPClient
from parser import parse_tool_calls

# ANSI colours
RED    = "\033[0;31m"
GREEN  = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE   = "\033[0;34m"
NC     = "\033[0m"


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
    if not logger.handlers:
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(fh)
    return logger


async def run_phase(
    client: AsyncOpenAI,
    mcp: MCPClient,
    model: str,
    recipe: dict,
    task: str,
    max_iterations: int,
    state_dir: str,
    log: logging.Logger,
) -> int:
    """
    Single phase (worker or reviewer): inject tools, send completions,
    dispatch tool calls, loop until no tool calls remain.
    Returns 0 on success, 1 on failure.
    """
    tools = mcp.get_openai_tools()
    system_prompt = recipe.get("instructions", "")
    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": task},
    ]

    print(f"{BLUE}[ael] model:  {model}{NC}")
    print(f"{BLUE}[ael] tools:  {len(tools)}{NC}")
    print(f"{BLUE}[ael] task:   {task[:80]}{'...' if len(task) > 80 else ''}{NC}")
    log.info("phase start model=%s tools=%d task=%s", model, len(tools), task)

    for iteration in range(1, max_iterations + 1):
        print(f"\n{BLUE}[ael] ── iteration {iteration}/{max_iterations} ──{NC}")
        log.debug("iteration %d/%d", iteration, max_iterations)

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools or None,
            stream=False,
        )

        message = response.choices[0].message
        content = message.content or ""
        log.debug("iteration %d model response:\n%s", iteration, content)
        tool_calls: list[dict] = []

        if message.tool_calls:
            for tc in message.tool_calls:
                try:
                    arguments = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                tool_calls.append({"id": tc.id, "name": tc.function.name, "arguments": arguments})
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
            parsed = parse_tool_calls(content)
            if parsed:
                for tc in parsed:
                    tc["id"] = f"call_{uuid.uuid4().hex[:8]}"
                tool_calls = parsed
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
                messages.append({"role": "assistant", "content": content})

        if not tool_calls:
            print(f"\n{GREEN}[ael] response:{NC}\n{content}")
            write_state(state_dir, "work-summary.txt", content)
            return 0

        for tc in tool_calls:
            print(f"{YELLOW}[ael] → {tc['name']}({json.dumps(tc['arguments'])}){NC}")
            log.debug("tool call: %s args=%s", tc["name"], json.dumps(tc["arguments"]))
            result = await mcp.call_tool(tc["name"], tc["arguments"])
            log.debug("tool result: %s", result)
            preview = result[:200] + ("..." if len(result) > 200 else "")
            print(f"[ael] ← {preview}")
            messages.append({"role": "tool", "content": result, "tool_call_id": tc["id"]})

        # Check for work-complete signal written by the model via MCP
        if os.path.exists(os.path.join(state_dir, "work-complete.txt")):
            log.info("work-complete.txt detected — phase complete")
            print(f"\n{GREEN}[ael] work-complete detected{NC}")
            return 0

    print(f"\n{RED}[ael] max iterations ({max_iterations}) reached{NC}")
    log.warning("max iterations %d reached", max_iterations)
    return 1


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
) -> int:
    """Full Ralph Loop: worker/reviewer cycle until SHIP or max_iterations."""
    print(f"{BLUE}{'═' * 63}{NC}")
    print(f"{BLUE}  Ralph Loop — AEL{NC}")
    print(f"{BLUE}{'═' * 63}{NC}")
    print(f"  worker:   {worker_model}")
    print(f"  reviewer: {reviewer_model}")
    print(f"  task:     {task[:60]}{'...' if len(task) > 60 else ''}\n")
    log.info("loop start worker=%s reviewer=%s task=%s", worker_model, reviewer_model, task)

    clear_state(state_dir,
                "review-result.txt", "review-feedback.txt",
                "work-complete.txt", "work-summary.txt", ".ralph-complete")

    i = 0
    _extra = 0
    while True:
        i += 1
        if i > max_iterations + _extra:
            print(f"\n{RED}✗ max iterations ({max_iterations + _extra}) reached without SHIP{NC}")
            log.warning("max iterations %d reached without SHIP", max_iterations + _extra)
            try:
                print(f"{YELLOW}[ael] Continue for another {max_iterations} iteration(s)? [y/N]: {NC}", end="", flush=True)
                answer = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = "n"
            if answer != "y":
                return 1
            _extra += max_iterations
            log.info("user elected to continue: %d total additional iterations", _extra)
            continue
        print(f"{BLUE}{'─' * 63}{NC}")
        print(f"{BLUE}  iteration {i} / {max_iterations + _extra}{NC}")
        print(f"{BLUE}{'─' * 63}{NC}")

        write_state(state_dir, "iteration.txt", str(i))
        log.info("loop iteration %d/%d", i, max_iterations + _extra)

        print(f"\n{YELLOW}▶ WORK PHASE{NC}")
        rc = await run_phase(client, mcp, worker_model, work_recipe,
                             task, phase_max_iterations, state_dir, log)
        log.info("work phase rc=%d", rc)
        if rc != 0:
            print(f"{RED}✗ WORK PHASE FAILED{NC}")
            return 1

        blocked = os.path.join(state_dir, "RALPH-BLOCKED.md")
        if os.path.exists(blocked):
            blocked_content = open(blocked).read()
            log.warning("BLOCKED:\n%s", blocked_content)
            print(f"\n{RED}✗ BLOCKED{NC}")
            print(blocked_content)
            return 1

        print(f"\n{YELLOW}▶ REVIEW PHASE{NC}")
        review_task = (
            f"Review the work in state directory '{state_dir}'. "
            f"Original task: {task}"
        )
        rc = await run_phase(client, mcp, reviewer_model, review_recipe,
                             review_task, phase_max_iterations, state_dir, log)
        log.info("review phase rc=%d", rc)
        if rc != 0:
            print(f"{RED}✗ REVIEW PHASE FAILED{NC}")
            return 1

        result = read_state(state_dir, "review-result.txt")
        if result == "SHIP":
            print(f"\n{GREEN}{'═' * 63}{NC}")
            print(f"{GREEN}  ✓ SHIPPED after {i} iteration(s){NC}")
            print(f"{GREEN}{'═' * 63}{NC}")
            log.info("SHIPPED iteration=%d", i)
            write_state(state_dir, ".ralph-complete", f"COMPLETE: iteration {i}")
            return 0

        print(f"\n{YELLOW}↻ REVISE — feedback for next iteration:{NC}")
        feedback = read_state(state_dir, "review-feedback.txt")
        if feedback:
            log.debug("review feedback:\n%s", feedback)
            print(feedback)

        clear_state(state_dir, "work-complete.txt", "review-result.txt")


async def main_async(args: argparse.Namespace) -> int:
    config   = load_yaml(args.config)
    omlx_cfg = config["omlx"]
    state_dir        = config["loop"]["state_dir"]
    max_iter         = args.max_iterations or config["loop"]["max_iterations"]
    phase_max_iter   = config["loop"].get("phase_max_iterations", max_iter)
    model            = args.model or omlx_cfg["default_model"]

    log = setup_logging(state_dir)
    log.info("AEL start mode=%s model=%s", args.mode, model)

    recipe_dir  = os.path.join(os.path.dirname(__file__), "..", "recipes")
    work_recipe = load_yaml(os.path.join(recipe_dir, "ralph-work.yaml"))
    rev_recipe  = load_yaml(os.path.join(recipe_dir, "ralph-review.yaml"))

    client = AsyncOpenAI(base_url=omlx_cfg["base_url"], api_key=omlx_cfg["api_key"])
    mcp    = MCPClient(config.get("mcp_servers", {}))
    await mcp.connect()

    if args.task and os.path.exists(args.task):
        raw = open(args.task).read()
        # Extract tactical_brief from T04 YAML if present
        try:
            import re as _re
            _m = _re.search(r"```yaml\n(.*?)```", raw, _re.DOTALL)
            if _m:
                _doc = yaml.safe_load(_m.group(1))
                _brief = (_doc or {}).get("tactical_brief", "").strip()
            else:
                _brief = ""
        except Exception:
            _brief = ""
        task = _brief if _brief and not _brief.startswith("#") else raw
    else:
        task = args.task or read_state(state_dir, "task.md")

    if not task:
        print(f"{RED}[ael] error: no task provided (--task or {state_dir}/task.md){NC}")
        await mcp.close()
        return 1

    os.makedirs(state_dir, exist_ok=True)
    write_state(state_dir, "task.md", task)

    try:
        if args.mode == "worker":
            rc = await run_phase(client, mcp, model, work_recipe, task, phase_max_iter, state_dir, log)
        elif args.mode == "reviewer":
            rc = await run_phase(client, mcp, model, rev_recipe, task, phase_max_iter, state_dir, log)
        else:
            worker_model   = args.worker_model   or model
            reviewer_model = args.reviewer_model or model
            rc = await run_loop(client, mcp, worker_model, reviewer_model,
                                work_recipe, rev_recipe, task, max_iter, phase_max_iter, state_dir, log)
    finally:
        await mcp.close()

    return rc


def main() -> None:
    default_config = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    p = argparse.ArgumentParser(description="AEL Orchestrator — Ralph Loop")
    p.add_argument("--config",         default=default_config, help="Path to config.yaml")
    p.add_argument("--mode",           choices=["worker", "reviewer", "loop"],
                   default="loop",     help="Execution mode (default: loop)")
    p.add_argument("--task",           help="Task string or path to task file")
    p.add_argument("--model",          help="Model for all phases (overrides config default)")
    p.add_argument("--worker-model",   help="Model for work phase (loop mode only)")
    p.add_argument("--reviewer-model", help="Model for review phase (loop mode only)")
    p.add_argument("--max-iterations", type=int, help="Iteration limit override")
    args = p.parse_args()
    sys.exit(asyncio.run(main_async(args)))


if __name__ == "__main__":
    main()
