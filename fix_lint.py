import re
from pathlib import Path

path = Path("pyrme/devtools/superpowers/skills_loader.py")
content = path.read_text()

search = '        self.superpowers_dir = config.superpowers_dir or (home_dir / ".codex" / "superpowers" / "skills")'
replace = '        self.superpowers_dir = config.superpowers_dir or (\n            home_dir / ".codex" / "superpowers" / "skills"\n        )'

path.write_text(content.replace(search, replace))
