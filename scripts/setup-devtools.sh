#!/usr/bin/env bash
# ============================================================
# PyRME DevTools Setup Script
# Sets up GSD-2 (npm), Superpowers (git clone), and Python env
#
# Official conventions (from Context7 docs):
#   GSD-2: npm install + .gsd/ + .pi/agent/skills/
#   Superpowers: git clone into .superpowers/
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔧 PyRME DevTools Setup"
echo "========================"
echo "Project root: $PROJECT_ROOT"
echo ""

# ── 1. Check prerequisites ──────────────────────────────────
echo "📋 Checking prerequisites..."

command -v node >/dev/null 2>&1 || { echo "❌ Node.js 22+ is required. Install: https://nodejs.org"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required."; exit 1; }
command -v python >/dev/null 2>&1 || { echo "❌ Python 3.12+ is required."; exit 1; }
command -v cargo >/dev/null 2>&1 || { echo "❌ Rust/Cargo is required. Install: https://rustup.rs"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git is required."; exit 1; }

NODE_MAJOR="$(node -p "process.versions.node.split('.')[0]")"
if [ "$NODE_MAJOR" -lt 22 ]; then
    echo "❌ Node.js 22+ is required for the local gsd-pi toolchain."
    echo "   Current version: $(node -v)"
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# ── 2. Install GSD-2 via npm ────────────────────────────────
echo "📦 Installing GSD-2 via npm..."
cd "$PROJECT_ROOT"
npm install --silent
echo "✅ GSD-2 installed"
echo ""

# ── 3. Clone Superpowers skills ──────────────────────────────
# Per Context7 docs: clone into project's .superpowers/ directory
echo "📦 Installing Superpowers skills..."
SUPERPOWERS_DIR="$PROJECT_ROOT/.superpowers"

if [ -d "$SUPERPOWERS_DIR/.git" ]; then
    echo "  Updating existing Superpowers installation..."
    cd "$SUPERPOWERS_DIR"
    git pull --quiet
else
    echo "  Cloning Superpowers skills repository..."
    git clone --depth=1 https://github.com/obra/superpowers.git "$SUPERPOWERS_DIR"
fi
echo "✅ Superpowers skills installed at .superpowers/"
echo ""

# ── 4. Create GSD project directories ───────────────────────
# Per Context7 docs: .gsd/ for preferences, .pi/agent/skills/ for project skills
echo "📁 Creating GSD project directories..."
mkdir -p "$PROJECT_ROOT/.gsd"
mkdir -p "$PROJECT_ROOT/.gsd/milestones"
mkdir -p "$PROJECT_ROOT/.pi/agent/skills"
echo "✅ GSD directories created"
echo ""

# ── 5. Set up Python virtual environment ────────────────────
echo "🐍 Setting up Python environment..."
cd "$PROJECT_ROOT"
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "  Created .venv"
fi

# Activate
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

pip install --quiet --upgrade pip
pip install --quiet maturin
pip install --quiet -e ".[dev]"
echo "✅ Python environment ready"
echo ""

# ── 6. Build Rust core ──────────────────────────────────────
echo "🦀 Building Rust core (rme_core)..."
maturin develop
echo "✅ Rust core built and installed"
echo ""

# ── 7. Verification ─────────────────────────────────────────
echo "🔍 Verification..."
python -c "from pyrme import rme_core; print(f'  rme_core v{rme_core.version()}')" 2>/dev/null || echo "  ⚠ rme_core import failed"
python -c "from pyrme.devtools.gsd.config import GSDConfig; c = GSDConfig(); print(f'  GSD project skills: {c.list_project_skills()}')" 2>/dev/null || echo "  ⚠ GSD config failed"
python -c "from pyrme.devtools.superpowers.skills_loader import SkillsLoader; s = SkillsLoader(); print(f'  Superpowers skills: {len(s.find_skills())} found')" 2>/dev/null || echo "  ⚠ Skills loader failed"
echo ""

echo "============================================================"
echo "✅ PyRME DevTools setup complete!"
echo ""
echo "Project structure:"
echo "  .gsd/                  GSD-2 preferences & milestones"
echo "  .pi/agent/skills/      Project-scope GSD skills"
echo "  .superpowers/          Superpowers skills (git clone)"
echo "  .agent/skills/         Antigravity workspace skills"
echo "  .agent/workflows/      Antigravity workflows"
echo ""
echo "Quick start:"
echo "  python -m pyrme          Launch the editor"
echo "  npm run gsd:auto         Start GSD autonomous mode (Node 22+)"
echo "  pytest tests/            Run tests"
echo "  maturin develop          Rebuild Rust core"
echo "============================================================"
