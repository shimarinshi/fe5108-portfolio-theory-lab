"""Reproduce the completed research checkpoint, not yet the four course stages."""
import argparse
from scripts.research import run

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--daily-root',help='Optional local tbic_returns directory: replay coverage from nine daily panels.')
    run(parser.parse_args().daily_root)
