"""Interactive text interface for PI-FINDER."""

from __future__ import annotations

import time
import tracemalloc
import webbrowser
from pathlib import Path

from benchmark_search import format_bytes
from generate_pi import write_pi
from pi_search import search_text

DEFAULT_PI_FILE = "pi.txt"
DEFAULT_AUTO_DIGITS = 100_000
AUTO_MAX_DIGITS = 10_000_000
RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

PI_PREFIX = "314159265358979323846264338327950288419716939937510"


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

    # Do not count a trailing newline from a downloaded copy as a digit.
    with file_path.open("rb") as file:
        file.seek(-1, 2)
        if file.read(1) == b"\\n":
            size -= 1
            if size > 0:
                file.seek(-1, 2)
                if file.read(1) == b"\\r":
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

    print(f"Generating pi to {target:,} digits...")
    start = time.perf_counter()
    write_pi(file_path, target)
    elapsed = time.perf_counter() - start
    print(f"Generated {target:,} digits in {elapsed:.3f} s.")

    return target


def auto_search(
    file_path: str | Path,
    pattern: str,
    label: str = "number",
) -> int:
    """Search and grow a verified digits-only pi database when needed."""
    path = Path(file_path)
    current_digits = _pi_digits_in_file(path)

    if current_digits:
        if not check_database_integrity(path):
            print(f"Rebuilding the {current_digits:,}-digit database...")
            start = time.perf_counter()
            write_pi(path, current_digits)
            elapsed = time.perf_counter() - start
            print(f"Rebuilt {current_digits:,} digits in {elapsed:.3f} s.")
            if not check_database_integrity(path):
                raise ValueError("rebuilt pi database failed integrity check")

    if current_digits == 0:
        current_digits = _generate_more_pi(path, 0, len(pattern))

    while True:
        print(f"Searching {current_digits:,} pi digits...")
        position = search_text(path, pattern)

        if position != -1:
            return position

        if current_digits >= AUTO_MAX_DIGITS:
            print(
                f"Not found after searching {current_digits:,} digits. "
                "Automatic generation limit reached."
            )
            return -1

        print(f"Not found in the current {label} dataset.")
        next_digits = _generate_more_pi(path, current_digits, len(pattern))

        if next_digits == current_digits:
            return -1

        current_digits = next_digits


def print_result(position: int) -> None:
    if position == -1:
        print("Not found.")
    else:
        print(f"Found at position: {position:,}")


def database_info(file_path: Path) -> None:
    """Display information about the current pi database."""
    digits = _pi_digits_in_file(file_path)

    print("\nPI-FINDER DATABASE")
    print("-" * 32)

    if not file_path.exists():
        print("Status:      NOT FOUND")
        print("Database:    pi.txt")
        print("Digits:      0")
        print("File size:   0 B")
        print("\nNo database exists yet.")
        return

    size = file_path.stat().st_size
    modified = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(file_path.stat().st_mtime),
    )

    print("Status:      AVAILABLE")
    print(f"Database:    {file_path}")
    print(f"Digits:      {digits:,}")
    print(f"File size:   {format_bytes(size)}")
    print(f"Last update: {modified}")

    if digits:
        progress = min(100, digits / AUTO_MAX_DIGITS * 100)
        filled = int(progress / 5)
        bar = "[" + "#" * filled + "." * (20 - filled) + "]"
        print(f"Progress:    {bar} {digits:,}/{AUTO_MAX_DIGITS:,}")


def continue_generation(file_path: Path) -> None:
    """Double the current database size and regenerate pi."""
    current_digits = _pi_digits_in_file(file_path)

    if current_digits == 0:
        target = DEFAULT_AUTO_DIGITS
    else:
        target = min(current_digits * 2, AUTO_MAX_DIGITS)

    if target <= current_digits:
        print(f"Database is already at the {AUTO_MAX_DIGITS:,}-digit limit.")
        return

    _generate_more_pi(file_path, current_digits, target)


def check_database_integrity(file_path: Path) -> bool:
    """Check the dataset and report the exact location of invalid bytes."""
    if not file_path.exists():
        print("\nDatabase integrity: FAILED")
        print("Reason: pi.txt does not exist.")
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
                actual_value = (
                    f"0x{actual[0]:02X} ({actual!r})" if actual else "EOF"
                )
                expected_value = (
                    f"0x{expected[0]:02X} ({expected!r})"
                    if expected else "EOF"
                )

                print("\nDatabase integrity: FAILED")
                print(f"Reason: π prefix mismatch at position {mismatch + 1:,}.")
                print(f"Expected: {expected_value}")
                print(f"Found:    {actual_value}")
                return False

            checked = len(prefix)
            file_size = file_path.stat().st_size

            while True:
                chunk_start = checked
                chunk = file.read(8 * 1024 * 1024)
                if not chunk:
                    break

                is_last_chunk = file.tell() == file_size

                if is_last_chunk:
                    if chunk.endswith(b"\\r\\n"):
                        chunk = chunk[:-2]
                    elif chunk.endswith(b"\\n"):
                        chunk = chunk[:-1]

                invalid_index = next(
                    (index for index, byte in enumerate(chunk) if byte < ord("0") or byte > ord("9")),
                    None,
                )

                if invalid_index is not None:
                    position = chunk_start + invalid_index + 1
                    value = chunk[invalid_index]
                    context_start = max(0, invalid_index - 10)
                    context_end = min(len(chunk), invalid_index + 11)
                    context = chunk[context_start:context_end]

                    print("\nDatabase integrity: FAILED")
                    print("Reason: non-digit data detected.")
                    print(f"Position: {position:,}")
                    print(f"Byte:     0x{value:02X} ({value!r})")
                    print(f"Context:  {context!r}")
                    return False

                checked += len(chunk)

    except (OSError, UnicodeError) as exc:
        print(f"\nDatabase integrity: FAILED\nReason: {exc}")
        return False

    print("\nDatabase integrity: OK")
    print(f"Checked: {checked:,} characters")
    print("Format: continuous decimal digits (3.14159...)")
    return True
