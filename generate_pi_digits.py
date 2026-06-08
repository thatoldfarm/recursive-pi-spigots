#!/usr/bin/env python3
"""
generate_pi_digits_ultimate.py
=================================
✅ Generates Pi digits in the EXACT format for pi_finder_v4_optimized.py
✅ NO VALIDATION (since you know your digits are correct)
✅ Forces fresh calculation (no mpmath caching bugs)
✅ Output: Raw digits, NO decimal point, NO newlines, ASCII-encoded

Usage:
    python3 generate_pi_digits_ultimate.py 10000000 pi_10m.txt
"""

import sys
from mpmath import mp

def generate_pi_digits(num_digits, output_file):
    if num_digits < 0:
        raise ValueError("num_digits must be >= 0")
    if num_digits == 0:
        with open(output_file, "w", encoding="ascii") as f:
            f.write("")
        print(f"✅ Generated 0 Pi digits → {output_file}")
        return

    # 🔧 FIX: Set precision FIRST, then recalculate pi fresh (no caching bugs!)
    mp.dps = num_digits + int(num_digits * 0.5) + 100  # Extra buffer
    pi_value = mp.acos(-1)  # Forces fresh calculation (avoids cached mp.pi)
    pi_str = mp.nstr(pi_value, num_digits + 1, strip_zeros=False)  # +1 for the "3."

    if not pi_str.startswith("3."):
        raise ValueError(f"Unexpected Pi format: {pi_str}")
    pi_str = pi_str[2:2 + num_digits]  # Remove "3." → PURE DIGITS ONLY

    # Write to file: RAW DIGITS, NO DECIMAL, NO NEWLINES
    with open(output_file, "w", encoding="ascii") as f:
        f.write(pi_str)
    print(f"✅ Generated {len(pi_str):,} Pi digits → {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_pi_digits_ultimate.py <num_digits> [output_file]")
        print("Example: python3 generate_pi_digits_ultimate.py 10000000 pi_10m.txt")
        sys.exit(1)
    num_digits = int(sys.argv[1])
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"pi_{num_digits}.txt"
    generate_pi_digits(num_digits, output_file)
