import sys
import argparse
import os
import logging
from colorama import init, Fore, Style
from core import find_chars

# Initialize color output
init(autoreset=True)

# Windows-specific UTF-8 setup
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')

# Setup CLI-specific logger
logger = logging.getLogger("charfinder.cli")
logger.propagate = False  # Prevent double logging from root
if not logger.hasHandlers():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')  # no levelname prefix for CLI
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def threshold_range(value: str) -> float:
    val = float(value)
    if not (0.0 <= val <= 1.0):
        raise argparse.ArgumentTypeError("Threshold must be between 0.0 and 1.0")
    return val

def should_use_color(color_mode: str) -> bool:
    if color_mode == "never":
        return False
    elif color_mode == "always":
        return True
    # 'auto'
    return sys.stdout.isatty()

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find Unicode characters by name using substring or fuzzy search.",
        epilog="""
        Examples:
          python cli.py -q heart
          python cli.py -q smilng --fuzzy --threshold 0.6
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-q", "--query", type=str, required=True,
        help="Query string to search Unicode names."
    )
    parser.add_argument(
        "--fuzzy", action="store_true",
        help="Enable fuzzy search when no exact matches found."
    )
    parser.add_argument(
        "--threshold", type=threshold_range, default=0.7,
        help="Fuzzy match threshold (0.0 to 1.0)"
    )
    parser.add_argument(
        "--color", choices=["auto", "always", "never"],
        default="auto", help="Color output: 'auto' (default), 'always', or 'never'."
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress info messages."
    )

    # Optional autocomplete support
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args()
    use_color = should_use_color(args.color)

    if not args.query.strip():
        logger.error(f"{Fore.RED if use_color else ''}[ERROR]{Style.RESET_ALL if use_color else ''} Query string is empty.")
        sys.exit(1)

    try:
        results = list(find_chars(
            args.query,
            fuzzy=args.fuzzy,
            threshold=args.threshold,
            verbose=not args.quiet
        ))

        if not results:
            sys.exit(2)

        for line in results:
            parts = line.split('\t')
            if len(parts) >= 3:
                if use_color:
                    print(f"{Fore.CYAN}{parts[0]}{Style.RESET_ALL}\t"
                          f"{Fore.YELLOW}{parts[1]}{Style.RESET_ALL}\t"
                          f"{parts[2]}")
                else:
                    print(line)
            else:
                print(line)

    except KeyboardInterrupt:
        logger.error("Search cancelled by user.")
    except Exception as e:
        logger.error(f"{Fore.RED if use_color else ''}[ERROR]{Style.RESET_ALL if use_color else ''} {e}")

if __name__ == '__main__':
    main()