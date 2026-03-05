'use strict';

const fs = require('fs');
const path = require('path');

function defaultFixturesPath() {
    // cwd is the Caliper workspace root
    return path.resolve(process.cwd(), 'benchmarks', 'telecom-marketplace', 'fixtures', 'fixtures.json');
}

class FixturePool {
    constructor(opts = {}) {
        this.fixturesPath = opts.fixturesPath || process.env.CALIPER_FIXTURES_PATH || defaultFixturesPath();
        this._loaded = false;

        // cursors per list
        this._cursors = new Map();

        // for HireAsset scaling (remaining slices per asset)
        this._remainingSlices = new Map();
    }

    load() {
        if (this._loaded) {
            return;
        }

        if (!fs.existsSync(this.fixturesPath)) {
            throw new Error(`fixtures.json not found at: ${this.fixturesPath}. Set CALIPER_FIXTURES_PATH or place the file in benchmarks/telecom-marketplace/fixtures/.`);
        }

        const raw = fs.readFileSync(this.fixturesPath, 'utf8');
        this.data = JSON.parse(raw);

        // build remaining slices for assets that can be hired incrementally
        const initialSlices = Number(this.data.assetInitialSlices ?? process.env.CALIPER_ASSET_INITIAL_SLICES ?? 10);
        const hireList = this.data.assetsForHire || [];
        for (const id of hireList) {
            this._remainingSlices.set(id, initialSlices);
        }

        this._loaded = true;
    }

    /**
     * Returns next element from an array field (round-robin).
     * Throws if missing/empty.
     */
    nextFromArray(fieldName) {
        this.load();
        const arr = this.data[fieldName];
        if (!Array.isArray(arr) || arr.length === 0) {
            throw new Error(`fixtures.json: field "${fieldName}" is missing or empty`);
        }
        const idx = this._cursors.get(fieldName) ?? 0;
        const val = arr[idx % arr.length];
        this._cursors.set(fieldName, idx + 1);
        return val;
    }

    /**
     * Returns the next asset id that still has >= slicesWanted remaining.
     * If none available, throws (benchmark should create more assets or reduce slicesWanted).
     */
    nextHireableAsset(slicesWanted) {
        this.load();
        const wanted = Number(slicesWanted);
        const listName = 'assetsForHire';
        const assets = this.data[listName] || [];
        if (assets.length === 0) {
            throw new Error('fixtures.json: assetsForHire is empty; cannot run HireAsset workload');
        }

        // try at most N assets to find one that still has slices
        const startIdx = this._cursors.get(listName) ?? 0;
        for (let i = 0; i < assets.length; i++) {
            const idx = (startIdx + i) % assets.length;
            const id = assets[idx];
            const remaining = this._remainingSlices.get(id) ?? 0;
            if (remaining >= wanted) {
                this._cursors.set(listName, idx + 1);
                this._remainingSlices.set(id, remaining - wanted);
                return id;
            }
        }

        throw new Error(`No hireable assets left with >=${wanted} slices (assetsForHire exhausted)`);
    }
}

module.exports = { FixturePool };