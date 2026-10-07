"""Reproduce the completed research checkpoint, not yet the four course stages."""
import argparse
from scripts.research import run

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--daily-root',help='Optional local tbic_returns directory: replay coverage from nine daily panels.')
    parser.add_argument('--monthly', action='store_true', help='Also build monthly returns from local daily panels.')
    args = parser.parse_args()
    run(args.daily_root)
    if args.monthly:
        from scripts.monthly import build
        build(args.daily_root or 'tbic_returns')