def generate_pi_file(file_path: Path) -> None:
    """Generate a new pi file from the interactive menu."""
    raw_digits = input("Total pi digits (including the leading 3): ").strip()
    digits = int(raw_digits)

    if digits <= 0:
        raise ValueError("total digits must be greater than zero")

    print(f"\nGenerating exactly {digits:,} total digits of pi...")
    print("Large values can require substantial CPU time and RAM.")
    start = time.perf_counter()
    write_pi(file_path, digits)
    elapsed = time.perf_counter() - start

    print(f"Written: {file_path}")
    print(f"Digits written: {digits:,} total digits")
    print(f"Time: {elapsed:.3f} s")


def run_search(file_path: Path, pattern: str, label: str) -> None:
    """Run an automatic search and show search statistics."""
    start = time.perf_counter()
    position = auto_search(file_path, pattern, label)
    elapsed = time.perf_counter() - start

    print_result(position)

    print("\nSearch Statistics")
    print("-" * 32)
    print(f"Search:     {pattern}")
    if position != -1:
        print(f"Position:   {position:,}")
    print(f"Dataset:    {_pi_digits_in_file(file_path):,} digits")
    print(f"Time:       {elapsed:.4f} s")


def run_benchmark(file_path: Path) -> None:
    """Benchmark a search through the current pi file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Pi file not found: {file_path}")

    pattern = input("Enter number to benchmark: ").strip()
    if not pattern:
        raise ValueError("pattern cannot be empty")

    repeat_text = input("Repeats [1]: ").strip() or "1"
    repeat = int(repeat_text)
    if repeat <= 0:
        raise ValueError("repeats must be greater than zero")

    file_size = file_path.stat().st_size
    first_position = search_text(file_path, pattern)

    tracemalloc.start()
    start = time.perf_counter()
    position = first_position

    for _ in range(repeat):
        position = search_text(file_path, pattern)

    elapsed = time.perf_counter() - start
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    average = elapsed / repeat
    mib_per_second = (
        file_size / 1024 / 1024 / average if average else float("inf")
    )

    print("\nPI-FINDER Benchmark")
    print("-" * 32)
    print(f"File:       {file_path}")
    print(f"Size:       {format_bytes(file_size)}")
    print(f"Pattern:    {pattern}")
    print(f"Result:     {'FOUND' if position != -1 else 'NOT FOUND'}")
    if position != -1:
        print(f"Position:   {position:,}")
    print(f"Time:       {average:.4f} s")
    print(f"Speed:      {mib_per_second:.2f} MiB/s")
    print("Chunk:      8.00 MiB")
    print(f"Peak RAM:   {format_bytes(peak_memory)}")
    print(f"Repeats:    {repeat}")


def database_menu(file_path: Path) -> None:
    """Interactive persistent database management menu."""
    while True:
        print("\n================================")
        print("       PI DATABASE")
        print("================================")
        print("1. Database info")
        print("2. Continue generation (2x)")
        print("3. Check database integrity")
        print("4. Back")
        print()

        choice = input("Select: ").strip()

        try:
            if choice == "1":
                database_info(file_path)
            elif choice == "2":
                continue_generation(file_path)
            elif choice == "3":
                check_database_integrity(file_path)
            elif choice == "4":
                return
            else:
                print("Invalid choice.")
        except (OSError, UnicodeError, ValueError) as exc:
            print(f"Error: {exc}")


def admin_mode() -> None:
    """PI-FINDER Easter egg: every input opens the Rickroll video."""
    print("\n================================")
    print("          ADMIN MODE")
    print("================================")
    print("Enter anything to continue.")
    input("> ")

    print("\nACCESS GRANTED.")
    print("Initializing administrator privileges...")
    print("RICKROLL.EXE")
    webbrowser.open(RICKROLL_URL)


def main() -> None:
    file_path = Path(DEFAULT_PI_FILE)

    while True:
        print("=" * 32)
        print("          PI-FINDER")
        print("=" * 32)
        print(f"Pi file: {file_path}")
        print(f"Database: {_pi_digits_in_file(file_path):,} digits")
        print()
        print("1. Search number")
        print("2. Search word")
        print("3. Generate pi")
        print("4. Benchmark")
        print("5. PI Database")
        print("6. Admin mode")
        print("7. Exit")
        print()

        choice = input("Select: ").strip()

        try:
            if choice == "1":
                pattern = input("Enter number: ").strip()
                if not pattern:
                    print("Number cannot be empty.\n")
                    continue

                print("\nSearching...")
                run_search(file_path, pattern, "number")

            elif choice == "2":
                word = input("Enter word: ").strip()
                encoded = encode_word(word)
                print(f"Encoded: {encoded}")
                print("\nSearching...")
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
                print("Goodbye!")
                break

            else:
                print("Invalid choice.")

        except (OSError, UnicodeError, ValueError) as exc:
            print(f"Error: {exc}")

        print()


if __name__ == "__main__":
    main()
