"""Core search algorithms for PI-FINDER."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SearchResult:
    position: int
    algorithm: str


def builtin_find(data: bytes, pattern: bytes) -> int:
    """Search using Python's optimized C implementation."""
    return data.find(pattern)


def naive_search(data: bytes, pattern: bytes) -> int:
    """Simple reference implementation for benchmarking."""
    n = len(data)
    m = len(pattern)

    if m == 0:
        return 0
    if m > n:
        return -1

    # Avoid creating a new slice for every candidate position.
    last = n - m
    first = pattern[0]
    for i in range(last + 1):
        if data[i] != first:
            continue
        for j in range(1, m):
            if data[i + j] != pattern[j]:
                break
        else:
            return i
    return -1


def kmp_search(data: bytes, pattern: bytes) -> int:
    """Knuth-Morris-Pratt string search."""
    m = len(pattern)
    if m == 0:
        return 0
    if m > len(data):
        return -1

    lps = [0] * m
    length = 0
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length:
            length = lps[length - 1]
        else:
            i += 1

    i = j = 0
    while i < len(data):
        if data[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                return i - j
        elif j:
            j = lps[j - 1]
        else:
            i += 1

    return -1


SEARCH_ALGORITHMS: dict[str, Callable[[bytes, bytes], int]] = {
    "builtin_find": builtin_find,
    "naive": naive_search,
    "kmp": kmp_search,
}
