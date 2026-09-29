"""Benchmark PI-FINDER search algorithms.

Run:
    python benchmark.py

The benchmark uses synthetic pi-like digit data so it does not require
a huge pi file. Results are useful for comparing the search implementations;
real pi datasets should be benchmarked separately before production use.
"""

from __future__ import annotations

import random
import time
from pathlib import Path

from search_engine import SEARCH_ALGORITHMS


SIZES = {
    "1 MB": 1_000_000,
    "10 MB": 10_000_000,
    "100 MB": 100_000_000,
}

PATTERN_LENGTHS = (8, 32, 128)
REPEATS = 5
SEED = 1337


def make_dataset(size: int) -> bytes:
    rng = random.Random(SEED)
    return bytes(rng.randrange(48, 58) for _ in range(size))


def benchmark_one(name: str, search, data: bytes, pattern: bytes) -> float:
    # Warm-up
    search(data, pattern)

    start = time.perf_counter()
    for _ in range(REPEATS):
        search(data, pattern)
    elapsed = time.perf_counter() - start
    return elapsed / REPEATS


def main() -> None:
    print("PI-FINDER search benchmark")
    print("=" * 32)
    print(f"Python: {__import__('sys').version.split()[0]}")
    print(f"Repeats: {REPEATS}")
    print()

    for size_name, size in SIZES.items():
        print(f"[{size_name}] generating dataset...")
        data = make_dataset(size)

        for pattern_length in PATTERN_LENGTHS:
            # A pattern that is almost certainly absent makes every algorithm
            # inspect the dataset instead of stopping near the beginning.
            pattern = b"9" * pattern_length

            print(f"  pattern={pattern_length:>3} digits")

            for name, search in SEARCH_ALGORITHMS.items():
                seconds = benchmark_one(name, search, data, pattern)
                mbps = size / seconds / 1_000_000
                print(f"    {name:<14} {seconds:>9.6f} s  {mbps:>10.2f} MB/s")

        del data
        print()


if __name__ == "__main__":
    main()
