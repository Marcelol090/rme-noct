#!/usr/bin/env node

import { createHash } from 'node:crypto';
import {
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = dirname(scriptDir);
const gsdRoot = join(repoRoot, 'node_modules', 'gsd-pi');
const gsdResourcesRoot = join(gsdRoot, 'dist', 'resources');
const piCodingAgentAliasRoot = join(repoRoot, 'node_modules', '@gsd', 'pi-coding-agent');
const nativeAliasRoot = join(repoRoot, 'node_modules', '@gsd', 'native');
const bundledResourceFingerprintName = '.managed-resource-fingerprint';

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

function collectBundledResourceEntries(dir, root, out) {
  if (!existsSync(dir)) {
    return;
  }

  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      collectBundledResourceEntries(fullPath, root, out);
      continue;
    }

    if (entry.name === bundledResourceFingerprintName) {
      continue;
    }

    const relPath = relative(root, fullPath);
    out.push(`${relPath}:${statSync(fullPath).size}`);
  }
}

function computeBundledResourceFingerprint() {
  const entries = [];
  collectBundledResourceEntries(gsdResourcesRoot, gsdResourcesRoot, entries);
  entries.sort();
  return createHash('sha256').update(entries.join('\n')).digest('hex').slice(0, 16);
}

function writeBundledResourceFingerprint() {
  if (!existsSync(gsdResourcesRoot)) {
    return;
  }

  const relPath = `dist/resources/${bundledResourceFingerprintName}`;
  const absPath = join(gsdResourcesRoot, bundledResourceFingerprintName);
  const next = `${computeBundledResourceFingerprint()}\n`;
  const before = existsSync(absPath) ? readFileSync(absPath, 'utf8') : null;
  if (before !== next) {
    writeFileSync(absPath, next);
    patchedFiles.push(relPath);
  }
}

function writeTextIfChanged(filePath, content) {
  const current = existsSync(filePath) ? readFileSync(filePath, 'utf8') : null;
  if (current !== content) {
    writeFileSync(filePath, content);
    patchedFiles.push(relative(repoRoot, filePath).split('\\').join('/'));
  }
}

function block(lines) {
  return `${lines.join('\n')}\n`;
}

function ensurePiCodingAgentAlias() {
  if (!existsSync(gsdRoot)) {
    return;
  }

  mkdirSync(piCodingAgentAliasRoot, { recursive: true });
  writeTextIfChanged(
    join(piCodingAgentAliasRoot, 'package.json'),
    block([
      '{',
      '  "name": "@gsd/pi-coding-agent",',
      '  "private": true,',
      '  "type": "module",',
      '  "exports": {',
      '    ".": "./index.js"',
      '  }',
      '}',
    ]),
  );
  writeTextIfChanged(
    join(piCodingAgentAliasRoot, 'index.js'),
    block([
      "export * from '../../gsd-pi/packages/pi-coding-agent/dist/index.js';",
    ]),
  );
  writeTextIfChanged(
    join(piCodingAgentAliasRoot, 'index.d.ts'),
    block([
      "export * from '../../gsd-pi/packages/pi-coding-agent/dist/index';",
    ]),
  );
}

function ensureGsdInternalWorkspacePackages() {
  const internalScopeRoot = join(gsdRoot, 'node_modules', '@gsd');
  const packageChecks = {
    native: 'package.json',
    'pi-agent-core': 'package.json',
    'pi-ai': 'dist/utils/overflow.js',
    'pi-coding-agent': 'dist/index.js',
    'pi-tui': 'package.json',
  };
  mkdirSync(internalScopeRoot, { recursive: true });

  for (const [packageName, criticalFile] of Object.entries(packageChecks)) {
    const source = join(gsdRoot, 'packages', packageName);
    const target = join(internalScopeRoot, packageName);
    if (!existsSync(join(source, 'package.json')) || existsSync(join(target, criticalFile))) {
      continue;
    }
    try {
      rmSync(target, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
    }
    catch {
      // Windows may leave copied package trees briefly locked. Copying over the
      // partial tree still repairs missing files for the loader.
    }
    cpSync(source, target, { recursive: true });
    patchedFiles.push(relative(repoRoot, target).split('\\').join('/'));
  }
}

function ensureNativeShim() {
  mkdirSync(nativeAliasRoot, { recursive: true });
  writeTextIfChanged(
    join(nativeAliasRoot, 'package.json'),
    block([
      '{',
      '  "name": "@gsd/native",',
      '  "private": true,',
      '  "type": "module",',
      '  "exports": {',
      '    ".": "./index.js",',
      '    "./clipboard": "./clipboard.js",',
      '    "./fd": "./fd.js",',
      '    "./image": "./image.js",',
      '    "./glob": "./glob.js",',
      '    "./text": "./text.js",',
      '    "./xxhash": "./xxhash.js"',
      '  }',
      '}',
    ]),
  );
  writeTextIfChanged(
    join(nativeAliasRoot, 'index.js'),
    block([
      "const ANSI_RE = /\\x1b\\[[0-9;]*[A-Za-z]/g;",
      '',
      'export function processStreamChunk(data, state) {',
      "  const text = Buffer.from(data).toString('utf8').replace(/\\r\\n?/g, '\\n').replace(ANSI_RE, '');",
      '  return { text, state };',
      '}',
      '',
      "export { copyToClipboard, readTextFromClipboard, readImageFromClipboard } from './clipboard.js';",
      "export { fuzzyFind } from './fd.js';",
      "export { glob } from './glob.js';",
      "export { ImageFormat, parseImage, SamplingFilter } from './image.js';",
      "export { EllipsisKind, extractSegments, sliceWithWidth, sliceByColumn, truncateToWidth, visibleWidth, wrapTextWithAnsi } from './text.js';",
      "export { xxHash32 } from './xxhash.js';",
    ]),
  );
  writeTextIfChanged(
    join(nativeAliasRoot, 'clipboard.js'),
    block([
      'export function copyToClipboard(_text) {',
      '  return undefined;',
      '}',
      '',
      'export function readTextFromClipboard() {',
      "  return '';",
      '}',
      '',
      'export async function readImageFromClipboard() {',
      '  return null;',
      '}',
    ]),
  );
  writeTextIfChanged(
    join(nativeAliasRoot, 'fd.js'),
    block([
      "import { readdirSync, statSync } from 'node:fs';",
      "import { join, relative, sep } from 'node:path';",
      '',
      'function walk(dir, out, options) {',
      '  for (const entry of readdirSync(dir, { withFileTypes: true })) {',
      '    if (!options.hidden && entry.name.startsWith(".")) {',
      '      continue;',
      '    }',
      '    if (options.gitignore && (entry.name === "node_modules" || entry.name === ".git")) {',
      '      continue;',
      '    }',
      '    const full = join(dir, entry.name);',
      '    if (entry.isDirectory()) {',
      '      out.push({ path: relative(options.root, full).split(sep).join("/") + "/", isDirectory: true });',
      '      walk(full, out, options);',
      '    }',
      '    else if (statSync(full).isFile()) {',
      '      out.push({ path: relative(options.root, full).split(sep).join("/"), isDirectory: false });',
      '    }',
      '  }',
      '}',
      '',
      'export function fuzzyFind({ query, path, hidden = true, gitignore = true, maxResults = 1000 }) {',
      '  const matches = [];',
      '  walk(path, matches, { hidden, gitignore, root: path });',
      '  const lowerQuery = query.toLowerCase();',
      '  const filtered = matches.filter((entry) => entry.path.toLowerCase().includes(lowerQuery));',
      '  return { matches: filtered.slice(0, maxResults) };',
      '}',
    ]),
  );
  writeTextIfChanged(
    join(nativeAliasRoot, 'image.js'),
    block([
      'export const ImageFormat = {',
      "  PNG: 'png',",
      "  JPEG: 'jpeg',",
      '};',
      '',
      'export const SamplingFilter = {',
      "  Lanczos3: 'Lanczos3',",
      '};',
      '',
      'function readUInt32BE(bytes, offset) {',
      '  return (bytes[offset] << 24) | (bytes[offset + 1] << 16) | (bytes[offset + 2] << 8) | bytes[offset + 3];',
      '}',
      '',
      'function detectDimensions(bytes) {',
      '  if (bytes.length >= 24 &&',
      '      bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47 &&',
      '      bytes[4] === 0x0d && bytes[5] === 0x0a && bytes[6] === 0x1a && bytes[7] === 0x0a) {',
      "    return { width: readUInt32BE(bytes, 16), height: readUInt32BE(bytes, 20), mimeType: 'image/png' };",
      '  }',
      '',
      '  if (bytes.length > 4 && bytes[0] === 0xff && bytes[1] === 0xd8) {',
      '    let offset = 2;',
      '    while (offset + 3 < bytes.length) {',
      '      if (bytes[offset] !== 0xff) {',
      '        offset++;',
      '        continue;',
      '      }',
      '      const marker = bytes[offset + 1];',
      '      const length = (bytes[offset + 2] << 8) | bytes[offset + 3];',
      '      if (length < 2) {',
      '        break;',
      '      }',
      '      const isSof = marker >= 0xc0 && marker <= 0xc3;',
      '      if (isSof && offset + 8 < bytes.length) {',
      '        return {',
      '          height: (bytes[offset + 5] << 8) | bytes[offset + 6],',
      '          width: (bytes[offset + 7] << 8) | bytes[offset + 8],',
      "          mimeType: 'image/jpeg',",
      '        };',
      '      }',
      '      offset += 2 + length;',
      '    }',
      "    return { width: 1, height: 1, mimeType: 'image/jpeg' };",
      '  }',
      '',
      "  return { width: 1, height: 1, mimeType: 'image/png' };",
      '}',
      '',
      'function createHandle(bytes, width, height, mimeType) {',
      '  return {',
      '    width,',
      '    height,',
      '    async resize(nextWidth, nextHeight) {',
      '      return createHandle(bytes, nextWidth, nextHeight, mimeType);',
      '    },',
      '    async encode(format, _quality) {',
      '      return bytes;',
      '    },',
      '  };',
      '}',
      '',
      'export async function parseImage(bytes) {',
      '  const input = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);',
      '  const { width, height, mimeType } = detectDimensions(input);',
      '  return createHandle(input, width, height, mimeType);',
      '}',
    ]),
  );
  writeTextIfChanged(
    join(nativeAliasRoot, 'text.js'),
    block([
      'export const EllipsisKind = {',
      "  Unicode: 'unicode',",
      "  Ascii: 'ascii',",
      "  None: 'none',",
      '};',
      '',
      'const ANSI_RE = /\\x1b\\[[0-9;]*[A-Za-z]/g;',
      '',
      'function stripAnsi(text) {',
      "  return text.replace(ANSI_RE, '');",
      '}',
      '',
      'function graphemes(text) {',
      '  return Array.from(text);',
      '}',
      '',
      'export function visibleWidth(str) {',
      '  return graphemes(stripAnsi(str)).length;',
      '}',
      '',
      'function sliceByCodePoints(text, start, end) {',
      '  return graphemes(text).slice(start, end).join("");',
      '}',
      '',
      'export function wrapTextWithAnsi(text, width) {',
      '  const lines = [];',
      '  for (const rawLine of String(text).split(/\\r?\\n/)) {',
      '    let line = "";',
      '    let currentWidth = 0;',
      '    for (const ch of graphemes(rawLine)) {',
      '      if (currentWidth >= width) {',
      '        lines.push(line);',
      '        line = "";',
      '        currentWidth = 0;',
      '      }',
      '      line += ch;',
      '      currentWidth += 1;',
      '    }',
      '    lines.push(line);',
      '  }',
      '  return lines;',
      '}',
      '',
      'export function truncateToWidth(text, maxWidth, ellipsis = EllipsisKind.Ascii, pad = false) {',
      '  const content = stripAnsi(String(text));',
      '  if (content.length <= maxWidth) {',
      '    return pad ? content.padEnd(maxWidth, " ") : content;',
      '  }',
      '  const ellipsisText = ellipsis === EllipsisKind.Unicode ? "…" : ellipsis === EllipsisKind.None ? "" : "...";',
      '  const sliceWidth = Math.max(0, maxWidth - ellipsisText.length);',
      '  return sliceByCodePoints(content, 0, sliceWidth) + ellipsisText;',
      '}',
      '',
      'export function sliceWithWidth(line, startCol, length, strict = false) {',
      '  const text = sliceByCodePoints(String(line), startCol, startCol + length);',
      '  return { text, width: visibleWidth(text) };',
      '}',
      '',
      'export function sliceByColumn(line, startCol, length, strict = false) {',
      '  return sliceWithWidth(line, startCol, length, strict).text;',
      '}',
      '',
      'export function extractSegments(line, beforeEnd, afterStart, afterLen, strictAfter = false) {',
      '  const before = sliceByCodePoints(String(line), 0, beforeEnd);',
      '  const after = sliceByCodePoints(String(line), afterStart, afterStart + afterLen);',
      '  return { before, beforeWidth: visibleWidth(before), after, afterWidth: visibleWidth(after) };',
      '}',
    ]),
  );
  writeTextIfChanged(
    join(nativeAliasRoot, 'glob.js'),
    block([
      "import { readdirSync, statSync } from 'node:fs';",
      "import { join, relative, sep } from 'node:path';",
      '',
      'function escapeRegex(text) {',
      "  return text.replace(/[|\\\\{}()[\\]^$+?.]/g, '\\\\$&');",
      '}',
      '',
      'function patternToRegex(pattern) {',
      "  const normalized = pattern.replaceAll('\\\\', '/');",
      '  const escaped = escapeRegex(normalized)',
      "    .replaceAll('\\\\*\\\\*/', '(?:.*/)?')",
      "    .replaceAll('\\\\*\\\\*', '.*')",
      "    .replaceAll('\\\\*', '[^/]*')",
      "    .replaceAll('\\\\?', '[^/]');",
      "  return new RegExp('^' + escaped + '$');",
      '}',
      '',
      'function walk(dir, out) {',
      '  for (const entry of readdirSync(dir, { withFileTypes: true })) {',
      '    const full = join(dir, entry.name);',
      '    if (entry.isDirectory()) {',
      '      walk(full, out);',
      '    }',
      '    else if (statSync(full).isFile()) {',
      '      out.push(full);',
      '    }',
      '  }',
      '}',
      '',
      'export async function glob({ pattern, path, hidden = true, gitignore = true, cache = true, maxResults = 1000 }) {',
      '  const files = [];',
      '  walk(path, files);',
      '  const regex = patternToRegex(pattern);',
      '  const matches = [];',
      '  for (const file of files) {',
      "    const rel = relative(path, file).split(sep).join('/');",
      '    if (regex.test(rel)) {',
      '      matches.push({ path: rel });',
      '      if (matches.length >= maxResults) {',
      '        break;',
      '      }',
      '    }',
      '  }',
      '  return { matches };',
      '}',
    ]),
  );
  writeTextIfChanged(
    join(nativeAliasRoot, 'xxhash.js'),
    block([
      'export function xxHash32(text, seed = 0) {',
      '  let hash = (seed >>> 0) ^ 0x811c9dc5;',
      '  for (let i = 0; i < text.length; i++) {',
      '    hash ^= text.charCodeAt(i);',
      '    hash = Math.imul(hash, 0x01000193) >>> 0;',
      '  }',
      '  return hash >>> 0;',
      '}',
    ]),
  );
}

function ensureReexportPackage(dirName, packageName, mainJsImport, mainDtsImport, extraFiles = []) {
  const root = join(repoRoot, 'node_modules', '@gsd', dirName);
  mkdirSync(root, { recursive: true });

  const exportsMap = {
    '.': {
      types: './index.d.ts',
      import: './index.js',
    },
  };
  for (const extra of extraFiles) {
    exportsMap[extra.exportPath] = {
      types: `./${extra.fileBase}.d.ts`,
      import: `./${extra.fileBase}.js`,
    };
  }

  writeTextIfChanged(
    join(root, 'package.json'),
    JSON.stringify(
      {
        name: packageName,
        private: true,
        type: 'module',
        exports: exportsMap,
      },
      null,
      2,
    ) + '\n',
  );
  writeTextIfChanged(join(root, 'index.js'), block([`export * from '${mainJsImport}';`]));
  writeTextIfChanged(join(root, 'index.d.ts'), block([`export * from '${mainDtsImport}';`]));

  for (const extra of extraFiles) {
    writeTextIfChanged(join(root, `${extra.fileBase}.js`), block([`export * from '${extra.jsImport}';`]));
    writeTextIfChanged(join(root, `${extra.fileBase}.d.ts`), block([`export * from '${extra.dtsImport}';`]));
  }
}

ensureReexportPackage(
  'pi-agent-core',
  '@gsd/pi-agent-core',
  '../../gsd-pi/packages/pi-agent-core/dist/index.js',
  '../../gsd-pi/packages/pi-agent-core/dist/index.d.ts',
);

ensureReexportPackage(
  'pi-ai',
  '@gsd/pi-ai',
  '../../gsd-pi/packages/pi-ai/dist/index.js',
  '../../gsd-pi/packages/pi-ai/dist/index.d.ts',
  [
    {
      exportPath: './oauth',
      fileBase: 'oauth',
      jsImport: '../../gsd-pi/packages/pi-ai/oauth.js',
      dtsImport: '../../gsd-pi/packages/pi-ai/oauth.d.ts',
    },
    {
      exportPath: './bedrock-provider',
      fileBase: 'bedrock-provider',
      jsImport: '../../gsd-pi/packages/pi-ai/bedrock-provider.js',
      dtsImport: '../../gsd-pi/packages/pi-ai/bedrock-provider.d.ts',
    },
  ],
);

ensureReexportPackage(
  'pi-tui',
  '@gsd/pi-tui',
  '../../gsd-pi/packages/pi-tui/dist/index.js',
  '../../gsd-pi/packages/pi-tui/dist/index.d.ts',
);

patchFile('dist/loader.js', (text) => {
  const marker = '// Fast-path `gsd headless query` before importing the full CLI bootstrap.';
  if (text.includes(marker)) {
    return text;
  }

  const anchor = 'process.env.GSD_BIN_PATH = process.argv[1];\n';
  const insertion = `// Fast-path \`gsd headless query\` before importing the full CLI bootstrap.\n// The query path is read-only and does not need the expensive resource sync,\n// workspace package linking, or CLI startup stack.\nfunction getHeadlessSubcommand(argv) {\n    let seenHeadless = false;\n    for (const arg of argv.slice(2)) {\n        if (arg.startsWith('-')) {\n            continue;\n        }\n        if (!seenHeadless) {\n            if (arg === 'headless') {\n                seenHeadless = true;\n            }\n            continue;\n        }\n        return arg;\n    }\n    return null;\n}\nconst headlessCommand = getHeadlessSubcommand(process.argv);\nif (headlessCommand === 'query') {\n    const { handleQuery } = await import('./headless-query.js');\n    await handleQuery(process.cwd());\n    process.exit(0);\n}\nif (headlessCommand === 'new-milestone') {\n    const { prepareHeadlessMilestoneSkeleton } = await import('./headless-context.js');\n    process.stderr.write('[gsd] headless new-milestone: pre-materializing canonical milestone skeleton...\\n');\n    const preparedMilestoneId = prepareHeadlessMilestoneSkeleton(process.cwd());\n    process.stderr.write(\`[gsd] headless new-milestone: canonical milestone skeleton prepared (\${preparedMilestoneId}).\\n\`);\n}\nconst shouldTraceLoaderCliImport = process.argv.includes('--mode') && process.argv.includes('rpc');\nif (shouldTraceLoaderCliImport) {\n    process.stderr.write('[gsd] loader: importing cli.js...\\n');\n}\nawait import('./cli.js');\nif (shouldTraceLoaderCliImport) {\n    process.stderr.write('[gsd] loader: cli.js imported.\\n');\n}\n`;

  if (!text.includes(anchor)) {
    throw new Error('Unable to patch dist/loader.js: fast-path anchor not found');
  }

  return text.replace(anchor, `${anchor}${insertion}`);
});

patchFile('dist/tool-bootstrap.js', (text) => {
  const marker =
    '// If PATH already exposes a working tool, do not abort RPC bootstrap';
  if (text.includes(marker)) {
    return text;
  }

  const copyBlock =
    '    copyFileSync(sourcePath, targetPath);\n    chmodSync(targetPath, 0o755);\n    return targetPath;\n';
  if (!text.includes(copyBlock)) {
    throw new Error('Unable to patch dist/tool-bootstrap.js: copy fallback block not found');
  }

  let next = text.replace(
    copyBlock,
    '    try {\n        copyFileSync(sourcePath, targetPath);\n        chmodSync(targetPath, 0o755);\n        return targetPath;\n    }\n    catch (error) {\n        // If PATH already exposes a working tool, do not abort RPC bootstrap\n        // just because we could not mirror it into the managed tool dir.\n        if (isRegularFile(sourcePath)) {\n            return null;\n        }\n        throw error;\n    }\n',
  );

  const pushLine = '        provisioned.push(provisionTool(targetDir, tool, sourcePath));\n';
  if (!next.includes(pushLine)) {
    throw new Error('Unable to patch dist/tool-bootstrap.js: provisioned push line not found');
  }

  next = next.replace(
    pushLine,
    '        const provisionedPath = provisionTool(targetDir, tool, sourcePath);\n        if (provisionedPath) {\n            provisioned.push(provisionedPath);\n        }\n',
  );

  return next;
});

patchFile('dist/headless-ui.js', (text) => {
  const marker =
    "// Import the lightweight JSONL reader directly instead of the full pi-coding-agent barrel.";
  if (text.includes(marker)) {
    return text;
  }

  const importLine = "import { attachJsonlLineReader } from '@gsd/pi-coding-agent';\n";
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch dist/headless-ui.js: import anchor not found');
  }

  const replacement =
    `${marker}\nimport { attachJsonlLineReader } from '../packages/pi-coding-agent/dist/modes/rpc/jsonl.js';\n`;
  return text.replace(importLine, replacement);
});

