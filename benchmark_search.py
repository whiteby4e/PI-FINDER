"""Benchmark PI-FINDER file-search performance."""

from __future__ import annotations

import argparse
import os
import time
import tracemalloc
from pathlib import Path

from pi_search import DEFAULT_CHUNK_SIZE, search_text


DEFAULT_CHUNK_SIZES = (
    1 * 1024 * 1024,
    4 * 1024 * 1024,
    8 * 1024 * 1024,
    16 * 1024 * 1024,
)


def format_bytes(value: int | float) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{value} B"


def benchmark_search(
    file_path: str | Path,
    pattern: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    repeat: int = 1,
) -> dict[str, float | int]:
    """Benchmark one real file search and return performance metrics."""
    if chunk_size <= 0:
        raise ValueError("chunk-size must be greater than zero")
    if repeat <= 0:
        raise ValueError("repeat must be greater than zero")

    path = Path(file_path)
    file_size = path.stat().st_size

    # Warm-up: validates the search and reduces first-run startup noise.
    first_position = search_text(path, pattern, chunk_size)

    tracemalloc.start()
    start_wall = time.perf_counter()
    start_cpu = time.process_time()

    position = first_position
    for _ in range(repeat):
        position = search_text(path, pattern, chunk_size)

    wall_elapsed = time.perf_counter() - start_wall
    cpu_elapsed = time.process_time() - start_cpu
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    average_wall = wall_elapsed / repeat
    average_cpu = cpu_elapsed / repeat
    mib_per_second = (
        file_size / 1024 / 1024 / average_wall
        if average_wall
        else float("inf")
    )
    cpu_percent = (
        min(999.9, average_cpu / average_wall * 100)
        if average_wall
        else 0.0
    )

    return {
        "position": position,
        "file_size": file_size,
        "time": average_wall,
        "cpu_time": average_cpu,
        "cpu_percent": cpu_percent,
        "speed": mib_per_second,
        "peak_memory": peak_memory,
        "chunk_size": chunk_size,
        "repeat": repeat,
    }


def print_benchmark_result(result: dict[str, float | int]) -> None:
    """Print one benchmark result."""
    position = int(result["position"])

    print(f"Result:     {'FOUND' if position != -1 else 'NOT FOUND'}")
    if position != -1:
        print(f"Position:   {position:,}")
    print(f"Time:       {float(result['time']):.4f} s")
    print(f"CPU time:   {float(result['cpu_time']):.4f} s")
    print(f"CPU usage:  {float(result['cpu_percent']):.1f}%")
    print(f"Speed:      {float(result['speed']):.2f} MiB/s")
    print(f"Chunk:      {format_bytes(int(result['chunk_size']))}")
    print(f"Peak RAM:   {format_bytes(int(result['peak_memory']))}")
    print(f"Repeats:    {int(result['repeat'])}")


def compare_chunk_sizes(
    file_path: str | Path,
    pattern: str,
    chunk_sizes: tuple[int, ...] = DEFAULT_CHUNK_SIZES,
    repeat: int = 1,
) -> list[dict[str, float | int]]:
    """Benchmark the same real pi file with several chunk sizes."""
    return [
        benchmark_search(file_path, pattern, chunk_size, repeat)
        for chunk_size in chunk_sizes
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark PI-FINDER file-search performance."
    )
    parser.add_argument("file", help="Path to the file to search")
    parser.add_argument("pattern", help="Digits or a decimal representation")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Chunk size in bytes (default: 8 MiB)",
    )
    parser.add_argument(
        "--compare-chunks",
        action="store_true",
        help="Compare the standard 1, 4, 8 and 16 MiB chunk sizes.",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of timed searches per test (default: 1)",
    )
    args = parser.parse_args()

    path = Path(args.file)

    if args.compare_chunks:
        results = compare_chunk_sizes(path, args.pattern, repeat=args.repeat)
        print("PI-FINDER Real File Benchmark")
        print("=" * 40)
        print(f"File:       {path}")
        print(f"Size:       {format_bytes(path.stat().st_size)}")
        print(f"Pattern:    {args.pattern}")
        print()

        for result in results:
            print(f"[{format_bytes(int(result['chunk_size']))} chunk]")
            print_benchmark_result(result)
            print()
        return

    result = benchmark_search(
        path,
        args.pattern,
        args.chunk_size,
        args.repeat,
    )

    print("PI-FINDER Benchmark")
    print("-" * 32)
    print(f"File:       {path}")
    print(f"Size:       {format_bytes(path.stat().st_size)}")
    print(f"Pattern:    {args.pattern}")
    print_benchmark_result(result)
    print(f"Python PID: {os.getpid()}")


if __name__ == "__main__":
    main()
