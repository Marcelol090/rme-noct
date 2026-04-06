import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_package_json_requires_node_22_for_gsd() -> None:
    """The repo should expose a Node 22 local install contract for GSD."""
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    assert package["engines"]["node"] == ">=22.0.0"
    assert package["devDependencies"]["gsd-pi"] == "2.64.0"
    assert package["scripts"]["gsd"] == "gsd"
    assert package["scripts"]["gsd:auto"] == "gsd auto"
    assert package["scripts"]["gsd:plan"] == "gsd plan"
    assert package["scripts"]["gsd:status"] == "gsd status"


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
    assert "npm run gsd:auto" in readme