patchFile('dist/headless-context.js', (text) => {
  if (text.includes('prepareHeadlessMilestoneSkeleton')) {
    return text;
  }

  const importLine = "import { readFileSync, mkdirSync } from 'node:fs';\n";
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch dist/headless-context.js: fs import not found');
  }

  let next = text.replace(
    importLine,
    "import { existsSync, mkdirSync, readFileSync, unlinkSync, writeFileSync } from 'node:fs';\nimport { findMilestoneIds, nextMilestoneId } from './resources/extensions/gsd/milestone-ids.js';\nimport { loadEffectiveGSDPreferences } from './resources/extensions/gsd/preferences.js';\nconst HEADLESS_MILESTONE_SEED_FILE = join('runtime', 'headless-milestone-id.txt');\nfunction seedPath(basePath) {\n    return join(basePath, '.gsd', HEADLESS_MILESTONE_SEED_FILE);\n}\nfunction gsdRootDir(basePath) {\n    return join(basePath, '.gsd');\n}\nfunction writeIfMissing(path, content) {\n    if (!existsSync(path) || readFileSync(path, 'utf-8').trim() === '') {\n        writeFileSync(path, content, 'utf-8');\n    }\n}\nfunction buildProjectSkeleton(milestoneId) {\n    return `# Project\\n\\n## What This Is\\n\\nHeadless milestone bootstrap seeded the canonical planning files before the model responded.\\n\\n## Core Value\\n\\nThe first milestone exists on disk before the model fills in the content.\\n\\n## Current State\\n\\nCanonical skeleton seeded; project details and milestone content are pending model fill.\\n\\n## Architecture / Key Patterns\\n\\nHeadless bootstrap writes the canonical files first, then the milestone discussion flow fills them in.\\n\\n## Capability Contract\\n\\nSee \\`.gsd/REQUIREMENTS.md\\` for the explicit capability contract.\\n\\n## Milestone Sequence\\n\\n| ID | Title | Status |\\n|---|---|---|\\n| ${milestoneId} | Seeded milestone | 📋 Next |\\n`;\n}\nfunction buildRequirementsSkeleton() {\n    return `# Requirements\\n\\nThis file is the explicit capability and coverage contract for the project.\\n\\nUse it to track what is actively in scope, what has been validated by completed work, what is intentionally deferred, and what is explicitly out of scope.\\n\\n## Active\\n\\n## Validated\\n\\n## Deferred\\n\\n## Out of Scope\\n\\n## Traceability\\n\\n| ID | Class | Status | Primary owner | Supporting | Proof |\\n|---|---|---|---|---|---|\\n\\n## Coverage Summary\\n\\n- Active requirements: 0\\n- Mapped to slices: 0\\n- Validated: 0\\n- Unmapped active requirements: 0\\n`;\n}\nfunction buildDecisionsSkeleton() {\n    return `# Decisions Register\\n\\n<!-- Append-only. Never edit or remove existing rows. -->\\n\\n| # | When | Scope | Decision | Choice | Rationale | Revisable? | Made By |\\n|---|------|-------|----------|--------|-----------|------------|---------|\\n`;\n}\nfunction buildQueueSkeleton() {\n    return `# Queue\\n\\nAppend-only log of queued milestones.\\n\\n- None yet.\\n`;\n}\nfunction buildMilestoneContextSkeleton(milestoneId) {\n    return `# ${milestoneId}: Seeded milestone\\n\\n## Scope\\n\\nThis milestone was pre-materialized by headless new-milestone before the model responded.\\n\\n## Goals\\n\\n- Provide a concrete milestone record on disk so state derivation can discover it.\\n- Let the model refine this context into the full planning artifact.\\n\\n## Assumptions\\n\\n- Roadmap and slices will be filled in after the initial prompt.\\n- No dependencies are declared yet.\\n`;\n}\nfunction buildStateSkeleton(milestoneId) {\n    const timestamp = new Date().toISOString();\n    return `# GSD State\\n\\n**Active Milestone:** ${milestoneId}: Seeded milestone\\n**Active Slice:** None\\n**Phase:** pre-planning\\n**Next Action:** Plan milestone ${milestoneId}.\\n**Last Updated:** ${timestamp}\\n**Requirements Status:** 0 active · 0 validated · 0 deferred · 0 out of scope\\n\\n## Recent Decisions\\n\\n- None recorded\\n\\n## Blockers\\n\\n- None\\n`;\n}\n",
  );

  const projectBootstrapBlock =
    "/**\n * Bootstrap .gsd/ directory structure for headless new-milestone.\n * Mirrors the bootstrap logic from guided-flow.ts showSmartEntry().\n */\nexport function bootstrapGsdProject(basePath) {\n    const gsdDir = join(basePath, '.gsd');\n    mkdirSync(join(gsdDir, 'milestones'), { recursive: true });\n    mkdirSync(join(gsdDir, 'runtime'), { recursive: true });\n}\n";
  if (!next.includes(projectBootstrapBlock)) {
    throw new Error('Unable to patch dist/headless-context.js: bootstrap block not found');
  }

  next = next.replace(
    projectBootstrapBlock,
    "/**\n * Bootstrap .gsd/ directory structure for headless new-milestone.\n * Mirrors the bootstrap logic from guided-flow.ts showSmartEntry().\n */\nexport function readHeadlessMilestoneSeed(basePath) {\n    const path = seedPath(basePath);\n    if (!existsSync(path)) {\n        return null;\n    }\n    const content = readFileSync(path, 'utf-8').trim();\n    return content || null;\n}\nexport function clearHeadlessMilestoneSeed(basePath) {\n    const path = seedPath(basePath);\n    if (existsSync(path)) {\n        unlinkSync(path);\n    }\n}\nexport function prepareHeadlessMilestoneSkeleton(basePath) {\n    const gsd = gsdRootDir(basePath);\n    const runtimeDir = join(gsd, 'runtime');\n    const milestonesDir = join(gsd, 'milestones');\n    mkdirSync(runtimeDir, { recursive: true });\n    mkdirSync(milestonesDir, { recursive: true });\n    const existingIds = findMilestoneIds(basePath);\n    const uniqueEnabled = !!loadEffectiveGSDPreferences()?.preferences?.unique_milestone_ids;\n    const nextId = nextMilestoneId(existingIds, uniqueEnabled);\n    writeFileSync(seedPath(basePath), `${nextId}\\n`, 'utf-8');\n    mkdirSync(join(milestonesDir, nextId, 'slices'), { recursive: true });\n    writeIfMissing(join(milestonesDir, nextId, `${nextId}-CONTEXT.md`), buildMilestoneContextSkeleton(nextId));\n    writeIfMissing(join(gsd, 'PROJECT.md'), buildProjectSkeleton(nextId));\n    writeIfMissing(join(gsd, 'REQUIREMENTS.md'), buildRequirementsSkeleton());\n    writeIfMissing(join(gsd, 'DECISIONS.md'), buildDecisionsSkeleton());\n    writeIfMissing(join(gsd, 'QUEUE.md'), buildQueueSkeleton());\n    writeIfMissing(join(gsd, 'STATE.md'), buildStateSkeleton(nextId));\n    return nextId;\n}\nexport function bootstrapGsdProject(basePath) {\n    const root = gsdRootDir(basePath);\n    mkdirSync(join(root, 'milestones'), { recursive: true });\n    mkdirSync(join(root, 'runtime'), { recursive: true });\n}\n",
  );

  const headlessSeedBlock =
    '    const existingIds = findMilestoneIds(basePath);\n    const uniqueEnabled = !!loadEffectiveGSDPreferences()?.preferences?.unique_milestone_ids;\n    const nextId = nextMilestoneId(existingIds, uniqueEnabled);\n    writeFileSync(seedPath(basePath), `${nextId}\\n`, \'utf-8\');\n';
  if (next.includes(headlessSeedBlock)) {
    next = next.replace(
      headlessSeedBlock,
      '    const seededNextId = readHeadlessMilestoneSeed(basePath);\n    let nextId;\n    if (seededNextId) {\n        nextId = seededNextId;\n    }\n    else {\n        const existingIds = findMilestoneIds(basePath);\n        const uniqueEnabled = !!loadEffectiveGSDPreferences()?.preferences?.unique_milestone_ids;\n        nextId = nextMilestoneId(existingIds, uniqueEnabled);\n        writeFileSync(seedPath(basePath), `${nextId}\\n`, \'utf-8\');\n    }\n',
    );
  }

  return next;
});

patchFile('dist/resources/extensions/gsd/guided-flow.js', (text) => {
  if (text.includes('headlessMilestoneSeedPath(basePath)')) {
    return text;
  }

  const seedHelpersMarker =
    'function nextMilestoneIdReserved(existingIds, uniqueEnabled) {\n    const allIds = [...new Set([...existingIds, ...getReservedMilestoneIds()])];\n    const id = nextMilestoneId(allIds, uniqueEnabled);\n    reserveMilestoneId(id);\n    return id;\n}\n';
  if (!text.includes(seedHelpersMarker)) {
    throw new Error('Unable to patch guided-flow.js: reservation block not found');
  }

  let next = text.replace(
    seedHelpersMarker,
    'function nextMilestoneIdReserved(existingIds, uniqueEnabled) {\n    const allIds = [...new Set([...existingIds, ...getReservedMilestoneIds()])];\n    const id = nextMilestoneId(allIds, uniqueEnabled);\n    reserveMilestoneId(id);\n    return id;\n}\nfunction headlessMilestoneSeedPath(basePath) {\n    return join(gsdRoot(basePath), "runtime", "headless-milestone-id.txt");\n}\nfunction readHeadlessMilestoneSeed(basePath) {\n    const path = headlessMilestoneSeedPath(basePath);\n    if (!existsSync(path)) {\n        return null;\n    }\n    const content = readFileSync(path, "utf-8").trim();\n    return content || null;\n}\nfunction clearHeadlessMilestoneSeed(basePath) {\n    const path = headlessMilestoneSeedPath(basePath);\n    if (existsSync(path)) {\n        unlinkSync(path);\n    }\n}\n',
  );

  const generationBlock =
    '    // Generate next milestone ID\n    const existingIds = findMilestoneIds(basePath);\n    const prefs = loadEffectiveGSDPreferences();\n    const nextId = nextMilestoneIdReserved(existingIds, prefs?.preferences?.unique_milestone_ids ?? false);\n';
  if (!next.includes(generationBlock)) {
    throw new Error('Unable to patch guided-flow.js: new-milestone ID block not found');
  }

  next = next.replace(
    generationBlock,
    '    // Reuse the milestone ID prepared by the headless parent when available.\n    const seededNextId = readHeadlessMilestoneSeed(basePath);\n    let nextId;\n    if (seededNextId) {\n        nextId = seededNextId;\n        reserveMilestoneId(nextId);\n        clearHeadlessMilestoneSeed(basePath);\n    }\n    else {\n        // Generate next milestone ID\n        const existingIds = findMilestoneIds(basePath);\n        const prefs = loadEffectiveGSDPreferences();\n        nextId = nextMilestoneIdReserved(existingIds, prefs?.preferences?.unique_milestone_ids ?? false);\n    }\n',
  );

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/model-resolver.js', (text) => {
  const marker =
    '// Keep model-resolver.js focused on pure pattern matching so startup does not pull pi-ai models.';
  if (text.includes(marker) || text.includes('function modelsAreEqual(a, b)')) {
    return text;
  }

  const importLine = 'import { modelsAreEqual } from "@gsd/pi-ai";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch model-resolver.js: modelsAreEqual import not found');
  }

  const replacement =
    `${marker}\nfunction modelsAreEqual(a, b) {\n    if (!a || !b)\n        return false;\n    return a.id === b.id && a.provider === b.provider;\n}\n`;
  return text.replace(importLine, replacement);
});

patchFile('packages/pi-coding-agent/dist/cli/args.js', (text) => {
  const marker = '// Keep CLI argument parsing lightweight by avoiding the full built-in tool catalog at import time.';
  if (text.includes(marker) || text.includes('VALID_TOOL_NAMES = ["read", "bash", "edit", "write", "lsp", "grep", "find", "ls"]')) {
    return text;
  }

  const importLine = 'import { allTools } from "../core/tools/index.js";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch cli/args.js: allTools import not found');
  }

  let next = text.replace(
    importLine,
    `${marker}\nconst VALID_TOOL_NAMES = ["read", "bash", "edit", "write", "lsp", "grep", "find", "ls"];\n`,
  );

  const toolsBlock =
    '            for (const name of toolNames) {\n                if (name in allTools) {\n                    validTools.push(name);\n                }\n                else {\n                    console.error(chalk.yellow(`Warning: Unknown tool "${name}". Valid tools: ${Object.keys(allTools).join(", ")}`));\n                }\n            }\n';
  if (!next.includes(toolsBlock)) {
    throw new Error('Unable to patch cli/args.js: --tools validation block not found');
  }

  next = next.replace(
    toolsBlock,
    '            for (const name of toolNames) {\n                if (VALID_TOOL_NAMES.includes(name)) {\n                    validTools.push(name);\n                }\n                else {\n                    console.error(chalk.yellow(`Warning: Unknown tool "${name}". Valid tools: ${VALID_TOOL_NAMES.join(", ")}`));\n                }\n            }\n',
  );

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/resource-loader.js', (text) => {
  const marker =
    '// Lazy-load extension loader dependencies so importing DefaultResourceLoader stays cheap.';
  if (
    text.includes(marker) ||
    (text.includes('loadExtensionsLoaderModule') && text.includes('loadThemeModule'))
  ) {
    return text;
  }

  const importLine =
    'import { createExtensionRuntime, loadExtensionFromFactory, loadExtensions } from "./extensions/loader.js";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch core/resource-loader.js: extension loader import not found');
  }

  let next = text.replace(
    importLine,
    `${marker}\nlet extensionsLoaderModulePromise;\nasync function loadExtensionsLoaderModule() {\n    if (!extensionsLoaderModulePromise) {\n        extensionsLoaderModulePromise = import("./extensions/loader.js");\n    }\n    return extensionsLoaderModulePromise;\n}\n`,
  );

  const runtimeLine =
    '        this.extensionsResult = { extensions: [], errors: [], runtime: createExtensionRuntime() };\n';
  if (!next.includes(runtimeLine)) {
    throw new Error(
      'Unable to patch core/resource-loader.js: extension runtime initialization not found',
    );
  }
  next = next.replace(runtimeLine, '        this.extensionsResult = { extensions: [], errors: [], runtime: null };\n');

  const reloadLine = '        const extensionsResult = await loadExtensions(extensionPaths, this.cwd, this.eventBus);\n';
  if (!next.includes(reloadLine)) {
    throw new Error('Unable to patch core/resource-loader.js: loadExtensions call not found');
  }
  next = next.replace(
    reloadLine,
    '        const { loadExtensions } = await loadExtensionsLoaderModule();\n        const extensionsResult = await loadExtensions(extensionPaths, this.cwd, this.eventBus);\n',
  );

  const factoryLine = '    async loadExtensionFactories(runtime) {\n';
  if (!next.includes(factoryLine)) {
    throw new Error(
      'Unable to patch core/resource-loader.js: loadExtensionFactories signature not found',
    );
  }
  next = next.replace(
    factoryLine,
    '    async loadExtensionFactories(runtime) {\n        const { loadExtensionFromFactory } = await loadExtensionsLoaderModule();\n',
  );

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/resource-loader.js', (text) => {
  const marker =
    '// Lazy-load theme loading so importing DefaultResourceLoader stays cheap.';
  if (
    text.includes(marker) ||
    (text.includes('loadThemeModule') && text.includes('async loadThemeFromFile'))
  ) {
    return text;
  }

  const importLine = 'import { loadThemeFromPath } from "../modes/interactive/theme/theme.js";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch core/resource-loader.js: theme import not found');
  }

  let next = text.replace(
    importLine,
    `${marker}\nlet themeModulePromise;\nasync function loadThemeModule() {\n    if (!themeModulePromise) {\n        themeModulePromise = import("../modes/interactive/theme/theme.js");\n    }\n    return themeModulePromise;\n}\n`,
  );

  const extendLine = '            this.updateThemesFromPaths(this.lastThemePaths, themePaths);\n';
  if (!next.includes(extendLine)) {
    throw new Error(
      'Unable to patch core/resource-loader.js: extendResources theme call not found',
    );
  }
  next = next.replace(extendLine, '            void this.updateThemesFromPaths(this.lastThemePaths, themePaths);\n');

  const reloadLine = '        this.updateThemesFromPaths(themePaths);\n';
  if (!next.includes(reloadLine)) {
    throw new Error('Unable to patch core/resource-loader.js: reload theme call not found');
  }
  next = next.replace(reloadLine, '        await this.updateThemesFromPaths(themePaths);\n');

  const updateSignature = '    updateThemesFromPaths(themePaths, extensionPaths = []) {\n';
  if (!next.includes(updateSignature)) {
    throw new Error(
      'Unable to patch core/resource-loader.js: updateThemesFromPaths signature not found',
    );
  }
  next = next.replace(
    updateSignature,
    '    async updateThemesFromPaths(themePaths, extensionPaths = []) {\n',
  );

  const loadedLine = '            const loaded = this.loadThemes(themePaths, false);\n';
  if (!next.includes(loadedLine)) {
    throw new Error('Unable to patch core/resource-loader.js: loadThemes call not found');
  }
  next = next.replace(loadedLine, '            const loaded = await this.loadThemes(themePaths, false);\n');

  const loadThemesSignature = '    loadThemes(paths, includeDefaults = true) {\n';
  if (!next.includes(loadThemesSignature)) {
    throw new Error('Unable to patch core/resource-loader.js: loadThemes signature not found');
  }
  next = next.replace(loadThemesSignature, '    async loadThemes(paths, includeDefaults = true) {\n');

  const defaultDirLine = '                this.loadThemesFromDir(dir, themes, diagnostics);\n';
  if (!next.includes(defaultDirLine)) {
    throw new Error(
      'Unable to patch core/resource-loader.js: default theme directory call not found',
    );
  }
  next = next.replace(defaultDirLine, '                await this.loadThemesFromDir(dir, themes, diagnostics);\n');

  const dirLoadLine = '                    this.loadThemesFromDir(resolved, themes, diagnostics);\n';
  if (!next.includes(dirLoadLine)) {
    throw new Error('Unable to patch core/resource-loader.js: theme dir load call not found');
  }
  next = next.replace(dirLoadLine, '                    await this.loadThemesFromDir(resolved, themes, diagnostics);\n');

  const fileLoadLine = '                    this.loadThemeFromFile(resolved, themes, diagnostics);\n';
  if (!next.includes(fileLoadLine)) {
    throw new Error('Unable to patch core/resource-loader.js: theme file load call not found');
  }
  next = next.replace(fileLoadLine, '                    await this.loadThemeFromFile(resolved, themes, diagnostics);\n');

  const dirSignature = '    loadThemesFromDir(dir, themes, diagnostics) {\n';
  if (!next.includes(dirSignature)) {
    throw new Error('Unable to patch core/resource-loader.js: loadThemesFromDir signature not found');
  }
  next = next.replace(dirSignature, '    async loadThemesFromDir(dir, themes, diagnostics) {\n');

  const dirFileLoadLine = '                this.loadThemeFromFile(join(dir, entry.name), themes, diagnostics);\n';
  if (!next.includes(dirFileLoadLine)) {
    throw new Error(
      'Unable to patch core/resource-loader.js: loadThemesFromDir file load call not found',
    );
  }
  next = next.replace(
    dirFileLoadLine,
    '                await this.loadThemeFromFile(join(dir, entry.name), themes, diagnostics);\n',
  );

  const fileSignature = '    loadThemeFromFile(filePath, themes, diagnostics) {\n';
  if (!next.includes(fileSignature)) {
    throw new Error('Unable to patch core/resource-loader.js: loadThemeFromFile signature not found');
  }
  next = next.replace(fileSignature, '    async loadThemeFromFile(filePath, themes, diagnostics) {\n');

  const themeLoadLine = '            themes.push(loadThemeFromPath(filePath));\n';
  if (!next.includes(themeLoadLine)) {
    throw new Error('Unable to patch core/resource-loader.js: loadThemeFromPath call not found');
  }
  next = next.replace(
    themeLoadLine,
    '            const { loadThemeFromPath } = await loadThemeModule();\n            themes.push(loadThemeFromPath(filePath));\n',
  );

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/agent-session.js', (text) => {
  const marker =
    '// Import pi-ai helpers directly and lazy-load theme, prompt templates, and bash execution only when needed.';
  if (
    text.includes(marker) ||
    (text.includes('loadBashExecutorModule') && text.includes('loadPromptTemplatesModule'))
  ) {
    return text;
  }

  const bashImport =
    'import { executeBash as executeBashCommand, executeBashWithOperations } from "./bash-executor.js";\n';
  const promptTemplatesImport = 'import { expandPromptTemplate } from "./prompt-templates.js";\n';
  const apiImport = 'import { modelsAreEqual, resetApiProviders, supportsXhigh } from "@gsd/pi-ai";\n';
  const themeImport = 'import { theme } from "../modes/interactive/theme/theme.js";\n';
  const extensionsImport =
    'import { ExtensionRunner, wrapRegisteredTools, } from "./extensions/index.js";\n';

  let next = text;
  if (next.includes(bashImport)) {
    next = next.replace(
      bashImport,
      `${marker}\nlet bashExecutorModulePromise;\nasync function loadBashExecutorModule() {\n    if (!bashExecutorModulePromise) {\n        bashExecutorModulePromise = import("./bash-executor.js");\n    }\n    return bashExecutorModulePromise;\n}\nlet promptTemplatesModulePromise;\nasync function loadPromptTemplatesModule() {\n    if (!promptTemplatesModulePromise) {\n        promptTemplatesModulePromise = import("./prompt-templates.js");\n    }\n    return promptTemplatesModulePromise;\n}\n`,
    );
  } else if (!next.includes('loadBashExecutorModule') || !next.includes('loadPromptTemplatesModule')) {
    throw new Error('Unable to patch agent-session.js: bash/prompt template imports not found');
  }
  if (next.includes(promptTemplatesImport)) {
    next = next.replace(promptTemplatesImport, '');
  }
  if (next.includes(apiImport)) {
    next = next.replace(
      apiImport,
      'import { clearApiProviders as resetApiProviders } from "../../../pi-ai/dist/api-registry.js";\nimport { modelsAreEqual, supportsXhigh } from "../../../pi-ai/dist/models.js";\n',
    );
  }
  if (next.includes(themeImport)) {
    next = next.replace(
      themeImport,
      `let themeModulePromise;\nasync function loadThemeModule() {\n    if (!themeModulePromise) {\n        themeModulePromise = import("../modes/interactive/theme/theme.js");\n    }\n    return themeModulePromise;\n}\n`,
    );
  }
  if (next.includes(extensionsImport)) {
    next = next.replace(
      extensionsImport,
      'import { ExtensionRunner } from "./extensions/runner.js";\nimport { wrapRegisteredTools } from "./extensions/wrapper.js";\n',
    );
  }

  const exportHtmlLine = '        const themeName = this.settingsManager.getTheme();\n';
  const exportHtmlBlock =
    '        const themeName = this.settingsManager.getTheme();\n        const { theme } = await loadThemeModule();\n';
  if (next.includes(exportHtmlBlock)) {
    // already patched
  } else if (!next.includes(exportHtmlLine)) {
    throw new Error('Unable to patch agent-session.js: exportToHtml anchor not found');
  } else {
    next = next.replace(exportHtmlLine, exportHtmlBlock);
  }

  const expandPromptLine = '            expandedText = expandPromptTemplate(expandedText, [...this.promptTemplates]);\n';
  if (!next.includes(expandPromptLine)) {
    throw new Error('Unable to patch agent-session.js: prompt template expansion anchor not found');
  }
  next = next.replace(
    expandPromptLine,
    '            expandedText = (await loadPromptTemplatesModule()).expandPromptTemplate(expandedText, [...this.promptTemplates]);\n',
  );

  const steerPromptLine = '        expandedText = expandPromptTemplate(expandedText, [...this.promptTemplates]);\n';
  if (!next.includes(steerPromptLine)) {
    throw new Error('Unable to patch agent-session.js: steer prompt template anchor not found');
  }
  next = next.replace(
    steerPromptLine,
    '        expandedText = (await loadPromptTemplatesModule()).expandPromptTemplate(expandedText, [...this.promptTemplates]);\n',
  );

  const followUpPromptLine = '        expandedText = expandPromptTemplate(expandedText, [...this.promptTemplates]);\n';
  if (!next.includes(followUpPromptLine)) {
    throw new Error('Unable to patch agent-session.js: follow-up prompt template anchor not found');
  }
  next = next.replace(
    followUpPromptLine,
    '        expandedText = (await loadPromptTemplatesModule()).expandPromptTemplate(expandedText, [...this.promptTemplates]);\n',
  );

  const executeBashBlock =
    '            const result = options?.operations\n                ? await executeBashWithOperations(resolvedCommand, process.cwd(), options.operations, {\n                    onChunk,\n                    signal: this._bashAbortController.signal,\n                })\n                : await executeBashCommand(resolvedCommand, {\n                    onChunk,\n                    signal: this._bashAbortController.signal,\n                    loginShell: options?.loginShell,\n                });\n';
  if (!next.includes(executeBashBlock)) {
    throw new Error('Unable to patch agent-session.js: bash execution anchor not found');
  }
  next = next.replace(
    executeBashBlock,
    '            const { executeBash: executeBashCommand, executeBashWithOperations } = await loadBashExecutorModule();\n            const result = options?.operations\n                ? await executeBashWithOperations(resolvedCommand, process.cwd(), options.operations, {\n                    onChunk,\n                    signal: this._bashAbortController.signal,\n                })\n                : await executeBashCommand(resolvedCommand, {\n                    onChunk,\n                    signal: this._bashAbortController.signal,\n                    loginShell: options?.loginShell,\n                });\n',
  );

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/compaction-orchestrator.js', (text) => {
  const marker =
    '// Import isContextOverflow directly so compaction orchestration does not pull the pi-ai barrel.';
  if (
    text.includes(marker) ||
    text.includes('from "../../../pi-ai/dist/utils/overflow.js";')
  ) {
    return text;
  }

  const importLine = 'import { isContextOverflow } from "@gsd/pi-ai";\n';
  if (!text.includes(importLine)) {
    throw new Error(
      'Unable to patch compaction-orchestrator.js: isContextOverflow import not found',
    );
  }

  return text.replace(
    importLine,
    `${marker}\nimport { isContextOverflow } from "../../../pi-ai/dist/utils/overflow.js";\n`,
  );
});

