'use strict';

const { WorkloadModuleBase } = require('@hyperledger/caliper-core');
const { invoke } = require('./lib/caliperInvoke');

class BaseMarketplaceWorkload extends WorkloadModuleBase {
  async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
    await super.initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext);
    this.workerIndex = workerIndex;
    this.totalWorkers = totalWorkers;
    this.roundArguments = roundArguments;
  }
}

module.exports = { BaseMarketplaceWorkload, invoke };