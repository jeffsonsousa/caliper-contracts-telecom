'use strict'

const { loadFixtures, pickFromArray } = require('./lib/fixtures')

class W5_CreateServiceRecordWithAssets {
  async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
    this.workerIndex = workerIndex
    this.numberOfWorkers = totalWorkers
    this.roundIndex = roundIndex
    this.sutAdapter = sutAdapter
    this.fx = loadFixtures(this)
    this.nextBlueprint = pickFromArray(this, this.fx.composedToCreate)
  }

  async submitTransaction() {
    const bp = this.nextBlueprint()

    const args = {
      contract: 'ServiceContract',
      verb: 'CreateServiceRecordWithAssets',
      args: [
        bp.serviceId,
        bp.assetIds,
        bp.slices,
        bp.description,
        bp.monthsAvailable,
        bp.price,
        bp.finalPrice,
      ],
      readOnly: false,
    }
    return this.sutAdapter.sendRequests(args)
  }
}

function createWorkloadModule() {
  return new W5_CreateServiceRecordWithAssets()
}

module.exports.createWorkloadModule = createWorkloadModule
