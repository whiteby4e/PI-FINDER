"""Search digit patterns in large pi files without loading the whole file."""

from __future__ import annotations

from pathlib import Path


DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MiB


def search_file(
    file_path: str | Path,
    pattern: bytes,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> int:
    """Return the zero-based position of pattern in a file, or -1.

    The file is read in chunks, so memory usage stays roughly bounded by
    chunk_size plus the pattern overlap. Matches spanning two chunks are
    handled correctly.
    """
    if not pattern:
        return 0

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    path = Path(file_path)
    pattern_length = len(pattern)
    overlap = pattern_length - 1
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
            else:
                tail = b""

            position += len(chunk)

    return -1


def search_text(file_path: str | Path, pattern: str, encoding: str = "ascii") -> int:
    """Search for a text pattern in a digit file."""
    return search_file(file_path, pattern.encode(encoding))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Search a digit pattern inside a large pi file."
    )
    parser.add_argument("file", help="Path to the pi digit file")
    parser.add_argument("pattern", help="Digits to search for")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Chunk size in bytes (default: 8388608)",
    )
    args = parser.parse_args()

    position = search_text(args.file, args.pattern, encoding="ascii")

    if position == -1:
        print("Pattern not found.")
    else:
        print(f"Pattern found at position {position:,}.")


if __name__ == "__main__":
    main()
