"""scripts/day11_figures.py — Day 11: build every paper figure from results/.

Runs shellform.figures.main: Fig. 1 (form gallery, shellform.gallery, both
spans) and Figs. 2-5 (mechanism, strategy difference, carbon drivers, S5
periods). Each figure is written to figures/ as PNG and PDF (Figs. 2-5) with
a JSON file of the plotted numbers and the ShellBench tag of the record.
No figure is edited by hand.

Usage (from the repository root):
    python scripts/day11_figures.py               # all figures
    python scripts/day11_figures.py --no-gallery  # Figs. 2-5 only (no form finding)
"""

import sys

from shellform.figures import main

if __name__ == "__main__":
    main(sys.argv[1:])
