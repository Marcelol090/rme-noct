#!/usr/bin/env node

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = dirname(scriptDir);
const gsdRoot = join(repoRoot, 'node_modules', 'gsd-pi');

if (!existsSync(gsdRoot)) {
  process.exit(0);
}

const patchedFiles = [];

function normalize(text) {
  return text.replace(/\r\n/g, '\n');
}

function patchFile(relPath, transform) {
  const absPath = join(gsdRoot, relPath);
  if (!existsSync(absPath)) {
    throw new Error(`Missing expected gsd-pi file: ${relPath}`);
  }

  const before = normalize(readFileSync(absPath, 'utf8'));
  const after = transform(before);

  if (after !== before) {
    writeFileSync(absPath, after);
    patchedFiles.push(relPath);
  }
}

patchFile('dist/loader.js', (text) => {
  const marker = '// Fast-path `gsd headless query` before importing the full CLI bootstrap.';
  if (text.includes(marker)) {
    return text;
  }

  const anchor = 'process.env.GSD_BIN_PATH = process.argv[1];\n';
  const insertion = `// Fast-path \`gsd headless query\` before importing the full CLI bootstrap.\n// The query path is read-only and does not need the expensive resource sync,\n// workspace package linking, or CLI startup stack.\nfunction getHeadlessSubcommand(argv) {\n    let seenHeadless = false;\n    for (const arg of argv.slice(2)) {\n        if (arg.startsWith('-')) {\n            continue;\n        }\n        if (!seenHeadless) {\n            if (arg === 'headless') {\n                seenHeadless = true;\n            }\n            continue;\n        }\n        return arg;\n    }\n    return null;\n}\nif (getHeadlessSubcommand(process.argv) === 'query') {\n    const { handleQuery } = await import('./headless-query.js');\n    await handleQuery(process.cwd());\n    process.exit(0);\n}\n`;

  if (!text.includes(anchor)) {
    throw new Error('Unable to patch dist/loader.js: fast-path anchor not found');
  }

  return text.replace(anchor, `${anchor}${insertion}`);
});

patchFile('dist/headless-query.js', (text) => {
  const desiredChunk = `async function loadExtensionModules() {\n    try {\n        const [stateModule, dispatchModule, sessionModule, prefsModule] = await Promise.all([\n            import('./resources/extensions/gsd/state.js'),\n            import('./resources/extensions/gsd/auto-dispatch.js'),\n            import('./resources/extensions/gsd/session-status-io.js'),\n            import('./resources/extensions/gsd/preferences.js'),\n        ]);\n        return {\n            deriveState: stateModule.deriveState,\n            resolveDispatch: dispatchModule.resolveDispatch,\n            readAllSessionStatuses: sessionModule.readAllSessionStatuses,\n            loadEffectiveGSDPreferences: prefsModule.loadEffectiveGSDPreferences,\n        };\n    }\n    catch (err) {\n        const stateModule = await jiti.import(gsdExtensionPath('state.ts'), {});\n        const dispatchModule = await jiti.import(gsdExtensionPath('auto-dispatch.ts'), {});\n        const sessionModule = await jiti.import(gsdExtensionPath('session-status-io.ts'), {});\n        const prefsModule = await jiti.import(gsdExtensionPath('preferences.ts'), {});\n        return {\n            deriveState: stateModule.deriveState,\n            resolveDispatch: dispatchModule.resolveDispatch,\n            readAllSessionStatuses: sessionModule.readAllSessionStatuses,\n            loadEffectiveGSDPreferences: prefsModule.loadEffectiveGSDPreferences,\n        };\n    }\n}\n`;
  const start = text.indexOf('async function loadExtensionModules() {');
  const end = text.indexOf('// ─── Implementation ─────────────────────────────────────────────────────────');
  if (start === -1 || end === -1 || end <= start) {
    throw new Error('Unable to patch dist/headless-query.js: loadExtensionModules block not found');
  }

  return `${text.slice(0, start)}${desiredChunk}\n\n${text.slice(end)}`;
});

patchFile('dist/bundled-resource-path.js', (text) => {
  const desired = `import { existsSync } from "node:fs";\nimport { dirname, join, resolve } from "node:path";\nimport { fileURLToPath } from "node:url";\n/**\n * Resolve bundled raw resource files from the package root.\n *\n * Prefer compiled \`dist/*.js\` resources when they exist because they load\n * much faster in installed packages. Fall back to \`src/*.ts\` for source-tree\n * workflows that do not have compiled resources yet.\n */\nexport function resolveBundledSourceResource(importUrl, ...segments) {\n    const moduleDir = dirname(fileURLToPath(importUrl));\n    const packageRoot = resolve(moduleDir, "..");\n    const distSegments = segments.map(segment => segment.replace(/\\.tsx?$/i, ".js"));\n    const distPath = join(packageRoot, "dist", "resources", ...distSegments);\n    if (existsSync(distPath)) {\n        return distPath;\n    }\n    return join(packageRoot, "src", "resources", ...segments);\n}\n`;

  return desired;
});

patchFile('dist/resources/extensions/gsd/auto-prompts.js', (text) => {
  const pattern = /import \{\s*getLoadedSkills(?:,\s*type\s+Skill)?\s*\}\s+from\s+["'][^"']+["'];/;
  if (!pattern.test(text)) {
    throw new Error('Unable to patch dist/resources/extensions/gsd/auto-prompts.js: getLoadedSkills import not found');
  }
  return text.replace(pattern, 'import { getLoadedSkills } from "../../../../packages/pi-coding-agent/dist/core/skills.js";');
});

patchFile('src/resources/extensions/gsd/auto-prompts.ts', (text) => {
  const pattern = /import \{\s*getLoadedSkills(?:,\s*type\s+Skill)?\s*\}\s+from\s+["'][^"']+["'];/;
  if (!pattern.test(text)) {
    throw new Error('Unable to patch src/resources/extensions/gsd/auto-prompts.ts: getLoadedSkills import not found');
  }
  return text.replace(pattern, 'import { getLoadedSkills, type Skill } from "../../../../packages/pi-coding-agent/dist/core/skills.js";');
});

if (patchedFiles.length > 0) {
  process.stdout.write(`[gsd-pi] patched ${patchedFiles.length} file(s): ${patchedFiles.join(', ')}\n`);
} else {
  process.stdout.write('[gsd-pi] postinstall check complete\n');
}
