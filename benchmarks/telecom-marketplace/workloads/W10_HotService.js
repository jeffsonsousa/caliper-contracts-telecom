'use strict';

const OperationBase = require('./utils/operation-base');
const MarketplaceState = require('./utils/marketplace-state');

class W10_HotService extends OperationBase {
    createState() {
        return new MarketplaceState(this.workerIndex, this.roundArguments);
    }

    async submitTransaction() {
        const hotServiceId = this.state.getHotServiceId();
        const args = [hotServiceId];
        await this.sutAdapter.sendRequests(this.createConnectorRequest('HireService', 'hireService', args));
    }
}

module.exports.createWorkloadModule = () => new W10_HotService();
