# Outside Documentation — Problem 4 (Matrix Addition Timing)

## Statement of the Problem

Measure how long it takes to add two square matrices under two different nested-loop orders, and observe how those times change as the matrix order grows.

- **Version 1:** outer index walks rows; each step updates an entire row (row-major–friendly access on C-contiguous storage).
- **Version 2:** outer index walks columns; each step updates an entire column (column-oriented access).

Initialization of the source matrices is **excluded** from the timed region. The experiment should show whether (and when) column-oriented access becomes slower due to cache and virtual-memory behavior as problem size increases.

The program does not solve a numerical “answer”; the deliverable is a sequence of self-explanatory timing reports suitable for forming a hypothesis about memory hierarchy effects.

## Top-Down Design

1. **Choose the experimental size sequence**  
   Work through a predetermined list of matrix orders (powers of two from a modest in-cache size up through very large orders that may exhaust physical memory).

2. **For each order n**  
   a. Report the planned size and an estimate of memory needed for three matrices.  
   b. Attempt to allocate three `n × n` single-precision arrays (sources filled with ones; destination empty).  
   c. If allocation fails, record that this size was skipped and continue.  
   d. Otherwise, time Version 1 addition, then time Version 2 addition, on the same allocated arrays.  
   e. Report both times and their ratio when the first time is positive.

3. **After all sizes**  
   If at least one size succeeded, print a compact summary table of all successful timings; otherwise stop quietly after the per-size messages.

4. **Helpers (encapsulation)**  
   Separate concerns: byte estimate, allocation (with out-of-memory handling), the two addition kernels, a timer that runs both kernels, per-size orchestration, and summary printing. No shared mutable module state for experiment parameters.

## Input

This program takes **no interactive or file input**. The only “input” to the experiment is the built-in size sequence defined inside the driver:

```
128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768
```

There is no free-form numeric format to parse. Environment requirements:

- A Python 3 interpreter.
- The NumPy library must be importable; if it is missing, the process exits with a short message naming the dependency.

If a future revision were to read sizes from standard input, each read would be paired with a write (echo or status line), optionally gated by a quiet-mode flag, so that the read/write pairing remains present in the source.

## Assumptions (and Justification)

| Assumption | Justification |
|------------|----------------|
| Matrices are stored in C-contiguous (row-major) layout | Matches typical NumPy defaults and the assignment’s contrast between row-friendly and column-friendly traversal. |
| Element type is 32-bit floating point | Keeps memory pressure predictable (`3 × n² × 4` bytes) while remaining a realistic dense-array type. |
| Source matrices are filled with ones; destination starts uninitialized then overwritten | Values do not affect addition timing meaningfully; ones avoid uninitialized-source concerns. Filling sources is done before timing starts. |
| Each outer step may update a full row or column via a vectorized slice | Preserves the intended access *order* of the assignment’s double loop while remaining practical in Python for large `n`. |
| Allocation failure means “skip this size,” not abort the whole run | Large `n` may exceed available RAM; continuing yields useful data for smaller sizes. |
| Wall-clock `perf_counter` intervals are acceptable timing measures | Matches the course guidance to time execution and interpret results with awareness of OS noise; users should repeat runs when analyzing reliability. |
| No global experiment parameters | Style requirement: sizes and related constants live in the driver or are passed as parameters. |

## Data Structures

- **Three dense 2-D arrays** of shape `(n, n)`, dtype float32: two sources and one destination. These are the only bulk structures; they hold all matrix data for a given trial.
- **A list of integers** — the predetermined matrix orders to try.
- **A list of triples** — for each successful size: `(n, time_version1, time_version2)`, used only to build the final summary table.
- **Scalar floats** — start/stop timestamps and elapsed seconds for each timed kernel.

No graphs, trees, or custom container classes are required.

## Testing Notes

Testing means running the program and comparing observed behavior to expectations:

- Small `n` (e.g. 128–512): both versions complete; Version 1 is typically not much slower than Version 2 (often faster).
- Larger `n`: Version 2 should tend to slow relative to Version 1 if cache/VMM effects appear; ratio message appears when Version 1 time is positive.
- Extreme `n`: if memory is insufficient, the run should print a skip message for that size and continue.
- Missing NumPy: process should exit with a clear dependency message rather than a raw import traceback after a silent failure.

Output labels and units are intended to stand alone; this document does not interpret or restate printed results.
