'use strict';

const OperationBase = require('./utils/operation-base');
const MarketplaceState = require('./utils/marketplace-state');

class W11_PayloadScaling extends OperationBase {
    createState() {
        return new MarketplaceState(this.workerIndex, this.roundArguments);
    }

    async submitTransaction() {
        const Ns = this.roundArguments.N || [1, 3, 5, 10];
        const N = this.state.pick(Ns, 1);

        const assetIds = this.state.buildAssetList(N);
        const slices = assetIds.map(() => 1);

        const serviceId = this.state.randId('svcScale');
        const args = [serviceId, assetIds, slices, 'payload scaling', 1, 200, 260];

        await this.sutAdapter.sendRequests(this.createConnectorRequest('ServiceContract', 'CreateServiceRecordWithAssets', args));
    }
}

module.exports.createWorkloadModule = () => new W11_PayloadScaling();
