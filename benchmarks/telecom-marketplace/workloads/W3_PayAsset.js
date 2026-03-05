'use strict'

const { loadFixtures, pickFromArray } = require('./lib/fixtures')

class W3_PayAsset {
  async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
    this.workerIndex = workerIndex
    this.numberOfWorkers = totalWorkers
    this.roundIndex = roundIndex
    this.sutAdapter = sutAdapter

    this.fx = loadFixtures(this)
    this.nextAsset = pickFromArray(this, this.fx.assetsForPay)

    // defaults: paga um pouco e não devolve
    this.renter = this.fx.renter
    this.payment = String(roundArguments.payment ?? 1)
    this.refund = String(roundArguments.refund ?? 0)
  }

  async submitTransaction() {
    const assetId = this.nextAsset()

    const args = {
      contract: 'HireAsset',
      verb: 'payAsset',
      args: [assetId, this.renter, this.payment, this.refund],
      readOnly: false,
    }

    return this.sutAdapter.sendRequests(args)
  }
}

function createWorkloadModule() {
  return new W3_PayAsset()
}

module.exports.createWorkloadModule = createWorkloadModule
