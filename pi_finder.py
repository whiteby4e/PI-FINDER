"""Interactive terminal interface for PI-FINDER."""

from __future__ import annotations

import ctypes
import os
import time
import webbrowser
from pathlib import Path

from benchmark_search import (
    DEFAULT_CHUNK_SIZES,
    benchmark_search,
    compare_chunk_sizes,
    format_bytes,
    print_benchmark_result,
)
from generate_pi import write_pi
from pi_search import search_text

DEFAULT_PI_FILE = "pi.txt"
DEFAULT_AUTO_DIGITS = 100_000
AUTO_MAX_DIGITS = 10_000_000
RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
PI_PREFIX = "314159265358979323846264338327950288419716939937510"


class UI:
    """Small ANSI terminal UI with a safe Windows fallback."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"

    @classmethod
    def enable(cls) -> None:
        if os.name != "nt":
            return
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except (AttributeError, OSError):
            pass

    @classmethod
    def paint(cls, text: str, color: str = "") -> str:
        return f"{color}{text}{cls.RESET}" if color else text

    @classmethod
    def clear(cls) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    @classmethod
    def header(cls, title: str, subtitle: str = "") -> None:
        print()
        print(cls.paint("╔════════════════════════════════════════════════════════════╗", cls.CYAN))
        print(cls.paint(f"║  {title:<56}║", cls.BOLD + cls.WHITE))
        if subtitle:
            print(cls.paint(f"║  {subtitle:<56}║", cls.DIM + cls.CYAN))
        print(cls.paint("╚════════════════════════════════════════════════════════════╝", cls.CYAN))

    @classmethod
    def section(cls, title: str) -> None:
        print()
        print(cls.paint(f"── {title} " + "─" * max(0, 54 - len(title)), cls.BLUE))

    @classmethod
    def success(cls, text: str) -> None:
        print(cls.paint(f"✓ {text}", cls.GREEN))

    @classmethod
    def error(cls, text: str) -> None:
        print(cls.paint(f"✗ {text}", cls.RED))

    @classmethod
    def warn(cls, text: str) -> None:
        print(cls.paint(f"! {text}", cls.YELLOW))

    @classmethod
    def info(cls, text: str) -> None:
        print(cls.paint(f"› {text}", cls.CYAN))

    @classmethod
    def stat(cls, label: str, value: str) -> None:
        print(f"  {cls.paint(label + ':', cls.DIM):<24}{cls.paint(value, cls.WHITE)}")

    @classmethod
    def bar(cls, current: int, total: int, width: int = 34) -> str:
        if total <= 0:
            return "[" + "·" * width + "]"
        ratio = min(1.0, max(0.0, current / total))
        filled = int(ratio * width)
        return "[" + "█" * filled + "░" * (width - filled) + "]"


def encode_word(word: str) -> str:
    """Encode A-Z as fixed-width A1Z26 digits."""
    cleaned = "".join(word.split()).upper()

    if not cleaned:
        raise ValueError("word cannot be empty")

    if not cleaned.isascii() or not cleaned.isalpha():
        raise ValueError("word must contain only A-Z letters")

    return "".join(f"{ord(char) - ord('A') + 1:02d}" for char in cleaned)


def search_number(file_path: str | Path, number: str) -> int:
    """Search a numeric pattern in a pi file."""
    return search_text(file_path, number)


def search_word(file_path: str | Path, word: str) -> tuple[str, int]:
    """Encode a word and search its digit representation."""
    encoded = encode_word(word)
    return encoded, search_text(file_path, encoded)


def _pi_digits_in_file(file_path: Path) -> int:
    """Return the number of digits in the continuous pi dataset."""
    if not file_path.exists():
        return 0

    size = file_path.stat().st_size
    if size == 0:
        return 0

    with file_path.open("rb") as file:
        file.seek(-1, 2)
        if file.read(1) == b"\n":
            size -= 1
            if size > 0:
                file.seek(-1, 2)
                if file.read(1) == b"\r":
                    size -= 1

    return size


def _generate_more_pi(file_path: Path, current_digits: int, required_digits: int) -> int:
    """Generate a larger pi dataset and return its new digit count."""
    if current_digits == 0:
        target = max(DEFAULT_AUTO_DIGITS, required_digits)
    else:
        target = max(current_digits * 2, required_digits)

    target = min(target, AUTO_MAX_DIGITS)

    if target <= current_digits:
        return current_digits

    UI.section("PI GENERATOR")
    UI.info(f"Growing database: {current_digits:,} → {target:,} digits")
    start = time.perf_counter()
    write_pi(file_path, target)
    elapsed = time.perf_counter() - start
    UI.success(f"Generated {target:,} digits in {elapsed:.3f} s.")
    return target


def auto_search(file_path: str | Path, pattern: str, label: str = "number") -> int:
    """Search and grow a verified digits-only pi database when needed."""
    path = Path(file_path)
    current_digits = _pi_digits_in_file(path)

    if current_digits:
        if not check_database_integrity(path, repair=True):
            raise ValueError("pi database could not be repaired")

    if current_digits == 0:
        current_digits = _generate_more_pi(path, 0, len(pattern))

    while True:
        UI.info(f"Scanning {current_digits:,} pi digits...")
        position = search_text(path, pattern)

        if position != -1:
            return position

        if current_digits >= AUTO_MAX_DIGITS:
            UI.warn(
                f"Pattern not found after {current_digits:,} digits. "
                "Automatic generation limit reached."
            )
            return -1

        UI.warn(f"Not found in the current {label} dataset.")
        next_digits = _generate_more_pi(path, current_digits, len(pattern))

        if next_digits == current_digits:
            return -1

        current_digits = next_digits


def print_result(position: int) -> None:
    if position == -1:
        UI.error("Pattern not found.")
    else:
        UI.success(f"Found at position {position:,}.")


def database_info(file_path: Path) -> None:
    """Display information about the current pi database."""
    digits = _pi_digits_in_file(file_path)

    UI.header("PI DATABASE", "Persistent π dataset status")

    if not file_path.exists():
        UI.error("Database not found.")
        UI.stat("Database", str(file_path))
        UI.stat("Digits", "0")
        UI.stat("File size", "0 B")
        UI.info("Generate a database from the main menu.")
        return

    size = file_path.stat().st_size
    modified = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_path.stat().st_mtime))

    UI.success("Database is available.")
    UI.stat("Path", str(file_path))
    UI.stat("Digits", f"{digits:,}")
    UI.stat("File size", format_bytes(size))
    UI.stat("Last update", modified)

    if digits:
        progress = min(100, digits / AUTO_MAX_DIGITS * 100)
        print(f"\n  {UI.bar(digits, AUTO_MAX_DIGITS)} {progress:6.2f}%")
        UI.stat("Auto-search limit", f"{AUTO_MAX_DIGITS:,} digits")


def continue_generation(file_path: Path) -> None:
    """Double the current database size and regenerate pi."""
    current_digits = _pi_digits_in_file(file_path)

    if current_digits == 0:
        target = DEFAULT_AUTO_DIGITS
    else:
        target = min(current_digits * 2, AUTO_MAX_DIGITS)

    if target <= current_digits:
        UI.warn(f"Database is already at the {AUTO_MAX_DIGITS:,}-digit limit.")
        return

    _generate_more_pi(file_path, current_digits, target)


def check_database_integrity(file_path: Path, repair: bool = False) -> bool:
    """Check the dataset and optionally rebuild it when corruption is found."""
    if not file_path.exists():
        UI.error("Database integrity: FAILED")
        UI.warn("Reason: pi.txt does not exist.")
        return False

    prefix_bytes = PI_PREFIX.encode("ascii")

    try:
        with file_path.open("rb") as file:
            prefix = file.read(len(prefix_bytes))
            if prefix != prefix_bytes:
                mismatch = min(len(prefix), len(prefix_bytes))
                while mismatch < len(prefix) and mismatch < len(prefix_bytes):
                    if prefix[mismatch] != prefix_bytes[mismatch]:
                        break
                    mismatch += 1

                actual = prefix[mismatch:mismatch + 1]
                expected = prefix_bytes[mismatch:mismatch + 1]
                actual_value = f"0x{actual[0]:02X} ({actual!r})" if actual else "EOF"
                expected_value = f"0x{expected[0]:02X} ({expected!r})" if expected else "EOF"

                UI.error("Database integrity: FAILED")
                UI.stat("Reason", f"π prefix mismatch at {mismatch + 1:,}")
                UI.stat("Expected", expected_value)
                UI.stat("Found", actual_value)
                return _repair_database(file_path) if repair else False

            checked = len(prefix)
            file_size = file_path.stat().st_size

            while True:
                chunk_start = checked
                chunk = file.read(8 * 1024 * 1024)
                if not chunk:
                    break

                is_last_chunk = file.tell() == file_size

                if is_last_chunk:
                    if chunk.endswith(b"\r\n"):
                        chunk = chunk[:-2]
                    elif chunk.endswith(b"\n"):
                        chunk = chunk[:-1]

                invalid_index = next(
                    (
                        index
                        for index, byte in enumerate(chunk)
                        if byte < ord("0") or byte > ord("9")
                    ),
                    None,
                )

                if invalid_index is not None:
                    position = chunk_start + invalid_index + 1
                    value = chunk[invalid_index]
                    context_start = max(0, invalid_index - 10)
                    context_end = min(len(chunk), invalid_index + 11)
                    context = chunk[context_start:context_end]

                    UI.error("Database integrity: FAILED")
                    UI.stat("Reason", "Non-digit data detected")
                    UI.stat("Position", f"{position:,}")
                    UI.stat("Byte", f"0x{value:02X} ({value!r})")
                    UI.stat("Context", repr(context))
                    return _repair_database(file_path) if repair else False

                checked += len(chunk)

    except (OSError, UnicodeError) as exc:
        UI.error("Database integrity: FAILED")
        UI.stat("Reason", str(exc))
        return False

    UI.success("Database integrity: OK")
    UI.stat("Checked", f"{checked:,} characters")
    UI.stat("Format", "digits-only (314159...)")
    return True


def _repair_database(file_path: Path) -> bool:
    """Rebuild a corrupted database using its current digit count."""
    try:
        raw = file_path.read_bytes()
        digit_count = sum(ord("0") <= byte <= ord("9") for byte in raw)

        if digit_count < len(PI_PREFIX):
            UI.error("Repair failed: database is too small to rebuild safely.")
            return False

        UI.warn(f"Corruption detected. Rebuilding {digit_count:,} digits...")
        start = time.perf_counter()
        write_pi(file_path, digit_count)
        elapsed = time.perf_counter() - start
        UI.success(f"Repair complete in {elapsed:.3f} s.")
        return check_database_integrity(file_path, repair=False)
    except (OSError, ValueError) as exc:
        UI.error(f"Repair failed: {exc}")
        return False


def generate_pi_file(file_path: Path) -> None:
    """Generate a new pi file from the interactive menu."""
    raw_digits = input("Total pi digits (including the leading 3): ").strip()
    digits = int(raw_digits)

    if digits <= 0:
        raise ValueError("total digits must be greater than zero")

    UI.header("PI GENERATOR", "Creating a fresh π dataset")
    UI.info(f"Target: {digits:,} total digits")
    UI.warn("Large values can require substantial CPU time and RAM.")

    start = time.perf_counter()
    write_pi(file_path, digits)
    elapsed = time.perf_counter() - start

    UI.success(f"Written: {file_path}")
    UI.stat("Digits", f"{digits:,}")
    UI.stat("Time", f"{elapsed:.3f} s")


def run_search(file_path: Path, pattern: str, label: str) -> None:
    """Run an automatic search and show polished search statistics."""
    UI.header("PI SEARCH", f"{label.title()} lookup")

    start = time.perf_counter()
    position = auto_search(file_path, pattern, label)
    elapsed = time.perf_counter() - start
    digits = _pi_digits_in_file(file_path)

    print_result(position)

    UI.section("SEARCH STATISTICS")
    UI.stat("Pattern", pattern)
    UI.stat("Mode", label.upper())
    UI.stat("Position", f"{position:,}" if position != -1 else "NOT FOUND")
    UI.stat("Dataset", f"{digits:,} digits")
    UI.stat("Time", f"{elapsed:.4f} s")
    if elapsed > 0:
        UI.stat("Throughput", f"{digits / 1024 / 1024 / elapsed:.2f} MiB/s")


def run_benchmark(file_path: Path) -> None:
    """Benchmark the real pi database."""
    if not file_path.exists():
        raise FileNotFoundError(f"Pi file not found: {file_path}")

    pattern = input("Enter number to benchmark: ").strip()
    if not pattern:
        raise ValueError("pattern cannot be empty")

    repeat_text = input("Repeats [1]: ").strip() or "1"
    repeat = int(repeat_text)
    if repeat <= 0:
        raise ValueError("repeats must be greater than zero")

    UI.header("BENCHMARK LAB", "Real-file performance test")
    print(UI.paint("  [1] Single chunk size", UI.WHITE))
    print(UI.paint("  [2] Compare 1 / 4 / 8 / 16 MiB", UI.WHITE))
    mode = input("\nSelect [2]: ").strip() or "2"

    if mode == "1":
        chunk_text = input("Chunk size MiB [8]: ").strip() or "8"
        chunk_mib = float(chunk_text)
        if chunk_mib <= 0:
            raise ValueError("chunk size must be greater than zero")

        chunk_size = int(chunk_mib * 1024 * 1024)
        result = benchmark_search(file_path, pattern, chunk_size, repeat)

        UI.section("RESULT")
        UI.stat("File", str(file_path))
        UI.stat("Size", format_bytes(file_path.stat().st_size))
        UI.stat("Pattern", pattern)
        print_benchmark_result(result)
        return

    if mode == "2":
        results = compare_chunk_sizes(file_path, pattern, DEFAULT_CHUNK_SIZES, repeat)

        UI.section("CHUNK COMPARISON")
        UI.stat("File", str(file_path))
        UI.stat("Size", format_bytes(file_path.stat().st_size))
        UI.stat("Pattern", pattern)
        UI.stat("Repeats", str(repeat))
        print()

        for result in results:
            print(UI.paint(f"  ▸ {format_bytes(int(result['chunk_size']))} chunk", UI.MAGENTA))
            print_benchmark_result(result)
            print()

        fastest = min(results, key=lambda item: float(item["time"]))
        UI.success(
            f"Fastest chunk: {format_bytes(int(fastest['chunk_size']))} "
            f"({float(fastest['time']):.4f} s)"
        )
        return

    raise ValueError("invalid benchmark mode")


def database_menu(file_path: Path) -> None:
    """Interactive persistent database management menu."""
    while True:
        UI.header("PI DATABASE", "Storage & integrity controls")
        print("  " + UI.paint("[1]", UI.CYAN) + " Database info")
        print("  " + UI.paint("[2]", UI.CYAN) + " Continue generation (2×)")
        print("  " + UI.paint("[3]", UI.CYAN) + " Check integrity + auto-repair")
        print("  " + UI.paint("[4]", UI.CYAN) + " Back")

        choice = input("\n  Select › ").strip()

        try:
            if choice == "1":
                database_info(file_path)
            elif choice == "2":
                continue_generation(file_path)
            elif choice == "3":
                check_database_integrity(file_path, repair=True)
            elif choice == "4":
                return
            else:
                UI.warn("Invalid choice. Select 1–4.")
        except (OSError, UnicodeError, ValueError) as exc:
            UI.error(f"Error: {exc}")

        input("\n  Press Enter to continue...")


def admin_mode() -> None:
    """PI-FINDER Easter egg: every input opens the Rickroll video."""
    UI.header("ADMIN MODE", "Restricted administrator console")
    input("  Enter anything to continue › ")

    print()
    UI.success("ACCESS GRANTED.")
    UI.info("Initializing administrator privileges...")
    UI.warn("RICKROLL.EXE")
    webbrowser.open(RICKROLL_URL)


def main() -> None:
    UI.enable()
    file_path = Path(DEFAULT_PI_FILE)

    while True:
        digits = _pi_digits_in_file(file_path)
        status = UI.paint("ONLINE", UI.GREEN) if file_path.exists() else UI.paint("EMPTY", UI.YELLOW)

        UI.header("π  PI-FINDER", "Fast digit & word search engine")
        print(f"  Database  {UI.paint(status, UI.WHITE)}")
        print(f"  Digits    {UI.paint(f'{digits:,}', UI.CYAN)}")
        print(f"  File      {UI.paint(str(file_path), UI.DIM)}")
        print()
        print("  " + UI.paint("[1]", UI.CYAN) + " Search number")
        print("  " + UI.paint("[2]", UI.CYAN) + " Search word")
        print("  " + UI.paint("[3]", UI.CYAN) + " Generate π")
        print("  " + UI.paint("[4]", UI.CYAN) + " Benchmark Lab")
        print("  " + UI.paint("[5]", UI.CYAN) + " PI Database")
        print("  " + UI.paint("[6]", UI.MAGENTA) + " Admin mode")
        print("  " + UI.paint("[7]", UI.RED) + " Exit")
        print()
        print(UI.paint("  ──────────────────────────────────────────────────────────", UI.DIM))

        choice = input(UI.paint("  Select › ", UI.BOLD + UI.CYAN)).strip()

        try:
            if choice == "1":
                pattern = input("  Number › ").strip()
                if not pattern:
                    UI.error("Number cannot be empty.")
                    continue
                run_search(file_path, pattern, "number")

            elif choice == "2":
                word = input("  Word (A-Z) › ").strip()
                encoded = encode_word(word)
                UI.info(f"Encoded: {encoded}")
                run_search(file_path, encoded, "word")

            elif choice == "3":
                generate_pi_file(file_path)

            elif choice == "4":
                run_benchmark(file_path)

            elif choice == "5":
                database_menu(file_path)

            elif choice == "6":
                admin_mode()

            elif choice == "7":
                print()
                UI.success("Goodbye. Keep searching π. π never ends.")
                break

            else:
                UI.warn("Invalid choice. Select 1–7.")

        except (OSError, UnicodeError, ValueError) as exc:
            UI.error(f"Error: {exc}")
            UI.info("Check your input and try again.")

        input("\n  Press Enter to return to the main menu...")


if __name__ == "__main__":
    main()
