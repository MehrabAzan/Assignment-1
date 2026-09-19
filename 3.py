def quick_sort(A, lo, hi, depth=0, stats=None):
    if hi - lo <= 1:
        return A[lo:hi]

    if stats is not None:
        stats["partitions"] += 1
        stats["maxDepth"] = max(stats["maxDepth"], depth)

    pivotIndex = partition(A, lo, hi)
    leftSize = pivotIndex - lo
    rightSize = hi - pivotIndex - 1
    if stats is not None:
        stats["splits"].append((leftSize, rightSize))

    pivotVal = A[pivotIndex]
    return (
        quick_sort(A, lo, pivotIndex, depth + 1, stats)
        + [pivotVal]
        + quick_sort(A, pivotIndex + 1, hi, depth + 1, stats)
    )

def partition(A, lo, hi):
    A[hi - 2], A[hi - 1] = A[hi - 1], A[hi - 2]
    pivot = A[hi - 1]
    leftwall = lo

    for n in range(lo, hi - 1):
        if A[n] <= pivot:
            A[n], A[leftwall] = A[leftwall], A[n]
            leftwall += 1

    A[leftwall], A[hi - 1] = A[hi - 1], A[leftwall]
    return leftwall

def build_optimal(n):
    if n == 0:
        return []
    if n == 1:
        return [1]

    median = (n + 1) // 2
    leftCount = median - 1
    rightCount = n - median
    leftPart = build_optimal(leftCount)
    rightPart = build_optimal(rightCount)
    rightPart = [x + median for x in rightPart]

    arr = leftPart + rightPart[: rightCount - 1] + [median]
    if rightCount > 0:
        arr.append(rightPart[-1])
    return arr

def build_slowest(n):
    if n <= 1:
        return list(range(1, n + 1))
    return list(range(1, n - 1)) + [n, n - 1]

def run_case(label, arr):
    stats = {"partitions": 0, "maxDepth": 0, "splits": []}
    copy = arr[:]
    result = quick_sort(copy, 0, len(copy), stats=stats)
    print(f"{label}")
    print(f"  input:      {arr}")
    print(f"  sorted:     {result}")
    print(f"  maxDepth:   {stats['maxDepth']}")
    print(f"  partitions: {stats['partitions']}")
    print(f"  splits:     {stats['splits']}")
    print()

optimalCases = [build_optimal(n) for n in [3, 7, 15]]
slowestCases = [build_slowest(n) for n in [3, 7, 15]]

print("=== OPTIMAL (balanced splits) ===\n")
for arr in optimalCases:
    run_case(f"n = {len(arr)}", arr)

print("=== SLOWEST (unbalanced splits) ===\n")
for arr in slowestCases:
    run_case(f"n = {len(arr)}", arr)