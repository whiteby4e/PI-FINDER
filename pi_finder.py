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
RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


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


def print_result(position: int) -> None:
    if position == -1:
        print("Not found.")
    else:
        print(f"Found at position: {position:,}")


def generate_pi_file(file_path: Path) -> None:
    """Generate a new pi file from the interactive menu."""
    raw_digits = input("Digits after decimal point: ").strip()
    digits = int(raw_digits)

    if digits < 0:
        raise ValueError("digits must be non-negative")

    print(f"\nGenerating {digits:,} digits of pi...")
    print("Large values can require substantial CPU time and RAM.")
    start = time.perf_counter()
    write_pi(file_path, digits)
    elapsed = time.perf_counter() - start

    print(f"Written: {file_path}")
    print(f"Digits written: {digits:,}")
    print(f"Time: {elapsed:.3f} s")


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

    # Warm-up search is not included in the timed measurement.
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
        print()
        print("1. Search number")
        print("2. Search word")
        print("3. Generate pi")
        print("4. Benchmark")
        print("5. Admin mode")
        print("6. Exit")
        print()

        choice = input("Select: ").strip()

        try:
            if choice == "1":
                pattern = input("Enter number: ").strip()
                if not pattern:
                    print("Number cannot be empty.\n")
                    continue

                print("\nSearching...")
                position = search_number(file_path, pattern)
                print_result(position)

            elif choice == "2":
                word = input("Enter word: ").strip()
                encoded, position = search_word(file_path, word)
                print(f"Encoded: {encoded}")
                print("\nSearching...")
                print_result(position)

            elif choice == "3":
                generate_pi_file(file_path)

            elif choice == "4":
                run_benchmark(file_path)

            elif choice == "5":
                admin_mode()

            elif choice == "6":
                print("Goodbye!")
                break

            else:
                print("Invalid choice.")

        except (OSError, UnicodeEncodeError, ValueError) as exc:
            print(f"Error: {exc}")

        print()


if __name__ == "__main__":
    main()
