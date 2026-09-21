"""
Problem 2 — page transfers under LRU (reads and writes counted separately).

Parameters
- page size: 1000 words
- main memory: 2000 pages (LRU)
- arrays A, B, C each (1:4000, 1:4000), one word per element
- N = 4000
- inner-loop accesses (in order):
    read  C[I,J]
    read  B[I,J]
    write A[I,J]
    read  C[J, N-I+1]
    read  B[J,I]
    write B[I,J]

Assumptions
- memory starts empty
- write-allocate: a write miss loads the page (1 read transfer) then dirties it
- write-back: evicting a dirty page costs 1 write transfer
- no final flush of dirty pages still resident at the end

Answers (from full LRU simulation)
(a) row-major:    reads = 32,040,009   writes = 31,998
(b) column-major: reads = 48,025,340   writes = 31,998,667
"""

from collections import OrderedDict

N = 4000
PAGE_SIZE = 1000
MEMORY_FRAMES = 2000
A, B, C = 0, 1, 2

def page_id(array_id, i, j, row_major):
    if row_major:
        linear = (i - 1) * N + (j - 1)
    else:
        linear = (j - 1) * N + (i - 1)
    return (array_id, linear // PAGE_SIZE)

class LruMemory:
    def __init__(self, frames):
        self.frames = frames
        self.pages = OrderedDict()
        self.read_transfers = 0
        self.write_transfers = 0

    def touch(self, page, is_write):
        if page in self.pages:
            dirty = self.pages.pop(page)
            self.pages[page] = dirty or is_write
            return

        if len(self.pages) >= self.frames:
            _, was_dirty = self.pages.popitem(last=False)
            if was_dirty:
                self.write_transfers += 1

        self.read_transfers += 1
        self.pages[page] = is_write

def run_simulation(row_major, show_progress=True):
    mem = LruMemory(MEMORY_FRAMES)
    layout = "row-major" if row_major else "column-major"

    for i in range(1, N + 1):
        col = N - i + 1
        for j in range(1, N + 1):
            mem.touch(page_id(C, i, j, row_major), False)
            mem.touch(page_id(B, i, j, row_major), False)
            mem.touch(page_id(A, i, j, row_major), True)
            mem.touch(page_id(C, j, col, row_major), False)
            mem.touch(page_id(B, j, i, row_major), False)
            mem.touch(page_id(B, i, j, row_major), True)

        if show_progress and i % 500 == 0:
            print(
                f"  [{layout}] I={i}/{N}  "
                f"reads={mem.read_transfers:,}  writes={mem.write_transfers:,}"
            )

    return mem.read_transfers, mem.write_transfers

def print_answer(label, reads, writes):
    print(f"{label}")
    print(f"  READ  transfers: {reads:,}")
    print(f"  WRITE transfers: {writes:,}")

def main():
    print("Problem 2: LRU page transfers")
    print(f"  N={N}, page_size={PAGE_SIZE}, memory_frames={MEMORY_FRAMES}")
    print("  arrays: A, B, C each {0}x{0}".format(N))
    print()

    print("Running (a) row-major...")
    reads_a, writes_a = run_simulation(True)
    print()

    print("Running (b) column-major...")
    reads_b, writes_b = run_simulation(False)
    print()

    print("=" * 48)
    print("FINAL ANSWERS")
    print("=" * 48)
    print_answer("(a) Row-major order", reads_a, writes_a)
    print()
    print_answer("(b) Column-major order", reads_b, writes_b)
    print("=" * 48)
    print()
    print("Why column-major is worse here:")
    print("  The outer loop walks rows of A/B/C[I,J], which thrash under")
    print("  column-major layout, so A/B writebacks happen far more often.")
    print("  Row-major matches that scan; only the column-style refs thrash.")

if __name__ == "__main__":
    main()
