"""Text interface for PI-FINDER with number and word search."""

from __future__ import annotations

from pathlib import Path

from pi_search import search_text

DEFAULT_PI_FILE = "pi.txt"


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


def main() -> None:
    file_path = Path(DEFAULT_PI_FILE)

    print("=" * 32)
    print("          PI-FINDER")
    print("=" * 32)
    print(f"Pi file: {file_path}")
    print()

    while True:
        print("1. Search number")
        print("2. Search word")
        print("3. Exit")
        print()

        choice = input("Select: ").strip()

        if choice == "1":
            pattern = input("Enter number: ").strip()
            if not pattern:
                print("Number cannot be empty.\n")
                continue

            try:
                print("\nSearching...")
                position = search_number(file_path, pattern)
                print_result(position)
            except (OSError, UnicodeEncodeError, ValueError) as exc:
                print(f"Error: {exc}")

            print()

        elif choice == "2":
            word = input("Enter word: ").strip()
            try:
                encoded, position = search_word(file_path, word)
                print(f"Encoded: {encoded}")
                print("\nSearching...")
                print_result(position)
            except (OSError, ValueError) as exc:
                print(f"Error: {exc}")

            print()

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
