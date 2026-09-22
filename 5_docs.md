# Outside Documentation — Problem 5 (Heap Fragmentation)

## Problem statement

This program studies how a heap allocator behaves when free space is broken into many holes that are each too small for a later request size. The experiment:

1. Allocates a large number of equal-sized blocks so that much of usable RAM is occupied.
2. Releases every other block, leaving a checkerboard of free holes.
3. Attempts a second wave of allocations whose individual size is larger than those holes.

The goal is to measure how long each phase takes and to observe whether the third phase succeeds, slows down, or fails because the free regions cannot satisfy the larger requests without coalescing or obtaining new address space.

This program targets **macOS (Darwin)** only.

## Top-down design

1. **Resolve workload size `m`.**  
   Either take a positive integer from the command line, or estimate `m` from approximate available physical memory so that about `3m` mebibytes are requested in phase 1 (with safety caps).

2. **Phase 1 — fill.**  
   Allocate `3m` blocks of 1 MiB each. After each allocation, touch every memory page in the block so the operating system commits physical pages rather than only reserving virtual address space. Record wall-clock time for the whole phase.

3. **Phase 2 — punch holes.**  
   Free every odd-indexed block from phase 1. This leaves roughly `1.5m` free holes of about 1 MiB interleaved with still-live 1 MiB blocks. Record the time for these frees.

4. **Phase 3 — oversized requests.**  
   Allocate `m` blocks of 1.45 MiB each (again touching pages). Each request is larger than a single hole left in phase 2, so the allocator must find coalesced space, grow the heap, or map new regions. Record time; if allocation fails mid-phase, report failure and stop after cleanup.

5. **Cleanup.**  
   Free any remaining phase-3 and phase-1 blocks and the pointer arrays that hold them.

Helper responsibilities are split by concern: timing, page size, page touching, memory estimate, choosing `m`, allocating timed batches, freeing odd slots, freeing everything, parsing the optional argument, printing the plan, and running the three phases.

## Input format

- Invocation: `5.exe` or `5.exe <m>`
- `<m>` is optional.
- When present, `<m>` must be a single positive decimal integer (base 10). A value of `0` or a non-positive conversion is rejected.
- No other command-line options are accepted.
- No interactive stdin prompts; the only program input is the optional argc/argv argument.
- Units implied by the experiment (not typed by the user): phase-1 block size is 1 MiB; phase-3 block size is 1.45 MiB; counts are `3m` then `m`.

## Assumptions and justification

| Assumption | Justification |
|------------|----------------|
| Running on macOS with Mach VM APIs and `sysctl` available | Available-memory estimation uses `host_statistics64` / `host_page_size`, with `hw.memsize` as fallback. |
| Wall time via `CLOCK_MONOTONIC` (or UTC clock fallback) is adequate for relative phase comparison | Absolute “correct” timings are environment-dependent; the experiment needs comparable durations across phases on one run. |
| Touching one byte per page forces commit of physical RAM | Without touching, macOS may lazy-allocate; timings would not reflect real memory pressure. |
| Default `m` uses ~50–80% of estimated available MiB divided by 3, capped at 2500 | Keeps the demo stressful but reduces risk of freezing an interactive machine; users can pass a larger `m` deliberately. |
| Odd-index frees create predominantly ~1 MiB holes | Adjacent live blocks prevent many small holes from merging into a single 1.45 MiB region without extra work. |
| `malloc` / `free` from the system C library are the objects of study | The assignment is about observed allocator/OS behavior under fragmentation, not a custom heap. |
| Failure of phase 3 is an acceptable experimental outcome | Fragmentation (or genuine exhaustion) may make 1.45 MiB requests impossible while 1 MiB holes remain. |

## Data structures

- **Pointer array (`char **`)** — holds addresses of individually `malloc`’d blocks for a phase. Indexed `0 .. count-1`. Odd indices may be set to null after phase 2.
- **Heap blocks** — contiguous byte regions of either 1 MiB or 1.45 MiB obtained from `malloc`; treated as opaque storage except for page-stride stores that force commitment.
- **Scalar locals** — sizes (`m`, counts, byte lengths), timestamps (doubles), and loop indices; no file-scope mutable variables.
- **Platform structs (locals only)** — Mach `vm_statistics64_data_t` and related counts when estimating free pages; `struct timespec` when sampling the clock.
