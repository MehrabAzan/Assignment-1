"""
Problem 4: time matrix addition for two loop orders.

Version 1: outer i, inner j.
Version 2: outer j, inner i.
Init of A and B is not timed. Arrays are float32 and C-contiguous.
"""

import time

try:
    import numpy as np
except ImportError:
    raise SystemExit("numpy is required: pip install numpy")

from numba import njit

@njit(cache=True)
def add_version1(matrixA, matrixB, matrixC, sizeN):
    """
    C[i,j] = A[i,j] + B[i,j] with i outer and j inner.
    Input: matrixA, matrixB, matrixC, sizeN.
    Output: fills matrixC in place.
    Locals: i, j.
    """
    for i in range(sizeN):
        for j in range(sizeN):
            matrixC[i, j] = matrixA[i, j] + matrixB[i, j]

@njit(cache=True)
def add_version2(matrixA, matrixB, matrixC, sizeN):
    """
    C[i,j] = A[i,j] + B[i,j] with j outer and i inner.
    Input: matrixA, matrixB, matrixC, sizeN.
    Output: fills matrixC in place.
    Locals: i, j.
    """
    for j in range(sizeN):
        for i in range(sizeN):
            matrixC[i, j] = matrixA[i, j] + matrixB[i, j]

def bytes_needed(sizeN):
    """
    Bytes for three float32 n-by-n matrices.
    Input: sizeN. Output: byte count. Locals: none.
    """
    return 3 * sizeN * sizeN * 4

def allocate_matrices(sizeN):
    """
    Allocate A=ones, B=ones, C=empty as float32.
    Input: sizeN.
    Output: (matrixA, matrixB, matrixC) or None on MemoryError.
    Locals: matrixA, matrixB, matrixC.
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
    Warm up both kernels, then time each once.
    Input: matrixA, matrixB, matrixC, sizeN.
    Output: (timeVersion1, timeVersion2) in seconds.
    Locals: startVersion1, startVersion2, timeVersion1, timeVersion2.
    """
    add_version1(matrixA, matrixB, matrixC, sizeN)
    add_version2(matrixA, matrixB, matrixC, sizeN)

    startVersion1 = time.perf_counter()
    add_version1(matrixA, matrixB, matrixC, sizeN)
    timeVersion1 = time.perf_counter() - startVersion1

    startVersion2 = time.perf_counter()
    add_version2(matrixA, matrixB, matrixC, sizeN)
    timeVersion2 = time.perf_counter() - startVersion2

    return timeVersion1, timeVersion2

def run_size(sizeN):
    """
    Allocate and time both versions for one n.
    Input: sizeN.
    Output: (timeVersion1, timeVersion2) or None if allocation failed.
    Locals: gibEstimate, matrices, matrixA, matrixB, matrixC,
            timeVersion1, timeVersion2.
    """
    gibEstimate = bytes_needed(sizeN) / (1024 ** 3)
    print(f"n = {sizeN}  (~{gibEstimate:.2f} GiB for A+B+C)")

    matrices = allocate_matrices(sizeN)
    if matrices is None:
        print("  skipped: not enough memory\n")
        return None

    matrixA, matrixB, matrixC = matrices
    timeVersion1, timeVersion2 = time_both_versions(
        matrixA, matrixB, matrixC, sizeN
    )

    print(f"  version1 (i, then j): {timeVersion1:.6f} s")
    print(f"  version2 (j, then i): {timeVersion2:.6f} s")
    if timeVersion1 > 0:
        print(f"  ratio version2/version1: {timeVersion2 / timeVersion1:.2f}x")
    print()
    return timeVersion1, timeVersion2

def print_summary_table(results):
    """
    Print the timing table.
    Input: results list of (sizeN, timeVersion1, timeVersion2).
    Output: none. Locals: sizeN, timeVersion1, timeVersion2, ratio.
    """
    print("=" * 60)
    print(f"{'n':>8}  {'version1 (s)':>14}  {'version2 (s)':>14}  {'ratio':>8}")
    print("=" * 60)
    for sizeN, timeVersion1, timeVersion2 in results:
        if timeVersion1 > 0:
            ratio = timeVersion2 / timeVersion1
        else:
            ratio = float("inf")
        print(
            f"{sizeN:>8}  {timeVersion1:>14.6f}  "
            f"{timeVersion2:>14.6f}  {ratio:>7.2f}x"
        )
    print("=" * 60)

def main():
    """
    Time both loop orders for the assignment size list.
    Input: none. Output: per-size timings and a summary table.
    Locals: sizeList, results, sizeN, timed.
    """
    sizeList = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

    print("Problem 4: matrix addition timings")
    print("float32 C-contiguous arrays, init not timed\n")

    results = []
    for sizeN in sizeList:
        timed = run_size(sizeN)
        if timed is not None:
            results.append((sizeN, timed[0], timed[1]))

    if results:
        print_summary_table(results)

if __name__ == "__main__":
    main()
