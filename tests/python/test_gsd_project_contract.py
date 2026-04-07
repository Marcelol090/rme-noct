import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_package_json_requires_node_22_for_gsd() -> None:
    """The repo should expose a Node 22 local install contract for GSD."""
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    assert package["engines"]["node"] == ">=22.0.0"
    assert package["devDependencies"]["gsd-pi"] == "2.64.0"
    assert package["scripts"]["gsd"] == "gsd"
    assert package["scripts"]["gsd:patch"] == "node scripts/patch-gsd-pi.mjs"
    assert package["scripts"]["gsd:auto"] == "gsd headless auto"
    assert package["scripts"]["gsd:plan"] == "gsd headless new-milestone --context-text"
    assert package["scripts"]["gsd:status"] == "gsd headless query"
    assert package["scripts"]["postinstall"] == "node scripts/patch-gsd-pi.mjs"


def test_setup_script_and_readme_match_node_22_contract() -> None:
    """Project docs and setup checks should match the same Node contract."""
    setup_script = (ROOT / "scripts" / "setup-devtools.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Node.js 22+" in setup_script
    assert "Node.js 22+" in readme
    assert "npm install --silent" in setup_script
    assert "npm run gsd:auto" in readme


def test_readme_documents_local_gsd_commands() -> None:
    """README should describe the local npm-based GSD workflow."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "npm install" in readme
    assert "postinstall" in readme
    assert "npm run gsd:auto" in readme
    assert "gsd headless query" in readme
    assert "gsd headless new-milestone --context-text" in readme


def test_postinstall_patch_script_targets_gsd_runtime_files() -> None:
    """The patch script should codify the exact runtime files we rely on."""
    patch_script = (ROOT / "scripts" / "patch-gsd-pi.mjs").read_text(encoding="utf-8")

    assert "dist/loader.js" in patch_script
    assert "dist/headless-query.js" in patch_script
    assert "dist/bundled-resource-path.js" in patch_script
    assert "dist/resources/extensions/gsd/auto-prompts.js" in patch_script
    assert "src/resources/extensions/gsd/auto-prompts.ts" in patch_script


def test_preferences_are_codex_first() -> None:
    """GSD preferences should default to OpenAI/Codex-aligned models."""
    preferences = (ROOT / ".gsd" / "preferences.md").read_text(encoding="utf-8")

    assert "research: gpt-5.4-mini" in preferences
    assert "planning: gpt-5.4" in preferences
    assert "execution: gpt-5.4-mini" in preferences
    assert "completion: gpt-5.4-mini" in preferences
    assert "Codex/OpenAI is the primary runtime contract" in preferences


def test_python_wrappers_use_real_superpowers_skill_names() -> None:
    """The Python assistant should call upstream skill names that actually exist."""
    assistant = (ROOT / "pyrme" / "tools" / "ai_assistant.py").read_text(encoding="utf-8")

    assert "superpowers:writing-plans" in assistant
    assert "superpowers:test-driven-development" in assistant
    assert "superpowers:requesting-code-review" in assistant
    assert "superpowers:planning" not in assistant
    assert "superpowers:tdd" not in assistant
    assert "superpowers:code-review" not in assistant


def test_gsd_config_uses_codex_skill_locations() -> None:
    """GSD config should point at Codex skill directories, not legacy GSD-only paths."""
    config = (ROOT / "pyrme" / "devtools" / "gsd" / "config.py").read_text(encoding="utf-8")

    assert '".agents" / "skills"' in config
    assert 'Path.home() / ".agents" / "skills"' in config
    assert ".pi" not in config
    assert '"research": "gpt-5.4-mini"' in config
    assert '"planning": "gpt-5.4"' in config


def test_readme_documents_codex_first_layering() -> None:
    """README should separate Codex, Superpowers, and GSD responsibilities."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Codex/OpenAI" in readme
    assert "Superpowers" in readme
    assert "GSD 2" in readme
    assert "Context7" in readme
