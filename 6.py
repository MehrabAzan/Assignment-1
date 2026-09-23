"""
Problem 6: binary search timing experiment (Python).

Times 30,000,000 unsuccessful searches over sorted arrays of increasing
size. Array construction is excluded from the timed region. Theory: O(log n).
"""

import math
import os
import sys
import time

SIZES = (100, 400, 1600, 6400, 25600, 102400, 409600, 1638400)
DEFAULT_ITERS = 30_000_000

def binary_search(arr, target):
    lo = 0
    hi = len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = arr[mid]
        if val < target:
            lo = mid + 1
        elif val > target:
            hi = mid - 1
        else:
            return mid
    return -1

def make_sorted_array(n):
    return list(range(n))

def time_searches(arr, target, iters):
    search = binary_search
    t0 = time.perf_counter()
    for _ in range(iters):
        search(arr, target)
    t1 = time.perf_counter()
    return t1 - t0

def parse_iters(argv):
    iters = DEFAULT_ITERS
    env = os.environ.get("BINARY_SEARCH_ITERS")
    if env is not None:
        iters = int(env)
    i = 0
    while i < len(argv):
        if argv[i] == "--iters" and i + 1 < len(argv):
            iters = int(argv[i + 1])
            i += 2
            continue
        i += 1
    if iters < 1:
        raise SystemExit("iters must be >= 1")
    return iters

def print_table(rows, iters):
    print(f"iterations per size: {iters:,}")
    print()
    header = f"{'n':>10}  {'time_s':>12}  {'time/log2(n)':>14}"
    print(header)
    print("-" * len(header))
    for n, elapsed in rows:
        logN = math.log2(n) if n > 1 else 1.0
        ratio = elapsed / logN
        print(f"{n:>10}  {elapsed:>12.6f}  {ratio:>14.6f}")

def main():
    print("Problem 6 - Python version of the 3-language binary search timing experiment")
    print()

    iters = parse_iters(sys.argv[1:])
    rows = []

    for n in SIZES:
        arr = make_sorted_array(n)
        target = -1
        if binary_search(arr, target) != -1:
            raise SystemExit(f"expected miss for target={target} at n={n}")
        if binary_search(arr, 0) != 0:
            raise SystemExit(f"expected hit at index 0 for n={n}")

        elapsed = time_searches(arr, target, iters)
        rows.append((n, elapsed))
        print(f"n={n:>8}: {elapsed:.6f} s", flush=True)

    print()
    print_table(rows, iters)
    print()
    print(
        "Reminder: binary search is O(log n), so wall time should grow slowly "
        "with n (roughly a near-constant bump each time n grows by 4x)."
    )

if __name__ == "__main__":
    main()
