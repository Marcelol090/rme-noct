import os
import subprocess
import sys
import sysconfig
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPRITE_SHADER = REPO_ROOT / "crates" / "rme_core" / "src" / "render" / "sprite.wgsl"


def test_sprite_shader_validates_with_naga_example():
    env = os.environ.copy()
    env["PATH"] = f"{Path.home() / '.cargo' / 'bin'}{os.pathsep}{env['PATH']}"
    env["PYO3_PYTHON"] = sys.executable
    if libdir := sysconfig.get_config_var("LIBDIR"):
        env["LD_LIBRARY_PATH"] = os.pathsep.join(
            part for part in (str(libdir), env.get("LD_LIBRARY_PATH", "")) if part
        )

    result = subprocess.run(
        [
            "cargo",
            "run",
            "-p",
            "rme_core",
            "--example",
            "validate_sprite_shader",
            "--locked",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        env=env,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "sprite WGSL validated with naga" in result.stdout


def test_sprite_shader_keeps_clear_color_out_of_wgsl():
    source = SPRITE_SHADER.read_text(encoding="utf-8")

    assert "Void Black" not in source
    assert "#0A0A12" not in source
