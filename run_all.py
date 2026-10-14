"""Reproduce research, monthly data and the completed Stage 1 and Stage 2 exhibits."""
import argparse

from scripts.research import run as run_research


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--daily-root",
        help="Optional local tbic_returns directory: replay coverage from nine daily panels.",
    )
    parser.add_argument(
        "--monthly", action="store_true",
        help="Also build monthly returns from local daily panels.",
    )
    parser.add_argument(
        "--stage1", action="store_true",
        help="Build static Stage 1 exhibits from cached monthly returns and year-end capitalization.",
    )
    parser.add_argument(
        "--stage2", action="store_true",
        help="Build CAPM, SML and GRS exhibits; also rebuild the required Stage 1 outputs.",
    )
    parser.add_argument(
        "--stage4", action="store_true",
        help="Build MSCI World CAPM, SML, GRS and comparisons; also rebuild Stage 1 and Stage 2 outputs.",
    )
    args = parser.parse_args()

    if args.stage4:
        args.stage2 = True

    run_research(args.daily_root)

    if args.monthly:
        from scripts.monthly import build
        build(args.daily_root or "tbic_returns")

    if args.stage1 or args.stage2:
        from scripts.stage1 import run as run_stage1
        run_stage1()

    if args.stage2:
        from scripts.stage2 import run as run_stage2
        run_stage2()

    if args.stage4:
        from scripts.stage4 import run as run_stage4
        run_stage4()


if __name__ == "__main__":
    main()