patchFile('packages/pi-coding-agent/dist/core/extensions/runner.js', (text) => {
  const marker =
    '// Inline the theme proxy so importing ExtensionRunner does not pull the full theme module.';
  if (
    text.includes(marker) ||
    text.includes('Symbol.for("@gsd/pi-coding-agent:theme")')
  ) {
    return text;
  }

  const importLine = 'import { theme } from "../../modes/interactive/theme/theme.js";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch extensions/runner.js: theme import not found');
  }

  return text.replace(
    importLine,
    `${marker}\nconst THEME_KEY = Symbol.for("@gsd/pi-coding-agent:theme");\nconst theme = new Proxy({}, {\n    get(_target, prop) {\n        const t = globalThis[THEME_KEY];\n        if (!t)\n            throw new Error("Theme not initialized. Call initTheme() first.");\n        return t[prop];\n    },\n});\n`,
  );
});

patchFile('packages/pi-coding-agent/dist/core/compaction/compaction.js', (text) => {
  const marker =
    '// Lazy-load completeSimple so compaction does not pull the pi-ai stream bootstrap.';
  if (text.includes(marker) || text.includes('loadCompleteSimpleModule')) {
    return text;
  }

  const importLine = 'import { completeSimple } from "@gsd/pi-ai";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch compaction.js: completeSimple import not found');
  }

  let next = text.replace(
    importLine,
    `${marker}\nlet piAiStreamModulePromise;\nasync function loadCompleteSimpleModule() {\n    if (!piAiStreamModulePromise) {\n        piAiStreamModulePromise = import("../../../../pi-ai/dist/stream.js");\n    }\n    return piAiStreamModulePromise;\n}\n`,
  );

  const summaryLine = '    const complete = _completeFn ?? completeSimple;\n';
  if (!next.includes(summaryLine)) {
    throw new Error('Unable to patch compaction.js: generateSummary complete anchor not found');
  }
  next = next.replace(
    summaryLine,
    '    const complete = _completeFn ?? (await loadCompleteSimpleModule()).completeSimple;\n',
  );

  const singlePassSignature =
    'async function singlePassSummary(currentMessages, model, reserveTokens, apiKey, signal, customInstructions, previousSummary, complete = completeSimple) {\n';
  if (!next.includes(singlePassSignature)) {
    throw new Error('Unable to patch compaction.js: singlePassSummary signature not found');
  }
  next = next.replace(
    singlePassSignature,
    'async function singlePassSummary(currentMessages, model, reserveTokens, apiKey, signal, customInstructions, previousSummary, complete) {\n',
  );

  const completeCall =
    '    const response = await complete(model, { systemPrompt: SUMMARIZATION_SYSTEM_PROMPT, messages: createSummarizationMessage(promptText) }, completionOptions);\n';
  if (!next.includes(completeCall)) {
    throw new Error('Unable to patch compaction.js: complete call not found');
  }
  next = next.replace(
    completeCall,
    '    const completeFn = complete ?? (await loadCompleteSimpleModule()).completeSimple;\n    const response = await completeFn(model, { systemPrompt: SUMMARIZATION_SYSTEM_PROMPT, messages: createSummarizationMessage(promptText) }, completionOptions);\n',
  );

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/compaction/branch-summarization.js', (text) => {
  const marker =
    '// Lazy-load completeSimple so branch summarization does not pull the pi-ai stream bootstrap.';
  if (text.includes(marker) || text.includes('loadCompleteSimpleModule')) {
    return text;
  }

  const importLine = 'import { completeSimple } from "@gsd/pi-ai";\n';
  if (!text.includes(importLine)) {
    throw new Error(
      'Unable to patch branch-summarization.js: completeSimple import not found',
    );
  }

  let next = text.replace(
    importLine,
    `${marker}\nlet piAiStreamModulePromise;\nasync function loadCompleteSimpleModule() {\n    if (!piAiStreamModulePromise) {\n        piAiStreamModulePromise = import("../../../../pi-ai/dist/stream.js");\n    }\n    return piAiStreamModulePromise;\n}\n`,
  );

  const responseLine = '    const response = await completeSimple(model, { systemPrompt: SUMMARIZATION_SYSTEM_PROMPT, messages: createSummarizationMessage(promptText) }, { apiKey, signal, maxTokens: 2048 });\n';
  if (!next.includes(responseLine)) {
    throw new Error('Unable to patch branch-summarization.js: completeSimple call not found');
  }
  next = next.replace(
    responseLine,
    '    const { completeSimple } = await loadCompleteSimpleModule();\n    const response = await completeSimple(model, { systemPrompt: SUMMARIZATION_SYSTEM_PROMPT, messages: createSummarizationMessage(promptText) }, { apiKey, signal, maxTokens: 2048 });\n',
  );

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/retry-handler.js', (text) => {
  const marker =
    '// Import isContextOverflow directly so retry handling does not pull the pi-ai barrel.';
  if (text.includes(marker) || text.includes('from "../../../pi-ai/dist/utils/overflow.js";')) {
    return text;
  }

  const importLine = 'import { isContextOverflow } from "@gsd/pi-ai";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch retry-handler.js: isContextOverflow import not found');
  }

  return text.replace(
    importLine,
    `${marker}\nimport { isContextOverflow } from "../../../pi-ai/dist/utils/overflow.js";\n`,
  );
});

patchFile('packages/pi-coding-agent/dist/core/export-html/index.js', (text) => {
  const marker =
    '// Lazy-load theme helpers so HTML export does not pull the theme subsystem at import time.';
  if (text.includes(marker) || text.includes('loadThemeModule')) {
    return text;
  }

  const importLine =
    'import { getResolvedThemeColors, getThemeExportColors } from "../../modes/interactive/theme/theme.js";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch export-html/index.js: theme import not found');
  }

  let next = text.replace(
    importLine,
    `${marker}\nlet themeModulePromise;\nasync function loadThemeModule() {\n    if (!themeModulePromise) {\n        themeModulePromise = import("../../modes/interactive/theme/theme.js");\n    }\n    return themeModulePromise;\n}\n`,
  );

  const themeVarsSignature = 'function generateThemeVars(themeName) {\n';
  if (!next.includes(themeVarsSignature)) {
    throw new Error('Unable to patch export-html/index.js: generateThemeVars signature not found');
  }
  next = next.replace(themeVarsSignature, 'async function generateThemeVars(themeName) {\n');

  const themeVarsCall = '    const colors = getResolvedThemeColors(themeName);\n';
  if (!next.includes(themeVarsCall)) {
    throw new Error('Unable to patch export-html/index.js: getResolvedThemeColors call not found');
  }
  next = next.replace(
    themeVarsCall,
    '    const { getResolvedThemeColors, getThemeExportColors } = await loadThemeModule();\n    const colors = getResolvedThemeColors(themeName);\n',
  );

  const htmlSignature = 'function generateHtml(sessionData, themeName) {\n';
  if (!next.includes(htmlSignature)) {
    throw new Error('Unable to patch export-html/index.js: generateHtml signature not found');
  }
  next = next.replace(htmlSignature, 'async function generateHtml(sessionData, themeName) {\n');

  const htmlThemeVarsCall = '    const themeVars = generateThemeVars(themeName);\n';
  if (!next.includes(htmlThemeVarsCall)) {
    throw new Error('Unable to patch export-html/index.js: generateThemeVars call not found');
  }
  next = next.replace(
    htmlThemeVarsCall,
    '    const themeVars = await generateThemeVars(themeName);\n    const { getResolvedThemeColors } = await loadThemeModule();\n',
  );

  const sessionHtmlCall = '    const html = generateHtml(sessionData, opts.themeName);\n';
  if (!next.includes(sessionHtmlCall)) {
    throw new Error('Unable to patch export-html/index.js: exportSessionToHtml call not found');
  }
  next = next.replace(sessionHtmlCall, '    const html = await generateHtml(sessionData, opts.themeName);\n');

  const fileHtmlCall = '    const html = generateHtml(sessionData, opts.themeName);\n';
  if (!next.includes(fileHtmlCall)) {
    throw new Error('Unable to patch export-html/index.js: exportFromFile call not found');
  }
  next = next.replace(fileHtmlCall, '    const html = await generateHtml(sessionData, opts.themeName);\n');

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/tools/index.js', (text) => {
  const marker =
    '// Lazy-load the LSP tool so importing the tool catalog does not pull the entire LSP stack.';
  if (
    text.includes('loadBashToolModule') &&
    text.includes('loadEditToolModule') &&
    text.includes('loadLspToolModule')
  ) {
    return text;
  }

  const exportLine = 'export { createLspTool, lspSchema, lspTool, } from "../lsp/index.js";\n';
  const importLine = 'import { createLspTool, lspTool } from "../lsp/index.js";\n';
  if (!text.includes(exportLine) || !text.includes(importLine)) {
    throw new Error('Unable to patch tools/index.js: LSP import/export anchors not found');
  }

  const replacement = `import { DEFAULT_MAX_BYTES, DEFAULT_MAX_LINES, formatSize, truncateHead, truncateLine, truncateTail, } from "./truncate.js";\nimport { Type } from "@sinclair/typebox";\n${marker}\nexport { lspSchema } from "../lsp/types.js";\nimport { lspSchema } from "../lsp/types.js";\nconst bashSchema = Type.Object({\n    command: Type.String({ description: "Bash command to execute" }),\n    timeout: Type.Optional(Type.Number({ description: "Timeout in seconds (optional, no default timeout)" })),\n});\nconst editSchema = Type.Object({\n    path: Type.String({ description: "Path to the file to edit (relative or absolute)" }),\n    oldText: Type.String({ description: "Exact text to find and replace (must match exactly)" }),\n    newText: Type.String({ description: "New text to replace the old text with" }),\n});\nfunction endsWithBackgroundOperator(fragment) {\n    const stripped = fragment.replace(/'[^']*'/g, "''");\n    return /(?<!&)&\\s*(?:disown\\s*)?(?:#.*)?$/.test(stripped.trim());\n}\nfunction hasOutputRedirect(segment) {\n    const stripped = segment.replace(/'[^']*'/g, "''");\n    return /(?<!\\d)(?:>>?|&>|>&|\\|)/.test(stripped);\n}\nexport function rewriteBackgroundCommand(command) {\n    if (!command.includes("&"))\n        return { command, rewritten: false };\n    const segments = command.split(/(?<=[;\\n])/);\n    let anyRewritten = false;\n    const rewrittenSegments = segments.map((segment) => {\n        if (!endsWithBackgroundOperator(segment))\n            return segment;\n        if (hasOutputRedirect(segment))\n            return segment;\n        anyRewritten = true;\n        return segment.replace(/(?<!&)(&\\s*(?:disown\\s*)?(?:#.*)?)$/, ">\\/dev\\/null 2>&1 $1");\n    });\n    if (!anyRewritten)\n        return { command, rewritten: false };\n    return { command: rewrittenSegments.join(""), rewritten: true };\n}\nlet bashToolModulePromise;\nasync function loadBashToolModule() {\n    if (!bashToolModulePromise) {\n        bashToolModulePromise = import("./bash.js");\n    }\n    return bashToolModulePromise;\n}\nlet editToolModulePromise;\nasync function loadEditToolModule() {\n    if (!editToolModulePromise) {\n        editToolModulePromise = import("./edit.js");\n    }\n    return editToolModulePromise;\n}\nfunction createLazyBashTool(cwd, options) {\n    let resolvedToolPromise;\n    const getTool = async () => {\n        if (!resolvedToolPromise) {\n            resolvedToolPromise = loadBashToolModule().then((module) => module.createBashTool(cwd, options));\n        }\n        return resolvedToolPromise;\n    };\n    return {\n        name: "bash",\n        label: "bash",\n        description: \`Execute a bash command in the current working directory. Returns stdout and stderr. Output is truncated to last \${DEFAULT_MAX_LINES} lines or \${DEFAULT_MAX_BYTES / 1024}KB (whichever is hit first). If truncated, full output is saved to a temp file. Optionally provide a timeout in seconds.\`,\n        parameters: bashSchema,\n        execute: async (...args) => (await getTool()).execute(...args),\n    };\n}\nfunction createLazyEditTool(cwd, options) {\n    let resolvedToolPromise;\n    const getTool = async () => {\n        if (!resolvedToolPromise) {\n            resolvedToolPromise = loadEditToolModule().then((module) => module.createEditTool(cwd, options));\n        }\n        return resolvedToolPromise;\n    };\n    return {\n        name: "edit",\n        label: "edit",\n        description: "Edit a file by replacing exact text. The oldText must match exactly (including whitespace). Use this for precise, surgical edits.",\n        parameters: editSchema,\n        execute: async (...args) => (await getTool()).execute(...args),\n    };\n}\nexport function createBashTool(cwd, options) {\n    return createLazyBashTool(cwd, options);\n}\nexport const bashTool = createLazyBashTool(process.cwd());\nexport function createEditTool(cwd, options) {\n    return createLazyEditTool(cwd, options);\n}\nexport const editTool = createLazyEditTool(process.cwd());\nlet lspToolModulePromise;\nasync function loadLspToolModule() {\n    if (!lspToolModulePromise) {\n        lspToolModulePromise = import("../lsp/index.js");\n    }\n    return lspToolModulePromise;\n}\nfunction createLazyLspTool(cwd) {\n    return {\n        name: "lsp",\n        label: "LSP",\n        description: "Language Server Protocol tool",\n        parameters: lspSchema,\n        async execute(...args) {\n            const module = await loadLspToolModule();\n            return module.createLspTool(cwd).execute(...args);\n        },\n    };\n}\nexport function createLspTool(cwd) {\n    return createLazyLspTool(cwd);\n}\nexport const lspTool = createLazyLspTool(process.cwd());\n`;
  return text.replace(exportLine + '\n' + importLine, replacement);
});

patchFile('packages/pi-coding-agent/dist/core/tools/find.js', (text) => {
  const marker =
    '// Lazy-load @gsd/native/glob so importing the find tool does not pull the native glob binding during bootstrap.';
  if (text.includes(marker) || text.includes('loadNativeGlobModule')) {
    return text;
  }

  const importLine = 'import { glob as nativeGlob } from "@gsd/native/glob";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch find.js: native glob import not found');
  }

  let next = text.replace(
    importLine,
    `${marker}\nlet nativeGlobModulePromise;\nasync function loadNativeGlobModule() {\n    if (!nativeGlobModulePromise) {\n        nativeGlobModulePromise = import("@gsd/native/glob");\n    }\n    return nativeGlobModulePromise;\n}\n`,
  );
  const globCall = '                        const globResult = await nativeGlob({\n';
  if (!next.includes(globCall)) {
    throw new Error('Unable to patch find.js: native glob call not found');
  }
  next = next.replace(
    globCall,
    '                        const { glob: nativeGlob } = await loadNativeGlobModule();\n                        const globResult = await nativeGlob({\n',
  );
  return next;
});

