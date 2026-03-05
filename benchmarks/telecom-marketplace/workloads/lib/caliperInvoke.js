'use strict';

/**
 * Adjust here if your Caliper Ethereum connector uses different request fields.
 * Most commonly it accepts: { contract, verb, args, readOnly }
 */
function buildInvokeRequest(contract, verb, args, readOnly = false) {
  return { contract, verb, args, readOnly };
}

async function invoke(sutAdapter, contract, verb, args, readOnly = false) {
  return sutAdapter.sendRequests(buildInvokeRequest(contract, verb, args, readOnly));
}

module.exports = { invoke, buildInvokeRequest };