# T01 Summary - WSL preflight launcher

## Result

Restored WSL preflight by:

- adding `scripts/run-python.mjs` to resolve a usable repo-local Python interpreter
- moving npm Python scripts off hardcoded `py -3`
- removing the repo-forced Windows `.npmrc` `script-shell`

## Verification

- `node scripts/run-python.mjs -m pyrme stack --quiet` - passed.
- `npm run preflight --silent` - passed.
