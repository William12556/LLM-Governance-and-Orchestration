Created: 2026 July 08

```yaml
prompt_info:
  id: "prompt-d42e64a9"
  task_type: "refactor"
  source_ref: "change-d42e64a9"
  target_profile: "ael"
  date: "2026-07-08"
  iteration: 1
  coupled_docs:
    change_ref: "change-d42e64a9"
    change_iteration: 1

context:
  purpose: >
    Consolidate context-window resolution into a single tiered resolver
    in orchestrator.py, remove the filesystem-glob dependency on
    context.models_dir, and make MCP server spawn arguments in
    config.yaml portable across installations.
  integration: >
    orchestrator.py is the AEL Ralph Loop entry point. Its
    resolve_context_window() function is called at startup to size the
    context budget bar and write context-budget.md. config.yaml is read
    once at startup via load_yaml() and passed to MCPClient for
    stdio server spawning.
  knowledge_references: []
  constraints:
    - "No new third-party dependency — use urllib.request (stdlib) for the oMLX admin query, not httpx or requests"
    - "Do not modify ai/src/govwatch.py — explicitly out of scope, paused"
    - "Do not modify ai/ael/src/budget.py — retired separately by the Strategic Domain (git mv), not part of this deliverable"
    - "Preserve existing behavior for context.model_context_windows: North-Mini-Code-1.0-6bit must continue to resolve to 262144 when the live query returns null"
    - "context.models_dir must be removed from config.yaml; no code path may reference it"
    - "PROJECT_ROOT must be derived from os.getcwd(), consistent with the existing _archive_audit_artifacts() precedent already in this file — do not introduce a different project-root convention"

specification:
  description: >
    Replace resolve_context_window() with a four-tier resolution chain
    and add a live oMLX query helper. Add a module-level PROJECT_ROOT
    constant and a config-loading step that substitutes the literal
    string "{PROJECT_ROOT}" wherever it appears in mcp_servers server
    definitions (command and args) before the config dict is passed to
    MCPClient. Update config.yaml to remove context.models_dir and
    replace committed absolute paths with the "{PROJECT_ROOT}"
    placeholder where they denote the project root.
  requirements:
    functional:
      - "resolve_context_window(model_name, config) tries, in order: (1) config['context']['context_window'] if not null, (2) a live query to the oMLX admin endpoint for settings.max_context_window keyed by model_name, if not null, (3) config['context']['model_context_windows'][model_name] if present, (4) return None"
      - "The live-query helper builds the admin URL by taking config['omlx']['base_url'], stripping a trailing '/v1', and appending '/admin/api/models?model_id=<model_name>' (URL-encode model_name)"
      - "The live-query helper catches all network/timeout/JSON-decode errors and returns None on any failure, logging at WARNING with the exception message — it must never raise"
      - "A config-loading step walks config['mcp_servers'], and for every server's 'command' string and each string in its 'args' list, replaces the literal substring '{PROJECT_ROOT}' with PROJECT_ROOT (os.getcwd()) before the config is passed to MCPClient(...)"
      - "context.models_dir and any glob-based config.json search are removed entirely from orchestrator.py"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Thread-safe if concurrent access"
        - "Comprehensive error handling"
        - "Debug logging with traceback"
        - "Professional docstrings"
  performance: []

design:
  architecture: "Single resolver function, tiered fallback, no new module"
  components:
    - name: "resolve_context_window"
      type: "function"
      purpose: "Return the context window size in tokens for the configured model, trying explicit override, live oMLX query, per-model config override, then unknown, in that order"
      interface:
        inputs:
          - name: "model_name"
            type: "str"
            description: "The model id as configured in omlx.default_model"
          - name: "config"
            type: "dict"
            description: "The parsed config.yaml contents"
        outputs:
          type: "int | None"
          description: "Context window size in tokens, or None if unresolved at every tier"
        raises: []
      logic:
        - "Read config['context']['context_window']; if not None, return it (tier 1)"
        - "Call the live-query helper with model_name and config['omlx']['base_url']; if it returns a non-null int, return it (tier 2)"
        - "Read config['context']['model_context_windows'].get(model_name); if present, return it (tier 3)"
        - "Log a warning identifying which tiers were tried and return None (tier 4)"
    - name: "_query_omlx_context_window"
      type: "function"
      purpose: "Perform a single GET against the oMLX admin API and extract settings.max_context_window for one model id"
      interface:
        inputs:
          - name: "model_name"
            type: "str"
            description: "Model id to query"
          - name: "base_url"
            type: "str"
            description: "config['omlx']['base_url'], e.g. http://127.0.0.1:8000/v1"
        outputs:
          type: "int | None"
          description: "The value of settings.max_context_window for the matching model entry, or None"
        raises: []
      logic:
        - "Strip a trailing '/v1' from base_url to get the admin root"
        - "GET {admin_root}/admin/api/models?model_id={model_name} (URL-encoded) with a short timeout (e.g. 5-10s)"
        - "Parse the JSON response's 'models' array; find the entry whose 'id' matches model_name"
        - "Return entry['settings']['max_context_window'] if present and not null, else None"
        - "On any exception (connection error, timeout, malformed JSON, missing keys), log at WARNING and return None"
    - name: "PROJECT_ROOT substitution"
      type: "module-level step"
      purpose: "Make config.yaml MCP server definitions portable across installations"
      interface:
        inputs:
          - name: "config['mcp_servers']"
            type: "dict"
            description: "Server name to {command, args, env} mapping"
        outputs:
          type: "dict"
          description: "Same structure with '{PROJECT_ROOT}' substrings replaced"
        raises: []
      logic:
        - "PROJECT_ROOT = os.getcwd(), computed once at module load or at the point config is loaded"
        - "For each server dict, replace '{PROJECT_ROOT}' in 'command' and in each element of 'args' with PROJECT_ROOT"
        - "Leave 'env' values untouched unless they also contain the placeholder"
  dependencies:
    internal:
      - "config.yaml context and mcp_servers sections"
    external:
      - "urllib.request and urllib.parse (stdlib only — no new third-party dependency)"

data_schema:
  entities:
    - name: "config.yaml context section"
      attributes:
        - name: "context_window"
          type: "int | null"
          constraints: "Explicit global override; unchanged field"
        - name: "model_context_windows"
          type: "dict[str, int]"
          constraints: "Per-model override; unchanged field"
        - name: "models_dir"
          type: "removed"
          constraints: "Delete this key and its value entirely"
      validation:
        - "config.yaml remains valid YAML after edit"
    - name: "config.yaml mcp_servers section"
      attributes:
        - name: "command / args"
          type: "str"
          constraints: "May contain the literal placeholder '{PROJECT_ROOT}' in place of any absolute path denoting the repository root"
      validation:
        - "No literal absolute path (e.g. /Users/...) remains in mcp_servers after edit, other than the npx binary path and the mcp-grep venv interpreter path if those are left as operator-specific — substitute only the project-root path"

error_handling:
  strategy: >
    The live-query helper never raises; all failure modes degrade to the
    next resolution tier. Startup must not fail if oMLX is unreachable.
  exceptions:
    - exception: "requests/connection error from urllib"
      condition: "oMLX server unreachable or refusing connections"
      handling: "Log at WARNING with the exception message; return None from the helper"
    - exception: "TimeoutError"
      condition: "oMLX server slow to respond"
      handling: "Log at WARNING; return None from the helper"
    - exception: "json.JSONDecodeError / KeyError / IndexError"
      condition: "Unexpected or malformed admin API response shape"
      handling: "Log at WARNING with the exception message; return None from the helper"
  logging:
    level: "WARNING"
    format: "Consistent with existing logging calls in orchestrator.py (the log.warning(...) pattern already used elsewhere in the file)"

testing:
  unit_tests:
    - scenario: "config['context']['context_window'] is set to a non-null int"
      expected: "resolve_context_window returns that value without querying oMLX"
    - scenario: "context_window is null; live query returns settings.max_context_window = 262144"
      expected: "resolve_context_window returns 262144"
    - scenario: "context_window is null; live query returns null; model_context_windows has an entry for the model"
      expected: "resolve_context_window returns the model_context_windows value"
    - scenario: "context_window is null; live query fails (connection error); no model_context_windows entry"
      expected: "resolve_context_window returns None; a WARNING is logged"
  edge_cases:
    - "oMLX admin endpoint returns a 404 or an entry whose id does not match model_name"
    - "settings key absent entirely from the matched model entry"
    - "config['mcp_servers'] contains a server definition with no '{PROJECT_ROOT}' placeholder at all (must pass through unchanged)"
  validation:
    - "ai/ael/src/orchestrator.py imports cleanly and has no syntax errors"
    - "config.yaml parses as valid YAML after edit and contains no reference to models_dir"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: ""
    - path: "ai/ael/config.yaml"
      content: ""

success_criteria:
  - "resolve_context_window implements the four-tier chain exactly as specified, in order"
  - "A new helper performs the live oMLX admin query using only stdlib HTTP, never raising"
  - "context.models_dir and all glob-based config.json search logic are removed from orchestrator.py"
  - "config.yaml contains no committed absolute path denoting the project root; '{PROJECT_ROOT}' is substituted at runtime before MCP server connection"
  - "North-Mini-Code-1.0-6bit continues to resolve to 262144 via the existing model_context_windows override, unchanged from current behavior"

element_registry:
  source: ""
  entries:
    modules: []
    classes: []
    functions:
      - name: "resolve_context_window"
        module: "ai/ael/src/orchestrator.py"
        signature: "def resolve_context_window(model_name: str, config: dict) -> int | None"
      - name: "_query_omlx_context_window"
        module: "ai/ael/src/orchestrator.py"
        signature: "def _query_omlx_context_window(model_name: str, base_url: str) -> int | None"
    constants:
      - name: "PROJECT_ROOT"
        module: "ai/ael/src/orchestrator.py"
        type: "str"

tactical_brief: |
  File: ai/ael/src/orchestrator.py, ai/ael/config.yaml. Read before editing.
  Replace resolve_context_window(model_name, config) with a 4-tier chain:
  (1) config.context.context_window if not null; (2) live query to
  {omlx.base_url minus trailing /v1}/admin/api/models?model_id=<model_name>,
  parse models[].settings.max_context_window for the matching id; (3)
  config.context.model_context_windows[model_name]; (4) None, log WARNING
  naming which tiers were tried. Add _query_omlx_context_window(model_name,
  base_url) using urllib.request (stdlib only, no httpx/requests); catch
  every exception, log WARNING, return None, never raise. Remove
  context.models_dir and any glob(...)/config.json search entirely. Add
  module constant PROJECT_ROOT = os.getcwd() (matches existing
  _archive_audit_artifacts() precedent in this file). Before constructing
  MCPClient(config.get("mcp_servers", {})), walk each server's
  command/args and replace literal "{PROJECT_ROOT}" with PROJECT_ROOT.
  In config.yaml: delete context.models_dir; replace the project-root
  absolute path in mcp_servers.filesystem.args with "{PROJECT_ROOT}";
  leave context_window, model_context_windows, npx binary path, and
  mcp-grep interpreter path as-is. Do not touch budget.py or govwatch.py.
  Preserve model_context_windows override behavior (North-Mini-Code-1.0-6bit
  -> 262144). Deliverable: both files edited in place. Success: 4-tier
  chain implemented in order and never raises; models_dir and glob search
  fully removed; PROJECT_ROOT substitution applied before MCP connection;
  North-Mini-Code-1.0-6bit still resolves to 262144.

notes: >
  Stream A of change-d42e64a9. Stream B (governance.md, primer.md,
  docs/claude/primer.md, workflow.md, ael-requirements.md wording) is a
  direct Strategic Domain edit, not part of this prompt. budget.py
  retirement (git mv to deprecated/) is also a direct Strategic Domain
  filesystem action, not part of this deliverable. No formal name
  registry master exists for this project; element_registry entries
  above are supplied directly rather than copied from a registry
  document.

version_history:
  - version: "1.0"
    date: "2026-07-08"
    changes:
      - "Initial prompt document targeting orchestrator.py and config.yaml under change-d42e64a9 Stream A"
```
