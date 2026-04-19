#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = dirname(scriptDir);

const candidates = process.platform === 'win32'
  ? [
      { command: join(repoRoot, '.venv', 'Scripts', 'python.exe'), prefix: [] },
      { command: 'py', prefix: ['-3'] },
      { command: 'python', prefix: [] },
    ]
  : [
      { command: join(repoRoot, '.venv', 'bin', 'python3.12'), prefix: [] },
      { command: join(repoRoot, '.venv', 'bin', 'python3'), prefix: [] },
      { command: 'python3.12', prefix: [] },
      { command: 'python3', prefix: [] },
      { command: 'python', prefix: [] },
    ];

function isPathCommand(command) {
  return command.includes('/') || command.includes('\\');
}

function probeCandidate({ command, prefix }) {
  if (isPathCommand(command) && !existsSync(command)) {
    return false;
  }

  const probe = spawnSync(command, [...prefix, '-c', 'import sys'], {
    cwd: repoRoot,
    stdio: 'ignore',
    env: process.env,
  });
  return !probe.error && probe.status === 0;
}

const selected = candidates.find(probeCandidate);

if (!selected) {
  console.error('[python-launcher] No usable Python interpreter was found.');
  process.exit(1);
}

const result = spawnSync(
  selected.command,
  [...selected.prefix, ...process.argv.slice(2)],
  {
    cwd: repoRoot,
    stdio: 'inherit',
    env: process.env,
  },
);

if (result.error) {
  console.error(
    `[python-launcher] Failed to launch ${selected.command}: ${result.error.message}`,
  );
  process.exit(1);
}

process.exit(result.status ?? 1);
