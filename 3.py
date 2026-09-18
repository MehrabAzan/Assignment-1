def quick_sort(A, lo, hi):
    if lo < hi:
        pivot = partition(A, lo, hi)
        return quick_sort(A, lo, pivot) + [pivot] + quick_sort(A, pivot + 1, hi)

def partition(A, lo, hi):
    pivot = A[lo]
    leftwall = lo

    for i in range(lo + 1, hi):
        if A[i] < pivot:
            A[i], A[leftwall] = A[leftwall], A[i]
            leftwall += 1

    pivot, A[leftwall] = A[leftwall], pivot

    return leftwall

print(quick_sort([3, 6, 8, 10, 1, 2, 1], 0, 7))