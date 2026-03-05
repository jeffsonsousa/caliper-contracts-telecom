# Hardhat Fixture Setup (for Caliper)

This folder contains `setup-fixtures.js` to prepare the marketplace state for Caliper rounds W1–W7.

## Requirements
- Run this inside your **Hardhat project** (same repo where contracts are compiled).
- Contract names must match: Telecoin, AssetsContract, HireAsset, ServiceContract.

## Environment variables (addresses)
Set deployed addresses:
- TELECOIN
- ASSETS
- HIRE_ASSET
- SERVICE
- HIRE_SERVICE

Optional tuning:
- N_ASSETS (default 5)
- ASSET_SLICES (default 10)
- MONTHS_AVAILABLE (default 12)
- APPROVAL_AMOUNT (default 1e24)

## Run
npx hardhat run scripts/setup-fixtures.js --network <network>

The script prints `export ...` lines to set Caliper fixture env vars.