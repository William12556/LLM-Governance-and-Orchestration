Created: 2026 June 27

```yaml
prompt_info:
  id: "prompt-a3f1c7d9"
  task_type: "refactor"
  source_ref: "change-a3f1c7d9"
  date: "2026-06-27"
  iteration: 1
  coupled_docs:
    change_ref: "change-a3f1c7d9"
    change_iteration: 1

context:
  purpose: >
    Eliminate the anyio cancel-scope RuntimeError at MCP teardown by owning all
    stdio_client and ClientSession contexts in a single AsyncExitStack entered
    and exited within the same task (issue-a3f1c7d9 Option B).
  integration: >
    ai/ael/src/mcp_client.py — MCPClient.__init__, connect, close.
  constraints:
    - "connect() and close() are awaited in the same task (main_async) — preserve this"
    - "Retain per-server try/except so one failed server does not abort the rest"
    - "Do not change get_openai_tools, call_tool, or the tool catalogue"
    - "Do not modify orchestrator main() os._exit/log flush (out of scope)"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Refactor MCPClient connection lifecycle to use one instance-owned
    AsyncExitStack; remove the ctx.__aexit__ skip workaround.
  requirements:
    functional:
      - "Add `from contextlib import AsyncExitStack`"
      - "Create an AsyncExitStack on the MCPClient instance (in __init__ or connect)"
      - "In connect(), enter each stdio_client context and each ClientSession context via stack.enter_async_context(); keep session.initialize() and tool-catalogue building"
      - "Retain the per-server try/except; only successfully entered contexts are pushed onto the stack"
      - "In close(), tear down via stack.aclose() in the same task; remove the manual session.__aexit__ loop, the _contexts list, and the ctx.__aexit__ skip-workaround comment"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Comprehensive error handling"
        - "Preserve existing print/log output conventions"

design:
  architecture: "Single instance-owned AsyncExitStack entered in connect, aclosed in close, same task"
  components:
    - name: "MCPClient.__init__"
      type: "method"
      purpose: "Hold the AsyncExitStack and session/tool state"
      logic:
        - "Initialise self._stack (AsyncExitStack) or create it in connect()"
        - "Retain self._sessions and self._tools"
    - name: "MCPClient.connect"
      type: "method"
      purpose: "Enter all contexts via the stack"
      logic:
        - "For each server: read, write = await stack.enter_async_context(stdio_client(params))"
        - "session = await stack.enter_async_context(ClientSession(read, write))"
        - "await session.initialize(); store session; build tool catalogue"
        - "Keep per-server try/except with the existing warning on failure"
    - name: "MCPClient.close"
      type: "method"
      purpose: "Tear down all contexts cleanly in the same task"
      logic:
        - "await self._stack.aclose() if the stack exists"
        - "Clear sessions; remove the _contexts list and skip-workaround comment"
        - "Document that connect/close must run in the same task"
  dependencies:
    internal: []
    external:
      - "contextlib.AsyncExitStack (stdlib)"

deliverable:
  format_requirements:
    - "Edit ai/ael/src/mcp_client.py in place"
  files:
    - path: "ai/ael/src/mcp_client.py"
      content: "Refactor connect/close to AsyncExitStack per design"

success_criteria:
  - "mcp_client.py imports AsyncExitStack and the MCPClient owns a single stack"
  - "connect() enters all stdio_client and ClientSession contexts via the stack"
  - "close() tears down via stack.aclose(); the ctx.__aexit__ skip workaround and _contexts list are removed"
  - "Per-server try/except is retained"
  - "Running --mode worker and --mode loop to completion produces no anyio cancel-scope tracebacks; exit code remains 0"
  - "No orphaned MCP stdio subprocesses remain after exit"
  - "ai/ael/src/mcp_client.py has no syntax errors"

tactical_brief: |
  File: ai/ael/src/mcp_client.py (MCPClient __init__, connect, close). Read before editing.
  Option B: own all stdio_client and ClientSession contexts in one instance AsyncExitStack.
  - import AsyncExitStack from contextlib; create the stack on the instance.
  - connect(): enter each stdio_client and ClientSession via stack.enter_async_context(); keep session.initialize(), tool-catalogue build, and per-server try/except.
  - close(): await stack.aclose(); remove the manual session.__aexit__ loop, the _contexts list, and the ctx.__aexit__ skip-workaround comment.
  Constraints: connect and close run in the same task; do not touch get_openai_tools/call_tool or orchestrator os._exit; verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Claude Code consumes this full document; the
  tactical_brief is retained for schema/govwatch compliance. Forward path: the
  issue remains open until this is implemented and verified. No AEL/oMLX
  context-budget gate applies.
```
