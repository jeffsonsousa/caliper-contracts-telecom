'use strict';
const { BaseMarketplaceWorkload, invoke } = require('./BaseMarketplaceWorkload');
const { randId, pick, makeDescription } = require('./lib/helpers');

class W4 extends BaseMarketplaceWorkload {
  async submitTransaction() {
    const descSize = this.roundArguments.descSize || ['short'];
    const monthsAvailable = this.roundArguments.monthsAvailable || [1];
    const priceProfile = this.roundArguments.priceProfile || [{initialPrice: 100, totalPrice: 120}];

    const serviceId = randId(`svc-${this.workerIndex}`);
    const description = makeDescription(pick(descSize));
    const m = pick(monthsAvailable);
    const pp = pick(priceProfile);

    return invoke(this.sutAdapter, 'ServiceContract', 'CreateServiceRecord',
      [serviceId, description, m, pp.initialPrice, pp.totalPrice], false);
  }
}
module.exports.createWorkloadModule = () => new W4();