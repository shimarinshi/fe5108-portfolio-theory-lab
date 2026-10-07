"""Reproduce the completed research checkpoint, with optional Stage 1 portfolio exhibits."""
import argparse
from scripts.research import run

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--daily-root',help='Optional local tbic_returns directory: replay coverage from nine daily panels.')
    parser.add_argument('--monthly', action='store_true', help='Also build monthly returns from local daily panels.')
    parser.add_argument('--stage1', action='store_true', help='Build static Stage 1 exhibits from cached monthly returns and year-end capitalization.')
    args = parser.parse_args()
    run(args.daily_root)
    if args.monthly:
        from scripts.monthly import build
        build(args.daily_root or 'tbic_returns')

    if args.stage1:
        from scripts.stage1 import run as run_stage1
        run_stage1()
