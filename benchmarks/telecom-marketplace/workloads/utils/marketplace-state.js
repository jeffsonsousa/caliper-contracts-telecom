'use strict';

/**
 * Shared state helper to generate IDs, descriptions and read fixtures.
 * Prefer strings for big integers to avoid BigInt JSON serialization issues.
 */
class MarketplaceState {
    constructor(workerIndex, roundArguments) {
        this.workerIndex = workerIndex;
        this.args = roundArguments || {};
    }

    randId(prefix='id') {
        const s = Math.random().toString(16).slice(2, 10);
        return `${prefix}-${Date.now()}-${this.workerIndex}-${s}`;
    }

    pick(arr, fallback) {
        if (!arr || arr.length === 0) return fallback;
        return arr[Math.floor(Math.random() * arr.length)];
    }

    makeDescription(size='short') {
        if (size === 'short') return 'Benchmark description';
        return 'L'.repeat(2048); // ~2KB
    }

    // Fixtures
    getAssetId() {
        return process.env.CALIPER_ASSET_ID || this.args.assetId || 'asset-fixture-1';
    }

    getAssetIdsCsv() {
        return process.env.CALIPER_ASSET_IDS || this.args.assetIdsCsv || '';
    }

    getServiceId() {
        return process.env.CALIPER_SERVICE_ID || this.args.serviceId || 'service-fixture-1';
    }

    getRenterAddress() {
        return process.env.CALIPER_RENTER || this.args.renter || '0xRENTER_ADDRESS_FIXTURE';
    }

    getHotAssetId() {
        return process.env.CALIPER_HOT_ASSET_ID || this.args.hotAssetId || this.getAssetId();
    }

    getHotServiceId() {
        return process.env.CALIPER_HOT_SERVICE_ID || this.args.hotServiceId || this.getServiceId();
    }

    getInitialSlices() {
        const v = process.env.CALIPER_ASSET_INITIAL_SLICES || this.args.initialSlices || 100;
        return Number(v);
    }

    // Use env to pass nominal locked values for settlement tests
    getAssetLockedValue() {
        const v = process.env.CALIPER_ASSET_LOCKED_VALUE || this.args.assetLockedValue || 900;
        return Number(v);
    }

    getServiceLockedValue() {
        const v = process.env.CALIPER_SERVICE_LOCKED_VALUE || this.args.serviceLockedValue || 500;
        return Number(v);
    }

    buildAssetList(N) {
        const csv = this.getAssetIdsCsv();
        if (csv) {
            const ids = csv.split(',').map(s => s.trim()).filter(Boolean);
            return ids.slice(0, N);
        }
        // fallback placeholders
        return Array.from({length: N}, (_,i) => `asset-fixture-${i+1}`);
    }
}

module.exports = MarketplaceState;
