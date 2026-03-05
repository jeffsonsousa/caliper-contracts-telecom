#!/usr/bin/env bash

set -e  # para o script se algo falhar

# ==============================
# Configurações
# ==============================
TPS_VALUES=(10 15)

WORKSPACE="."
BENCHCONFIG="benchmarks/telecom-marketplace/W3.yaml"
NETWORKCONFIG="networks/besu-qbft.json"
REPORT_BASE="src/reports/W3"

CALIPER_CMD="npx caliper launch manager \
  --caliper-workspace ${WORKSPACE} \
  --caliper-benchconfig ${BENCHCONFIG} \
  --caliper-networkconfig ${NETWORKCONFIG} \
  --caliper-bind-sut besu:latest \
  --caliper-flow-skip-install"

# ==============================
# Preparação
# ==============================
mkdir -p "${REPORT_BASE}"

echo "🚀 Iniciando varredura de TPS para W3"
echo "TPS: ${TPS_VALUES[*]}"
echo "Relatórios em: ${REPORT_BASE}"
echo "----------------------------------"

# Backup do YAML original
cp "${BENCHCONFIG}" "${BENCHCONFIG}.bak"

# ==============================
# Loop de TPS
# ==============================
for TPS in "${TPS_VALUES[@]}"; do
  echo ""
  echo "▶️  Executando benchmark com TPS=${TPS}"

  # Atualiza o TPS no YAML (assume linha no formato correto)
  sed -i \
    -E "s/(rateControl:.*tps:)[[:space:]]*[0-9]+/\1 ${TPS}/" \
    "${BENCHCONFIG}"

  echo "✔️  TPS atualizado no YAML"

  # Executa o Caliper
  ${CALIPER_CMD}

  # Timestamp
  TS=$(date +"%Y%m%d_%H%M%S")

  # Move o report.html gerado
  if [ -f "report.html" ]; then
    OUT="${REPORT_BASE}/report_${TPS}TPS_${TS}.html"
    mv report.html "${OUT}"
    echo "📄 Relatório salvo em: ${OUT}"
  else
    echo "⚠️  report.html não encontrado!"
  fi

  echo "⏸️  Aguardando 5s antes da próxima rodada..."
  sleep 5
done

# ==============================
# Restauração
# ==============================
mv "${BENCHCONFIG}.bak" "${BENCHCONFIG}"
echo ""
echo "✅ YAML restaurado para o estado original"
echo "🏁 Varredura de TPS finalizada"
