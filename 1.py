"""
Problem 1: Hanoi on G with pegs Start,A1,A2,A3,A4,Dest.
Edges (Start,A1),(A1,A2),(A2,A3),(A3,A4),(A4,A1),(A1,Dest).
Bidirectional BFS; time O(6^n*n), space O(6^n).
"""

from collections import deque

def build_graph():
    """
    Build the assignment peg graph.
    Input: none.
    Output: pegNames (list[str]), adjacency (list[list[int]]).
    Locals: pegNames, adjacency.
    """
    pegNames = ["Start", "A1", "A2", "A3", "A4", "Dest"]
    adjacency = [[1], [0, 2, 4, 5], [1, 3], [2, 4], [3, 1], [1]]
    return pegNames, adjacency

def tops_of(state, numPegs):
    """
    Smallest disk on each peg, or -1 if the peg is empty.
    Input: state (tuple disk->peg), numPegs.
    Output: tops list of length numPegs.
    Locals: tops, disk, peg.
    """
    tops = [-1] * numPegs
    for disk, peg in enumerate(state):
        if tops[peg] == -1:
            tops[peg] = disk
    return tops

def neighbors(state, adjacency):
    """
    Generate every legal one-disk successor of state.
    Input: state, adjacency.
    Output: yields (nextState, srcPeg, dstPeg).
    Locals: tops, src, disk, dst, topDst, newState.
    """
    tops = tops_of(state, len(adjacency))
    for src in range(len(adjacency)):
        disk = tops[src]
        if disk < 0:
            continue
        for dst in adjacency[src]:
            topDst = tops[dst]
            if topDst < 0 or topDst > disk:
                newState = list(state)
                newState[disk] = dst
                yield tuple(newState), src, dst

def expand(queue, parent, moveMap, otherParent, adjacency):
    """
    Expand one BFS node; return a meeting state if the other search is hit.
    Input: queue, parent, moveMap (this side), otherParent, adjacency.
    Output: meeting state or None.
    Locals: state, nxt, src, dst.
    """
    state = queue.popleft()
    for nxt, src, dst in neighbors(state, adjacency):
        if nxt in parent:
            continue
        parent[nxt] = state
        moveMap[nxt] = (src, dst)
        if nxt in otherParent:
            return nxt
        queue.append(nxt)
    return None

def reconstruct_path(meeting, parentA, moveA, parentB, moveB):
    """
    Build Start->Dest moves from bidirectional BFS maps.
    Input: meeting state; parentA/moveA; parentB/moveB.
    Output: list of (srcPeg, dstPeg).
    Locals: path, cur, src, dst.
    """
    path = []
    cur = meeting
    while moveA[cur] is not None:
        path.append(moveA[cur])
        cur = parentA[cur]
    path.reverse()
    cur = meeting
    while moveB[cur] is not None:
        src, dst = moveB[cur]
        path.append((dst, src))
        cur = parentB[cur]
    return path

def solve_hanoi(n, adjacency):
    """
    Shortest legal move sequence for n disks from Start to Dest.
    Input: n, adjacency (Start=0, Dest=last index).
    Output: list of (srcPeg, dstPeg).
    Locals: start, goal, parentA, moveA, parentB, moveB, queueA, queueB, meeting.
    """
    start = tuple([0] * n)
    goal = tuple([len(adjacency) - 1] * n)
    if start == goal:
        return []
    parentA = {start: None}
    moveA = {start: None}
    parentB = {goal: None}
    moveB = {goal: None}
    queueA = deque([start])
    queueB = deque([goal])
    meeting = None
    while queueA and queueB:
        if len(queueA) <= len(queueB):
            meeting = expand(queueA, parentA, moveA, parentB, adjacency)
        else:
            meeting = expand(queueB, parentB, moveB, parentA, adjacency)
        if meeting is not None:
            break
    else:
        raise RuntimeError(f"No solution found for n={n}")
    return reconstruct_path(meeting, parentA, moveA, parentB, moveB)

def print_moves(moves, pegNames, firstLast=100):
    """
    Print each move; if very long, print first and last firstLast only.
    Input: moves, pegNames, firstLast.
    Output: printed PegX -> PegY lines (and an omission line if trimmed).
    Locals: total, src, dst.
    """
    total = len(moves)
    if total <= 2 * firstLast:
        for src, dst in moves:
            print(f"{pegNames[src]} -> {pegNames[dst]}")
        return
    for src, dst in moves[:firstLast]:
        print(f"{pegNames[src]} -> {pegNames[dst]}")
    print(f"... ({total - 2 * firstLast} moves omitted) ...")
    for src, dst in moves[-firstLast:]:
        print(f"{pegNames[src]} -> {pegNames[dst]}")

def verify_moves(n, moves, pegNames, adjacency):
    """
    Check legality and final tower on Dest; raise AssertionError if wrong.
    Input: n, moves, pegNames, adjacency.
    Output: none.
    Locals: dest, stacks, src, dst, disk, i, stack.
    """
    dest = len(pegNames) - 1
    stacks = [[] for _ in pegNames]
    stacks[0] = list(range(n - 1, -1, -1))
    for src, dst in moves:
        if dst not in adjacency[src]:
            raise AssertionError("non-adjacent move")
        disk = stacks[src].pop()
        if stacks[dst] and stacks[dst][-1] < disk:
            raise AssertionError("larger on smaller")
        stacks[dst].append(disk)
    if stacks[dest] != list(range(n - 1, -1, -1)):
        raise AssertionError("bad final Dest stack")
    for i, stack in enumerate(stacks):
        if i != dest and stack:
            raise AssertionError("disks left off Dest")

def main():
    """
    Solve and print Hanoi on the assignment graph for n = 1..10.
    Input: none (n range fixed by the assignment); each n is echoed.
    Output: for each n, echoed n, header with move count, then moves.
    Locals: pegNames, adjacency, n, moves.
    """
    pegNames, adjacency = build_graph()
    print("input: n = 1..10 (fixed by assignment)")
    print()
    for n in range(1, 11):
        print(f"input n: {n}")
        moves = solve_hanoi(n, adjacency)
        verify_moves(n, moves, pegNames, adjacency)
        print(f"=== n={n}  ({len(moves)} moves) ===")
        print_moves(moves, pegNames)
        print()

if __name__ == "__main__":
    main()