"""Build a small Scope 2 ledger from synthetic electricity activity data."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ACTIVITY_PATH = ROOT / "data" / "electricity_activity.csv"
LINE_ITEMS_PATH = ROOT / "results" / "line_items.csv"
REPORT_PATH = ROOT / "results" / "report.json"
DEFAULT_SEED = 39
PERIODS = ("2026-Q1", "2026-Q2", "2026-Q3", "2026-Q4")
SITES = {
    "campus": {"location": 0.46, "market": 0.12},
    "biology_lab": {"location": 0.51, "market": 0.18},
    "library": {"location": 0.43, "market": 0.10},
}


def generate_activity(seed: int = DEFAULT_SEED) -> list[dict[str, str]]:
    rng = random.Random(seed)
    rows: list[dict[str, str]] = []
    for site, factors in SITES.items():
        site_scale = {"campus": 1.0, "biology_lab": 0.62, "library": 0.76}[site]
        for quarter_index, period in enumerate(PERIODS):
            seasonal = (1.0, 1.06, 0.94, 1.12)[quarter_index]
            electricity = 42_000 * site_scale * seasonal * rng.uniform(0.96, 1.04)
            rows.append(
                {
                    "period": period,
                    "facility": site,
                    "electricity_kwh": f"{electricity:.2f}",
                    "location_factor_kg_co2e_per_kwh": f"{factors['location']:.4f}",
                    "market_factor_kg_co2e_per_kwh": f"{factors['market']:.4f}",
                    "factor_source": "illustrative_placeholder_not_a_published_factor",
                    "data_kind": "synthetic",
                }
            )
    return rows


def calculate_ledger(activity_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, object]]:
    line_items: list[dict[str, str]] = []
    totals: dict[str, float] = defaultdict(float)
    facility_totals: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in activity_rows:
        electricity = float(row["electricity_kwh"])
        location_factor = float(row["location_factor_kg_co2e_per_kwh"])
        market_factor = float(row["market_factor_kg_co2e_per_kwh"])
        if electricity < 0 or location_factor < 0 or market_factor < 0:
            raise ValueError("Activity and emission factors must be non-negative")
        for method, factor in (("location-based", location_factor), ("market-based", market_factor)):
            emissions = electricity * factor
            line_items.append(
                {
                    "period": row["period"],
                    "facility": row["facility"],
                    "method": method,
                    "electricity_kwh": f"{electricity:.2f}",
                    "factor_kg_co2e_per_kwh": f"{factor:.4f}",
                    "emissions_kg_co2e": f"{emissions:.4f}",
                    "factor_source": row["factor_source"],
                }
            )
            totals[method] += emissions
            facility_totals[row["facility"]][method] += emissions
    location = totals["location-based"]
    market = totals["market-based"]
    report = {
        "project": "scope2-emissions-ledger",
        "data_kind": "synthetic",
        "seed": DEFAULT_SEED,
        "activity_rows": len(activity_rows),
        "factor_unit": "kg CO2e per kWh",
        "totals_kg_co2e": {method: round(value, 4) for method, value in sorted(totals.items())},
        "totals_t_co2e": {method: round(value / 1000, 6) for method, value in sorted(totals.items())},
        "facility_totals_kg_co2e": {
            facility: {method: round(value, 4) for method, value in sorted(methods.items())}
            for facility, methods in sorted(facility_totals.items())
        },
        "market_minus_location_kg_co2e": round(market - location, 4),
        "factor_status": "all factors are placeholders for demonstration; replace and document sources before any real accounting",
        "limitations": [
            "Electricity use and factors are synthetic or illustrative placeholders, not sourced inventory inputs.",
            "No contractual instrument quality, supplier evidence, residual mix, grid region, or factor vintage is validated.",
            "This teaching ledger is not a compliance assessment or a reportable greenhouse-gas inventory.",
        ],
    }
    return line_items, report


def write_outputs(seed: int = DEFAULT_SEED) -> dict[str, object]:
    activity = generate_activity(seed)
    line_items, report = calculate_ledger(activity)
    report["seed"] = seed
    ACTIVITY_PATH.parent.mkdir(parents=True, exist_ok=True)
    LINE_ITEMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ACTIVITY_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(activity[0]))
        writer.writeheader()
        writer.writerows(activity)
    with LINE_ITEMS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(line_items[0]))
        writer.writeheader()
        writer.writerows(line_items)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="deterministic synthetic-data seed")
    args = parser.parse_args()
    report = write_outputs(args.seed)
    for method, amount in report["totals_t_co2e"].items():
        print(f"{method}: {amount:.6f} t CO2e (placeholder factors)")
    print(f"Wrote {ACTIVITY_PATH.relative_to(ROOT)}, {LINE_ITEMS_PATH.relative_to(ROOT)} and {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
