"""
Problem 4: time matrix addition under two loop orders.

Version 1 (i outer, j inner) walks memory in row-major order for C-contiguous
arrays. Version 2 (j outer, i inner) walks by columns and should be slower
once matrices no longer fit comfortably in cache / RAM (VMM effects).

Each outer iteration updates one full row (v1) or column (v2) so the access
order matches the assignment pseudocode while staying practical in Python
for large n. Initialization of A and B is excluded from the timed region.

n sequence: 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768
(largest sizes may fail on memory)
"""

import time

try:
    import numpy as np
except ImportError:
    raise SystemExit("numpy is required: pip install numpy")

SIZES = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

def add_version1(a, b, c, n):
    for i in range(n):
        c[i, :] = a[i, :] + b[i, :]

def add_version2(a, b, c, n):
    for j in range(n):
        c[:, j] = a[:, j] + b[:, j]

def bytes_needed(n):
    return 3 * n * n * 4

def run_size(n):
    print(f"n = {n}  (~{bytes_needed(n) / (1024 ** 3):.2f} GiB for A+B+C)")
    try:
        a = np.ones((n, n), dtype=np.float32)
        b = np.ones((n, n), dtype=np.float32)
        c = np.empty((n, n), dtype=np.float32)
    except MemoryError:
        print("  skipped: not enough memory\n")
        return None

    t1 = time.perf_counter()
    add_version1(a, b, c, n)
    t1 = time.perf_counter() - t1

    t2 = time.perf_counter()
    add_version2(a, b, c, n)
    t2 = time.perf_counter() - t2

    print(f"  version1 (i, then j): {t1:.4f} s")
    print(f"  version2 (j, then i): {t2:.4f} s")
    if t1 > 0:
        print(f"  ratio version2/version1: {t2 / t1:.2f}x")
    print()
    return t1, t2

def main():
    print("Problem 4: matrix addition timings (float32, C-contiguous / row-major)")
    print("Init time is NOT included in measurements.\n")

    results = []
    for n in SIZES:
        timed = run_size(n)
        if timed is not None:
            results.append((n, timed[0], timed[1]))

    if not results:
        return

    print("=" * 56)
    print(f"{'n':>8}  {'version1 (s)':>14}  {'version2 (s)':>14}  {'ratio':>8}")
    print("=" * 56)
    for n, t1, t2 in results:
        ratio = t2 / t1 if t1 > 0 else float("inf")
        print(f"{n:>8}  {t1:>14.4f}  {t2:>14.4f}  {ratio:>7.2f}x")
    print("=" * 56)
    print("Expect version2 slower for large n; doubling n ~4x time if in-core.")

if __name__ == "__main__":
    main()
