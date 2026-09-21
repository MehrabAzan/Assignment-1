def quick_sort(a, lo, hi, depth=0, stats=None):
    if hi - lo <= 1:
        return a[lo:hi]

    if stats is not None:
        stats["partitions"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth)

    pivot_index = partition(a, lo, hi)
    left_size = pivot_index - lo
    right_size = hi - pivot_index - 1
    if stats is not None:
        stats["splits"].append((left_size, right_size))

    pivot_val = a[pivot_index]
    return (
        quick_sort(a, lo, pivot_index, depth + 1, stats)
        + [pivot_val]
        + quick_sort(a, pivot_index + 1, hi, depth + 1, stats)
    )

def partition(a, lo, hi):
    a[hi - 2], a[hi - 1] = a[hi - 1], a[hi - 2]
    pivot = a[hi - 1]
    leftwall = lo

    for n in range(lo, hi - 1):
        if a[n] <= pivot:
            a[n], a[leftwall] = a[leftwall], a[n]
            leftwall += 1

    a[leftwall], a[hi - 1] = a[hi - 1], a[leftwall]
    return leftwall

def build_optimal(n):
    if n == 0:
        return []
    if n == 1:
        return [1]

    median = (n + 1) // 2
    left_count = median - 1
    right_count = n - median
    left_part = build_optimal(left_count)
    right_part = build_optimal(right_count)
    right_part = [x + median for x in right_part]

    arr = left_part + right_part[: right_count - 1] + [median]
    if right_count > 0:
        arr.append(right_part[-1])
    return arr

def build_slowest(n):
    if n <= 1:
        return list(range(1, n + 1))
    return list(range(1, n - 1)) + [n, n - 1]

def run_case(label, arr):
    stats = {"partitions": 0, "max_depth": 0, "splits": []}
    copy = arr[:]
    result = quick_sort(copy, 0, len(copy), stats=stats)
    print(f"{label}")
    print(f"  input:      {arr}")
    print(f"  sorted:     {result}")
    print(f"  max_depth:  {stats['max_depth']}")
    print(f"  partitions: {stats['partitions']}")
    print(f"  splits:     {stats['splits']}")
    print()

optimal_cases = [build_optimal(n) for n in [3, 7, 15]]
slowest_cases = [build_slowest(n) for n in [3, 7, 15]]

print("=== OPTIMAL (balanced splits) ===\n")
for arr in optimal_cases:
    run_case(f"n = {len(arr)}", arr)

print("=== SLOWEST (unbalanced splits) ===\n")
for arr in slowest_cases:
    run_case(f"n = {len(arr)}", arr)
