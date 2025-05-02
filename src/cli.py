"""
Unicode Character Finder CLI

This script provides a command-line interface for searching Unicode
characters by name using strict and fuzzy matching via core.py.

Features:
- Colorized and aligned output using colorama
- Configurable fuzzy threshold
- UTF-8 handling for Windows

Usage:
    python cli.py -q "heart"
    python cli.py -q "smilng" --fuzzy --threshold 0.6
"""
import sys
import argparse
import os
import logging
from colorama import init, Fore, Style
from core import find_chars

init(autoreset=True)

logger = logging.getLogger("core")
logging.basicConfig(level=logging.INFO, format="%(message)s")

if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')

def threshold_range(value: str) -> float:
    val = float(value)
    if not (0.0 <= val <= 1.0):
        raise argparse.ArgumentTypeError("Threshold must be between 0.0 and 1.0")
    return val

def main():
    parser = argparse.ArgumentParser(
        description="Find Unicode characters by name using substring or fuzzy search.",
        epilog="""
Examples:
  python core.py -q heart
  python core.py -q smilng --fuzzy --threshold 0.6
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-q', '--query', type=str, required=True, help='Query string to search Unicode names.')
    parser.add_argument('--fuzzy', action='store_true', help='Enable fuzzy search when no exact matches found.')
    parser.add_argument('--threshold', type=threshold_range, default=0.7,
                        help='Fuzzy match threshold (0.0 to 1.0)')
    parser.add_argument('--no-color', action='store_true', help='Disable colorized output (useful for tests).')
    parser.add_argument('--quiet', action='store_true', help='Suppress info messages.')
    parser.add_argument('--version', action='version', version="Unicode Finder 1.0")
    args = parser.parse_args()

    if not args.query.strip():
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Query string is empty.", file=sys.stderr)
        sys.exit(1)

    try:
        results = list(find_chars(
            args.query,
            fuzzy=args.fuzzy,
            threshold=args.threshold,
            verbose=not args.quiet
        ))

        if not results:
            if not args.quiet:
                logger.info("No matching results.")
            sys.exit(0)

        for line in results:
            parts = line.split('\t')
            if len(parts) >= 3:
                if args.no_color:
                    print(line)
                else:
                    print(f"{Fore.CYAN}{parts[0]}{Style.RESET_ALL}\t"
                          f"{Fore.YELLOW}{parts[1]}{Style.RESET_ALL}\t"
                          f"{parts[2]}")
            else:
                print(line)

    except KeyboardInterrupt:
        logger.info("\nSearch cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
