import argparse
import logging
import sys

from colorama import Fore, Style, init

# Exit code constants
from .constants import (
    DEFAULT_THRESHOLD,
    EXIT_CANCELLED,
    EXIT_INVALID_USAGE,
    EXIT_NO_RESULTS,
    EXIT_SUCCESS,
    VALID_FUZZY_ALGOS,
    VALID_MATCH_MODES,
)
from .core import find_chars

# Initialize color output
init(autoreset=True)

# Windows-specific UTF-8 setup
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

# Setup CLI-specific logger
logger = logging.getLogger("charfinder.cli")
logger.propagate = False
if not logger.hasHandlers():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def threshold_range(value: str) -> float:
    """
    Validate and convert the threshold argument to a float between 0.0 and 1.0.

    Args:
        value (str): Threshold string from CLI input.

    Returns:
        float: Parsed threshold value.

    Raises:
        argparse.ArgumentTypeError: If the value is not in the 0.0–1.0 range.
    """
    val = float(value)
    if not 0.0 <= val <= 1.0:
        raise argparse.ArgumentTypeError("Threshold must be between 0.0 and 1.0")
    return val


def should_use_color(mode: str) -> bool:
    """
    Determine whether to use color output based on the mode and terminal capability.

    Args:
        mode (str): One of 'auto', 'always', or 'never'.

    Returns:
        bool: True if color should be used.
    """
    if mode == "never":
        return False
    if mode == "always":
        return True
    return sys.stdout.isatty()


def print_result_lines(lines: list[str], use_color: bool) -> None:
    """
    Print the list of result lines with optional color formatting.

    Args:
        lines (list[str]): Lines to print.
        use_color (bool): Whether to use color formatting.
    """
    for line in lines:
        if not use_color:
            print(line)
        elif line.startswith("CODE"):
            print(Fore.CYAN + line + Style.RESET_ALL)
        elif line.startswith("U+"):
            print(Fore.YELLOW + line + Style.RESET_ALL)
        else:
            print(line)


def main() -> None:
    """
    Main function for the CLI. Parses arguments, executes the search, and prints results.
    Handles fuzzy match options, CLI flags, logging, and exit codes.
    """
    parser = argparse.ArgumentParser(
        description="Find Unicode characters by name using substring or fuzzy search.",
        epilog="""Examples:
  python cli.py -q heart
  python cli.py -q smilng --fuzzy --threshold 0.6""",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-q", "--query", required=True, help="Query string to search Unicode names."
    )
    parser.add_argument(
        "--fuzzy", action="store_true", help="Enable fuzzy search if no exact matches."
    )
    parser.add_argument(
        "--threshold",
        type=threshold_range,
        default=DEFAULT_THRESHOLD,
        help="Fuzzy match threshold (0.0–1.0)",
    )
    parser.add_argument(
        "--color", choices=["auto", "always", "never"], default="always", help="Colored output"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress info messages.")
    parser.add_argument("--fuzzy-algo", choices=VALID_FUZZY_ALGOS, default="sequencematcher")
    parser.add_argument("--match-mode", choices=VALID_MATCH_MODES, default="single")

    try:
        import argcomplete

        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args()
    use_color = should_use_color(args.color)

    if not args.query.strip():
        logger.error(
            f"{Fore.RED if use_color else ''}[ERROR]{Style.RESET_ALL if use_color else ''} Query string is empty."
        )
        sys.exit(EXIT_INVALID_USAGE)

    try:
        results = list(
            find_chars(
                query=args.query,
                fuzzy=args.fuzzy,
                threshold=args.threshold,
                verbose=not args.quiet,
                use_color=use_color,
                fuzzy_algo=args.fuzzy_algo,
                match_mode=args.match_mode,
            )
        )

        if not results:
            sys.exit(EXIT_NO_RESULTS)

        print_result_lines(results, use_color)
        sys.exit(EXIT_SUCCESS)

    except KeyboardInterrupt:
        logger.error(
            f"{Fore.RED if use_color else ''}[ERROR]{Style.RESET_ALL if use_color else ''} Search cancelled by user."
        )
        sys.exit(EXIT_CANCELLED)
    except Exception as e:
        logger.error(
            f"{Fore.RED if use_color else ''}[ERROR]{Style.RESET_ALL if use_color else ''} {e}"
        )
        sys.exit(EXIT_INVALID_USAGE)


if __name__ == "__main__":
    main()
