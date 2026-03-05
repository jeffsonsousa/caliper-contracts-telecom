# Caliper Benchmark Pack — Telecom Marketplace (Besu)

This package provides a **Caliper benchmark skeleton** for your marketplace contracts:
W1–W7 (micro), W8 (mix end-to-end), W9–W11 (contention & payload scaling).

## Assumptions
- Besu JSON-RPC: `http://127.0.0.1:8545`
- Contracts deployed: Telecoin, AssetsContract, HireAsset, ServiceContract, HireService
- You can export each contract ABI JSON and deployed address.

## Fill ABIs and addresses
1) Put ABIs in `./contracts/abi/`:
- Telecoin.json
- AssetsContract.json
- HireAsset.json
- ServiceContract.json
- HireService.json

2) Update:
- `./networks/besu-qbft.json`
- `./benchmarks/telecom-marketplace/config/contracts.json`

## IMPORTANT: Allowances (transferFrom)
Your Solidity code requires the **user** to approve spenders:

- Assets hiring:
  - spender = AssetsContract (because transferFrom is executed inside AssetsContract)
  - so renters must `approve(AssetsContract, amount)` **before** calling HireAsset.hireAsset

- Service hiring:
  - spender = ServiceContract (because transferFrom is executed inside ServiceContract)
  - so renters must `approve(ServiceContract, amount)` **before** calling HireService.hireService
  - (your HireService contract approves from itself, not from the user, so it doesn't set user allowance)

Recommended: run a Hardhat setup script to:
- withdraw TLC from Telecoin to all accounts
- approve allowances to AssetsContract and ServiceContract for all renters

## Running (typical)
`npx caliper launch manager --caliper-workspace . --caliper-benchconfig benchmarks/telecom-marketplace/benchconfig.yaml --caliper-networkconfig networks/besu-qbft.json`

If your connector expects different request fields, edit:
`benchmarks/telecom-marketplace/workloads/lib/caliperInvoke.js`

## Workload style
All workloads use the same pattern as your working example: `OperationBase + State` and create requests as `{contract, verb, args, readOnly}`.
