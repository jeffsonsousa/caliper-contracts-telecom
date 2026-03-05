'use strict';

function randId(prefix='id') {
  const s = Math.random().toString(16).slice(2, 10);
  return `${prefix}-${Date.now()}-${s}`;
}
function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function makeDescription(size='short') {
  if (size === 'short') return 'Benchmark description';
  return 'L'.repeat(2048);
}
module.exports = { randId, pick, makeDescription };