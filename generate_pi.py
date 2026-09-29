"""Generate decimal digits of pi for PI-FINDER.

This is a dependency-free reference generator based on the Chudnovsky
formula and binary splitting. It is intended for generating test datasets;
very large datasets are much faster with a GMP-backed implementation.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path


# Python 3.11+ limits int-to-string conversion to 4300 digits by default.
# PI-FINDER intentionally works with much larger integers while generating pi.
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


C = 640320
C3_OVER_24 = C**3 // 24
DIGITS_PER_TERM = 14.181647462725477


def binary_split(a: int, b: int) -> tuple[int, int, int]:
    """Return (P, Q, T) for the Chudnovsky binary-splitting series."""
    if b - a == 1:
        if a == 0:
            return 1, 1, 13591409

        k = a
        p = (6 * k - 5) * (2 * k - 1) * (6 * k - 1)
        q = k * k * k * C3_OVER_24
        t = p * (13591409 + 545140134 * k)

        if k & 1:
            t = -t

        return p, q, t

    m = (a + b) // 2
    p1, q1, t1 = binary_split(a, m)
    p2, q2, t2 = binary_split(m, b)

    return p1 * p2, q1 * q2, t1 * q2 + p1 * t2


def pi_digits(digits: int) -> str:
    """Return pi with exactly digits after the decimal point."""
    if digits < 0:
        raise ValueError("digits must be non-negative")
    if digits == 0:
        return "3"

    guard = 10
    total_digits = digits + guard
    terms = int(total_digits / DIGITS_PER_TERM) + 1

    p, q, t = binary_split(0, terms)

    # pi = (426880 * sqrt(10005) * Q) / T
    sqrt_scaled = math.isqrt(10005 * 10 ** (2 * total_digits))
    pi_scaled = (426880 * sqrt_scaled * q * 10 ** total_digits) // t

    text = str(pi_scaled)
    if len(text) <= total_digits:
        text = text.zfill(total_digits + 1)

    integer_part = text[:-total_digits]
    fraction = text[-total_digits:][:digits]
    return integer_part + "." + fraction


def write_pi(file_path: str | Path, digits: int) -> None:
    """Generate pi and write it to a text file."""
    text = pi_digits(digits)
    path = Path(file_path)
    with path.open("w", encoding="ascii", newline="") as file:
        file.write(text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate decimal digits of pi for PI-FINDER."
    )
    parser.add_argument(
        "digits",
        type=int,
        help="Number of digits after the decimal point",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="pi.txt",
        help="Output file (default: pi.txt)",
    )
    args = parser.parse_args()

    print(f"Generating {args.digits:,} digits of pi...")
    print("Large values can require substantial CPU time and RAM.")

    write_pi(args.output, args.digits)

    print(f"Written: {args.output}")
    print(f"Digits written: {args.digits:,} after the decimal point")


if __name__ == "__main__":
    main()