patchFile('packages/pi-coding-agent/dist/core/tools/write.js', (text) => {
  const marker =
    '// Lazy-load lsp client notifications so importing the write tool does not pull the LSP client at startup.';
  if (text.includes(marker) || text.includes('loadNotifyFileChangedModule')) {
    return text;
  }

  const importLine = 'import { notifyFileChanged } from "../lsp/client.js";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch write.js: notifyFileChanged import not found');
  }

  let next = text.replace(
    importLine,
    `${marker}\nlet notifyFileChangedModulePromise;\nasync function loadNotifyFileChangedModule() {\n    if (!notifyFileChangedModulePromise) {\n        notifyFileChangedModulePromise = import("../lsp/client.js");\n    }\n    return notifyFileChangedModulePromise;\n}\n`,
  );
  const notifyCall = '                        await ops.writeFile(absolutePath, content);\n                        try {\n                            notifyFileChanged(absolutePath);\n';
  if (!next.includes(notifyCall)) {
    throw new Error('Unable to patch write.js: notifyFileChanged call not found');
  }
  next = next.replace(
    notifyCall,
    '                        await ops.writeFile(absolutePath, content);\n                        try {\n                            const { notifyFileChanged } = await loadNotifyFileChangedModule();\n                            notifyFileChanged(absolutePath);\n',
  );
  return next;
});

patchFile('packages/pi-coding-agent/dist/modes/rpc/rpc-mode.js', (text) => {
  const marker =
    '// Lazy-load InteractiveMode so RPC startup does not pull the full TUI stack unless needed.';
  if (text.includes(marker) || text.includes('loadInteractiveModeModule')) {
    return text;
  }

  const importLine = 'import { InteractiveMode } from "../interactive/interactive-mode.js";\n';
  if (!text.includes(importLine)) {
    throw new Error('Unable to patch rpc-mode.js: InteractiveMode import not found');
  }

  let next = text.replace(
    importLine,
    `${marker}\nlet interactiveModeModulePromise;\nasync function loadInteractiveModeModule() {\n    if (!interactiveModeModulePromise) {\n        interactiveModeModulePromise = import("../interactive/interactive-mode.js");\n    }\n    return interactiveModeModulePromise;\n}\n`,
  );

  const interactiveModeLine = '            embeddedInteractiveMode = new InteractiveMode(session, {\n';
  if (!next.includes(interactiveModeLine)) {
    throw new Error('Unable to patch rpc-mode.js: InteractiveMode construction not found');
  }
  next = next.replace(
    interactiveModeLine,
    '            const { InteractiveMode } = await loadInteractiveModeModule();\n            embeddedInteractiveMode = new InteractiveMode(session, {\n',
  );

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/sdk.js', (text) => {
  const marker =
    '// Keep sdk.js focused on session bootstrap so RPC startup does not pull the tool catalog.';
  if (
    text.includes(marker) ||
    (text.includes('loadAgentModule') &&
      text.includes('loadAgentSessionModule') &&
      text.includes('loadResourceLoaderModule'))
  ) {
    return text;
  }

  const agentImportLine = 'import { Agent } from "@gsd/pi-agent-core";\n';
  const agentSessionImportLine = 'import { AgentSession } from "./agent-session.js";\n';
  const resourceLoaderImportLine = 'import { DefaultResourceLoader } from "./resource-loader.js";\n';
  let next = text;
  if (next.includes(agentImportLine)) {
    next = next.replace(agentImportLine, '');
  }
  if (next.includes(agentSessionImportLine)) {
    next = next.replace(agentSessionImportLine, '');
  }
  if (next.includes(resourceLoaderImportLine)) {
    next = next.replace(resourceLoaderImportLine, '');
  }

  const helperAnchor =
    'function getDefaultAgentDir() {\n    return getAgentDir();\n}\n';
  if (!next.includes(helperAnchor)) {
    throw new Error('Unable to patch sdk.js: getDefaultAgentDir anchor not found');
  }
  next = next.replace(
    helperAnchor,
    `${helperAnchor}let agentModulePromise;\nasync function loadAgentModule() {\n    if (!agentModulePromise) {\n        agentModulePromise = import("@gsd/pi-agent-core");\n    }\n    return agentModulePromise;\n}\nlet agentSessionModulePromise;\nasync function loadAgentSessionModule() {\n    if (!agentSessionModulePromise) {\n        agentSessionModulePromise = import("./agent-session.js");\n    }\n    return agentSessionModulePromise;\n}\nlet resourceLoaderModulePromise;\nasync function loadResourceLoaderModule() {\n    if (!resourceLoaderModulePromise) {\n        resourceLoaderModulePromise = import("./resource-loader.js");\n    }\n    return resourceLoaderModulePromise;\n}\n`,
  );

  const importLine =
    'import { allTools, bashTool, codingTools, createBashTool, createCodingTools, createEditTool, createFindTool, createGrepTool, createLsTool, createReadOnlyTools, createReadTool, createWriteTool, editTool, findTool, grepTool, hashlineCodingTools, hashlineEditTool, hashlineReadTool, createHashlineCodingTools, createHashlineEditTool, createHashlineReadTool, lsTool, readOnlyTools, readTool, writeTool, } from "./tools/index.js";\n';
  if (!text.includes(importLine)) {
    return next;
  }

  next = next.replace(importLine, `${marker}\n`);

  const exportBlock = `export {\n// Pre-built tools (use process.cwd())\nreadTool, bashTool, editTool, writeTool, grepTool, findTool, lsTool, codingTools, readOnlyTools, allTools as allBuiltInTools, \n// Tool factories (for custom cwd)\ncreateCodingTools, createReadOnlyTools, createReadTool, createBashTool, createEditTool, createWriteTool, createGrepTool, createFindTool, createLsTool, \n// Hashline edit mode\nhashlineCodingTools, hashlineEditTool, hashlineReadTool, createHashlineCodingTools, createHashlineEditTool, createHashlineReadTool, };\n`;
  if (next.includes(exportBlock)) {
    next = next.replace(exportBlock, "");
  }

  const initialActiveToolNames = '    const initialActiveToolNames = options.tools\n        ? options.tools.map((t) => t.name).filter((n) => n in allTools)\n        : defaultActiveToolNames;\n';
  if (!next.includes(initialActiveToolNames)) {
    throw new Error('Unable to patch sdk.js: initialActiveToolNames anchor not found');
  }
  next = next.replace(
    initialActiveToolNames,
    '    const initialActiveToolNames = options.tools\n        ? options.tools.map((t) => t.name)\n        : defaultActiveToolNames;\n',
  );

  const resourceLoaderLine =
    '        resourceLoader = new DefaultResourceLoader({ cwd, agentDir, settingsManager });\n';
  if (next.includes(resourceLoaderLine)) {
    next = next.replace(
      resourceLoaderLine,
      '        const { DefaultResourceLoader } = await loadResourceLoaderModule();\n        resourceLoader = new DefaultResourceLoader({ cwd, agentDir, settingsManager });\n',
    );
  }

  const agentLine = '    agent = new Agent({\n';
  if (next.includes(agentLine)) {
    next = next.replace(agentLine, '    const { Agent } = await loadAgentModule();\n    agent = new Agent({\n');
  }

  const agentSessionLine = '    const session = new AgentSession({\n';
  if (next.includes(agentSessionLine)) {
    next = next.replace(
      agentSessionLine,
      '    const { AgentSession } = await loadAgentSessionModule();\n    const session = new AgentSession({\n',
    );
  }

  return next;
});

patchFile('packages/pi-coding-agent/dist/index.js', (text) => {
  const marker =
    '// Re-export tool factories directly from the tool catalog instead of sdk.js.';
  if (text.includes(marker) || text.includes('from "./core/tools/index.js";')) {
    return text;
  }

  const sdkExport =
    'export { \n// Factory\ncreateAgentSession, createBashTool, \n// Tool factories (for custom cwd)\ncreateCodingTools, createEditTool, createFindTool, createGrepTool, createLsTool, createReadOnlyTools, createReadTool, createWriteTool, \n// Pre-built tools (use process.cwd())\nreadOnlyTools, } from "./core/sdk.js";\n';
  if (!text.includes(sdkExport)) {
    throw new Error('Unable to patch index.js: sdk export block not found');
  }

  return text.replace(
    sdkExport,
    `export { createAgentSession } from "./core/sdk.js";\n${marker}\nexport { createBashTool, createCodingTools, createEditTool, createFindTool, createGrepTool, createLsTool, createReadOnlyTools, createReadTool, createWriteTool, readOnlyTools, } from "./core/tools/index.js";\n`,
  );
});

patchFile('dist/resource-loader.js', (text) => {
  const marker =
    '// Lazy-load pi-coding-agent resource loader dependencies only when buildResourceLoader() runs.';
  const stageMarker =
    '// Emit fine-grained initResources stage markers for headless milestone bootstrap.';
  const fingerprintMarker =
    '// Prefer a cached bundled resource fingerprint file to avoid repeated directory hashing on mounted filesystems.';
  let next = text;

  if (!next.includes(marker)) {
    const importLine =
      "import { DefaultResourceLoader, sortExtensionPaths } from '@gsd/pi-coding-agent';\n";
    const lazyImportBlock = `${marker}\nlet piCodingAgentResourceLoaderDepsPromise;\nasync function loadPiCodingAgentResourceLoaderDeps() {\n    if (!piCodingAgentResourceLoaderDepsPromise) {\n        piCodingAgentResourceLoaderDepsPromise = Promise.all([\n            import('../packages/pi-coding-agent/dist/core/resource-loader.js'),\n            import('../packages/pi-coding-agent/dist/core/extensions/extension-sort.js'),\n        ]).then(([resourceLoaderModule, extensionSortModule]) => ({\n            DefaultResourceLoader: resourceLoaderModule.DefaultResourceLoader,\n            sortExtensionPaths: extensionSortModule.sortExtensionPaths,\n        }));\n    }\n    return piCodingAgentResourceLoaderDepsPromise;\n}\n`;
    if (!next.includes(importLine)) {
      throw new Error(
        'Unable to patch dist/resource-loader.js: pi-coding-agent import not found',
      );
    }

    next = next.replace(importLine, lazyImportBlock);
    const signature = 'export function buildResourceLoader(agentDir) {';
    if (!next.includes(signature)) {
      throw new Error(
        'Unable to patch dist/resource-loader.js: buildResourceLoader signature not found',
      );
    }
    next = next.replace(signature, 'export async function buildResourceLoader(agentDir) {');

    const registryAnchor = '    const registry = loadRegistry();\n';
    if (!next.includes(registryAnchor)) {
      throw new Error(
        'Unable to patch dist/resource-loader.js: buildResourceLoader anchor not found',
      );
    }
    next = next.replace(
      registryAnchor,
      `${registryAnchor}    const { DefaultResourceLoader, sortExtensionPaths } = await loadPiCodingAgentResourceLoaderDeps();\n`,
    );
  }

  if (!next.includes(stageMarker)) {
    const helperAnchor = "const resourceVersionManifestName = 'managed-resources.json';\n";
    if (!next.includes(helperAnchor)) {
      throw new Error(
        'Unable to patch dist/resource-loader.js: initResources helper anchor not found',
      );
    }
    const helperBlock = `${helperAnchor}${stageMarker}\nconst shouldDebugInitResources = process.argv.includes('headless') && process.argv.includes('new-milestone');\nfunction debugInitResourcesStage(message) {\n    if (shouldDebugInitResources) {\n        process.stderr.write(\`[gsd] \${message}\\n\`);\n    }\n}\n`;
    next = next.replace(helperAnchor, helperBlock);

    const initResourcesBody = `export function initResources(agentDir) {\n    mkdirSync(agentDir, { recursive: true });\n    const currentVersion = getBundledGsdVersion();\n    const manifest = readManagedResourceManifest(agentDir);\n    // Always prune root-level extension files that were removed from the bundle.\n    // This is cheap (a few existence checks + at most one rmSync) and must run\n    // unconditionally so that stale files left by a previous version are cleaned\n    // up even when the version/hash match causes the full sync to be skipped.\n    pruneRemovedBundledExtensions(manifest, agentDir);\n    // Ensure ~/.gsd/agent/node_modules symlinks to GSD's node_modules on EVERY\n    // launch, not just during resource syncs. A stale/broken symlink makes ALL\n    // extensions fail to resolve @gsd/* packages, rendering GSD non-functional.\n    ensureNodeModulesSymlink(agentDir);\n    // Migrate legacy skills on every launch (not gated by manifest) so that\n    // partial-failure retries don't wait for a version bump.\n    migrateSkillsToEcosystemDir(agentDir);\n    // Skip the full copy when both version AND content fingerprint match.\n    // Version-only checks miss same-version content changes (npm link dev workflow,\n    // hotfixes within a release). The content hash catches those at ~1ms cost.\n    if (manifest && manifest.gsdVersion === currentVersion) {\n        // Version matches — check content fingerprint for same-version staleness.\n        const currentHash = computeResourceFingerprint();\n        const hasStaleExtensionFiles = hasStaleCompiledExtensionSiblings(join(agentDir, 'extensions'));\n        if (manifest.contentHash && manifest.contentHash === currentHash && !hasStaleExtensionFiles) {\n            return;\n        }\n    }\n    // Sync bundled resources — overwrite so updates land on next launch.\n    syncResourceDir(bundledExtensionsDir, join(agentDir, 'extensions'));\n    syncResourceDir(join(resourcesDir, 'agents'), join(agentDir, 'agents'));\n    // Skills are no longer force-synced here. Users install skills via the\n    // skills.sh CLI (\`npx skills add <repo>\`) into ~/.agents/skills/ which\n    // is the industry-standard Agent Skills ecosystem directory.\n    //\n    // Migration from the legacy ~/.gsd/agent/skills/ directory is handled\n    // above the manifest check so it runs on every launch (including retries\n    // after partial copy failures).\n    // Sync GSD-WORKFLOW.md to agentDir as a fallback for when GSD_WORKFLOW_PATH\n    // env var is not set (e.g. fork/dev builds, alternative entry points).\n    const workflowSrc = join(resourcesDir, 'GSD-WORKFLOW.md');\n    if (existsSync(workflowSrc)) {\n        try {\n            copyFileSync(workflowSrc, join(agentDir, 'GSD-WORKFLOW.md'));\n        }\n        catch { /* non-fatal */ }\n    }\n    // Ensure all newly copied files are owner-writable so the next run can\n    // overwrite them (covers extensions, agents, and skills in one walk).\n    makeTreeWritable(agentDir);\n    writeManagedResourceManifest(agentDir);\n    ensureRegistryEntries(join(agentDir, 'extensions'));\n}\n`;
    if (!next.includes(initResourcesBody)) {
      throw new Error(
        'Unable to patch dist/resource-loader.js: initResources body anchor not found',
      );
    }
    const instrumentedInitResourcesBody = `export function initResources(agentDir) {\n    debugInitResourcesStage('initResources: ensure agent dir');\n    mkdirSync(agentDir, { recursive: true });\n    const currentVersion = getBundledGsdVersion();\n    const manifest = readManagedResourceManifest(agentDir);\n    // Always prune root-level extension files that were removed from the bundle.\n    // This is cheap (a few existence checks + at most one rmSync) and must run\n    // unconditionally so that stale files left by a previous version are cleaned\n    // up even when the version/hash match causes the full sync to be skipped.\n    debugInitResourcesStage('initResources: prune removed bundled extensions');\n    pruneRemovedBundledExtensions(manifest, agentDir);\n    // Ensure ~/.gsd/agent/node_modules symlinks to GSD's node_modules on EVERY\n    // launch, not just during resource syncs. A stale/broken symlink makes ALL\n    // extensions fail to resolve @gsd/* packages, rendering GSD non-functional.\n    debugInitResourcesStage('initResources: ensure node_modules symlink');\n    ensureNodeModulesSymlink(agentDir);\n    // Migrate legacy skills on every launch (not gated by manifest) so that\n    // partial-failure retries don't wait for a version bump.\n    debugInitResourcesStage('initResources: migrate legacy skills');\n    migrateSkillsToEcosystemDir(agentDir);\n    // Skip the full copy when both version AND content fingerprint match.\n    // Version-only checks miss same-version content changes (npm link dev workflow,\n    // hotfixes within a release). The content hash catches those at ~1ms cost.\n    if (manifest && manifest.gsdVersion === currentVersion) {\n        // Version matches — check content fingerprint for same-version staleness.\n        debugInitResourcesStage('initResources: compute resource fingerprint');\n        const currentHash = computeResourceFingerprint();\n        debugInitResourcesStage('initResources: scan stale compiled extension siblings');\n        const hasStaleExtensionFiles = hasStaleCompiledExtensionSiblings(join(agentDir, 'extensions'));\n        if (manifest.contentHash && manifest.contentHash === currentHash && !hasStaleExtensionFiles) {\n            debugInitResourcesStage('initResources: manifest matches, skipping sync');\n            return;\n        }\n    }\n    // Sync bundled resources — overwrite so updates land on next launch.\n    debugInitResourcesStage('initResources: sync bundled extensions');\n    syncResourceDir(bundledExtensionsDir, join(agentDir, 'extensions'));\n    debugInitResourcesStage('initResources: sync bundled agents');\n    syncResourceDir(join(resourcesDir, 'agents'), join(agentDir, 'agents'));\n    // Skills are no longer force-synced here. Users install skills via the\n    // skills.sh CLI (\`npx skills add <repo>\`) into ~/.agents/skills/ which\n    // is the industry-standard Agent Skills ecosystem directory.\n    //\n    // Migration from the legacy ~/.gsd/agent/skills/ directory is handled\n    // above the manifest check so it runs on every launch (including retries\n    // after partial copy failures).\n    // Sync GSD-WORKFLOW.md to agentDir as a fallback for when GSD_WORKFLOW_PATH\n    // env var is not set (e.g. fork/dev builds, alternative entry points).\n    const workflowSrc = join(resourcesDir, 'GSD-WORKFLOW.md');\n    if (existsSync(workflowSrc)) {\n        try {\n            debugInitResourcesStage('initResources: sync workflow doc');\n            copyFileSync(workflowSrc, join(agentDir, 'GSD-WORKFLOW.md'));\n        }\n        catch { /* non-fatal */ }\n    }\n    // Ensure all newly copied files are owner-writable so the next run can\n    // overwrite them (covers extensions, agents, and skills in one walk).\n    debugInitResourcesStage('initResources: make tree writable');\n    makeTreeWritable(agentDir);\n    debugInitResourcesStage('initResources: write managed resource manifest');\n    writeManagedResourceManifest(agentDir);\n    debugInitResourcesStage('initResources: ensure extension registry entries');\n    ensureRegistryEntries(join(agentDir, 'extensions'));\n    debugInitResourcesStage('initResources: complete');\n}\n`;
    next = next.replace(initResourcesBody, instrumentedInitResourcesBody);
  }

  if (!next.includes(fingerprintMarker)) {
    const helperAnchor = "export { discoverExtensionEntryPaths } from './extension-discovery.js';\n";
    if (!next.includes(helperAnchor)) {
      throw new Error(
        'Unable to patch dist/resource-loader.js: fingerprint helper anchor not found',
      );
    }
    const helperBlock = `${helperAnchor}${fingerprintMarker}\nconst bundledResourceFingerprintFileName = '.managed-resource-fingerprint';\nfunction getCurrentResourceFingerprint() {\n    try {\n        const cached = readFileSync(join(resourcesDir, bundledResourceFingerprintFileName), 'utf-8').trim();\n        if (cached) {\n            return cached;\n        }\n    }\n    catch {\n        // Fall back to live directory hashing when the cache file is absent.\n    }\n    return computeResourceFingerprint();\n}\n`;
    next = next.replace(helperAnchor, helperBlock);

    const collectAnchor = "    for (const entry of readdirSync(dir, { withFileTypes: true })) {\n";
    if (!next.includes(collectAnchor)) {
      throw new Error(
        'Unable to patch dist/resource-loader.js: fingerprint collect anchor not found',
      );
    }
    next = next.replace(
      collectAnchor,
      `${collectAnchor}        if (entry.name === bundledResourceFingerprintFileName) {\n            continue;\n        }\n`,
    );
  }

  const fingerprintCall = '        const currentHash = computeResourceFingerprint();\n';
  if (next.includes(fingerprintCall)) {
    next = next.replace(fingerprintCall, '        const currentHash = getCurrentResourceFingerprint();\n');
  } else if (!next.includes('        const currentHash = getCurrentResourceFingerprint();\n')) {
    throw new Error(
      'Unable to patch dist/resource-loader.js: fingerprint call anchor not found',
    );
  }

  return next;
});

