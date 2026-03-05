'use strict';

const OperationBase = require('./utils/operation-base');
const MarketplaceState = require('./utils/marketplace-state');

class W9_HotAsset extends OperationBase {
    createState() {
        return new MarketplaceState(this.workerIndex, this.roundArguments);
    }

    async submitTransaction() {
        const hotAssetId = this.state.getHotAssetId();
        const requestSlice = this.roundArguments.requestSlice || 1;

        const args = [hotAssetId, requestSlice];
        await this.sutAdapter.sendRequests(this.createConnectorRequest('HireAsset', 'hireAsset', args));
    }
}

module.exports.createWorkloadModule = () => new W9_HotAsset();
