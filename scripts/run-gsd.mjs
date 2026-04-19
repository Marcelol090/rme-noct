#!/usr/bin/env node

import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = dirname(scriptDir);
const gsdHome = join(repoRoot, '.gsd');
function resolveGsdCommand(args = process.argv.slice(2)) {
  const binDir = join(repoRoot, 'node_modules', '.bin');
  const loaderPath = join(repoRoot, 'node_modules', 'gsd-pi', 'dist', 'loader.js');
  const candidates = process.platform === 'win32'
    ? [join(binDir, 'gsd.cmd'), loaderPath, join(binDir, 'gsd')]
    : [loaderPath, join(binDir, 'gsd')];

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      if (process.platform === 'win32' && candidate.endsWith('.cmd')) {
        return {
          command: candidate,
          args,
          shell: true,
        };
      }

      if (candidate.endsWith('.js')) {
        return {
          command: process.execPath,
          args: [candidate, ...args],
          shell: false,
        };
      }

      return {
        command: candidate,
        args,
        shell: false,
      };
    }
  }

  return {
    command: process.platform === 'win32' ? join(binDir, 'gsd.cmd') : join(binDir, 'gsd'),
    args,
    shell: process.platform === 'win32',
  };
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

const gsdArgs = process.argv.slice(2);
const isHeadlessAuto = gsdArgs[0] === 'headless' && gsdArgs[1] === 'auto';
const effectiveGsdArgs = [...gsdArgs];

function appendDefaultOption(args, option, value) {
  if (!args.some((arg) => arg === option || arg.startsWith(`${option}=`))) {
    args.push(option, value);
  }
}

if (isHeadlessAuto) {
  appendDefaultOption(effectiveGsdArgs, '--timeout', '600000');
  appendDefaultOption(effectiveGsdArgs, '--response-timeout', '420000');
  appendDefaultOption(effectiveGsdArgs, '--max-restarts', '0');

  console.log('→ preflight: validating stack...');
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
    console.error('✗ preflight failed. Rode npm run preflight para detalhes.');
    process.exit(1);
  }

  console.log('✓ stack ok, iniciando gsd:auto');
}

const gsdCommand = resolveGsdCommand(effectiveGsdArgs);
const child = spawn(gsdCommand.command, gsdCommand.args, {
  cwd: repoRoot,
  env,
  shell: gsdCommand.shell,
  stdio: 'inherit',
  windowsHide: true,
});

const exitCode = await new Promise((resolve) => {
  child.once('error', (error) => {
    console.error(`[gsd] Failed to launch ${gsdCommand.command}: ${error.message}`);
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