patchFile('dist/cli.js', (text) => {
  const printApiMarker =
    '// Lazy-load the print/RPC API without importing the full pi-coding-agent barrel.';
  const prefsMarker =
    '// Lazy-load GSD preferences inside ensureRtkBootstrap() to keep RPC startup fast.';
  const sharedStateMarker =
    '// Load the shared auth/model/settings API before the common startup block uses it.';
  const headlessStageMarker =
    '// Emit startup markers for headless new-milestone before the headless orchestrator loads.';
  let next = text;

  const original = 'const resourceLoader = buildResourceLoader(agentDir);';
  const patched = 'const resourceLoader = await buildResourceLoader(agentDir);';
  if (next.includes(original)) {
    next = next.replace(original, patched);
  } else if (!next.includes(patched)) {
    throw new Error('Unable to patch dist/cli.js: buildResourceLoader call not found');
  }

  const piAgentBarrelImport =
    "import { AuthStorage, DefaultResourceLoader, ModelRegistry, runPackageCommand, SettingsManager, SessionManager, createAgentSession, InteractiveMode, runPrintMode, runRpcMode, } from '@gsd/pi-coding-agent';\n";
  const piAgentApiLoaderBlock = [
    'let piAgentApiPromise = null;',
    'async function loadPiAgentApi() {',
    '    if (!piAgentApiPromise) {',
    "        piAgentApiPromise = import('@gsd/pi-coding-agent');",
    '    }',
    '    return piAgentApiPromise;',
    '}',
    '',
  ].join('\n');
  if (next.includes(piAgentBarrelImport)) {
    next = next.replace(piAgentBarrelImport, `${piAgentBarrelImport}${piAgentApiLoaderBlock}`);
  }

  if (!next.includes(printApiMarker)) {
    const apiLoaderBlock = `let piAgentApiPromise = null;\nasync function loadPiAgentApi() {\n    if (!piAgentApiPromise) {\n        piAgentApiPromise = import('@gsd/pi-coding-agent');\n    }\n    return piAgentApiPromise;\n}\n`;
    const printApiBlock = `${apiLoaderBlock}${printApiMarker}\nlet piAgentPrintApiPromise = null;\nasync function loadPiAgentPrintApi() {\n    if (!piAgentPrintApiPromise) {\n        const timedImport = async (label, specifier) => {\n            debugRpcBootstrapStage(\`loading print/api module \${label}...\`);\n            const startedAt = Date.now();\n            try {\n                const module = await import(specifier);\n                debugRpcBootstrapStage(\`loaded print/api module \${label} in \${Date.now() - startedAt}ms.\`);\n                return module;\n            }\n            catch (error) {\n                debugRpcBootstrapStage(\`failed print/api module \${label} after \${Date.now() - startedAt}ms.\`);\n                throw error;\n            }\n        };\n        piAgentPrintApiPromise = Promise.all([\n            timedImport('auth-storage', '../packages/pi-coding-agent/dist/core/auth-storage.js'),\n            timedImport('resource-loader', '../packages/pi-coding-agent/dist/core/resource-loader.js'),\n            timedImport('model-registry', '../packages/pi-coding-agent/dist/core/model-registry.js'),\n            timedImport('settings-manager', '../packages/pi-coding-agent/dist/core/settings-manager.js'),\n            timedImport('session-manager', '../packages/pi-coding-agent/dist/core/session-manager.js'),\n            timedImport('sdk', '../packages/pi-coding-agent/dist/core/sdk.js'),\n            timedImport('print-mode', '../packages/pi-coding-agent/dist/modes/print-mode.js'),\n            timedImport('rpc-mode', '../packages/pi-coding-agent/dist/modes/rpc/rpc-mode.js'),\n        ]).then(([\n            authModule,\n            resourceLoaderModule,\n            modelRegistryModule,\n            settingsModule,\n            sessionModule,\n            sdkModule,\n            printModeModule,\n            rpcModeModule,\n        ]) => ({\n            AuthStorage: authModule.AuthStorage,\n            DefaultResourceLoader: resourceLoaderModule.DefaultResourceLoader,\n            ModelRegistry: modelRegistryModule.ModelRegistry,\n            SettingsManager: settingsModule.SettingsManager,\n            SessionManager: sessionModule.SessionManager,\n            createAgentSession: sdkModule.createAgentSession,\n            runPrintMode: printModeModule.runPrintMode,\n            runRpcMode: rpcModeModule.runRpcMode,\n        }));\n    }\n    return piAgentPrintApiPromise;\n}\n`;
    if (!next.includes(apiLoaderBlock)) {
      throw new Error('Unable to patch dist/cli.js: pi-agent loader block not found');
    }
    next = next.replace(apiLoaderBlock, printApiBlock);
  }

  next = next.replaceAll(
    "            timedImport('print-mode', '../packages/pi-coding-agent/dist/modes/print-mode.js'),",
    "            cliFlags.mode === 'rpc' ? Promise.resolve(null) : timedImport('print-mode', '../packages/pi-coding-agent/dist/modes/print-mode.js'),",
  );
  next = next.replaceAll(
    'runPrintMode: printModeModule.runPrintMode',
    'runPrintMode: printModeModule?.runPrintMode',
  );

  if (!next.includes('debugPrintRpcStage')) {
    const printModeBranch = 'if (isPrintMode) {\n';
    if (!next.includes(printModeBranch)) {
      throw new Error('Unable to patch dist/cli.js: print-mode branch not found');
    }
    next = next.replace(
      printModeBranch,
      `${printModeBranch}    const debugPrintRpcStage = (message) => {\n        if (cliFlags.mode === 'rpc') {\n            process.stderr.write(\`[gsd] rpc-child: \${message}\\n\`);\n        }\n    };\n    debugPrintRpcStage('loading print/api bundle...');\n    const { AuthStorage, DefaultResourceLoader, ModelRegistry, SettingsManager, SessionManager, createAgentSession, runPrintMode, runRpcMode, } = await loadPiAgentPrintApi();\n`,
    );

    const printApiCall = '    const { AuthStorage, DefaultResourceLoader, ModelRegistry, SettingsManager, SessionManager, createAgentSession, runPrintMode, runRpcMode, } = await loadPiAgentPrintApi();\n';
    if (!next.includes(printApiCall)) {
      throw new Error('Unable to patch dist/cli.js: print api call not found');
    }
    next = next.replace(
      printApiCall,
      "    const { AuthStorage, DefaultResourceLoader, ModelRegistry, SettingsManager, SessionManager, createAgentSession, runPrintMode, runRpcMode, } = await loadPiAgentPrintApi();\n    debugPrintRpcStage('print/api bundle loaded.');\n    debugPrintRpcStage('bootstrapping RTK...');\n",
    );

    const bootstrapCall = '    await ensureRtkBootstrap();\n';
    if (!next.includes(bootstrapCall)) {
      throw new Error('Unable to patch dist/cli.js: ensureRtkBootstrap call not found');
    }
    next = next.replace(
      bootstrapCall,
      "    await ensureRtkBootstrap();\n    debugPrintRpcStage('RTK bootstrap complete.');\n",
    );

    const exitManagedResourcesCall = '    exitIfManagedResourcesAreNewer(agentDir);\n    initResources(agentDir);\n';
    if (!next.includes(exitManagedResourcesCall)) {
      throw new Error('Unable to patch dist/cli.js: managed resources call not found');
    }
    next = next.replace(
      exitManagedResourcesCall,
      "    exitIfManagedResourcesAreNewer(agentDir);\n    debugPrintRpcStage('initializing managed resources...');\n    initResources(agentDir);\n    debugPrintRpcStage('managed resources initialized.');\n",
    );

    const resourceLoaderReloadCall = '    await resourceLoader.reload();\n';
    if (!next.includes(resourceLoaderReloadCall)) {
      throw new Error('Unable to patch dist/cli.js: resourceLoader.reload call not found');
    }
    next = next.replace(
      resourceLoaderReloadCall,
      "    debugPrintRpcStage('reloading resource loader...');\n    await resourceLoader.reload();\n    debugPrintRpcStage('resource loader ready.');\n",
    );

    const createSessionCall = '    const { session, extensionsResult, modelFallbackMessage } = await createAgentSession({\n';
    if (!next.includes(createSessionCall)) {
      throw new Error('Unable to patch dist/cli.js: createAgentSession call not found');
    }
    next = next.replace(
      createSessionCall,
      "    debugPrintRpcStage('creating agent session...');\n    const { session, extensionsResult, modelFallbackMessage } = await createAgentSession({\n",
    );

    const createSessionClose = '    markStartup(\'createAgentSession\');\n';
    if (!next.includes(createSessionClose)) {
      throw new Error('Unable to patch dist/cli.js: createAgentSession completion not found');
    }
    next = next.replace(
      createSessionClose,
      "    debugPrintRpcStage('agent session created.');\n    markStartup('createAgentSession');\n",
    );

    const rpcModeCall = '    if (mode === \'rpc\') {\n        printStartupTimings();\n        await runRpcMode(session);\n        process.exit(0);\n    }\n';
    if (!next.includes(rpcModeCall)) {
      throw new Error('Unable to patch dist/cli.js: rpc mode call not found');
    }
    next = next.replace(
      rpcModeCall,
      "    if (mode === 'rpc') {\n        debugPrintRpcStage('entering rpc mode...');\n        printStartupTimings();\n        await runRpcMode(session);\n        process.exit(0);\n    }\n",
    );
  }

  if (!next.includes(prefsMarker)) {
    const prefsImport =
      "import { loadEffectiveGSDPreferences } from './resources/extensions/gsd/preferences.js';\n";
    if (!next.includes(prefsImport)) {
      throw new Error('Unable to patch dist/cli.js: preferences import not found');
    }
    next = next.replace(prefsImport, `${prefsMarker}\n`);

    const prefsUsage = "        const prefs = loadEffectiveGSDPreferences();\n";
    if (!next.includes(prefsUsage)) {
      throw new Error('Unable to patch dist/cli.js: preferences usage anchor not found');
    }
    next = next.replace(
      prefsUsage,
      "        const { loadEffectiveGSDPreferences } = await import('./resources/extensions/gsd/preferences.js');\n        const prefs = loadEffectiveGSDPreferences();\n",
    );
  }

  if (!next.includes(sharedStateMarker)) {
    const sharedStateAnchor = "// Pi's tool bootstrap can mis-detect already-installed fd/rg on some systems\n";
    if (!next.includes(sharedStateAnchor)) {
      throw new Error('Unable to patch dist/cli.js: shared-state anchor not found');
    }
    const sharedStateBlock = `${sharedStateMarker}\nconst debugRpcBootstrapStage = (message) => {\n    if (cliFlags.mode === 'rpc') {\n        process.stderr.write(\`[gsd] rpc-child: \${message}\\n\`);\n    }\n};\ndebugRpcBootstrapStage('loading shared auth/model/settings API...');\nconst {\n    AuthStorage: SharedAuthStorage,\n    ModelRegistry: SharedModelRegistry,\n    SettingsManager: SharedSettingsManager,\n} = await Promise.all([\n    import('../packages/pi-coding-agent/dist/core/auth-storage.js'),\n    import('../packages/pi-coding-agent/dist/core/model-registry.js'),\n    import('../packages/pi-coding-agent/dist/core/settings-manager.js'),\n]).then(([authModule, modelRegistryModule, settingsModule]) => ({\n    AuthStorage: authModule.AuthStorage,\n    ModelRegistry: modelRegistryModule.ModelRegistry,\n    SettingsManager: settingsModule.SettingsManager,\n}));\ndebugRpcBootstrapStage('shared auth/model/settings API loaded.');\n`;
    next = next.replace(sharedStateAnchor, `${sharedStateBlock}${sharedStateAnchor}`);
  }

  const authStorageLine = 'const authStorage = AuthStorage.create(authFilePath);';
  if (next.includes(authStorageLine)) {
    next = next.replace(
      authStorageLine,
      "debugRpcBootstrapStage('creating auth storage...');\nconst authStorage = SharedAuthStorage.create(authFilePath);\ndebugRpcBootstrapStage('auth storage ready.');",
    );
  } else if (!next.includes('const authStorage = SharedAuthStorage.create(authFilePath);')) {
    throw new Error('Unable to patch dist/cli.js: authStorage initialization not found');
  }

  const modelRegistryLine = 'const modelRegistry = new ModelRegistry(authStorage, modelsJsonPath);';
  if (next.includes(modelRegistryLine)) {
    next = next.replace(
      modelRegistryLine,
      "debugRpcBootstrapStage('creating model registry...');\nconst modelRegistry = new SharedModelRegistry(authStorage, modelsJsonPath);\ndebugRpcBootstrapStage('model registry ready.');",
    );
  } else if (
    !next.includes('const modelRegistry = new SharedModelRegistry(authStorage, modelsJsonPath);')
  ) {
    throw new Error('Unable to patch dist/cli.js: modelRegistry initialization not found');
  }

  const settingsManagerLine = 'const settingsManager = SettingsManager.create(agentDir);';
  if (next.includes(settingsManagerLine)) {
    next = next.replace(
      settingsManagerLine,
      "debugRpcBootstrapStage('creating settings manager...');\nconst settingsManager = SharedSettingsManager.create(agentDir);\ndebugRpcBootstrapStage('settings manager ready.');",
    );
  } else if (
    !next.includes('const settingsManager = SharedSettingsManager.create(agentDir);')
  ) {
    throw new Error('Unable to patch dist/cli.js: settingsManager initialization not found');
  }

  const envKeysLine = 'loadStoredEnvKeys(authStorage);';
  if (next.includes(envKeysLine)) {
    next = next.replace(
      envKeysLine,
      "debugRpcBootstrapStage('loading stored env keys...');\nloadStoredEnvKeys(authStorage);\ndebugRpcBootstrapStage('stored env keys loaded.');",
    );
  }

  const migrateLine = 'migratePiCredentials(authStorage);';
  if (next.includes(migrateLine)) {
    next = next.replace(
      migrateLine,
      "debugRpcBootstrapStage('migrating credentials...');\nmigratePiCredentials(authStorage);\ndebugRpcBootstrapStage('credentials migrated.');",
    );
  }

  const resolveModelsLine = "const { resolveModelsJsonPath } = await import('./models-resolver.js');";
  if (next.includes(resolveModelsLine)) {
    next = next.replace(
      resolveModelsLine,
      "debugRpcBootstrapStage('resolving models path...');\nconst { resolveModelsJsonPath } = await import('./models-resolver.js');",
    );
  }
  const modelsPathLine = 'const modelsJsonPath = resolveModelsJsonPath();';
  if (next.includes(modelsPathLine)) {
    next = next.replace(
      modelsPathLine,
      "const modelsJsonPath = resolveModelsJsonPath();\ndebugRpcBootstrapStage('models path resolved.');",
    );
  }

  const applySecurityOverridesLine = 'applySecurityOverrides(settingsManager);';
  if (next.includes(applySecurityOverridesLine)) {
    next = next.replace(
      applySecurityOverridesLine,
      "debugRpcBootstrapStage('applying security overrides...');\napplySecurityOverrides(settingsManager);\ndebugRpcBootstrapStage('security overrides applied.');",
    );
  }

  for (const line of [
    "debugRpcBootstrapStage('migrating credentials...');\n",
    "debugRpcBootstrapStage('credentials migrated.');\n",
    "debugRpcBootstrapStage('resolving models path...');\n",
    "debugRpcBootstrapStage('models path resolved.');\n",
    "debugRpcBootstrapStage('applying security overrides...');\n",
    "debugRpcBootstrapStage('security overrides applied.');\n",
  ]) {
    while (next.includes(line + line)) {
      next = next.replaceAll(line + line, line);
    }
  }

  const printLoader =
    '    const { AuthStorage, DefaultResourceLoader, ModelRegistry, SettingsManager, SessionManager, createAgentSession, runPrintMode, runRpcMode, } = await loadPiAgentApi();';
  if (next.includes(printLoader)) {
    next = next.replace(
      printLoader,
      '    const { AuthStorage, DefaultResourceLoader, ModelRegistry, SettingsManager, SessionManager, createAgentSession, runPrintMode, runRpcMode, } = await loadPiAgentPrintApi();',
    );
  } else if (
    !next.includes(
      '    const { AuthStorage, DefaultResourceLoader, ModelRegistry, SettingsManager, SessionManager, createAgentSession, runPrintMode, runRpcMode, } = await loadPiAgentPrintApi();',
    )
  ) {
    throw new Error('Unable to patch dist/cli.js: print-mode pi-agent loader not found');
  }

  if (!next.includes(headlessStageMarker)) {
    const headlessBranch = "if (cliFlags.messages[0] === 'headless') {\n";
    if (!next.includes(headlessBranch)) {
      throw new Error('Unable to patch dist/cli.js: headless branch not found');
    }
    next = next.replace(
      headlessBranch,
      `${headlessBranch}    ${headlessStageMarker}\n    const debugHeadlessCliStage = (message) => {\n        if (headlessCommand === 'new-milestone') {\n            process.stderr.write(\`[gsd] \${message}\\n\`);\n        }\n    };\n`,
    );
  }

  const headlessEnsureRtk = '    await ensureRtkBootstrap();\n';
  if (
    next.includes(headlessEnsureRtk) &&
    !next.includes("debugHeadlessCliStage('headless new-milestone: bootstrapping RTK...');")
  ) {
    next = next.replace(
      headlessEnsureRtk,
      "    debugHeadlessCliStage('headless new-milestone: bootstrapping RTK...');\n    await ensureRtkBootstrap();\n    debugHeadlessCliStage('headless new-milestone: RTK bootstrap complete.');\n",
    );
  }

  const headlessInitResources = '        initResources(agentDir);\n';
  if (
    next.includes(headlessInitResources) &&
    !next.includes("debugHeadlessCliStage('headless new-milestone: syncing managed resources...');")
  ) {
    next = next.replace(
      headlessInitResources,
      "        debugHeadlessCliStage('headless new-milestone: syncing managed resources...');\n        initResources(agentDir);\n        debugHeadlessCliStage('headless new-milestone: managed resources ready.');\n",
    );
  }

  const headlessImport = "    const { runHeadless, parseHeadlessArgs } = await import('./headless.js');\n";
  if (
    next.includes(headlessImport) &&
    !next.includes("debugHeadlessCliStage('headless new-milestone: loading orchestrator...');")
  ) {
    next = next.replace(
      headlessImport,
      "    debugHeadlessCliStage('headless new-milestone: loading orchestrator...');\n    const { runHeadless, parseHeadlessArgs } = await import('./headless.js');\n",
    );
  }

  return next;
});

