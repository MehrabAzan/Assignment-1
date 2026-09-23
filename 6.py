"""
Problem 6: binary search timing experiment (Python).

Times 30,000,000 unsuccessful searches over sorted arrays of increasing
size. Array construction is excluded from the timed region. Theory: O(log n).
"""

import math
import os
import sys
import time

SIZE_LIST = (100, 400, 1600, 6400, 25600, 102400, 409600, 1638400)
DEFAULT_ITERS = 30_000_000

def binary_search(sortedArr, searchTarget):
    """
    Iterative binary search on a sorted list.
    Input: sortedArr ascending, searchTarget.
    Output: index of hit, or -1 on miss.
    Locals: lo, hi, mid, midVal.
    """
    lo = 0
    hi = len(sortedArr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        midVal = sortedArr[mid]
        if midVal < searchTarget:
            lo = mid + 1
        elif midVal > searchTarget:
            hi = mid - 1
        else:
            return mid
    return -1

def make_sorted_array(sizeN):
    """
    Build a sorted array of values 0 .. sizeN-1.
    Input: sizeN. Output: list of length sizeN.
    Locals: none.
    """
    return list(range(sizeN))

def time_searches(sortedArr, searchTarget, numIters):
    """
    Time numIters binary searches. Array build is not included.
    Input: sortedArr, searchTarget, numIters.
    Output: elapsed seconds.
    Locals: searchFn, startTime, endTime, iterIndex.
    """
    searchFn = binary_search
    startTime = time.perf_counter()
    for iterIndex in range(numIters):
        searchFn(sortedArr, searchTarget)
    endTime = time.perf_counter()
    return endTime - startTime

def parse_iters(argvList):
    """
    Resolve iteration count from env or --iters.
    Input: argvList (sys.argv without the script name).
    Output: positive int, default DEFAULT_ITERS.
    Locals: numIters, envText, argIndex.
    """
    numIters = DEFAULT_ITERS
    envText = os.environ.get("BINARY_SEARCH_ITERS")
    if envText is not None:
        numIters = int(envText)
    argIndex = 0
    while argIndex < len(argvList):
        if argvList[argIndex] == "--iters" and argIndex + 1 < len(argvList):
            numIters = int(argvList[argIndex + 1])
            argIndex += 2
            continue
        argIndex += 1
    if numIters < 1:
        raise SystemExit("iters must be >= 1")
    return numIters

def print_table(resultRows, numIters):
    """
    Print n, wall time, and time/log2(n).
    Input: resultRows list of (sizeN, elapsedSeconds), numIters.
    Output: none.
    Locals: sizeN, elapsedSeconds, logN, ratio.
    """
    print(f"iterations per size: {numIters:,}")
    print()
    header = f"{'n':>10}  {'time_s':>12}  {'time/log2(n)':>14}"
    print(header)
    print("-" * len(header))
    for sizeN, elapsedSeconds in resultRows:
        logN = math.log2(sizeN) if sizeN > 1 else 1.0
        ratio = elapsedSeconds / logN
        print(f"{sizeN:>10}  {elapsedSeconds:>12.6f}  {ratio:>14.6f}")

def run_size(sizeN, searchTarget, numIters):
    """
    Build one array, check hit/miss, then time unsuccessful searches.
    Input: sizeN, searchTarget (should miss), numIters.
    Output: elapsed seconds.
    Locals: sortedArr, elapsedSeconds.
    """
    sortedArr = make_sorted_array(sizeN)
    if binary_search(sortedArr, searchTarget) != -1:
        raise SystemExit(f"expected miss for target={searchTarget} at n={sizeN}")
    if binary_search(sortedArr, 0) != 0:
        raise SystemExit(f"expected hit at index 0 for n={sizeN}")
    elapsedSeconds = time_searches(sortedArr, searchTarget, numIters)
    return elapsedSeconds

def main():
    """
    Time 30M unsuccessful searches for each assignment array size.
    Input: optional --iters N on the command line.
    Output: per-size timings and a summary table.
    Locals: numIters, resultRows, sizeN, elapsedSeconds, searchTarget.
    """
    print("Problem 6: binary search timings (Python)")
    print()

    numIters = parse_iters(sys.argv[1:])
    print(f"read iterations: {numIters}")
    searchTarget = -1
    print(f"search target (unsuccessful): {searchTarget}")
    print(f"array sizes: {list(SIZE_LIST)}")
    print()

    resultRows = []
    for sizeN in SIZE_LIST:
        elapsedSeconds = run_size(sizeN, searchTarget, numIters)
        resultRows.append((sizeN, elapsedSeconds))
        print(f"n={sizeN:>8}: {elapsedSeconds:.6f} s", flush=True)

    print()
    print_table(resultRows, numIters)
    print()
    print(
        "Binary search is O(log n), so time should grow slowly with n "
        "(about a constant bump each time n grows by 4x)."
    )

if __name__ == "__main__":
    main()