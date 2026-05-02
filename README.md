# 3806ICT Assignment 1 - Automated Reasoning Project

This repository contains my work for 3806ICT Logic and Automated Reasoning Assignment 1.

The main aim of this project is to build a small automated reasoning system for first-order logic formulae. The system reads formulae from text files, converts them into an internal formula structure, and then tries to prove them using a baseline proof-search method and an improved version.

## What is included

The project includes:

- a formula and term representation for first-order logic
- a parser for reading formulae from dataset files
- a baseline proof-search solver based on Algorithm 2 from the course textbook
- an improved solver with repeated-state caching and controlled quantifier handling
- three datasets with easy, medium, and hard formulae
- experiment results comparing the baseline and improved solvers
- the report draft in LNCS style

## Project files

- `logic.py`  
  Defines the term and formula classes used by the parser and solvers.

- `parser.py`  
  Reads formulae from text files and converts them into formula objects.

- `solver.py`  
  Contains the baseline solver and improved solver.

- `run_experiments.py`  
  Runs both solvers on all datasets and writes the results to CSV files.

- `datasets/`  
  Contains the easy, medium, and hard formula datasets.

- `results/`  
  Contains the generated experiment result files.

- `report/`  
  Contains the report draft.

## How to run

From the main project folder, run:

```bash
python run_experiments.py