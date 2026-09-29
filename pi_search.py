"""Search digit patterns in large pi files without loading the whole file."""

from __future__ import annotations

from pathlib import Path


DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MiB


def search_file(
    file_path: str | Path,
    pattern: bytes,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> int:
    """Return the zero-based position of pattern in a file, or -1."""
    if not pattern:
        return 0

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    path = Path(file_path)
    overlap = len(pattern) - 1
    position = 0
    tail = b""

    with path.open("rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break

            data = tail + chunk
            found = data.find(pattern)

            if found != -1:
                return position - len(tail) + found

            if overlap:
                tail = data[-overlap:]

            position += len(chunk)

    return -1


def search_text(file_path: str | Path, pattern: str) -> int:
    """Search for digits, ignoring a decimal point in input."""
    return search_file(file_path, pattern.replace(".", "").encode("ascii"))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Search a pattern inside a large pi file."
    )
    parser.add_argument("file", help="Path to the pi digit file")
    parser.add_argument("pattern", help="Digits or a decimal representation")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Chunk size in bytes (default: 8388608)",
    )
    args = parser.parse_args()

    position = search_text(args.file, args.pattern)

    if position == -1:
        print("Pattern not found.")
    else:
        print(f"Pattern found at position {position:,}.")


if __name__ == "__main__":
    main()
