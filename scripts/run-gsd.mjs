#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = dirname(scriptDir);
const gsdHome = join(repoRoot, '.gsd');
const gsdBinary = join(
  repoRoot,
  'node_modules',
  '.bin',
  process.platform === 'win32' ? 'gsd.cmd' : 'gsd',
);

mkdirSync(gsdHome, { recursive: true });

const env = {
  ...process.env,
  GSD_HOME: process.env.GSD_HOME || gsdHome,
};

const result = spawnSync(gsdBinary, process.argv.slice(2), {
  cwd: repoRoot,
  env,
  stdio: 'inherit',
});

if (result.error) {
  console.error(`[gsd] Failed to launch ${gsdBinary}: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
