#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse Hyperledger Caliper HTML reports and generate plots (latency/throughput + optional 3D bar).

Works best when you have multiple report.html files (one per configuration / SUT / send-rate).
For a single report, it still generates 2D plots for the available rounds.

Examples:
  python caliper_report_plots.py --input report.html --label SUT1 --out plots
  python caliper_report_plots.py --input "reports/**/*.html" --infer-label-from filename --out plots
"""

from __future__ import annotations

import argparse
import glob
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def _safe_float(x) -> Optional[float]:
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None


def _pick_label(path: Path, explicit: Optional[str], infer: bool) -> str:
    if explicit:
        return explicit
    if infer:
        return path.stem
    return "SUT"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


@dataclass
class CaliperReport:
    path: Path
    label: str
    summary: Optional[pd.DataFrame]
    rounds: pd.DataFrame
    resources: Optional[pd.DataFrame]


def parse_caliper_html(path: Path, label: str) -> CaliperReport:
    html = path.read_text(encoding="utf-8", errors="ignore")
    _ = BeautifulSoup(html, "html.parser")  # reserved if you want richer parsing later

    tables = pd.read_html(html)
    tables = [_normalize_columns(t) for t in tables]

    summary = None
    rounds = pd.DataFrame()
    resources = None

    for t in tables:
        cols = set(t.columns)
        if {"Name", "Succ", "Fail", "Send Rate (TPS)", "Throughput (TPS)"} <= cols:
            if "Round" in cols:
                rounds = t
            else:
                summary = t
        elif "Resource" in cols or {"Resource", "Max", "Min", "Avg"} <= cols:
            resources = t
        elif {"Name", "Avg CPU%", "Avg Memory (MB)"} <= cols:
            resources = t

    if rounds.empty:
        candidates = []
        for t in tables:
            cols = set(t.columns)
            if ("Send Rate (TPS)" in cols) and ("Throughput (TPS)" in cols):
                candidates.append(t)
        if candidates:
            rounds = max(candidates, key=lambda d: len(d))

    return CaliperReport(path=path, label=label, summary=summary, rounds=rounds, resources=resources)


def extract_longform(rounds: pd.DataFrame, label: str) -> pd.DataFrame:
    if rounds is None or rounds.empty:
        return pd.DataFrame()

    df = rounds.copy()
    df["sut"] = label

    avg_col = None
    max_col = None
    for c in df.columns:
        if re.fullmatch(r"Avg Latency \((s|ms)\)", c):
            avg_col = c
        if re.fullmatch(r"Max Latency \((s|ms)\)", c):
            max_col = c

    if avg_col and avg_col.endswith("(ms)"):
        df["avg_latency_s"] = df[avg_col].apply(_safe_float).apply(lambda v: None if v is None else v / 1000.0)
    elif avg_col:
        df["avg_latency_s"] = df[avg_col].apply(_safe_float)

    if max_col and max_col.endswith("(ms)"):
        df["max_latency_s"] = df[max_col].apply(_safe_float).apply(lambda v: None if v is None else v / 1000.0)
    elif max_col:
        df["max_latency_s"] = df[max_col].apply(_safe_float)

    if "Throughput (TPS)" in df.columns:
        df["throughput_tps"] = df["Throughput (TPS)"].apply(_safe_float)
    if "Send Rate (TPS)" in df.columns:
        df["send_rate_tps"] = df["Send Rate (TPS)"].apply(_safe_float)

    keep = ["sut", "Name"]
    for col in ["Round", "send_rate_tps", "throughput_tps", "avg_latency_s", "max_latency_s", "Succ", "Fail"]:
        if col in df.columns and col not in keep:
            keep.append(col)

    out = df[keep].copy()
    return out


def plot_latency_throughput(df: pd.DataFrame, outdir: Path) -> None:
    if df.empty:
        return

    outdir.mkdir(parents=True, exist_ok=True)

    for (sut, name), g in df.groupby(["sut", "Name"]):
        g = g.sort_values(by="send_rate_tps", na_position="last")

        if "avg_latency_s" in g.columns and g["avg_latency_s"].notna().any():
            plt.figure()
            plt.plot(g["send_rate_tps"], g["avg_latency_s"], marker="o")
            plt.xlabel("Send Rate (TPS)")
            plt.ylabel("Avg Latency (s)")
            plt.title(f"{sut} — {name}: Avg Latency vs Send Rate")
            plt.grid(True, which="both", linestyle="--", linewidth=0.5)
            plt.tight_layout()
            plt.savefig(outdir / f"{sut}__{name}__avg_latency.png", dpi=200)
            plt.close()

        if "throughput_tps" in g.columns and g["throughput_tps"].notna().any():
            plt.figure()
            plt.plot(g["send_rate_tps"], g["throughput_tps"], marker="o")
            plt.xlabel("Send Rate (TPS)")
            plt.ylabel("Throughput (TPS)")
            plt.title(f"{sut} — {name}: Throughput vs Send Rate")
            plt.grid(True, which="both", linestyle="--", linewidth=0.5)
            plt.tight_layout()
            plt.savefig(outdir / f"{sut}__{name}__throughput.png", dpi=200)
            plt.close()


def plot_3d_bar(df: pd.DataFrame, outpath: Path, metric: str = "avg_latency_s") -> None:
    if df.empty or metric not in df.columns:
        return

    g = df.dropna(subset=["send_rate_tps", metric]).copy()
    if g.empty:
        return

    if "Name" in g.columns and g["Name"].nunique() > 1:
        first_name = g["Name"].iloc[0]
        g = g[g["Name"] == first_name]

    suts = sorted(g["sut"].unique().tolist())
    rates = sorted(g["send_rate_tps"].unique().tolist())

    x_map = {s: i for i, s in enumerate(suts)}
    y_map = {r: j for j, r in enumerate(rates)}

    xs = g["sut"].map(x_map).astype(float).to_numpy()
    ys = g["send_rate_tps"].map(y_map).astype(float).to_numpy()
    zs = g[metric].astype(float).to_numpy()

    dx = 0.6
    dy = 0.6
    z0 = 0.0

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.bar3d(xs, ys, z0, dx, dy, zs, shade=True)

    ax.set_xlabel("System Under Test (SUT)")
    ax.set_ylabel("Send Rate (TPS)")
    ax.set_zlabel("Latency (s)" if metric.endswith("_s") else metric)

    ax.set_xticks([x_map[s] + dx / 2 for s in suts])
    ax.set_xticklabels(suts, rotation=15, ha="right")
    ax.set_yticks([y_map[r] + dy / 2 for r in rates])
    ax.set_yticklabels([str(int(r)) if float(r).is_integer() else str(r) for r in rates])

    ax.set_title(f"3D View — {metric}")
    fig.tight_layout()
    fig.savefig(outpath, dpi=220)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help='HTML report path or glob (e.g. "reports/**/*.html")')
    ap.add_argument("--out", default="plots", help="Output folder for images/CSVs")
    ap.add_argument("--label", default=None, help="Explicit label for this report (useful if input is a single file)")
    ap.add_argument("--infer-label-from", default="filename", choices=["filename", "none"],
                    help="How to infer label if multiple inputs")
    ap.add_argument("--export-csv", action="store_true", help="Export extracted metrics to CSV")
    ap.add_argument("--plot-3d", action="store_true", help="Generate a 3D bar chart (needs multiple points)")
    ap.add_argument("--metric", default="avg_latency_s", help="Metric column for 3D chart (avg_latency_s or max_latency_s)")
    args = ap.parse_args()

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    paths = [Path(p) for p in glob.glob(args.input, recursive=True)]
    if not paths:
        raise SystemExit(f"No inputs matched: {args.input}")

    reports: List[CaliperReport] = []
    for p in paths:
        lbl = _pick_label(p, args.label if len(paths) == 1 else None, infer=(args.infer_label_from == "filename"))
        rep = parse_caliper_html(p, lbl)
        reports.append(rep)

    long_frames = []
    for r in reports:
        lf = extract_longform(r.rounds, r.label)
        if not lf.empty:
            lf["source_file"] = str(r.path)
            long_frames.append(lf)

    if not long_frames:
        print("[ERR] Could not extract any round metrics from the provided reports.")
        return 2

    df = pd.concat(long_frames, ignore_index=True)

    if args.export_csv:
        df.to_csv(outdir / "caliper_round_metrics.csv", index=False)

    plot_latency_throughput(df, outdir)

    if args.plot_3d:
        plot_3d_bar(df, outdir / f"caliper_3d_{args.metric}.png", metric=args.metric)

    print(f"[OK] Plots saved to: {outdir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
