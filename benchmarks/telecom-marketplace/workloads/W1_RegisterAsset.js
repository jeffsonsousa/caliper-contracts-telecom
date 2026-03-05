'use strict';
const { BaseMarketplaceWorkload, invoke } = require('./BaseMarketplaceWorkload');
const { pick, makeDescription } = require('./lib/helpers');

class W1 extends BaseMarketplaceWorkload {
  async submitTransaction() {
    const slices = this.roundArguments.slices || [1];
    const monthsAvailable = this.roundArguments.monthsAvailable || [1];
    const descSize = this.roundArguments.descSize || ['short'];

    const Id = `asset-${this.workerIndex}-${Date.now()}-${Math.floor(Math.random()*1e6)}`;
    const description = makeDescription(pick(descSize));
    const amount = 1000;
    const s = pick(slices);
    const m = pick(monthsAvailable);
    const totalPrice = 1000;
    const pricePerSlice = 0;

    return invoke(this.sutAdapter, 'AssetsContract', 'CreateAssetsRegistry',
      [Id, description, amount, s, m, totalPrice, pricePerSlice], false);
  }
}
module.exports.createWorkloadModule = () => new W1();