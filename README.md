# 3806ICT Assignment 1 - FOL Proof Search Project

This project implements a small first-order logic automated reasoning pipeline based on backward sequent-calculus proof search.

## Files

- `logic.py` - term, formula and sequent data structures.
- `parser.py` - parser for one FOL formula per line.
- `solver.py` - baseline solver based on Algorithm 2 and improved solver.
- `run_experiments.py` - runs both solvers on all datasets and writes CSV files.
- `datasets/` - easy, medium and hard formula datasets.
- `report/report.tex` - LNCS-style report draft/template to edit in Overleaf.

## Formula syntax

Use one formula per line.

Connectives:

- `~` negation
- `&` conjunction
- `|` disjunction
- `->` implication
- `forall x. F`
- `exists x. F`

Examples:

```text
A -> A
forall x. P(x) -> P(a)
(forall x. (P(x) -> Q(x))) -> (P(a) -> Q(a))
```

## How to run

Use Python 3.10+.

```bash
cd fol_solver_project
python run_experiments.py
```

The output CSV files are written to `results/`.

## For the report

1. Run the experiment.
2. Copy the generated `results/summary_results.csv` numbers into the results table in `report/report.tex`.
3. Upload `report/report.tex` to the Springer LNCS Overleaf template.
4. Replace the GitHub link in the Data Availability section with your own repository link.
5. Rewrite the report wording in your own voice before submission.
