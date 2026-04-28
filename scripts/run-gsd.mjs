#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = dirname(scriptDir);
const gsdHome = join(repoRoot, '.gsd');
const gsdCmdShim = join(
  repoRoot,
  'node_modules',
  '.bin',
  process.platform === 'win32' ? 'gsd.cmd' : 'gsd',
);
const gsdLoader = join(repoRoot, 'node_modules', 'gsd-pi', 'dist', 'loader.js');

const command = existsSync(gsdLoader) ? process.execPath : gsdCmdShim;
const args = existsSync(gsdLoader)
  ? [gsdLoader, ...process.argv.slice(2)]
  : process.argv.slice(2);

mkdirSync(gsdHome, { recursive: true });

const env = {
  ...process.env,
  GSD_HOME: process.env.GSD_HOME || gsdHome,
};

const result = spawnSync(command, args, {
  cwd: repoRoot,
  env,
  stdio: 'inherit',
});

if (result.error) {
  console.error(`[gsd] Failed to launch ${command}: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
