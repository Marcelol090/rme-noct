import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_package_json_requires_node_22_for_gsd() -> None:
    """The repo should expose a Node 22 local install contract for GSD."""
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    assert package["engines"]["node"] == ">=22.0.0"
    assert package["scripts"]["gsd"] == "node scripts/run-gsd.mjs"
    assert package["devDependencies"]["gsd-pi"] == "2.64.0"
    assert package["scripts"]["gsd:patch"] == "node scripts/patch-gsd-pi.mjs"
    assert package["scripts"]["gsd:auto"] == "node scripts/run-gsd-auto.mjs"
    assert (
        package["scripts"]["gsd:plan"]
        == "node scripts/run-gsd.mjs headless new-milestone --context-text"
    )
    assert package["scripts"]["gsd:status"] == "node scripts/run-gsd.mjs headless query"
    assert package["scripts"]["postinstall"] == "node scripts/patch-gsd-pi.mjs"


def test_setup_script_and_readme_match_node_22_contract() -> None:
    """Project docs and setup checks should match the same Node contract."""
    setup_script = (ROOT / "scripts" / "setup-devtools.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Node.js 22+" in setup_script
    assert "Node.js 22+" in readme
    assert "npm install --silent" in setup_script
    assert "npm run preflight" in setup_script
    assert "npm run gsd:auto" in readme
    assert "gsd-pi" not in readme


def test_readme_documents_local_gsd_commands() -> None:
    """README should describe the local npm-based GSD workflow."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "npm install" in readme
    assert "npm run preflight" in readme
    assert "npm run stack" in readme
    assert "postinstall" in readme
    assert "GSD_HOME" in readme
    assert "npm run gsd:auto" in readme
    assert "gsd headless query" in readme
    assert "gsd headless new-milestone --context-text" in readme
    assert "RME Extended Edition 3.8" in readme
    assert "2.5 / 3.7" not in readme
    assert "gsd-pi" not in readme


def test_postinstall_patch_script_targets_gsd_runtime_files() -> None:
    """The patch script should codify the exact runtime files we rely on."""
    patch_script = (ROOT / "scripts" / "patch-gsd-pi.mjs").read_text(encoding="utf-8")

    assert "dist/loader.js" in patch_script
    assert "dist/tool-bootstrap.js" in patch_script
    assert "dist/headless-ui.js" in patch_script
    assert "dist/resource-loader.js" in patch_script
    assert "dist/headless-context.js" in patch_script
    assert "dist/headless.js" in patch_script
    assert "dist/headless-query.js" in patch_script
    assert "dist/bundled-resource-path.js" in patch_script
    assert "dist/security-overrides.js" in patch_script
    assert "packages/pi-coding-agent/dist/core/model-resolver.js" in patch_script
    assert "../../../pi-ai/dist/models.js" in patch_script
    assert "packages/pi-coding-agent/dist/core/resource-loader.js" in patch_script
    assert "loadExtensionsLoaderModule" in patch_script
    assert "loadThemeModule" in patch_script
    assert "packages/pi-coding-agent/dist/core/agent-session.js" in patch_script
    assert "loadPromptTemplatesModule" in patch_script
    assert "loadBashExecutorModule" in patch_script
    assert 'import("./prompt-templates.js")' in patch_script
    assert 'import("./bash-executor.js")' in patch_script
    assert "clearApiProviders as resetApiProviders" in patch_script
    assert 'import { ExtensionRunner } from "./extensions/runner.js";' in patch_script
    assert 'import { wrapRegisteredTools } from "./extensions/wrapper.js";' in patch_script
    assert "packages/pi-coding-agent/dist/core/compaction/compaction.js" in patch_script
    assert "../../../../pi-ai/dist/stream.js" in patch_script
    assert "packages/pi-coding-agent/dist/core/compaction/branch-summarization.js" in patch_script
    assert "packages/pi-coding-agent/dist/core/compaction-orchestrator.js" in patch_script
    assert (
        "Import isContextOverflow directly so compaction orchestration "
        "does not pull the pi-ai barrel."
        in patch_script
    )
    assert "packages/pi-coding-agent/dist/core/retry-handler.js" in patch_script
    assert "../../../pi-ai/dist/utils/overflow.js" in patch_script
    assert "packages/pi-coding-agent/dist/core/export-html/index.js" in patch_script
    assert "loadThemeModule" in patch_script
    assert "packages/pi-coding-agent/dist/core/tools/index.js" in patch_script
    assert (
        (
            "import { DEFAULT_MAX_BYTES, DEFAULT_MAX_LINES, formatSize, "
            "truncateHead, truncateLine, truncateTail, } from \"./truncate.js\";"
        )
        in patch_script
    )
    assert 'import { Type } from "@sinclair/typebox";' in patch_script
    assert "../lsp/types.js" in patch_script
    assert "bashSchema" in patch_script
    assert "editSchema" in patch_script
    assert "rewriteBackgroundCommand" in patch_script
    assert "loadBashToolModule" in patch_script
    assert "loadEditToolModule" in patch_script
    assert "createLazyBashTool" in patch_script
    assert "createLazyEditTool" in patch_script
    assert "packages/pi-coding-agent/dist/core/tools/find.js" in patch_script
    assert "loadNativeGlobModule" in patch_script
    assert "@gsd/native/glob" in patch_script
    assert "packages/pi-coding-agent/dist/core/tools/write.js" in patch_script
    assert "loadNotifyFileChangedModule" in patch_script
    assert "../lsp/client.js" in patch_script
    assert "packages/pi-coding-agent/dist/core/model-registry.js" in patch_script
    assert "../packages/pi-coding-agent/dist/modes/rpc/jsonl.js" in patch_script
    assert "packages/pi-coding-agent/dist/modes/rpc/rpc-mode.js" in patch_script
    assert "dist/resources/extensions/gsd/bootstrap/register-extension.js" in patch_script
    assert "dist/resources/extensions/gsd/index.js" in patch_script
    assert "prepareHeadlessMilestoneSkeleton" in patch_script
    assert "headless-milestone-id.txt" in patch_script
    assert "readHeadlessMilestoneSeed" in patch_script
    assert "clearHeadlessMilestoneSeed" in patch_script
    assert "pre-materializing canonical milestone skeleton" in patch_script
    assert "GSD_HEADLESS_COMMAND" in patch_script
    assert "resolve(gsdHome, 'agent')" in patch_script
    assert "buildMilestoneContextSkeleton" in patch_script
    assert "-CONTEXT.md" in patch_script
    assert "loadInteractiveModeModule" in patch_script
    assert 'import("../interactive/interactive-mode.js")' in patch_script
    assert "packages/pi-coding-agent/dist/core/sdk.js" in patch_script
    assert "packages/pi-coding-agent/dist/index.js" in patch_script
    assert "await registerGsdExtension(pi);" in patch_script
    assert "Re-export tool factories directly from the tool catalog" in patch_script
    assert "debugPrintRpcStage" in patch_script
    assert "loading print/api module" in patch_script
    assert "shouldTraceLoaderCliImport" in patch_script
    assert "PI_CODING_AGENT_DIR" in patch_script
    assert "multi-turn session ended with 0 tool calls" in patch_script
    assert "Timeout waiting for response to prompt after ${responseTimeout}ms" in patch_script
    assert "const RPC_INIT_TIMEOUT_MS = 240000;" in patch_script
    assert "DEFAULT_RPC_REQUEST_TIMEOUT_MS" in patch_script
    assert "DEFAULT_RPC_EVENT_TIMEOUT_MS" in patch_script
    assert "dist/resources/extensions/gsd/auto-prompts.js" in patch_script
    assert "src/resources/extensions/gsd/auto-prompts.ts" in patch_script
    assert "dist/resources/extensions/gsd/guided-flow.js" in patch_script
    assert "Materializing canonical milestone skeleton" in patch_script


def test_run_gsd_script_preflights_auto_mode() -> None:
    """The GSD launcher should preflight the stack before headless auto."""
    run_gsd = (ROOT / "scripts" / "run-gsd.mjs").read_text(encoding="utf-8")

    assert "preflight: validating stack" in run_gsd
    assert "npm run preflight" in run_gsd
    assert "preflight failed" in run_gsd
    assert "stack ok, iniciando gsd:auto" in run_gsd
    assert "const gsdArgs = process.argv.slice(2);" in run_gsd
    assert "const isHeadlessAuto = gsdArgs[0] === 'headless'" in run_gsd


def test_preferences_are_codex_first() -> None:
    """GSD preferences should default to the installed local Ollama model."""
    preferences = (ROOT / ".gsd" / "preferences.md").read_text(encoding="utf-8")

    assert "research: ollama/qwen3-8b-gsd" in preferences
    assert "planning: ollama/qwen3-8b-gsd" in preferences
    assert "execution: ollama/qwen3-8b-gsd" in preferences
    assert "completion: ollama/qwen3-8b-gsd" in preferences
    assert "search_provider: ollama" in preferences
    assert "skip_research: true" in preferences
    assert "skip_slice_research: true" in preferences
    assert "skip_reassess: true" in preferences
    assert (
        "Local-first runtime: prefer the installed lightweight Ollama coder "
        "model for default phases"
        in preferences
    )


def test_python_wrappers_use_real_superpowers_skill_names() -> None:
    """The Python assistant should call upstream skill names that actually exist."""
    assistant = (ROOT / "pyrme" / "tools" / "ai_assistant.py").read_text(encoding="utf-8")

    assert "superpowers:writing-plans" in assistant
    assert "superpowers:subagent-driven-development" in assistant
    assert "superpowers:requesting-code-review" in assistant
    assert "superpowers:planning" not in assistant
    assert "superpowers:tdd" not in assistant
    assert "superpowers:test-driven-development" not in assistant
    assert "superpowers:code-review" not in assistant


def test_gsd_config_uses_codex_skill_locations() -> None:
    """GSD config should point at Codex skill directories, not legacy GSD-only paths."""
    config = (ROOT / "pyrme" / "devtools" / "gsd" / "config.py").read_text(encoding="utf-8")

    assert 'self.project_root / ".pi" / "agent" / "skills"' in config
    assert '_safe_home() / ".gsd" / "agent" / "skills"' in config
    assert "def _safe_home() -> Path:" in config
    assert '".agents" / "skills"' not in config
    assert '"research": "ollama/qwen3-8b-gsd"' in config
    assert '"planning": "ollama/qwen3-8b-gsd"' in config


def test_local_ollama_models_json_seeds_runtime_provider() -> None:
    """The repo should seed the local agent dir with an Ollama provider contract."""
    models_json = ROOT / ".gsd" / "agent" / "models.json"
    data = json.loads(models_json.read_text(encoding="utf-8"))

    provider = data["providers"]["ollama"]
    assert provider["baseUrl"] == "http://127.0.0.1:11434/v1"
    assert provider["apiKey"] == "ollama"
    assert provider["api"] == "openai-completions"
    assert provider["models"][0]["id"] == "qwen3-8b-gsd"
    assert provider["models"][0]["api"] == "openai-completions"
    assert provider["models"][0]["name"] == "Qwen3 8B GSD (ctx 8192)"
    assert provider["models"][0]["contextWindow"] == 8192


def test_readme_documents_codex_first_layering() -> None:
    """README should separate Codex, Superpowers, and GSD responsibilities."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Codex/OpenAI" in readme
    assert "Superpowers" in readme
    assert "GSD 2" in readme
    assert "Context7" in readme
    assert ".pi/agent/skills/" in readme
    assert ".gsd/preferences.md" in readme
    assert "git.isolation: worktree" in readme
    assert "npm run preflight" in readme


def test_workflow_docs_keep_legacy_and_python_contracts_aligned() -> None:
    """Workflow docs should match the repo's Python/GSD contract and legacy authority."""
    codex_workflow = (
        ROOT
        / "docs"
        / "superpowers"
        / "workflows"
        / "2026-04-06-codex-first-superpowers-gsd.md"
    ).read_text(encoding="utf-8")
    tier2_workflow = (
        ROOT
        / "docs"
        / "superpowers"
        / "workflows"
        / "2026-04-06-tier2-docks-dialogs-workflow.md"
    ).read_text(encoding="utf-8")
    legacy_plan = (
        ROOT
        / "docs"
        / "superpowers"
        / "plans"
        / "2026-04-09-legacy-menu-parity-phase1.md"
    ).read_text(encoding="utf-8")

    assert "legacy redux C++ tree" in codex_workflow
    assert ".jules/newagents/" in codex_workflow
    assert "gpt-5.4-mini" in codex_workflow
    assert "git.isolation: worktree" in tier2_workflow
    assert "Python 3.12+" in legacy_plan
    assert "python -m pytest" in legacy_plan
    assert "python3 -m pytest" not in legacy_plan
    assert "Python 3.10" not in legacy_plan


def test_jules_subagent_contracts_are_reusable_and_mini_first() -> None:
    """Repo-local Jules subagents should exist for repeatable mini-model work."""
    jules_orchestrator = (ROOT / ".jules" / "agents" / "jules.md").read_text(
        encoding="utf-8"
    )
    python_agent = (ROOT / ".jules" / "newagents" / "python.md").read_text(
        encoding="utf-8"
    )
    rust_agent = (ROOT / ".jules" / "newagents" / "rust.md").read_text(
        encoding="utf-8"
    )
    bridge_agent = (ROOT / ".jules" / "newagents" / "bridge.md").read_text(
        encoding="utf-8"
    )
    review_agent = (ROOT / ".jules" / "newagents" / "review.md").read_text(
        encoding="utf-8"
    )
    test_agent = (ROOT / ".jules" / "newagents" / "test.md").read_text(
        encoding="utf-8"
    )
    utility_agent = (ROOT / ".jules" / "newagents" / "utility.md").read_text(
        encoding="utf-8"
    )
    invoke_workflow = (ROOT / ".github" / "workflows" / "jules-invoke.yml").read_text(
        encoding="utf-8"
    )
    dispatch_workflow = (
        ROOT / ".github" / "workflows" / "jules-dispatch.yml"
    ).read_text(encoding="utf-8")

    assert "reusable project-local subagent contracts" in jules_orchestrator
    assert "focus=review" in jules_orchestrator
    assert "focus=test" in jules_orchestrator
    assert "focus=utility" in jules_orchestrator
    assert "gpt-5.4-mini" in review_agent
    assert "gpt-5.4-mini" in test_agent
    assert "gpt-5.4-mini" in utility_agent
    assert "read-only legacy reference only" in review_agent
    assert "read-only legacy reference only" in test_agent
    assert "read-only legacy reference only" in utility_agent
    assert "AUTONOMOUS AGENT. NO QUESTIONS. NO COMMENTS. ACT." in python_agent
    assert "AUTONOMOUS AGENT. NO QUESTIONS. NO COMMENTS. ACT." in rust_agent
    assert "AUTONOMOUS AGENT. NO QUESTIONS. NO COMMENTS. ACT." in bridge_agent
    assert "review) prompt_file='.jules/newagents/review.md'" in invoke_workflow
    assert "test) prompt_file='.jules/newagents/test.md'" in invoke_workflow
    assert "utility) prompt_file='.jules/newagents/utility.md'" in invoke_workflow
    assert "review|test|utility" in dispatch_workflow


def test_gitignore_covers_repo_local_gsd_runtime_artifacts() -> None:
    """Runtime directories from the repo-local GSD home should stay untracked."""
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert ".gsd/agent/*" in gitignore
    assert "!.gsd/agent/models.json" in gitignore
    assert ".gsd/extensions/" in gitignore
    assert ".gsd/sessions/" in gitignore
    assert ".gsd/web-server.pid" in gitignore
    assert ".gsd/web-preferences.json" in gitignore
