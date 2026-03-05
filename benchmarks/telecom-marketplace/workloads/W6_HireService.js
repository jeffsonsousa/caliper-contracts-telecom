'use strict'

const { loadFixtures, pickFromArray } = require('./lib/fixtures')

class W6_HireService {
  async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
    this.workerIndex = workerIndex
    this.numberOfWorkers = totalWorkers
    this.roundIndex = roundIndex
    this.sutAdapter = sutAdapter

    this.fx = loadFixtures(this)
    this.nextService = pickFromArray(this, this.fx.servicesForHire)
  }

  async submitTransaction() {
    const serviceId = this.nextService()

    const args = {
      contract: 'HireService',
      verb: 'hireService',
      args: [serviceId],
      readOnly: false,
    }

    return this.sutAdapter.sendRequests(args)
  }
}

function createWorkloadModule() {
  return new W6_HireService()
}

module.exports.createWorkloadModule = createWorkloadModule