patchFile('dist/headless.js', (text) => {
  const marker =
    '// Lazy-load only the RPC/session modules we need instead of the pi-coding-agent barrel.';
  const zeroToolMarker =
    'multi-turn session ended with 0 tool calls and no terminal notification; treating as stalled';
  if (text.includes('prepareHeadlessMilestoneSkeleton') && text.includes(zeroToolMarker)) {
    return text;
  }
  const initTimeoutMarker =
    'const RPC_INIT_TIMEOUT_MS = 240000;';
  const newMilestoneInitTimeoutMarker =
    "const RPC_INIT_TIMEOUT_MS = options.command === 'new-milestone' ? 30000 : 240000;";
  const stageMarker =
    '// Emit explicit progress markers for headless new-milestone bootstrap stages.';
  let next = text;

  if (!next.includes(marker)) {
    const originalBlock = `let piAgentApiPromise = null;\nasync function loadPiAgentApi() {\n    if (!piAgentApiPromise) {\n        piAgentApiPromise = import('@gsd/pi-coding-agent');\n    }\n    return piAgentApiPromise;\n}\n`;
    const headlessBarrelImport =
      "import { RpcClient, SessionManager } from '@gsd/pi-coding-agent';\n";
    if (next.includes(headlessBarrelImport)) {
      next = next.replace(headlessBarrelImport, originalBlock);
    }
    const patchedBlock = `${marker}\nlet piAgentRpcClientPromise = null;\nlet piAgentSessionManagerPromise = null;\nasync function loadPiAgentRpcClient() {\n    if (!piAgentRpcClientPromise) {\n        piAgentRpcClientPromise = import('../packages/pi-coding-agent/dist/modes/rpc/rpc-client.js');\n    }\n    return piAgentRpcClientPromise;\n}\nasync function loadPiAgentSessionManager() {\n    if (!piAgentSessionManagerPromise) {\n        piAgentSessionManagerPromise = import('../packages/pi-coding-agent/dist/core/session-manager.js');\n    }\n    return piAgentSessionManagerPromise;\n}\n`;
    if (!next.includes(originalBlock)) {
      throw new Error('Unable to patch dist/headless.js: pi-agent barrel loader block not found');
    }
    next = next.replace(originalBlock, patchedBlock);
  }

  const headlessContextImport =
    "import { loadContext, bootstrapGsdProject, } from './headless-context.js';\n";
  if (
    next.includes(headlessContextImport) &&
    !next.includes('import { loadContext, bootstrapGsdProject, prepareHeadlessMilestoneSkeleton, } from')
  ) {
    next = next.replace(
      headlessContextImport,
      "import { loadContext, bootstrapGsdProject, prepareHeadlessMilestoneSkeleton, } from './headless-context.js';\n",
    );
  }

  const rpcLoader = '    const { RpcClient } = await loadPiAgentApi();';
  const rpcConstructor = '    const client = new RpcClient(clientOptions);\n';
  if (next.includes(rpcLoader)) {
    next = next.replace(rpcLoader, '    const { RpcClient } = await loadPiAgentRpcClient();');
  } else if (next.includes(rpcConstructor)) {
    next = next.replace(
      rpcConstructor,
      '    const { RpcClient } = await loadPiAgentRpcClient();\n    const client = new RpcClient(clientOptions);\n',
    );
  } else if (!next.includes('    const { RpcClient } = await loadPiAgentRpcClient();')) {
    throw new Error('Unable to patch dist/headless.js: RpcClient loader not found');
  }

  const sessionLoader = '        const { SessionManager } = await loadPiAgentApi();';
  const sessionListCall =
    '        const sessions = await SessionManager.list(process.cwd(), projectSessionsDir);\n';
  if (next.includes(sessionLoader)) {
    next = next.replace(
      sessionLoader,
      '        const { SessionManager } = await loadPiAgentSessionManager();',
    );
  } else if (next.includes(sessionListCall)) {
    next = next.replace(
      sessionListCall,
      '        const { SessionManager } = await loadPiAgentSessionManager();\n        const sessions = await SessionManager.list(process.cwd(), projectSessionsDir);\n',
    );
  } else if (!next.includes('        const { SessionManager } = await loadPiAgentSessionManager();')) {
    throw new Error('Unable to patch dist/headless.js: SessionManager loader not found');
  }

  if (!next.includes(newMilestoneInitTimeoutMarker) && next.includes(initTimeoutMarker)) {
    next = next.replace(initTimeoutMarker, newMilestoneInitTimeoutMarker);
  }

  if (!next.includes(newMilestoneInitTimeoutMarker)) {
    const completionMarker = '    // Completion promise\n';
    if (!next.includes(completionMarker)) {
      throw new Error('Unable to patch dist/headless.js: completion marker not found');
    }
    next = next.replace(
      completionMarker,
      `    ${newMilestoneInitTimeoutMarker}\n${completionMarker}`,
    );
  }

  if (next.includes("        if (isNewMilestone && !options.json) {\n            process.stderr.write(`[headless] ${message}\\n`);\n        }\n")) {
    next = next.replace(
      "        if (isNewMilestone && !options.json) {\n            process.stderr.write(`[headless] ${message}\\n`);\n        }\n",
      "        if (shouldTraceHeadless) {\n            process.stderr.write(`[headless] ${message}\\n`);\n        }\n",
    );
  }

  if (next.includes(stageMarker) && !next.includes('const shouldTraceHeadless =')) {
    next = next.replace(
      `${stageMarker}\n    const debugHeadlessStage = (message) => {`,
      `${stageMarker}\n    const shouldTraceHeadless = (process.env.GSD_DEBUG === '1' || isNewMilestone) && !options.json;\n    const debugHeadlessStage = (message) => {`,
    );
  }

  if (!next.includes(stageMarker)) {
    const newMilestoneAnchor = "    const isNewMilestone = options.command === 'new-milestone';\n";
    if (!next.includes(newMilestoneAnchor)) {
      throw new Error(
        'Unable to patch dist/headless.js: new-milestone anchor not found',
      );
    }
    next = next.replace(
      newMilestoneAnchor,
      `${newMilestoneAnchor}    ${stageMarker}\n    const shouldTraceHeadless = (process.env.GSD_DEBUG === '1' || isNewMilestone) && !options.json;\n    const debugHeadlessStage = (message) => {\n        if (shouldTraceHeadless) {\n            process.stderr.write(\`[headless] \${message}\\n\`);\n        }\n    };\n`,
    );
  }

  const contextLoad = '            contextContent = await loadContext(options);\n';
  if (next.includes(contextLoad) && !next.includes("debugHeadlessStage('Loading milestone context...');")) {
    next = next.replace(
      contextLoad,
      "            debugHeadlessStage('Loading milestone context...');\n            contextContent = await loadContext(options);\n            debugHeadlessStage('Context loaded.');\n",
    );
  }

  const bootstrapAnchor = "        const gsdDir = join(process.cwd(), '.gsd');\n";
  if (next.includes(bootstrapAnchor) && !next.includes("debugHeadlessStage('Ensuring .gsd bootstrap state...');")) {
    next = next.replace(
      bootstrapAnchor,
      "        debugHeadlessStage('Ensuring .gsd bootstrap state...');\n        const gsdDir = join(process.cwd(), '.gsd');\n",
    );
  }

  const contextPrepared = "        writeFileSync(join(runtimeDir, 'headless-context.md'), contextContent, 'utf-8');\n";
  if (next.includes(contextPrepared) && !next.includes("debugHeadlessStage('Milestone context prepared.');")) {
    next = next.replace(
      contextPrepared,
      "        writeFileSync(join(runtimeDir, 'headless-context.md'), contextContent, 'utf-8');\n        debugHeadlessStage('Milestone context prepared.');\n        try {\n            debugHeadlessStage('Materializing canonical milestone skeleton...');\n            const preparedMilestoneId = prepareHeadlessMilestoneSkeleton(process.cwd());\n            debugHeadlessStage(`Canonical milestone skeleton prepared (${preparedMilestoneId}).`);\n        }\n        catch (err) {\n            process.stderr.write(`[headless] Error preparing canonical skeleton: ${err instanceof Error ? err.message : String(err)}\\n`);\n            process.exit(1);\n        }\n",
    );
  }

  const clientOptionsBlock = "    const clientOptions = {\n        cliPath,\n        cwd: process.cwd(),\n    };\n";
  if (next.includes(clientOptionsBlock) && !next.includes('PI_CODING_AGENT_DIR')) {
    next = next.replace(
      clientOptionsBlock,
      "    const gsdHome = process.env.GSD_HOME ?? join(process.cwd(), '.gsd');\n    const codingAgentDir = resolve(gsdHome, 'agent');\n    const clientOptions = {\n        cliPath,\n        cwd: process.cwd(),\n        requestTimeoutMs: options.responseTimeout,\n    };\n",
    );
  }

  if (
    next.includes("    const clientOptions = {\n        cliPath,\n        cwd: process.cwd(),\n    };\n") &&
    !next.includes('requestTimeoutMs: options.responseTimeout')
  ) {
    next = next.replace(
      "    const clientOptions = {\n        cliPath,\n        cwd: process.cwd(),\n    };\n",
      "    const clientOptions = {\n        cliPath,\n        cwd: process.cwd(),\n        requestTimeoutMs: options.responseTimeout,\n    };\n",
    );
  }

  const headlessEnvBlock = "    clientOptions.env = { ...(clientOptions.env || {}), GSD_HEADLESS: '1' };\n";
  if (next.includes(headlessEnvBlock) && !next.includes('PI_CODING_AGENT_DIR')) {
    next = next.replace(
      headlessEnvBlock,
      "    clientOptions.env = {\n        ...(clientOptions.env || {}),\n        GSD_HEADLESS: '1',\n        GSD_HEADLESS_COMMAND: options.command,\n        PI_CODING_AGENT_DIR: codingAgentDir,\n    };\n",
    );
  }

  const clientStart = '        await client.start();\n';
  if (next.includes(clientStart) && !next.includes("debugHeadlessStage('Starting RPC child...');")) {
    next = next.replace(
      clientStart,
      "        debugHeadlessStage('Starting RPC child...');\n        await client.start();\n        debugHeadlessStage('RPC child started.');\n",
    );
  }

  const initStart = '        await Promise.race([\n';
  if (next.includes(initStart) && !next.includes("debugHeadlessStage('Waiting for RPC init...');")) {
    next = next.replace(
      initStart,
      "        debugHeadlessStage('Waiting for RPC init...');\n        await Promise.race([\n",
    );
  }

  const promptStart = '        await client.prompt(command);\n';
  if (next.includes(promptStart) && !next.includes("Timeout waiting for response to prompt after ${responseTimeout}ms")) {
    next = next.replace(
      promptStart,
      "        debugHeadlessStage('Sending milestone prompt to RPC child...');\n        await Promise.race([\n            client.prompt(command),\n            new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout waiting for response to prompt after ${responseTimeout}ms`)), responseTimeout)),\n        ]);\n",
    );
  }

  if (
    next.includes("        v2Enabled = true;\n") &&
    !next.includes("debugHeadlessStage('RPC init completed.');")
  ) {
    next = next.replace(
      "        v2Enabled = true;\n",
      "        debugHeadlessStage('RPC init completed.');\n        v2Enabled = true;\n",
    );
  }

  const initTimeoutLine = "    const RPC_INIT_TIMEOUT_MS = options.command === 'new-milestone' ? 30000 : 240000;\n";
  if (next.includes(initTimeoutLine)) {
    next = next.replace(
      initTimeoutLine,
      "    const RPC_INIT_TIMEOUT_MS = options.command === 'new-milestone'\n        ? Math.min(options.responseTimeout ?? 30000, 30000)\n        : (options.responseTimeout ?? 240000);\n",
    );
  }

  const cappedInitTimeoutLine = "    const RPC_INIT_TIMEOUT_MS = Math.min(options.responseTimeout ?? 240000, options.command === 'new-milestone' ? 30000 : 240000);\n";
  if (next.includes(cappedInitTimeoutLine)) {
    next = next.replace(
      cappedInitTimeoutLine,
      "    const RPC_INIT_TIMEOUT_MS = options.command === 'new-milestone'\n        ? Math.min(options.responseTimeout ?? 30000, 30000)\n        : (options.responseTimeout ?? 240000);\n",
    );
  }

  const initCatchLine = "        process.stderr.write(`[headless] Warning: v2 init failed, falling back to v1 string-matching (${err instanceof Error ? err.message : String(err)})\\n`);\n";
  if (
    next.includes(initCatchLine) &&
    !next.includes('if (err instanceof Error && /timed out|Timeout waiting/i.test(err.message))')
  ) {
    next = next.replace(
      initCatchLine,
      `${initCatchLine}        if (err instanceof Error && /timed out|Timeout waiting/i.test(err.message)) {\n            exitCode = EXIT_ERROR;\n        }\n`,
    );
  }

  if (
    next.includes("        ]);\n    }\n    catch (err) {\n        process.stderr.write(`[headless] Error: Failed to send prompt:") &&
    !next.includes("debugHeadlessStage('Prompt accepted by RPC child.');")
  ) {
    next = next.replace(
      "        ]);\n    }\n    catch (err) {\n        process.stderr.write(`[headless] Error: Failed to send prompt:",
      "        ]);\n        debugHeadlessStage('Prompt accepted by RPC child.');\n    }\n    catch (err) {\n        process.stderr.write(`[headless] Error: Failed to send prompt:",
    );
  }

  if (
    next.includes("    try {\n        debugHeadlessStage('Sending milestone prompt to RPC child...');\n        await Promise.race([") &&
    !next.includes("    if (exitCode === EXIT_SUCCESS) {\n        try {\n            debugHeadlessStage('Sending milestone prompt to RPC child...');")
  ) {
    next = next.replace(
      "    try {\n        debugHeadlessStage('Sending milestone prompt to RPC child...');\n        await Promise.race([\n            client.prompt(command),\n            new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout waiting for response to prompt after ${responseTimeout}ms`)), responseTimeout)),\n        ]);\n        debugHeadlessStage('Prompt accepted by RPC child.');\n    }\n    catch (err) {\n        process.stderr.write(`[headless] Error: Failed to send prompt: ${err instanceof Error ? err.message : String(err)}\\n`);\n        exitCode = EXIT_ERROR;\n    }\n",
      "    if (exitCode === EXIT_SUCCESS) {\n        try {\n            debugHeadlessStage('Sending milestone prompt to RPC child...');\n            await Promise.race([\n                client.prompt(command),\n                new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout waiting for response to prompt after ${responseTimeout}ms`)), responseTimeout)),\n            ]);\n            debugHeadlessStage('Prompt accepted by RPC child.');\n        }\n        catch (err) {\n            process.stderr.write(`[headless] Error: Failed to send prompt: ${err instanceof Error ? err.message : String(err)}\\n`);\n            exitCode = EXIT_ERROR;\n        }\n    }\n",
    );
  }

  if (
    next.includes("    if (exitCode === EXIT_SUCCESS || exitCode === EXIT_BLOCKED) {\n        await completionPromise;\n    }\n") &&
    !next.includes("debugHeadlessStage('Waiting for headless completion.');")
  ) {
    next = next.replace(
      "    if (exitCode === EXIT_SUCCESS || exitCode === EXIT_BLOCKED) {\n        await completionPromise;\n    }\n",
      "    if (exitCode === EXIT_SUCCESS || exitCode === EXIT_BLOCKED) {\n        debugHeadlessStage('Waiting for headless completion.');\n        await completionPromise;\n    }\n",
    );
  }

  const autoPromptStart = "            await client.prompt('/gsd auto');\n";
  if (next.includes(autoPromptStart) && !next.includes("await Promise.race([\n                client.prompt('/gsd auto'),")) {
    next = next.replace(
      autoPromptStart,
      "            await Promise.race([\n                client.prompt('/gsd auto'),\n                new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout waiting for response to prompt after ${responseTimeout}ms`)), responseTimeout)),\n            ]);\n",
    );
  }

  if (
    next.includes("        try {\n            await Promise.race([\n                client.prompt('/gsd auto'),") &&
    !next.includes("debugHeadlessStage('Sending auto prompt to RPC child...');")
  ) {
    next = next.replace(
      "        try {\n            await Promise.race([\n                client.prompt('/gsd auto'),",
      "        try {\n            debugHeadlessStage('Sending auto prompt to RPC child...');\n            await Promise.race([\n                client.prompt('/gsd auto'),",
    );
  }

  if (
    next.includes("                new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout waiting for response to prompt after ${responseTimeout}ms`)), responseTimeout)),\n            ]);\n        }\n        catch (err) {\n            process.stderr.write(`[headless] Error: Failed to start auto-mode:") &&
    !next.includes("debugHeadlessStage('Auto prompt accepted by RPC child.');")
  ) {
    next = next.replace(
      "                new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout waiting for response to prompt after ${responseTimeout}ms`)), responseTimeout)),\n            ]);\n        }\n        catch (err) {\n            process.stderr.write(`[headless] Error: Failed to start auto-mode:",
      "                new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout waiting for response to prompt after ${responseTimeout}ms`)), responseTimeout)),\n            ]);\n            debugHeadlessStage('Auto prompt accepted by RPC child.');\n        }\n        catch (err) {\n            process.stderr.write(`[headless] Error: Failed to start auto-mode:",
    );
  }

  if (
    next.includes("    // Cleanup\n    if (timeoutTimer)\n") &&
    !next.includes("debugHeadlessStage('Cleaning up headless child.');")
  ) {
    next = next.replace(
      "    // Cleanup\n    if (timeoutTimer)\n",
      "    // Cleanup\n    debugHeadlessStage('Cleaning up headless child.');\n    if (timeoutTimer)\n",
    );
  }

  if (
    next.includes("    await client.stop();\n    // Summary\n") &&
    !next.includes("debugHeadlessStage('Stopping RPC child...');")
  ) {
    next = next.replace(
      "    await client.stop();\n    // Summary\n",
      "    debugHeadlessStage('Stopping RPC child...');\n    await client.stop();\n    debugHeadlessStage('RPC child stopped.');\n    // Summary\n",
    );
  }

  const initCall = "        await client.init({ clientId: 'gsd-headless' });";
  if (next.includes(initCall)) {
    next = next.replace(
      initCall,
      "        await Promise.race([\n            client.init({ clientId: 'gsd-headless' }),\n            new Promise((_, reject) => setTimeout(() => {\n                const stderr = typeof client.getStderr === 'function' ? client.getStderr() : '';\n                reject(new Error(`RPC init timed out after ${RPC_INIT_TIMEOUT_MS}ms${stderr ? `. Child stderr: ${stderr}` : ''}`));\n            }, RPC_INIT_TIMEOUT_MS)),\n        ]);",
    );
  } else if (!next.includes('RPC init timed out after ${RPC_INIT_TIMEOUT_MS}ms')) {
    throw new Error('Unable to patch dist/headless.js: client.init call not found');
  }

  const genericInitCatch = "    catch {\n        process.stderr.write('[headless] Warning: v2 init failed, falling back to v1 string-matching\\n');\n    }\n";
  if (next.includes(genericInitCatch)) {
    next = next.replace(
      genericInitCatch,
      "    catch (err) {\n        process.stderr.write(`[headless] Warning: v2 init failed, falling back to v1 string-matching (${err instanceof Error ? err.message : String(err)})\\n`);\n    }\n",
    );
  } else if (
    !next.includes(
      "[headless] Warning: v2 init failed, falling back to v1 string-matching (${err instanceof Error ? err.message : String(err)})",
    )
  ) {
    throw new Error('Unable to patch dist/headless.js: init warning catch not found');
  }

  const zeroToolAnchor =
    '        // Long-running commands: agent_end after tool execution — possible completion\n' +
    '        // The idle timer + terminal notification handle this case.\n';
  if (next.includes(zeroToolAnchor) && !next.includes(zeroToolMarker)) {
    next = next.replace(
      zeroToolAnchor,
      "        // Long-running commands: agent_end after tool execution — possible completion.\\n" +
        "        // Normally terminal notification or idle timer resolves completion. If a\\n" +
        "        // multi-turn command ends with zero tool calls, the idle timer never arms\\n" +
        "        // and older builds hang forever after printing \"Session ended\".\\n" +
        "        if (eventObj.type === 'agent_end' && isMultiTurnCommand && !completed && toolCallCount === 0) {\\n" +
        "            process.stderr.write('[headless] Warning: multi-turn session ended with 0 tool calls and no terminal notification; treating as stalled\\\\n');\\n" +
        "            completed = true;\\n" +
        "            exitCode = EXIT_ERROR;\\n" +
        "            resolveCompletion();\\n" +
        "            return;\\n" +
        "        }\\n" +
        "        // The idle timer + terminal notification handle the remaining cases.\\n",
    );
  } else if (!next.includes(zeroToolMarker)) {
    throw new Error('Unable to patch dist/headless.js: zero-tool-call completion anchor not found');
  }

  return next;
});

patchFile('dist/resources/extensions/gsd/bootstrap/register-extension.js', (text) => {
  const marker = 'const minimalHeadlessBootstrap = process.env.GSD_HEADLESS_COMMAND === "new-milestone";';
  if (text.includes(marker)) {
    return text;
  }

  const importBlock =
    'import { registerGSDCommand } from "../commands.js";\n' +
    'import { registerExitCommand } from "../exit-command.js";\n' +
    'import { registerWorktreeCommand } from "../worktree-command.js";\n' +
    'import { registerDbTools } from "./db-tools.js";\n' +
    'import { registerDynamicTools } from "./dynamic-tools.js";\n' +
    'import { registerJournalTools } from "./journal-tools.js";\n' +
    'import { registerQueryTools } from "./query-tools.js";\n' +
    'import { registerHooks } from "./register-hooks.js";\n' +
    'import { registerShortcuts } from "./register-shortcuts.js";\n';
  const replacementImportBlock =
    'import { registerGSDCommand } from "../commands.js";\n' +
    'import { registerExitCommand } from "../exit-command.js";\n' +
    'import { registerDbTools } from "./db-tools.js";\n' +
    'import { registerDynamicTools } from "./dynamic-tools.js";\n' +
    'import { registerQueryTools } from "./query-tools.js";\n';
  let next = text;
  if (next.includes(importBlock)) {
    next = next.replace(importBlock, replacementImportBlock);
  }

  const functionBlock =
    'export function registerGsdExtension(pi) {\n' +
    '    registerGSDCommand(pi);\n' +
    '    registerWorktreeCommand(pi);\n' +
    '    registerExitCommand(pi);\n' +
    '    installEpipeGuard();\n' +
    '    pi.registerCommand("kill", {\n' +
    '        description: "Exit GSD immediately (no cleanup)",\n' +
    '        handler: async (_args, _ctx) => {\n' +
    '            process.exit(0);\n' +
    '        },\n' +
    '    });\n' +
    '    registerDynamicTools(pi);\n' +
    '    registerDbTools(pi);\n' +
    '    registerJournalTools(pi);\n' +
    '    registerQueryTools(pi);\n' +
    '    registerShortcuts(pi);\n' +
    '    registerHooks(pi);\n' +
    '}\n';
  const replacementFunctionBlock =
    'export async function registerGsdExtension(pi) {\n' +
    '    const minimalHeadlessBootstrap = process.env.GSD_HEADLESS_COMMAND === "new-milestone";\n' +
    '    const [{ registerGSDCommand }, { registerExitCommand }, { registerDbTools }, { registerDynamicTools }, { registerQueryTools }] = await Promise.all([\n' +
    '        import("../commands.js"),\n' +
    '        import("../exit-command.js"),\n' +
    '        import("./db-tools.js"),\n' +
    '        import("./dynamic-tools.js"),\n' +
    '        import("./query-tools.js"),\n' +
    '    ]);\n' +
    '    registerGSDCommand(pi);\n' +
    '    registerExitCommand(pi);\n' +
    '    installEpipeGuard();\n' +
    '    pi.registerCommand("kill", {\n' +
    '        description: "Exit GSD immediately (no cleanup)",\n' +
    '        handler: async (_args, _ctx) => {\n' +
    '            process.exit(0);\n' +
    '        },\n' +
    '    });\n' +
    '    registerDynamicTools(pi);\n' +
    '    registerDbTools(pi);\n' +
    '    registerQueryTools(pi);\n' +
    '    if (minimalHeadlessBootstrap) {\n' +
    '        return;\n' +
    '    }\n' +
    '    const [{ registerWorktreeCommand }, { registerJournalTools }, { registerHooks }, { registerShortcuts }] = await Promise.all([\n' +
    '        import("../worktree-command.js"),\n' +
    '        import("./journal-tools.js"),\n' +
    '        import("./register-hooks.js"),\n' +
    '        import("./register-shortcuts.js"),\n' +
    '    ]);\n' +
    '    registerWorktreeCommand(pi);\n' +
    '    registerJournalTools(pi);\n' +
    '    registerShortcuts(pi);\n' +
    '    registerHooks(pi);\n' +
    '}\n';
  if (next.includes(functionBlock)) {
    next = next.replace(functionBlock, replacementFunctionBlock);
  }

  return next;
});

