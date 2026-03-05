/**
 * Hardhat setup script for Telecom Marketplace benchmark fixtures.
 *
 * What it does:
 * 1) Loads deployed contract addresses from env
 * 2) Distributes TLC from Telecoin contract balance using withdraw() by owner
 * 3) Approves allowances for AssetsContract and ServiceContract for all renter accounts
 * 4) Creates asset fixtures (asset-fixture-1 ... asset-fixture-N) by supplier accounts
 * 5) Hires ALL slices for each asset by a service supplier (so asset becomes Inativo)
 * 6) Creates services:
 *    - service-fixture-1 (no assets)
 *    - serviceA-fixture-1 (with assets, N assets)
 *
 * IMPORTANT:
 * - Your contracts use transferFrom() in AssetsContract and ServiceContract.
 *   So the USER must approve spender = AssetsContract / ServiceContract.
 * - CreateServiceRecordWithAssets requires assetsMetadata.status == Status.Inativo.
 *   In AssetsContract, status becomes Inativo when slices == 0.
 *
 * Usage:
 *   TELECOIN=0x... ASSETS=0x... HIRE_ASSET=0x... SERVICE=0x... HIRE_SERVICE=0x... \
 *   APPROVAL_AMOUNT=1000000000000000000000000 \
 *   N_ASSETS=5 ASSET_SLICES=10 MONTHS_AVAILABLE=12 \
 *   npx hardhat run scripts/setup-fixtures.js --network <yourNetwork>
 *
 * After running, it prints env vars you can export for Caliper.
 */

const hre = require('hardhat');

function envAddr(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env ${name} (deployed address)`);
  return v;
}

function envNum(name, fallback) {
  const v = process.env[name];
  if (!v) return fallback;
  return Number(v);
}

function envBig(name, fallback) {
  const v = process.env[name];
  if (!v) return BigInt(fallback);
  return BigInt(v);
}

async function main() {
  const [admin, fa1, fs1, client1] = await hre.ethers.getSigners();

  const telecoinAddr  = envAddr('TELECOIN');
  const assetsAddr    = envAddr('ASSETS');
  const hireAssetAddr = envAddr('HIRE_ASSET');
  const serviceAddr   = envAddr('SERVICE');
  const hireSvcAddr   = envAddr('HIRE_SERVICE');

  const approvalAmount = envBig('APPROVAL_AMOUNT', '1000000000000000000000000'); // 1e24
  const nAssets = envNum('N_ASSETS', 5);
  const assetSlices = envNum('ASSET_SLICES', 10);
  const monthsAvailable = envNum('MONTHS_AVAILABLE', 12);

  const Telecoin = await hre.ethers.getContractFactory('Telecoin');
  const AssetsContract = await hre.ethers.getContractFactory('AssetsContract');
  const HireAsset = await hre.ethers.getContractFactory('HireAsset');
  const ServiceContract = await hre.ethers.getContractFactory('ServiceContract');

  const telecoin = Telecoin.attach(telecoinAddr);
  const assets = AssetsContract.attach(assetsAddr);
  const hireAsset = HireAsset.attach(hireAssetAddr);
  const service = ServiceContract.attach(serviceAddr);

  const toWei = (n) => BigInt(n) * 10n ** 18n;

  const participants = [fa1, fs1, client1];

  console.log('--- Addresses ---');
  console.log({ telecoinAddr, assetsAddr, hireAssetAddr, serviceAddr, hireSvcAddr });
  console.log('Admin:', admin.address);
  console.log('FA1:', fa1.address);
  console.log('FS1:', fs1.address);
  console.log('CLIENT1:', client1.address);

  // 1) Distribute TLC
  console.log('\n--- Distributing TLC ---');
  for (const p of participants) {
    const amount = toWei(2000); // 2000 TLC
    const tx = await telecoin.connect(admin).withdraw(p.address, amount);
    await tx.wait();
    console.log(`withdraw -> ${p.address}: ${amount.toString()}`);
  }

  // 2) Approvals
  console.log('\n--- Approvals ---');
  for (const p of participants) {
    const tx1 = await telecoin.connect(p).approve(assetsAddr, approvalAmount);
    await tx1.wait();
    const tx2 = await telecoin.connect(p).approve(serviceAddr, approvalAmount);
    await tx2.wait();
    console.log(`approved AssetsContract + ServiceContract for ${p.address}`);
  }

  // 3) Create assets
  console.log('\n--- Creating Asset fixtures ---');
  const assetIds = [];
  for (let i = 1; i <= nAssets; i++) {
    const id = `asset-fixture-${i}`;
    assetIds.push(id);

    const description = `fixture asset ${i}`;
    const amount = 1000;
    const slices = assetSlices;
    const totalPrice = 1000;
    const pricePerSlice = 0;

    const tx = await assets.connect(fa1).CreateAssetsRegistry(
      id, description, amount, slices, monthsAvailable, totalPrice, pricePerSlice
    );
    await tx.wait();
    console.log(`created asset: ${id} slices=${slices}`);
  }

  // 4) Hire ALL slices to make assets Inativo
  console.log('\n--- Hiring ALL slices (FS1) ---');
  for (const id of assetIds) {
    let hireSlices = assetSlices;
    try {
      const meta = await assets.getAssets(id);
      if (meta && meta.initialSlices) hireSlices = Number(meta.initialSlices);
    } catch (_) {}

    const tx = await hireAsset.connect(fs1).hireAsset(id, hireSlices);
    await tx.wait();
    console.log(`hired asset: ${id} slices=${hireSlices}`);
  }

  // 5) Create services
  console.log('\n--- Creating Service fixtures ---');

  {
    const serviceId = 'service-fixture-1';
    const desc = 'fixture service (no assets)';
    const initialPrice = 100;
    const totalPrice = 120;
    const tx = await service.connect(fs1).CreateServiceRecord(
      serviceId, desc, monthsAvailable, initialPrice, totalPrice
    );
    await tx.wait();
    console.log(`created service: ${serviceId}`);
  }

  {
    const serviceId = 'serviceA-fixture-1';
    const desc = 'fixture service (with assets)';
    const slices = assetIds.map(() => 1);
    const initialPrice = 200;
    const totalPrice = 260;

    const tx = await service.connect(fs1).CreateServiceRecordWithAssets(
      serviceId, assetIds, slices, desc, monthsAvailable, initialPrice, totalPrice
    );
    await tx.wait();
    console.log(`created service with assets: ${serviceId} assets=${assetIds.length}`);
  }

  console.log('\n=== Export these for Caliper ===');
  console.log(`export CALIPER_ASSET_ID=${assetIds[0]}`);
  console.log(`export CALIPER_ASSET_IDS=${assetIds.join(',')}`);
  console.log(`export CALIPER_ASSET_INITIAL_SLICES=${assetSlices}`);
  console.log(`export CALIPER_SERVICE_ID=service-fixture-1`);
  console.log(`export CALIPER_HOT_ASSET_ID=${assetIds[0]}`);
  console.log(`export CALIPER_HOT_SERVICE_ID=service-fixture-1`);
  console.log(`export CALIPER_RENTER=${fs1.address}`);
  console.log(`export CALIPER_ASSET_LOCKED_VALUE=900`);
  console.log(`export CALIPER_SERVICE_LOCKED_VALUE=200`);

  console.log('\nDone.');
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});