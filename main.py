#!/usr/bin/env python3
import argparse
import sys

from network.ip import get_ip_report
from output import console
from output.json import write_report
from services import run_all_checks


def parse_args():
    parser = argparse.ArgumentParser(description="Check Google service availability from your network.")
    parser.add_argument(
        "--json",
        nargs="?",
        const="report.json",
        default=None,
        metavar="PATH",
        help="Also write a machine-readable JSON report (default: report.json)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Don't print the live 'Checking...' progress lines",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    console.print_banner()

    ip_info = get_ip_report()
    console.print_ip_report(ip_info)

    print("Checking Google services...\n")

    def progress(name):
        if not args.quiet:
            console.print_checking(name)

    results = run_all_checks(progress_callback=progress if not args.quiet else None)

    if not args.quiet:
        print(" " * 40, end="\r")

    for r in results:
        console.print_result_line(r)
    print()

    console.print_summary(results)

    if args.json:
        path = write_report(ip_info, results, path=args.json)
        print(f"📄 JSON report written to: {path}")

    any_restricted = any(r.status != "AVAILABLE" for r in results)
    sys.exit(1 if any_restricted else 0)


if __name__ == "__main__":
    main()
