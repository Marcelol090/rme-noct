#!/usr/bin/env node

import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = dirname(scriptDir);
const gsdHome = join(repoRoot, '.gsd');
const loaderPath = join(repoRoot, 'node_modules', 'gsd-pi', 'dist', 'loader.js');

function appendDefaultOption(args, option, value) {
  if (!args.some((arg) => arg === option || arg.startsWith(`${option}=`))) {
    args.push(option, value);
  }
}

mkdirSync(gsdHome, { recursive: true });

const env = {
  ...process.env,
  GSD_HOME: process.env.GSD_HOME || gsdHome,
};

const patchResult = spawnSync(process.execPath, [join(scriptDir, 'patch-gsd-pi.mjs')], {
  cwd: repoRoot,
  env,
  shell: false,
  stdio: 'inherit',
  windowsHide: true,
});

if (patchResult.error) {
  console.error(`[gsd] Patch bootstrap failed: ${patchResult.error.message}`);
  process.exit(1);
}

if ((patchResult.status ?? 1) !== 0) {
  console.error('? gsd-pi patch failed. Rode node scripts/patch-gsd-pi.mjs para detalhes.');
  process.exit(1);
}

console.log('preflight: validating stack...');
const preflightResult = spawnSync('npm', ['run', 'preflight', '--silent'], {
  cwd: repoRoot,
  env,
  shell: false,
  stdio: 'inherit',
  windowsHide: true,
});

if (preflightResult.error) {
  console.error(`[gsd] Preflight launch failed: ${preflightResult.error.message}`);
  process.exit(1);
}

if ((preflightResult.status ?? 1) !== 0) {
  console.error('preflight failed. Rode npm run preflight para detalhes.');
  process.exit(1);
}

if (!existsSync(loaderPath)) {
  console.error(`[gsd] Loader not found: ${loaderPath}`);
  process.exit(1);
}

const gsdArgs = ['headless', 'auto', ...process.argv.slice(2)];
appendDefaultOption(gsdArgs, '--timeout', '600000');
appendDefaultOption(gsdArgs, '--response-timeout', '420000');
appendDefaultOption(gsdArgs, '--max-restarts', '0');

console.log('stack ok, iniciando gsd:auto');

const child = spawn(process.execPath, [loaderPath, ...gsdArgs], {
  cwd: repoRoot,
  env,
  shell: false,
  stdio: 'inherit',
  windowsHide: true,
});

const exitCode = await new Promise((resolve) => {
  child.once('error', (error) => {
    console.error(`[gsd] Failed to launch ${loaderPath}: ${error.message}`);
    resolve(1);
  });
  child.once('exit', (code, signal) => {
    if (signal) {
      resolve(1);
      return;
    }
    resolve(code ?? 1);
  });
});

process.exit(exitCode);
