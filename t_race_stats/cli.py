"""CLI interface for t_race_stats project."""

from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="Process T-Race stats")

    args = parser.parse_args()
    print(args)
