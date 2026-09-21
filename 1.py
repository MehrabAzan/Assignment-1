"""
Assignment Problem 1: Towers of Hanoi on a graph.

Graph G=(V,E) with V={Start,A1,A2,A3,A4,Dest} and undirected edges
  (Start,A1), (A1,A2), (A2,A3), (A3,A4), (A4,A1), (A1,Dest).
Classic Hanoi rules apply, and a disk may move only along an edge.

Approach: BFS (bidirectional) on the configuration graph. Each legal
layout of n disks is a peg assignment for every disk (stacks stay
size-ordered, so there are 6^n configurations). A move is legal iff
the disk is topmost on its peg, the destination peg is adjacent, and
the destination is empty or has a larger top disk. Shortest Start->Dest
paths are recovered from the BFS parent links.

Complexity of this BFS approach:
  Time  O(6^n * n)  — up to 6^n configs; each yields O(n) candidate moves
  Space O(6^n)      — visited / parent maps in the worst case
(A bespoke recursive construction is possible for some Hanoi graphs;
BFS is exact for this topology and practical for n <= 10.)
"""

from collections import deque

PEGS = ["Start", "A1", "A2", "A3", "A4", "Dest"]
NUM_PEGS = len(PEGS)

# Adjacency by peg index
ADJ = [
    [1],          # Start -> A1
    [0, 2, 4, 5],  # A1 -> Start, A2, A4, Dest
    [1, 3],        # A2 -> A1, A3
    [2, 4],        # A3 -> A2, A4
    [3, 1],        # A4 -> A3, A1
    [1],          # Dest -> A1
]

def tops_of(state):
    """Smallest disk on each peg, or -1 if empty (disk 0 = smallest)."""
    tops = [-1] * NUM_PEGS
    for disk, peg in enumerate(state):
        if tops[peg] == -1:
            tops[peg] = disk
    return tops

def neighbors(state):
    tops = tops_of(state)
    for src in range(NUM_PEGS):
        disk = tops[src]
        if disk < 0:
            continue
        for dst in ADJ[src]:
            top_dst = tops[dst]
            if top_dst < 0 or top_dst > disk:
                new_state = list(state)
                new_state[disk] = dst
                yield tuple(new_state), src, dst

def solve_hanoi(n):
    start = tuple([0] * n)
    goal = tuple([5] * n)
    if start == goal:
        return []

    parent_a = {start: None}
    move_a = {start: None}
    parent_b = {goal: None}
    move_b = {goal: None}
    queue_a = deque([start])
    queue_b = deque([goal])
    meeting = None

    while queue_a and queue_b:
        if len(queue_a) <= len(queue_b):
            meeting = expand(queue_a, parent_a, move_a, parent_b)
        else:
            meeting = expand(queue_b, parent_b, move_b, parent_a)
        if meeting is not None:
            break
    else:
        raise RuntimeError(f"No solution found for n={n}")

    path = []
    cur = meeting
    while move_a[cur] is not None:
        path.append(move_a[cur])
        cur = parent_a[cur]
    path.reverse()

    cur = meeting
    while move_b[cur] is not None:
        src, dst = move_b[cur]
        path.append((dst, src))
        cur = parent_b[cur]
    return path

def expand(queue, parent, move_map, other_parent):
    state = queue.popleft()
    for nxt, src, dst in neighbors(state):
        if nxt in parent:
            continue
        parent[nxt] = state
        move_map[nxt] = (src, dst)
        if nxt in other_parent:
            return nxt
        queue.append(nxt)
    return None

def print_moves(moves, first_last=100):
    total = len(moves)
    if total <= 2 * first_last:
        for src, dst in moves:
            print(f"{PEGS[src]} -> {PEGS[dst]}")
        return

    for src, dst in moves[:first_last]:
        print(f"{PEGS[src]} -> {PEGS[dst]}")
    skipped = total - 2 * first_last
    print(f"... ({skipped} moves omitted) ...")
    for src, dst in moves[-first_last:]:
        print(f"{PEGS[src]} -> {PEGS[dst]}")

def verify_moves(n, moves):
    stacks = [[] for _ in range(NUM_PEGS)]
    stacks[0] = list(range(n - 1, -1, -1))
    for src, dst in moves:
        if dst not in ADJ[src]:
            raise AssertionError(f"non-adjacent move {PEGS[src]} -> {PEGS[dst]}")
        if not stacks[src]:
            raise AssertionError(f"empty source {PEGS[src]}")
        disk = stacks[src].pop()
        if stacks[dst] and stacks[dst][-1] < disk:
            raise AssertionError("larger disk placed on smaller disk")
        stacks[dst].append(disk)
    if stacks[5] != list(range(n - 1, -1, -1)):
        raise AssertionError("final stack on Dest incorrect")
    for i, peg in enumerate(PEGS):
        if i != 5 and stacks[i]:
            raise AssertionError(f"disks left on {peg}")

def main():
    for n in range(1, 11):
        moves = solve_hanoi(n)
        verify_moves(n, moves)
        print(f"=== n={n}  ({len(moves)} moves) ===")
        print_moves(moves)
        print()

if __name__ == "__main__":
    main()
