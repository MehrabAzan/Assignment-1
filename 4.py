"""
Problem 4: time matrix addition under two loop orders.

Version 1 (i outer, j inner) walks memory in row-major order for C-contiguous
arrays. Version 2 (j outer, i inner) walks by columns and should be slower
once matrices no longer fit comfortably in cache / RAM (VMM effects).

Each outer iteration updates one full row (v1) or column (v2) so the access
order matches the assignment pseudocode while staying practical in Python
for large n. Initialization of A and B is excluded from the timed region.
"""

import time

try:
    import numpy as np
except ImportError:
    raise SystemExit("numpy is required: pip install numpy")


def add_version1(matrixA, matrixB, matrixC, sizeN):
    """
    Add two n-by-n matrices with i outer, then j (row-major friendly).

    Inputs: matrixA, matrixB (sources), matrixC (destination), sizeN (order).
    Output: matrixC is filled in place; nothing returned.
    Local: row index i walks each full row slice.
    """
    for i in range(sizeN):
        matrixC[i, :] = matrixA[i, :] + matrixB[i, :]


def add_version2(matrixA, matrixB, matrixC, sizeN):
    """
    Add two n-by-n matrices with j outer, then i (column-oriented).

    Inputs: matrixA, matrixB (sources), matrixC (destination), sizeN (order).
    Output: matrixC is filled in place; nothing returned.
    Local: column index j walks each full column slice.
    """
    for j in range(sizeN):
        matrixC[:, j] = matrixA[:, j] + matrixB[:, j]


def bytes_needed(sizeN):
    """
    Estimate bytes for three float32 n-by-n matrices (A, B, and C).

    Input: sizeN — matrix order.
    Output: integer byte count (3 * n * n * 4).
    """
    return 3 * sizeN * sizeN * 4


def allocate_matrices(sizeN):
    """
    Allocate float32 matrices A=ones, B=ones, C=empty of order sizeN.

    Input: sizeN — matrix order.
    Output: (matrixA, matrixB, matrixC) or None on MemoryError.
    Locals: none beyond the three arrays.
    """
    try:
        matrixA = np.ones((sizeN, sizeN), dtype=np.float32)
        matrixB = np.ones((sizeN, sizeN), dtype=np.float32)
        matrixC = np.empty((sizeN, sizeN), dtype=np.float32)
    except MemoryError:
        return None
    return matrixA, matrixB, matrixC


def time_both_versions(matrixA, matrixB, matrixC, sizeN):
    """
    Time both addition orders on already-allocated matrices.

    Inputs: matrixA, matrixB, matrixC, sizeN.
    Output: (timeVersion1, timeVersion2) in seconds (floats).
    Locals: startVersion1/2 mark perf_counter samples around each call.
    """
    startVersion1 = time.perf_counter()
    add_version1(matrixA, matrixB, matrixC, sizeN)
    timeVersion1 = time.perf_counter() - startVersion1

    startVersion2 = time.perf_counter()
    add_version2(matrixA, matrixB, matrixC, sizeN)
    timeVersion2 = time.perf_counter() - startVersion2

    return timeVersion1, timeVersion2


def run_size(sizeN, showOutput=True):
    """
    Allocate, time both add versions for one n, and report (or skip on OOM).

    Inputs: sizeN; showOutput — if False, suppress prints (write code still present).
    Output: (timeVersion1, timeVersion2) or None if allocation failed.
    Locals: matrices from allocation; timed pair from the timing helper.
    Note: any future stdin read of n must keep a matching write (flag-gated ok).
    """
    gibEstimate = bytes_needed(sizeN) / (1024 ** 3)
    if showOutput:
        print(f"n = {sizeN}  (~{gibEstimate:.2f} GiB for A+B+C)")

    matrices = allocate_matrices(sizeN)
    if matrices is None:
        if showOutput:
            print("  skipped: not enough memory\n")
        return None

    matrixA, matrixB, matrixC = matrices
    timeVersion1, timeVersion2 = time_both_versions(
        matrixA, matrixB, matrixC, sizeN
    )

    if showOutput:
        print(f"  version1 (i, then j): {timeVersion1:.4f} s")
        print(f"  version2 (j, then i): {timeVersion2:.4f} s")
        if timeVersion1 > 0:
            print(f"  ratio version2/version1: {timeVersion2 / timeVersion1:.2f}x")
        print()

    return timeVersion1, timeVersion2


def print_summary_table(results):
    """
    Print the aggregated timing table for successful sizes.

    Input: results — list of (sizeN, timeVersion1, timeVersion2).
    Output: none; writes a self-explanatory table to stdout.
    Local: ratio is version2/version1 when version1 > 0.
    """
    print("=" * 56)
    print(f"{'n':>8}  {'version1 (s)':>14}  {'version2 (s)':>14}  {'ratio':>8}")
    print("=" * 56)
    for sizeN, timeVersion1, timeVersion2 in results:
        if timeVersion1 > 0:
            ratio = timeVersion2 / timeVersion1
        else:
            ratio = float("inf")
        print(
            f"{sizeN:>8}  {timeVersion1:>14.4f}  "
            f"{timeVersion2:>14.4f}  {ratio:>7.2f}x"
        )
    print("=" * 56)
    print("Expect version2 slower for large n; doubling n ~4x time if in-core.")


def main():
    """
    Drive the matrix-addition timing experiment over a fixed size sequence.

    Input: none from stdin; sizes are defined locally in this procedure.
    Output: per-size timing lines plus a final summary table (or early exit
            if every size fails allocation).
    Locals: sizeList (orders to try), results (successful timings), timed pair.
    """
    sizeList = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

    print("Problem 4: matrix addition timings (float32, C-contiguous / row-major)")
    print("Init time is NOT included in measurements.\n")

    results = []
    for sizeN in sizeList:
        timed = run_size(sizeN)
        if timed is not None:
            results.append((sizeN, timed[0], timed[1]))

    if not results:
        return

    print_summary_table(results)


if __name__ == "__main__":
    main()
