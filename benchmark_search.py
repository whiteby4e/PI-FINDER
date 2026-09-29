"""Benchmark file-search performance for PI-FINDER."""

from __future__ import annotations

import argparse
import os
import time
import tracemalloc
from pathlib import Path

from pi_search import search_text


def format_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{value} B"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark PI-FINDER file-search performance."
    )
    parser.add_argument("file", help="Path to the file to search")
    parser.add_argument("pattern", help="Digits or a decimal representation")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=8 * 1024 * 1024,
        help="Chunk size in bytes (default: 8 MiB)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of timed searches (default: 1)",
    )
    args = parser.parse_args()

    if args.chunk_size <= 0:
        raise ValueError("chunk-size must be greater than zero")
    if args.repeat <= 0:
        raise ValueError("repeat must be greater than zero")

    path = Path(args.file)
    file_size = path.stat().st_size

    # Warm-up: validates the search and reduces first-run startup noise.
    first_position = search_text(path, args.pattern)

    tracemalloc.start()
    start = time.perf_counter()

    position = first_position
    for _ in range(args.repeat):
        position = search_text(path, args.pattern)

    elapsed = time.perf_counter() - start
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    average = elapsed / args.repeat
    mib_per_second = (file_size / 1024 / 1024) / average if average else float("inf")

    print("PI-FINDER Benchmark")
    print("-" * 32)
    print(f"File:       {path}")
    print(f"Size:       {format_bytes(file_size)}")
    print(f"Pattern:    {args.pattern}")
    print(f"Result:     {'FOUND' if position != -1 else 'NOT FOUND'}")
    if position != -1:
        print(f"Position:   {position:,}")
    print(f"Time:       {average:.4f} s")
    print(f"Speed:      {mib_per_second:.2f} MiB/s")
    print(f"Chunk:      {format_bytes(args.chunk_size)}")
    print(f"Peak RAM:   {format_bytes(peak_memory)}")
    print(f"Repeats:    {args.repeat}")
    print(f"Python PID: {os.getpid()}")


if __name__ == "__main__":
    main()