patchFile('dist/resources/extensions/gsd/index.js', (text) => {
  const marker = 'await registerGsdExtension(pi);';
  if (text.includes(marker)) {
    return text;
  }

  return `export { isDepthVerified, isQueuePhaseActive, setQueuePhaseActive, shouldBlockContextWrite, shouldBlockQueueExecution, } from "./bootstrap/write-gate.js";
export default async function registerExtension(pi) {
    const { registerGsdExtension } = await import("./bootstrap/register-extension.js");
    await registerGsdExtension(pi);
}
`;
});

patchFile('packages/pi-coding-agent/dist/modes/rpc/rpc-client.js', (text) => {
  const importAnchor =
    'import { attachJsonlLineReader, serializeJsonLine } from "./jsonl.js";\n';
  const requestTimeoutMarker = 'const DEFAULT_RPC_REQUEST_TIMEOUT_MS = 240000;';
  const eventTimeoutMarker = 'const DEFAULT_RPC_EVENT_TIMEOUT_MS = 240000;';
  if (text.includes(requestTimeoutMarker) && text.includes(eventTimeoutMarker)) {
    return text;
  }

  if (!text.includes(importAnchor)) {
    throw new Error(
      'Unable to patch packages/pi-coding-agent/dist/modes/rpc/rpc-client.js: import anchor not found',
    );
  }

  let next = text;
  if (!next.includes(requestTimeoutMarker)) {
    next = next.replace(
      importAnchor,
      `${importAnchor}const DEFAULT_RPC_REQUEST_TIMEOUT_MS = 240000;\nconst DEFAULT_RPC_EVENT_TIMEOUT_MS = 240000;\n`,
    );
  }

  next = next.replace('waitForIdle(timeout = 60000)', 'waitForIdle(timeout = DEFAULT_RPC_EVENT_TIMEOUT_MS)');
  next = next.replace('collectEvents(timeout = 60000)', 'collectEvents(timeout = DEFAULT_RPC_EVENT_TIMEOUT_MS)');
  next = next.replace('promptAndWait(message, images, timeout = 60000)', 'promptAndWait(message, images, timeout = DEFAULT_RPC_EVENT_TIMEOUT_MS)');
  next = next.replace('}, 30000);', '}, DEFAULT_RPC_REQUEST_TIMEOUT_MS);');
  return next;
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

patchFile('dist/security-overrides.js', (text) => {
  const directImport =
    "import { setAllowedCommandPrefixes } from '../packages/pi-coding-agent/dist/core/resolve-config-value.js';\n";
  if (text.includes(directImport)) {
    return text;
  }

  const barrelImport = "import { setAllowedCommandPrefixes } from '@gsd/pi-coding-agent';\n";
  if (!text.includes(barrelImport)) {
    throw new Error(
      'Unable to patch dist/security-overrides.js: setAllowedCommandPrefixes import not found',
    );
  }

  return text.replace(barrelImport, directImport);
});

patchFile('packages/pi-coding-agent/dist/core/auth-storage.js', (text) => {
  const directEnvImport =
    'import { getEnvApiKey } from "../../../pi-ai/dist/env-api-keys.js";\n';
  const directOauthImport =
    'import { getOAuthApiKey, getOAuthProvider, getOAuthProviders } from "../../../pi-ai/dist/oauth.js";\n';
  let next = text;

  const barrelEnvImport = 'import { getEnvApiKey, } from "@gsd/pi-ai";\n';
  if (next.includes(barrelEnvImport)) {
    next = next.replace(barrelEnvImport, directEnvImport);
  } else if (!next.includes(directEnvImport)) {
    throw new Error(
      'Unable to patch auth-storage.js: getEnvApiKey import not found',
    );
  }

  const barrelOauthImport =
    'import { getOAuthApiKey, getOAuthProvider, getOAuthProviders } from "@gsd/pi-ai/oauth";\n';
  if (next.includes(barrelOauthImport)) {
    next = next.replace(barrelOauthImport, directOauthImport);
  } else if (!next.includes(directOauthImport)) {
    throw new Error(
      'Unable to patch auth-storage.js: OAuth import not found',
    );
  }

  return next;
});

patchFile('packages/pi-coding-agent/dist/core/model-registry.js', (text) => {
  const marker =
    '// Lazy-load pi-ai provider registration so startup does not import every provider.';
  const schemaMarker =
    '// Lazy-load Ajv/TypeBox schema setup so model-registry import stays fast when models.json is absent.';
  const replacementImport =
    'import { applyCapabilityPatches, getModels, getProviders } from "../../../pi-ai/dist/models.js";\n' +
    'import { getApiProvider, registerApiProvider } from "../../../pi-ai/dist/api-registry.js";\n' +
    'import { registerOAuthProvider, resetOAuthProviders } from "../../../pi-ai/dist/oauth.js";\n' +
    `${marker}\n` +
    'let resetApiProvidersFn;\n' +
    'let resetApiProvidersPromise;\n' +
    'async function loadResetApiProviders() {\n' +
    '    if (!resetApiProvidersPromise) {\n' +
    '        resetApiProvidersPromise = import("../../../pi-ai/dist/providers/register-builtins.js").then((module) => {\n' +
    '            resetApiProvidersFn = module.resetApiProviders;\n' +
    '            return module.resetApiProviders;\n' +
    '        });\n' +
    '    }\n' +
    '    return resetApiProvidersPromise;\n' +
    '}\n';
  let next = text;

  const barrelImport =
    'import { applyCapabilityPatches, getApiProvider, getModels, getProviders, registerApiProvider, resetApiProviders, } from "@gsd/pi-ai";\n';
  const oldPatchedImport =
    'import { applyCapabilityPatches, getModels, getProviders } from "../../../pi-ai/dist/models.js";\n' +
    'import { getApiProvider, registerApiProvider } from "../../../pi-ai/dist/api-registry.js";\n' +
    'import { registerOAuthProvider, resetOAuthProviders } from "../../../pi-ai/dist/oauth.js";\n' +
    `${marker}\n` +
    'let resetApiProvidersFn;\n' +
    'const resetApiProvidersPromise =\n' +
    '    import("../../../pi-ai/dist/providers/register-builtins.js").then((module) => {\n' +
    '        resetApiProvidersFn = module.resetApiProviders;\n' +
    '        return module.resetApiProviders;\n' +
    '    });\n' +
    'async function loadResetApiProviders() {\n' +
    '    return resetApiProvidersPromise;\n' +
    '}\n';

  if (next.includes(barrelImport)) {
    next = next.replace(barrelImport, replacementImport);
  } else if (next.includes(oldPatchedImport)) {
    next = next.replace(oldPatchedImport, replacementImport);
  } else if (!next.includes(replacementImport)) {
    throw new Error(
      'Unable to patch model-registry.js: pi-ai import block not found',
    );
  }

  const oauthImport =
    'import { registerOAuthProvider, resetOAuthProviders } from "@gsd/pi-ai/oauth";\n';
  if (next.includes(oauthImport)) {
    next = next.replace(oauthImport, '');
  }

  const createRequireImport = 'import { createRequire } from "module";\n';
  const fsImport = 'import { existsSync, readFileSync } from "fs";\n';
  if (!next.includes(createRequireImport)) {
    if (!next.includes(fsImport)) {
      throw new Error(
        'Unable to patch model-registry.js: fs import anchor not found',
      );
    }
    next = next.replace(fsImport, `${createRequireImport}${fsImport}`);
  }

  if (!next.includes(schemaMarker)) {
    const eagerSchemaBlock =
      'const Ajv = AjvModule.default || AjvModule;\n' +
      'const ajv = new Ajv();\n' +
      '// Schema for OpenRouter routing preferences\n' +
      'const OpenRouterRoutingSchema = Type.Object({\n' +
      '    only: Type.Optional(Type.Array(Type.String())),\n' +
      '    order: Type.Optional(Type.Array(Type.String())),\n' +
      '});\n' +
      '// Schema for Vercel AI Gateway routing preferences\n' +
      'const VercelGatewayRoutingSchema = Type.Object({\n' +
      '    only: Type.Optional(Type.Array(Type.String())),\n' +
      '    order: Type.Optional(Type.Array(Type.String())),\n' +
      '});\n' +
      '// Schema for OpenAI compatibility settings\n' +
      'const OpenAICompletionsCompatSchema = Type.Object({\n' +
      '    supportsStore: Type.Optional(Type.Boolean()),\n' +
      '    supportsDeveloperRole: Type.Optional(Type.Boolean()),\n' +
      '    supportsReasoningEffort: Type.Optional(Type.Boolean()),\n' +
      '    supportsUsageInStreaming: Type.Optional(Type.Boolean()),\n' +
      '    maxTokensField: Type.Optional(Type.Union([Type.Literal("max_completion_tokens"), Type.Literal("max_tokens")])),\n' +
      '    requiresToolResultName: Type.Optional(Type.Boolean()),\n' +
      '    requiresAssistantAfterToolResult: Type.Optional(Type.Boolean()),\n' +
      '    requiresThinkingAsText: Type.Optional(Type.Boolean()),\n' +
      '    requiresMistralToolIds: Type.Optional(Type.Boolean()),\n' +
      '    thinkingFormat: Type.Optional(Type.Union([Type.Literal("openai"), Type.Literal("zai"), Type.Literal("qwen")])),\n' +
      '    openRouterRouting: Type.Optional(OpenRouterRoutingSchema),\n' +
      '    vercelGatewayRouting: Type.Optional(VercelGatewayRoutingSchema),\n' +
      '});\n' +
      'const OpenAIResponsesCompatSchema = Type.Object({\n' +
      '// Reserved for future use\n' +
      '});\n' +
      'const OpenAICompatSchema = Type.Union([OpenAICompletionsCompatSchema, OpenAIResponsesCompatSchema]);\n' +
      '// Schema for custom model definition\n' +
      '// Most fields are optional with sensible defaults for local models (Ollama, LM Studio, etc.)\n' +
      'const ModelDefinitionSchema = Type.Object({\n' +
      '    id: Type.String({ minLength: 1 }),\n' +
      '    name: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '    api: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '    baseUrl: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '    reasoning: Type.Optional(Type.Boolean()),\n' +
      '    input: Type.Optional(Type.Array(Type.Union([Type.Literal("text"), Type.Literal("image")]))),\n' +
      '    cost: Type.Optional(Type.Object({\n' +
      '        input: Type.Number(),\n' +
      '        output: Type.Number(),\n' +
      '        cacheRead: Type.Number(),\n' +
      '        cacheWrite: Type.Number(),\n' +
      '    })),\n' +
      '    contextWindow: Type.Optional(Type.Number()),\n' +
      '    maxTokens: Type.Optional(Type.Number()),\n' +
      '    headers: Type.Optional(Type.Record(Type.String(), Type.String())),\n' +
      '    compat: Type.Optional(OpenAICompatSchema),\n' +
      '});\n' +
      '// Schema for per-model overrides (all fields optional, merged with built-in model)\n' +
      'const ModelOverrideSchema = Type.Object({\n' +
      '    name: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '    reasoning: Type.Optional(Type.Boolean()),\n' +
      '    input: Type.Optional(Type.Array(Type.Union([Type.Literal("text"), Type.Literal("image")]))),\n' +
      '    cost: Type.Optional(Type.Object({\n' +
      '        input: Type.Optional(Type.Number()),\n' +
      '        output: Type.Optional(Type.Number()),\n' +
      '        cacheRead: Type.Optional(Type.Number()),\n' +
      '        cacheWrite: Type.Optional(Type.Number()),\n' +
      '    })),\n' +
      '    contextWindow: Type.Optional(Type.Number()),\n' +
      '    maxTokens: Type.Optional(Type.Number()),\n' +
      '    headers: Type.Optional(Type.Record(Type.String(), Type.String())),\n' +
      '    compat: Type.Optional(OpenAICompatSchema),\n' +
      '});\n' +
      'const ProviderConfigSchema = Type.Object({\n' +
      '    baseUrl: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '    apiKey: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '    api: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '    headers: Type.Optional(Type.Record(Type.String(), Type.String())),\n' +
      '    authHeader: Type.Optional(Type.Boolean()),\n' +
      '    models: Type.Optional(Type.Array(ModelDefinitionSchema)),\n' +
      '    modelOverrides: Type.Optional(Type.Record(Type.String(), ModelOverrideSchema)),\n' +
      '});\n' +
      'const ModelsConfigSchema = Type.Object({\n' +
      '    providers: Type.Record(Type.String(), ProviderConfigSchema),\n' +
      '});\n' +
      'ajv.addSchema(ModelsConfigSchema, "ModelsConfig");\n';
    const lazySchemaBlock =
      `${schemaMarker}\n` +
      'const require = createRequire(import.meta.url);\n' +
      'let modelsConfigSchemaValidator;\n' +
      'function getModelsConfigSchemaValidator() {\n' +
      '    if (!modelsConfigSchemaValidator) {\n' +
      '        const { Type } = require("@sinclair/typebox");\n' +
      '        const AjvModule = require("ajv");\n' +
      '        const Ajv = AjvModule.default || AjvModule;\n' +
      '        const ajv = new Ajv();\n' +
      '        const OpenRouterRoutingSchema = Type.Object({\n' +
      '            only: Type.Optional(Type.Array(Type.String())),\n' +
      '            order: Type.Optional(Type.Array(Type.String())),\n' +
      '        });\n' +
      '        const VercelGatewayRoutingSchema = Type.Object({\n' +
      '            only: Type.Optional(Type.Array(Type.String())),\n' +
      '            order: Type.Optional(Type.Array(Type.String())),\n' +
      '        });\n' +
      '        const OpenAICompletionsCompatSchema = Type.Object({\n' +
      '            supportsStore: Type.Optional(Type.Boolean()),\n' +
      '            supportsDeveloperRole: Type.Optional(Type.Boolean()),\n' +
      '            supportsReasoningEffort: Type.Optional(Type.Boolean()),\n' +
      '            supportsUsageInStreaming: Type.Optional(Type.Boolean()),\n' +
      '            maxTokensField: Type.Optional(Type.Union([Type.Literal("max_completion_tokens"), Type.Literal("max_tokens")])),\n' +
      '            requiresToolResultName: Type.Optional(Type.Boolean()),\n' +
      '            requiresAssistantAfterToolResult: Type.Optional(Type.Boolean()),\n' +
      '            requiresThinkingAsText: Type.Optional(Type.Boolean()),\n' +
      '            requiresMistralToolIds: Type.Optional(Type.Boolean()),\n' +
      '            thinkingFormat: Type.Optional(Type.Union([Type.Literal("openai"), Type.Literal("zai"), Type.Literal("qwen")])),\n' +
      '            openRouterRouting: Type.Optional(OpenRouterRoutingSchema),\n' +
      '            vercelGatewayRouting: Type.Optional(VercelGatewayRoutingSchema),\n' +
      '        });\n' +
      '        const OpenAIResponsesCompatSchema = Type.Object({\n' +
      '        // Reserved for future use\n' +
      '        });\n' +
      '        const OpenAICompatSchema = Type.Union([OpenAICompletionsCompatSchema, OpenAIResponsesCompatSchema]);\n' +
      '        const ModelDefinitionSchema = Type.Object({\n' +
      '            id: Type.String({ minLength: 1 }),\n' +
      '            name: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '            api: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '            baseUrl: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '            reasoning: Type.Optional(Type.Boolean()),\n' +
      '            input: Type.Optional(Type.Array(Type.Union([Type.Literal("text"), Type.Literal("image")]))),\n' +
      '            cost: Type.Optional(Type.Object({\n' +
      '                input: Type.Number(),\n' +
      '                output: Type.Number(),\n' +
      '                cacheRead: Type.Number(),\n' +
      '                cacheWrite: Type.Number(),\n' +
      '            })),\n' +
      '            contextWindow: Type.Optional(Type.Number()),\n' +
      '            maxTokens: Type.Optional(Type.Number()),\n' +
      '            headers: Type.Optional(Type.Record(Type.String(), Type.String())),\n' +
      '            compat: Type.Optional(OpenAICompatSchema),\n' +
      '        });\n' +
      '        const ModelOverrideSchema = Type.Object({\n' +
      '            name: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '            reasoning: Type.Optional(Type.Boolean()),\n' +
      '            input: Type.Optional(Type.Array(Type.Union([Type.Literal("text"), Type.Literal("image")]))),\n' +
      '            cost: Type.Optional(Type.Object({\n' +
      '                input: Type.Optional(Type.Number()),\n' +
      '                output: Type.Optional(Type.Number()),\n' +
      '                cacheRead: Type.Optional(Type.Number()),\n' +
      '                cacheWrite: Type.Optional(Type.Number()),\n' +
      '            })),\n' +
      '            contextWindow: Type.Optional(Type.Number()),\n' +
      '            maxTokens: Type.Optional(Type.Number()),\n' +
      '            headers: Type.Optional(Type.Record(Type.String(), Type.String())),\n' +
      '            compat: Type.Optional(OpenAICompatSchema),\n' +
      '        });\n' +
      '        const ProviderConfigSchema = Type.Object({\n' +
      '            baseUrl: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '            apiKey: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '            api: Type.Optional(Type.String({ minLength: 1 })),\n' +
      '            headers: Type.Optional(Type.Record(Type.String(), Type.String())),\n' +
      '            authHeader: Type.Optional(Type.Boolean()),\n' +
      '            models: Type.Optional(Type.Array(ModelDefinitionSchema)),\n' +
      '            modelOverrides: Type.Optional(Type.Record(Type.String(), ModelOverrideSchema)),\n' +
      '        });\n' +
      '        const ModelsConfigSchema = Type.Object({\n' +
      '            providers: Type.Record(Type.String(), ProviderConfigSchema),\n' +
      '        });\n' +
      '        ajv.addSchema(ModelsConfigSchema, "ModelsConfig");\n' +
      '        modelsConfigSchemaValidator = ajv.getSchema("ModelsConfig");\n' +
      '    }\n' +
      '    return modelsConfigSchemaValidator;\n' +
      '}\n';

    const eagerTypeImport = 'import { Type } from "@sinclair/typebox";\n';
    const eagerAjvImport = 'import AjvModule from "ajv";\n';
    if (next.includes(eagerTypeImport)) {
      next = next.replace(eagerTypeImport, '');
    }
    if (next.includes(eagerAjvImport)) {
      next = next.replace(eagerAjvImport, '');
    }
    if (!next.includes(eagerSchemaBlock)) {
      throw new Error(
        'Unable to patch model-registry.js: eager schema block not found',
      );
    }
    next = next.replace(eagerSchemaBlock, lazySchemaBlock);
  }

  const eagerValidatorUsage = '            const validate = ajv.getSchema("ModelsConfig");\n';
  if (next.includes(eagerValidatorUsage)) {
    next = next.replace(
      eagerValidatorUsage,
      '            const validate = getModelsConfigSchemaValidator();\n',
    );
  } else if (!next.includes('const validate = getModelsConfigSchemaValidator();')) {
    throw new Error(
      'Unable to patch model-registry.js: schema validator usage not found',
    );
  }

  const headlessSchemaBypassOriginal =
    '            // Validate schema\n' +
    '            const validate = getModelsConfigSchemaValidator();\n' +
    '            if (!validate(config)) {\n' +
    '                const errors = validate.errors?.map((e) => `  - ${e.instancePath || "root"}: ${e.message}`).join("\\n") ||\n' +
    '                    "Unknown schema error";\n' +
    '                return emptyCustomModelsResult(`Invalid models.json schema:\\n${errors}\\n\\nFile: ${modelsJsonPath}`);\n' +
    '            }\n';
  const headlessSchemaBypassPatched =
    '            // Ajv/TypeBox schema setup is very slow on Windows-mounted WSL paths.\n' +
    '            // Headless runs validate shape below and should not block RPC bootstrap.\n' +
    '            if (process.env.GSD_HEADLESS !== "1") {\n' +
    '                const validate = getModelsConfigSchemaValidator();\n' +
    '                if (!validate(config)) {\n' +
    '                    const errors = validate.errors?.map((e) => `  - ${e.instancePath || "root"}: ${e.message}`).join("\\n") ||\n' +
    '                        "Unknown schema error";\n' +
    '                    return emptyCustomModelsResult(`Invalid models.json schema:\\n${errors}\\n\\nFile: ${modelsJsonPath}`);\n' +
    '                }\n' +
    '            }\n';
  if (next.includes(headlessSchemaBypassOriginal)) {
    next = next.replace(headlessSchemaBypassOriginal, headlessSchemaBypassPatched);
  } else if (!next.includes('process.env.GSD_HEADLESS !== "1"')) {
    throw new Error('Unable to patch model-registry.js: headless schema bypass block not found');
  }

  const originalRefreshBody =
    '        resetApiProviders();\n' +
    '        resetOAuthProviders();\n' +
    '        this.loadModels();\n' +
    '        for (const [providerName, config] of this.registeredProviders.entries()) {\n' +
    '            this.applyProviderConfig(providerName, config);\n' +
    '        }\n';
  const patchedRefreshBody =
    '        if (!resetApiProvidersFn) {\n' +
    '            void loadResetApiProviders().then((resetApiProviders) => {\n' +
    '                resetApiProviders();\n' +
    '                resetOAuthProviders();\n' +
    '                this.loadModels();\n' +
    '                for (const [providerName, config] of this.registeredProviders.entries()) {\n' +
    '                    this.applyProviderConfig(providerName, config);\n' +
    '                }\n' +
    '            });\n' +
    '            return;\n' +
    '        }\n' +
    '        resetApiProvidersFn();\n' +
    '        resetOAuthProviders();\n' +
    '        this.loadModels();\n' +
    '        for (const [providerName, config] of this.registeredProviders.entries()) {\n' +
    '            this.applyProviderConfig(providerName, config);\n' +
    '        }\n';
  if (next.includes(originalRefreshBody)) {
    next = next.replace(originalRefreshBody, patchedRefreshBody);
  } else if (!next.includes(patchedRefreshBody)) {
    throw new Error(
      'Unable to patch model-registry.js: refresh body not found',
    );
  }

  return next;
});

patchFile('packages/pi-coding-agent/dist/modes/rpc/rpc-client.js', (text) => {
  let next = text;
  const spawnDebugOriginal =
    '        this.process = spawn("node", [cliPath, ...args], {\n';
  const spawnDebugPatched =
    '        if (process.env.GSD_DEBUG === "1") {\n' +
    '            process.stderr.write(`[rpc-client] spawn: node ${[cliPath, ...args].join(" ")} cwd=${this.options.cwd ?? process.cwd()}\\n`);\n' +
    '        }\n' +
    '        this.process = spawn("node", [cliPath, ...args], {\n';
  if (next.includes(spawnDebugOriginal)) {
    next = next.replace(spawnDebugOriginal, spawnDebugPatched);
  } else if (!next.includes('[rpc-client] spawn: node')) {
    throw new Error('Unable to patch rpc-client.js: spawn debug anchor not found');
  }

  const pidDebugOriginal =
    '        });\n' +
    '        // Collect stderr for debugging\n';
  const pidDebugPatched =
    '        });\n' +
    '        if (process.env.GSD_DEBUG === "1") {\n' +
    '            process.stderr.write(`[rpc-client] child pid: ${this.process.pid ?? "unknown"}\\n`);\n' +
    '        }\n' +
    '        // Collect stderr for debugging\n';
  if (next.includes(pidDebugOriginal)) {
    next = next.replace(pidDebugOriginal, pidDebugPatched);
  } else if (!next.includes('[rpc-client] child pid:')) {
    throw new Error('Unable to patch rpc-client.js: pid debug anchor not found');
  }

  const stderrForwardOriginal =
    '        this._stderrHandler = (data) => {\n' +
    '            this.stderr += data.toString();\n' +
    '        };\n';
  const stderrForwardPatched =
    '        this._stderrHandler = (data) => {\n' +
    '            const chunk = data.toString();\n' +
    '            this.stderr += chunk;\n' +
    '            if (process.env.GSD_DEBUG === "1") {\n' +
    '                process.stderr.write(chunk);\n' +
    '            }\n' +
    '        };\n';
  if (next.includes(stderrForwardOriginal)) {
    next = next.replace(stderrForwardOriginal, stderrForwardPatched);
  } else if (!next.includes('const chunk = data.toString();')) {
    throw new Error('Unable to patch rpc-client.js: stderr forward block not found');
  }

  const timeoutOriginal =
    '            const timeout = setTimeout(() => {\n' +
    '                this.pendingRequests.delete(id);\n' +
    '                reject(new Error(`Timeout waiting for response to ${command.type}. Stderr: ${this.stderr}`));\n' +
    '            }, DEFAULT_RPC_REQUEST_TIMEOUT_MS);\n';
  const timeoutPatched =
    '            const requestTimeoutMs = this.options.requestTimeoutMs ?? DEFAULT_RPC_REQUEST_TIMEOUT_MS;\n' +
    '            const timeout = setTimeout(() => {\n' +
    '                this.pendingRequests.delete(id);\n' +
    '                reject(new Error(`Timeout waiting for response to ${command.type}. Stderr: ${this.stderr}`));\n' +
    '            }, requestTimeoutMs);\n';
  if (next.includes(timeoutOriginal)) {
    next = next.replace(timeoutOriginal, timeoutPatched);
  } else if (!next.includes('this.options.requestTimeoutMs ?? DEFAULT_RPC_REQUEST_TIMEOUT_MS')) {
    throw new Error('Unable to patch rpc-client.js: request timeout block not found');
  }
  return next;
});

patchFile('packages/pi-coding-agent/dist/core/resource-loader.js', (text) => {
  let next = text;
  if (!next.includes('headlessExtensionAllowlist')) {
    const loadExtensionsAnchor =
      '        const { loadExtensions } = await loadExtensionsLoaderModule();\n' +
      '        const extensionsResult = await loadExtensions(extensionPaths, this.cwd, this.eventBus);\n';
    const patchedLoadExtensions =
      '        if (process.env.GSD_HEADLESS === "1" && ["auto", "next", "new-milestone"].includes(process.env.GSD_HEADLESS_COMMAND ?? "")) {\n' +
      '            const headlessExtensionAllowlist = new Set([\n' +
      '                "gsd",\n' +
      '                "slash-commands",\n' +
      '            ]);\n' +
      '            const extensionKey = (entryPath) => {\n' +
      '                const normalized = resolve(entryPath);\n' +
      '                const file = basename(normalized).replace(/\\.(?:mjs|cjs|js|ts)$/i, "");\n' +
      '                return file === "index" ? basename(dirname(normalized)) : file;\n' +
      '            };\n' +
      '            extensionPaths = extensionPaths.filter((entryPath) => headlessExtensionAllowlist.has(extensionKey(entryPath)));\n' +
      '        }\n' +
      loadExtensionsAnchor;
    if (next.includes(loadExtensionsAnchor)) {
      next = next.replace(loadExtensionsAnchor, patchedLoadExtensions);
    } else if (!next.includes('loading extensions (${extensionPaths.length})')) {
      throw new Error('Unable to patch resource-loader.js: loadExtensions anchor not found');
    }
  }
  return next;
});

patchFile('dist/resources/extensions/gsd/auto-prompts.js', (text) => {
  const pattern = /import \{\s*getLoadedSkills(?:,\s*type\s+Skill)?\s*\}\s+from\s+["'][^"']+["'];/;
  if (!pattern.test(text)) {
    throw new Error('Unable to patch dist/resources/extensions/gsd/auto-prompts.js: getLoadedSkills import not found');
  }
  let next = text.replace(pattern, 'import { getLoadedSkills } from "@gsd/pi-coding-agent";');
  next = next.replace('const MAX_PREAMBLE_CHARS = 30_000;', 'const MAX_PREAMBLE_CHARS = 12_000;');
  if (!next.includes('executionModelId?.startsWith("ollama/")')) {
    next = next.replace(
      '        windowTokens = resolveExecutorContextWindow(undefined, prefs?.preferences);\n',
      '        windowTokens = resolveExecutorContextWindow(undefined, prefs?.preferences);\n' +
        '        const executionModel = prefs?.preferences?.models?.execution;\n' +
        '        const executionModelId = typeof executionModel === "string"\n' +
        '            ? executionModel\n' +
        '            : executionModel?.model;\n' +
        '        if (executionModelId?.startsWith("ollama/") && windowTokens >= 200_000) {\n' +
        '            windowTokens = 8192;\n' +
        '        }\n',
    );
  }
  if (!next.includes('### Slice Plan Output Shape')) {
    next = next.replace(
      '    inlined.push(inlineTemplate("plan", "Slice Plan"));\n' +
        '    if (inlineLevel === "full") {\n',
      '    if (inlineLevel === "minimal") {\n' +
        '        inlined.push([\n' +
        '            "### Slice Plan Output Shape",\n' +
        '            "Call `gsd_plan_slice` with: goal, demo, must_haves, verification, tasks, and metadata.",\n' +
        '            "Each task needs title, why, files, steps, verify command, done_when, inputs, and expected_output.",\n' +
        '            "Use concrete backtick-wrapped file paths.",\n' +
        '        ].join("\\n"));\n' +
        '    }\n' +
        '    else {\n' +
        '        inlined.push(inlineTemplate("plan", "Slice Plan"));\n' +
        '    }\n' +
        '    if (inlineLevel === "full") {\n',
    );
  }
  return next;
});

patchFile('src/resources/extensions/gsd/auto-prompts.ts', (text) => {
  const pattern = /import \{\s*getLoadedSkills(?:,\s*type\s+Skill)?\s*\}\s+from\s+["'][^"']+["'];/;
  if (!pattern.test(text)) {
    throw new Error('Unable to patch src/resources/extensions/gsd/auto-prompts.ts: getLoadedSkills import not found');
  }
  let next = text.replace(pattern, 'import { getLoadedSkills, type Skill } from "@gsd/pi-coding-agent";');
  next = next.replace('const MAX_PREAMBLE_CHARS = 30_000;', 'const MAX_PREAMBLE_CHARS = 12_000;');
  if (!next.includes('executionModelId?.startsWith("ollama/")')) {
    next = next.replace(
      '    windowTokens = resolveExecutorContextWindow(undefined, prefs?.preferences);\n',
      '    windowTokens = resolveExecutorContextWindow(undefined, prefs?.preferences);\n' +
        '    const executionModel = prefs?.preferences?.models?.execution;\n' +
        '    const executionModelId = typeof executionModel === "string"\n' +
        '      ? executionModel\n' +
        '      : executionModel?.model;\n' +
        '    if (executionModelId?.startsWith("ollama/") && windowTokens >= 200_000) {\n' +
        '      windowTokens = 8192;\n' +
        '    }\n',
    );
  }
  if (!next.includes('### Slice Plan Output Shape')) {
    next = next.replace(
      '  inlined.push(inlineTemplate("plan", "Slice Plan"));\n' +
        '  if (inlineLevel === "full") {\n',
      '  if (inlineLevel === "minimal") {\n' +
        '    inlined.push([\n' +
        '      "### Slice Plan Output Shape",\n' +
        '      "Call `gsd_plan_slice` with: goal, demo, must_haves, verification, tasks, and metadata.",\n' +
        '      "Each task needs title, why, files, steps, verify command, done_when, inputs, and expected_output.",\n' +
        '      "Use concrete backtick-wrapped file paths.",\n' +
        '    ].join("\\n"));\n' +
        '  } else {\n' +
        '    inlined.push(inlineTemplate("plan", "Slice Plan"));\n' +
        '  }\n' +
        '  if (inlineLevel === "full") {\n',
    );
  }
  return next;
});

const COMPACT_PLAN_SLICE_PROMPT = `You are executing GSD auto-mode.

## UNIT
Plan slice {{sliceId}} ("{{sliceTitle}}") for milestone {{milestoneId}}.

## Working Directory
Use only \`{{workingDirectory}}\`. Do not \`cd\` elsewhere.

## Context
{{inlinedContext}}

## Dependency Summaries
{{dependencySummaries}}

## Source Files
{{sourceFilePaths}}

{{executorContextConstraints}}

## Required Action
You MUST call \`gsd_plan_slice\`. Do not answer with a markdown plan only.

Plan the smallest real slice that closes the roadmap item:
- preserve legacy parity from \`menubar.xml\`
- treat \`remeres-map-editor-redux/data/menubar.xml\` as read-only source of truth
- "close" a legacy menu group means expose, wire, test, or document gaps in PyRME; never delete legacy XML entries
- do not invent new shell taxonomy
- do not plan destructive edits to legacy reference files
- use concrete file paths
- include executable verification commands
- keep backend gaps explicit and safe

Each task object must use these exact camelCase fields:
- \`taskId\`: "T01", "T02", ...
- \`title\`: short action title
- \`description\`: include why, steps, must-haves, and done-when text
- \`estimate\`: short estimate like "10m"
- \`files\`: array of concrete file paths
- \`verify\`: executable command or concrete manual check
- \`inputs\`: array of concrete file paths
- \`expectedOutput\`: array of concrete output file paths/artifacts
- \`observabilityImpact\`: optional string

Do not use snake_case keys. Do not use \`verification\`; use \`verify\`. Do not use \`expected_output\`; use \`expectedOutput\`.

Use \`{{outputPath}}\` as the rendered slice plan path. The tool will write task plans under \`{{slicePath}}/tasks/\`.

Do not call \`ask_user_questions\` or \`secure_env_collect\`.
{{commitInstruction}}

When the tool call is done, say: "Slice {{sliceId}} planned."
`;

patchFile('dist/resources/extensions/gsd/prompts/plan-slice.md', () => COMPACT_PLAN_SLICE_PROMPT);
patchFile('src/resources/extensions/gsd/prompts/plan-slice.md', () => COMPACT_PLAN_SLICE_PROMPT);

patchFile('dist/resources/extensions/gsd/bootstrap/db-tools.js', (text) => {
  if (text.includes('toolDef?.name === "gsd_plan_slice"')) return text;
  return text.replace(
    'export function registerDbTools(pi) {\n',
    'export function registerDbTools(pi) {\n' +
      '    if (process.env.GSD_HEADLESS === "1" && process.env.GSD_HEADLESS_COMMAND === "auto") {\n' +
      '        const originalRegisterTool = pi.registerTool.bind(pi);\n' +
      '        pi = {\n' +
      '            ...pi,\n' +
      '            registerTool(toolDef) {\n' +
      '                if (toolDef?.name === "gsd_plan_slice") {\n' +
      '                    originalRegisterTool(toolDef);\n' +
      '                }\n' +
      '            },\n' +
      '        };\n' +
      '    }\n',
  );
});

patchFile('src/resources/extensions/gsd/bootstrap/db-tools.ts', (text) => {
  if (text.includes('toolDef?.name === "gsd_plan_slice"')) return text;
  return text.replace(
    'export function registerDbTools(pi: ExtensionAPI): void {\n',
    'export function registerDbTools(pi: ExtensionAPI): void {\n' +
      '  if (process.env.GSD_HEADLESS === "1" && process.env.GSD_HEADLESS_COMMAND === "auto") {\n' +
      '    const originalRegisterTool = pi.registerTool.bind(pi);\n' +
      '    pi = {\n' +
      '      ...pi,\n' +
      '      registerTool(toolDef) {\n' +
      '        if (toolDef?.name === "gsd_plan_slice") {\n' +
      '          originalRegisterTool(toolDef);\n' +
      '        }\n' +
      '      },\n' +
      '    } as ExtensionAPI;\n' +
      '  }\n',
  );
});

patchFile('dist/resources/extensions/gsd/bootstrap/register-extension.js', (text) => {
  if (text.includes('originalRegisterTool = pi.registerTool.bind(pi)')) return text;
  return text.replace(
    '    registerDynamicTools(pi);\n',
    '    if (process.env.GSD_HEADLESS === "1" && process.env.GSD_HEADLESS_COMMAND === "auto") {\n' +
      '        const originalRegisterTool = pi.registerTool.bind(pi);\n' +
      '        pi = {\n' +
      '            ...pi,\n' +
      '            registerTool(toolDef) {\n' +
      '                if (toolDef?.name === "gsd_plan_slice") {\n' +
      '                    originalRegisterTool(toolDef);\n' +
      '                }\n' +
      '            },\n' +
      '        };\n' +
      '    }\n' +
      '    registerDynamicTools(pi);\n',
  );
});

patchFile('src/resources/extensions/gsd/bootstrap/register-extension.ts', (text) => {
  if (text.includes('originalRegisterTool = pi.registerTool.bind(pi)')) return text;
  return text.replace(
    '  registerDynamicTools(pi);\n',
    '  if (process.env.GSD_HEADLESS === "1" && process.env.GSD_HEADLESS_COMMAND === "auto") {\n' +
      '    const originalRegisterTool = pi.registerTool.bind(pi);\n' +
      '    pi = {\n' +
      '      ...pi,\n' +
      '      registerTool(toolDef) {\n' +
      '        if (toolDef?.name === "gsd_plan_slice") {\n' +
      '          originalRegisterTool(toolDef);\n' +
      '        }\n' +
      '      },\n' +
      '    } as ExtensionAPI;\n' +
      '  }\n' +
      '\n' +
      '  registerDynamicTools(pi);\n',
  );
});

patchFile('packages/pi-coding-agent/dist/core/agent-session.js', (text) => {
  if (text.includes('headlessAutoGsdOnly')) return text;
  return text.replace(
    '        const defaultActiveToolNames = this._baseToolsOverride\n' +
      '            ? Object.keys(this._baseToolsOverride)\n' +
      '            : ["read", "bash", "edit", "write", "lsp"];\n',
      '        const headlessAutoGsdOnly = process.env.GSD_HEADLESS === "1" && process.env.GSD_HEADLESS_COMMAND === "auto";\n' +
      '        const defaultActiveToolNames = headlessAutoGsdOnly\n' +
      '            ? ["gsd_plan_slice"]\n' +
      '            : this._baseToolsOverride\n' +
      '            ? Object.keys(this._baseToolsOverride)\n' +
      '            : ["read", "bash", "edit", "write", "lsp"];\n',
  );
});

patchFile('packages/pi-coding-agent/dist/core/agent-session.js', (text) => {
  if (text.includes('const baseActiveToolNames = headlessAutoGsdOnly')) return text;
  return text.replace(
    '        const baseActiveToolNames = options.activeToolNames ?? defaultActiveToolNames;\n',
    '        const baseActiveToolNames = headlessAutoGsdOnly\n' +
      '            ? ["gsd_plan_slice"]\n' +
      '            : options.activeToolNames ?? defaultActiveToolNames;\n',
  );
});

patchFile('packages/pi-coding-agent/src/core/agent-session.ts', (text) => {
  if (text.includes('headlessAutoGsdOnly')) return text;
  return text.replace(
    '\t\tconst defaultActiveToolNames = this._baseToolsOverride\n' +
      '\t\t\t? Object.keys(this._baseToolsOverride)\n' +
      '\t\t\t: ["read", "bash", "edit", "write", "lsp"];\n',
      '\t\tconst headlessAutoGsdOnly =\n' +
      '\t\t\tprocess.env.GSD_HEADLESS === "1" && process.env.GSD_HEADLESS_COMMAND === "auto";\n' +
      '\t\tconst defaultActiveToolNames = headlessAutoGsdOnly\n' +
      '\t\t\t? ["gsd_plan_slice"]\n' +
      '\t\t\t: this._baseToolsOverride\n' +
      '\t\t\t? Object.keys(this._baseToolsOverride)\n' +
      '\t\t\t: ["read", "bash", "edit", "write", "lsp"];\n',
  );
});

patchFile('packages/pi-coding-agent/src/core/agent-session.ts', (text) => {
  if (text.includes('const baseActiveToolNames = headlessAutoGsdOnly')) return text;
  return text.replace(
    '\t\tconst baseActiveToolNames = options.activeToolNames ?? defaultActiveToolNames;\n',
    '\t\tconst baseActiveToolNames = headlessAutoGsdOnly\n' +
      '\t\t\t? ["gsd_plan_slice"]\n' +
    '\t\t\t: options.activeToolNames ?? defaultActiveToolNames;\n',
  );
});

ensurePiCodingAgentAlias();
ensureNativeShim();
ensureGsdInternalWorkspacePackages();
writeBundledResourceFingerprint();

if (patchedFiles.length > 0) {
  process.stdout.write(`[gsd-pi] patched ${patchedFiles.length} file(s): ${patchedFiles.join(', ')}\n`);
} else {
  process.stdout.write('[gsd-pi] postinstall check complete\n');
}
