"""CLI entrypoint: ``python -m eval`` (run from the ``models/`` directory).

Examples::

    python -m eval                          # synthetic set, print report
    python -m eval --json out.json          # also write the structured result
    python -m eval --dataset path/to.json   # target a real labelled catalog

A real run that actually exercises model quality also needs the OpenCLIP backend::

    ZETIX_EMBEDDER=openclip python -m eval --dataset real_10k.json
"""

from __future__ import annotations

import argparse
import sys

from .dataset import load_dataset, synthetic_dataset
from .harness import M1_TOP3_BAR, run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m eval", description=__doc__)
    parser.add_argument(
        "--dataset",
        metavar="PATH",
        help="Path to a real labelled dataset JSON (see README). Defaults to the "
        "built-in synthetic set.",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        dest="json_out",
        help="Also write the structured result as JSON to PATH.",
    )
    bar_pct = int(round(M1_TOP3_BAR * 100))
    parser.add_argument(
        "--require-bar",
        action="store_true",
        help=f"Exit non-zero if Top-3 accuracy is below the M1 bar ({bar_pct} percent). "
        "Only meaningful with the real model + a real catalog.",
    )
    args = parser.parse_args(argv)

    dataset = load_dataset(args.dataset) if args.dataset else synthetic_dataset()
    result = run(dataset, json_out=args.json_out)

    if args.require_bar and result["top3"] < M1_TOP3_BAR:
        print(f"FAIL: Top-3 {result['top3']:.1%} is below the M1 bar {M1_TOP3_BAR:.0%}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
