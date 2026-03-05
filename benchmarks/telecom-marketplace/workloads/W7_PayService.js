'use strict'

const { loadFixtures, pickFromArray } = require('./lib/fixtures')

class W7_PayService {
  async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
    this.workerIndex = workerIndex
    this.numberOfWorkers = totalWorkers
    this.roundIndex = roundIndex
    this.sutAdapter = sutAdapter

    this.fx = loadFixtures(this)
    this.nextService = pickFromArray(this, this.fx.servicesForPay)

    this.renter = this.fx.renter
    this.payment = String(roundArguments.payment ?? 1)
    this.refund = String(roundArguments.refund ?? 0)
  }

  async submitTransaction() {
    const serviceId = this.nextService()

    const args = {
      contract: 'HireService',
      verb: 'payService',
      args: [serviceId, this.renter, this.payment, this.refund],
      readOnly: false,
    }

    return this.sutAdapter.sendRequests(args)
  }
}

function createWorkloadModule() {
  return new W7_PayService()
}

module.exports.createWorkloadModule = createWorkloadModule
