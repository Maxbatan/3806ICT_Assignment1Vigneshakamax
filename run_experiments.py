from __future__ import annotations
import csv
import glob
import os
import time
from parser import parse_file
from solver import prove_baseline, prove_improved

DATASETS = [
    os.path.join("datasets", "easy.txt"),
    os.path.join("datasets", "medium.txt"),
    os.path.join("datasets", "hard.txt"),
]

def timed(fn, formula):
    start = time.perf_counter()
    result = fn(formula)
    elapsed = time.perf_counter() - start
    return result, elapsed

def main():
    os.makedirs("results", exist_ok=True)
    detailed_path = os.path.join("results", "detailed_results.csv")
    summary_path = os.path.join("results", "summary_results.csv")

    rows = []
    summary = []
    for path in DATASETS:
        dataset = os.path.splitext(os.path.basename(path))[0]
        formulas = parse_file(path)
        b_solved = i_solved = 0
        b_time_total = i_time_total = 0.0
        b_steps_total = i_steps_total = 0
        for idx, f in enumerate(formulas, 1):
            b, bt = timed(prove_baseline, f)
            i, it = timed(prove_improved, f)
            b_solved += int(b.proved)
            i_solved += int(i.proved)
            b_time_total += bt
            i_time_total += it
            b_steps_total += b.steps
            i_steps_total += i.steps
            rows.append({
                "dataset": dataset,
                "id": idx,
                "formula": str(f),
                "baseline_proved": b.proved,
                "improved_proved": i.proved,
                "baseline_time_s": f"{bt:.6f}",
                "improved_time_s": f"{it:.6f}",
                "baseline_steps": b.steps,
                "improved_steps": i.steps,
            })
        n = len(formulas)
        summary.append({
            "dataset": dataset,
            "formulas": n,
            "baseline_solved": b_solved,
            "improved_solved": i_solved,
            "baseline_total_time_s": f"{b_time_total:.6f}",
            "improved_total_time_s": f"{i_time_total:.6f}",
            "baseline_avg_steps": f"{b_steps_total / n:.1f}",
            "improved_avg_steps": f"{i_steps_total / n:.1f}",
        })

    with open(detailed_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    print("Summary")
    for r in summary:
        print(r)
    print(f"\nWrote {detailed_path} and {summary_path}")

if __name__ == "__main__":
    main()
