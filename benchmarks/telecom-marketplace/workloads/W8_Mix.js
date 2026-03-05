'use strict';

const OperationBase = require('./utils/operation-base');
const MarketplaceState = require('./utils/marketplace-state');

function weightedPick(weights) {
    const entries = Object.entries(weights);
    const total = entries.reduce((a, [, w]) => a + w, 0);
    let r = Math.random() * total;
    for (const [k, w] of entries) {
        r -= w;
        if (r <= 0) return k;
    }
    return entries[entries.length - 1][0];
}

class W8_Mix extends OperationBase {
    createState() {
        return new MarketplaceState(this.workerIndex, this.roundArguments);
    }
    async submitTransaction() {
        const mix = this.roundArguments.mix || {
            RegisterAsset: 0.10,
            HireAsset: 0.25,
            CreateServiceWithAssets: 0.20,
            HireService: 0.25,
            Pay: 0.20
        };
        console.log (this.state.getAssetId());

        const choice = weightedPick(mix);

        const assetId = this.state.getAssetId();
        const serviceId = this.state.getServiceId();
        const renter = this.state.getRenterAddress();
        console.log ("#1", assetId);
        console.log ("#2", serviceId);
        console.log ("#3", renter);

        if (choice === 'RegisterAsset') {
            const id = this.state.randId('assetMix');
            const args = [id, 'mix asset', 1000, 10, 1, 1000, 0];
            await this.sutAdapter.sendRequests(this.createConnectorRequest('AssetsContract', 'CreateAssetsRegistry', args));
            return;
        }

        if (choice === 'HireAsset') {
            const args = [assetId, 1];
            await this.sutAdapter.sendRequests(this.createConnectorRequest('HireAsset', 'hireAsset', args));
            return;
        }

        if (choice === 'CreateServiceWithAssets') {
            const ids = this.state.buildAssetList(1);
            const slices = ids.map(() => 1);
            const sid = this.state.randId('svcMix');
            const args = [sid, ids, slices, 'mix service', 1, 200, 260];
            await this.sutAdapter.sendRequests(this.createConnectorRequest('ServiceContract', 'CreateServiceRecordWithAssets', args));
            return;
        }

        if (choice === 'HireService') {
            const args = [serviceId];
            await this.sutAdapter.sendRequests(this.createConnectorRequest('HireService', 'hireService', args));
            return;
        }

        // Pay (randomly asset or service)
        if (Math.random() < 0.5) {
            const args = [assetId, renter, 450, 450];
            await this.sutAdapter.sendRequests(this.createConnectorRequest('HireAsset', 'payAsset', args));
        } else {
            const args = [serviceId, renter, 250, 250];
            await this.sutAdapter.sendRequests(this.createConnectorRequest('HireService', 'payService', args));
        }
    }
}

module.exports.createWorkloadModule = () => new W8_Mix();
