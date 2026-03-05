'use strict'

const { loadFixtures, pickFromArray } = require('./lib/fixtures')

class W2_HireAsset {
  async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
    this.workerIndex = workerIndex
    this.numberOfWorkers = totalWorkers
    this.roundIndex = roundIndex
    this.sutAdapter = sutAdapter

    this.fx = loadFixtures(this)
    this.nextAsset = pickFromArray(this, this.fx.assetsForHire)

    // default: 1 slice por tx (bom pra 5k tx)
    this.slices = Number(roundArguments.slices || 1)
  }

  async submitTransaction() {
    const assetId = this.nextAsset()

    const args = {
      contract: 'HireAsset',
      verb: 'hireAsset',
      args: [assetId, this.slices],
      readOnly: false,
    }

    return this.sutAdapter.sendRequests(args)
  }
}

function createWorkloadModule() {
  return new W2_HireAsset()
}

module.exports.createWorkloadModule = createWorkloadModule
