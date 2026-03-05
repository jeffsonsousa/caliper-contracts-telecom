import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

REPORT_ROOT = Path("src/reports")
PLOTS_DIR = REPORT_ROOT / "plots"
ROUND_FILTER = None  # ex: "W1_RegisterAsset"

LAT_KEYS = ["avg", "p95", "p99"]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _extract_tps_from_name(p: Path) -> int:
    m = re.search(r"report_(\d+)TPS", p.name, flags=re.IGNORECASE)
    if not m:
        raise ValueError(f"Não consegui extrair TPS do nome do arquivo: {p.name}")
    return int(m.group(1))


def _pick_summary_table(tables: list[pd.DataFrame]) -> pd.DataFrame:
    best = None
    best_score = -1

    for df in tables:
        cols = [_norm(c) for c in df.columns]
        score = 0
        if any(("name" == c) or ("round" in c) for c in cols): score += 3
        if any("succ" in c for c in cols): score += 3
        if any("fail" in c for c in cols): score += 2
        if any("latency" in c for c in cols): score += 3
        if any(("throughput" in c) or ("tps" == c) for c in cols): score += 2

        if score > best_score:
            best = df
            best_score = score

    if best is None or best_score < 4:
        raise ValueError("Não encontrei tabela de resumo confiável no report.html")

    return best


def _find_col(cols_norm: list[str], patterns: list[str]) -> int | None:
    for pat in patterns:
        for i, c in enumerate(cols_norm):
            if pat in c:
                return i
    return None


def _to_float(v):
    if pd.isna(v):
        return None
    s = str(v).strip()
    s = re.sub(r"[^0-9\.\-eE]", "", s)
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None


def parse_caliper_html(report_path: Path) -> dict:
    tables = pd.read_html(report_path)
    df = _pick_summary_table(tables)

    cols_norm = [_norm(c) for c in df.columns]
    name_col = _find_col(cols_norm, ["name", "round"]) or 0

    avg_col = _find_col(cols_norm, ["avg latency"])
    p95_col = _find_col(cols_norm, ["p95 latency", "95th"])
    p99_col = _find_col(cols_norm, ["p99 latency", "99th"])
    thr_col = _find_col(cols_norm, ["throughput"])
    succ_col = _find_col(cols_norm, ["succ"])
    fail_col = _find_col(cols_norm, ["fail"])

    row_idx = None
    if ROUND_FILTER:
        for i in range(len(df)):
            if _norm(df.iloc[i, name_col]) == _norm(ROUND_FILTER):
                row_idx = i
                break
    if row_idx is None:
        row_idx = 0

    round_name = str(df.iloc[row_idx, name_col])

    return {
        "round": round_name,
        "avg": _to_float(df.iloc[row_idx, avg_col]) if avg_col is not None else None,
        "p95": _to_float(df.iloc[row_idx, p95_col]) if p95_col is not None else None,
        "p99": _to_float(df.iloc[row_idx, p99_col]) if p99_col is not None else None,
        "throughput": _to_float(df.iloc[row_idx, thr_col]) if thr_col is not None else None,
        "succ": _to_float(df.iloc[row_idx, succ_col]) if succ_col is not None else None,
        "fail": _to_float(df.iloc[row_idx, fail_col]) if fail_col is not None else None,
    }


def load_reports(report_root: Path) -> pd.DataFrame:
    rows = []

    for scenario_dir in sorted([p for p in report_root.iterdir() if p.is_dir()]):
        scenario = scenario_dir.name
        htmls = sorted(scenario_dir.glob("report_*TPS_*.html"))
        if not htmls:
            continue

        for hp in htmls:
            tps_target = _extract_tps_from_name(hp)
            metrics = parse_caliper_html(hp)
            rows.append(
                {
                    "scenario": scenario,
                    "tps_target": tps_target,
                    "report": str(hp),
                    **metrics,
                }
            )

    if not rows:
        raise SystemExit(
            f"Nenhum report encontrado. Esperado algo como {report_root}/W2/report_5TPS_*.html"
        )

    df = pd.DataFrame(rows).sort_values(["scenario", "tps_target"]).reset_index(drop=True)
    return df


# =========================
# 2D: foco em LATÊNCIA
# =========================
def plot_latency_2d(df: pd.DataFrame, metric: str = "avg"):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for scenario, g in df.groupby("scenario"):
        g = g.sort_values("tps_target")
        x = g["tps_target"].astype(int).tolist()
        y = g[metric].astype(float).tolist()

        ax.plot(x, y, marker="o", label=scenario)

        # ✅ coloca o TPS em cada ponto
        for xi, yi in zip(x, y):
            ax.text(xi, yi, f"{xi}", fontsize=8, ha="left", va="bottom")

    ax.set_xlabel("TPS alvo")
    ax.set_ylabel("Latência (segundos)")
    ax.set_title(f"Latência vs TPS ({metric.upper()})")
    ax.grid(True)
    ax.legend()

    out = PLOTS_DIR / f"latency_2d_{metric}.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close(fig)
    print(f"[OK] saved: {out}")


# =========================
# 3D: foco em TPS (throughput REAL)
# =========================
def plot_tps_3d(df: pd.DataFrame):
    """
    X: Scenario
    Y: TPS alvo
    Z: Throughput real (TPS medido pelo Caliper)
    ✅ rótulo em cada barra: TPS real
    """
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = sorted(df["scenario"].unique().tolist())
    scen_to_x = {s: i for i, s in enumerate(scenarios)}

    xs, ys, zs = [], [], []

    for _, r in df.iterrows():
        thr = r.get("throughput")
        if thr is None:
            continue
        xs.append(scen_to_x[r["scenario"]])
        ys.append(int(r["tps_target"]))
        zs.append(float(thr))

    if not zs:
        raise SystemExit("Sem throughput para plotar (coluna throughput vazia).")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    dx = 0.6
    dy = 2.5
    ax.bar3d(xs, ys, [0] * len(zs), dx, dy, zs, shade=True)

    ax.set_xlabel("Scenario (Benchmark)")
    ax.set_ylabel("TPS alvo")
    ax.set_zlabel("TPS real (Throughput)")

    ax.set_xticks(list(scen_to_x.values()))
    ax.set_xticklabels(scenarios)

    ax.set_title("TPS real (Throughput) vs TPS alvo vs Scenario")

    # ✅ escreve o TPS real em cada barra
    for x, y, z in zip(xs, ys, zs):
        ax.text(x + dx/2, y + dy/2, z, f"{z:.2f}", fontsize=8, ha="center", va="bottom")

    out = PLOTS_DIR / "tps_3d_throughput.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close(fig)
    print(f"[OK] saved: {out}")


def main():
    df = load_reports(REPORT_ROOT)

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_out = PLOTS_DIR / "caliper_sweep_metrics.csv"
    df.to_csv(csv_out, index=False)
    print(f"[OK] saved: {csv_out}")

    # 2D (latência)
    for m in LAT_KEYS:
        if df[m].notna().any():
            plot_latency_2d(df, metric=m)

    # 3D (TPS)
    plot_tps_3d(df)


if __name__ == "__main__":
    main()
