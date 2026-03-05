'use strict'

const fs = require('fs')
const path = require('path')

function loadFixtures(ctx) {
  // ctx: Caliper context (workload module)
  const workspace = process.env.CALIPER_WORKSPACE || process.cwd()
  // Permite override por env, mas mantém default no seu layout
  const rel =
    process.env.CALIPER_FIXTURES ||
    path.join('benchmarks', 'telecom-marketplace', 'fixtures', 'fixtures.json')

  const p = path.resolve(workspace, rel)
  if (!fs.existsSync(p)) {
    throw new Error(`fixtures.json not found at: ${p}`)
  }
  const data = JSON.parse(fs.readFileSync(p, 'utf8'))

  // validações mínimas (pra falhar “bonito”)
  const mustArrays = [
    'assetsForHire',
    'assetsForPay',
    'assetsForComposed',
    'servicesForHire',
    'servicesForPay',
    'composedToCreate',
  ]
  for (const k of mustArrays) {
    if (!Array.isArray(data[k])) {
      throw new Error(`fixtures.${k} must be an array`)
    }
  }

  return data
}

/**
 * Retorna um índice determinístico por worker/round/tx, evitando colisão
 * entre workers e entre rounds.
 */
function makePicker(ctx, arrLen) {
  const wid = Number(ctx.workerIndex || 0)
  const rid = Number(ctx.roundIndex || 0)
  let cursor = 0

  return () => {
    if (arrLen <= 0) throw new Error('Empty fixtures list')
    // stride = totalWorkers (se existir), senão 1
    const totalWorkers = Number(ctx.numberOfWorkers || 1)
    const base = (rid * totalWorkers + wid) % arrLen
    const idx = (base + cursor * totalWorkers) % arrLen
    cursor++
    return idx
  }
}

/**
 * “Pega próximo item” de um array, de modo determinístico e distribuído entre workers.
 */
function pickFromArray(ctx, arr) {
  const nextIndex = makePicker(ctx, arr.length)
  return () => arr[nextIndex()]
}

module.exports = {
  loadFixtures,
  pickFromArray,
}
