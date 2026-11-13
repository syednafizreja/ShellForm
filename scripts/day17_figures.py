"""scripts/day17_figures.py

Draw the check-window figures (14 Nov 2026): Fig. 6 (carbon against the
first buckling factor, with the Pareto front) and Fig. S1 (verification
add-ons V1-V5). Run scripts/day17_verification.py first for Fig. S1.

Run from the repository root:

    python scripts/day17_figures.py

Output: figures/fig06_carbon_stability.{png,pdf,json} and
figures/figS1_verification.{png,pdf,json}.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shellform.verify_figures import main  # noqa: E402

if __name__ == "__main__":
    main()
