/*
 * Problem 5: heap fragmentation demo (Windows).
 *
 * 1) Allocate 3m blocks of 1 MiB.
 * 2) Free all odd-numbered blocks (1-based: 1st, 3rd, 5th, ...).
 * 3) Allocate m blocks of 1.45 MiB.
 *
 * Usage: 5.exe [m]
 *   If m is omitted, m is estimated from available physical memory.
 */

#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

#define MIB (1024ULL * 1024ULL)
#define SMALL_BLOCK MIB
#define LARGE_BLOCK ((size_t)(1.45 * MIB))

/*
 * Current high-resolution time in seconds.
 * Input: none. Output: seconds as double.
 * Locals: freq, counter for QueryPerformanceCounter.
 */
static double NowSeconds(void) {
    static LARGE_INTEGER freq = {0};
    LARGE_INTEGER counter;

    if (freq.QuadPart == 0) {
        QueryPerformanceFrequency(&freq);
    }
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / (double)freq.QuadPart;
}

/*
 * System memory page size in bytes.
 * Input: none. Output: page size from GetSystemInfo.
 * Locals: info holds SYSTEM_INFO.
 */
static size_t PageSize(void) {
    SYSTEM_INFO info;
    GetSystemInfo(&info);
    if (info.dwPageSize == 0) {
        return 4096;
    }
    return (size_t)info.dwPageSize;
}

/*
 * Touch every page in a block so Windows commits physical RAM.
 * Input: p points at bytes bytes of writable memory.
 * Output: none.
 * Locals: page stride, i page offset.
 */
static void TouchBlock(char *p, size_t bytes) {
    size_t page = PageSize();
    size_t i;

    for (i = 0; i < bytes; i += page) {
        p[i] = 1;
    }
    if (bytes > 0) {
        p[bytes - 1] = 1;
    }
}

/*
 * Approximate available physical RAM in MiB.
 * Input: none. Output: ullAvailPhys / 1 MiB, or 1024 on failure.
 * Locals: status for GlobalMemoryStatusEx.
 */
static size_t AvailableMib(void) {
    MEMORYSTATUSEX status;

    status.dwLength = sizeof(status);
    if (GlobalMemoryStatusEx(&status)) {
        return (size_t)(status.ullAvailPhys / MIB);
    }
    return 1024;
}

/*
 * Choose default m from available RAM, capped for safety.
 * Input: none. Output: m in [1, 2500].
 * Locals: avail, targetMib, m.
 */
static size_t ChooseM(void) {
    size_t avail = AvailableMib();
    size_t targetMib;
    size_t m;

    if (avail < 64) {
        targetMib = avail / 2;
    } else {
        targetMib = (avail * 8) / 10;
    }
    m = targetMib / 3;
    if (m < 1) {
        m = 1;
    }
    if (m > 2500) {
        m = 2500;
    }
    return m;
}

/*
 * Allocate count blocks of bytes each, touch pages, and time it.
 * Input: count, bytes; secondsOut receives elapsed seconds (0 on early fail).
 * Output: pointer array, or NULL on failure.
 * Locals: blocks, i, t0, t1, j.
 */
static char **AllocateBlocks(size_t count, size_t bytes, double *secondsOut) {
    char **blocks;
    size_t i;
    double t0;
    double t1;

    *secondsOut = 0.0;
    blocks = (char **)calloc(count, sizeof(char *));
    if (blocks == NULL) {
        return NULL;
    }

    t0 = NowSeconds();
    for (i = 0; i < count; i++) {
        blocks[i] = (char *)malloc(bytes);
        if (blocks[i] == NULL) {
            size_t j;
            t1 = NowSeconds();
            *secondsOut = t1 - t0;
            fprintf(stderr, "malloc failed at block %zu / %zu (%zu bytes)\n",
                    i, count, bytes);
            for (j = 0; j < i; j++) {
                free(blocks[j]);
            }
            free(blocks);
            return NULL;
        }
        TouchBlock(blocks[i], bytes);
    }
    t1 = NowSeconds();
    *secondsOut = t1 - t0;
    return blocks;
}

/*
 * Free every odd-numbered block (1-based) and time the frees.
 * Input: blocks of count pointers.
 * Output: elapsed seconds. Freed slots become NULL.
 * Locals: i, t0, t1.
 */
static double FreeOddBlocks(char **blocks, size_t count) {
    size_t i;
    double t0;
    double t1;

    t0 = NowSeconds();
    for (i = 0; i < count; i += 2) {
        free(blocks[i]);
        blocks[i] = NULL;
    }
    t1 = NowSeconds();
    return t1 - t0;
}

/*
 * Free every non-NULL block and the pointer array.
 * Input: blocks (may be NULL), count. Output: none.
 * Locals: i.
 */
static void FreeAllBlocks(char **blocks, size_t count) {
    size_t i;

    if (blocks == NULL) {
        return;
    }
    for (i = 0; i < count; i++) {
        free(blocks[i]);
    }
    free(blocks);
}

/*
 * Parse optional m from argv[1] and echo it when echoOn is set.
 * Input: argc, argv, echoOn.
 * Output: parsed m, or 0 if missing/invalid.
 * Locals: parsed.
 */
static size_t ParseMArgument(int argc, char **argv, int echoOn) {
    size_t parsed;

    if (argc < 2) {
        return 0;
    }
    parsed = (size_t)strtoull(argv[1], NULL, 10);
    if (echoOn) {
        printf("read m argument: %zu\n", parsed);
    }
    return parsed;
}

/*
 * Print the planned sizes for this run.
 * Input: m, smallCount. Output: setup lines on stdout.
 * Locals: none.
 */
static void PrintPlan(size_t m, size_t smallCount) {
    printf("Problem 5: heap fragmentation demo (Windows)\n");
    printf("  available RAM (approx): %zu MiB\n", AvailableMib());
    printf("  m = %zu\n", m);
    printf("  phase 1: allocate %zu x 1 MiB = %zu MiB\n",
           smallCount, smallCount);
    printf("  phase 2: free odd-numbered blocks (~%zu holes)\n",
           (smallCount + 1) / 2);
    printf("  phase 3: allocate %zu x 1.45 MiB = %.2f MiB\n\n",
           m, m * 1.45);
}

/*
 * Run the three fragmentation phases and print timings.
 * Input: m > 0.
 * Output: 0 on completion, 1 if phase 1 fails.
 * Locals: smallCount, block arrays, timings.
 */
static int RunFragmentationDemo(size_t m) {
    size_t smallCount = 3 * m;
    char **smallBlocks;
    char **largeBlocks;
    double tAllocSmall;
    double tFreeOdd;
    double tAllocLarge;

    PrintPlan(m, smallCount);

    smallBlocks = AllocateBlocks(smallCount, (size_t)SMALL_BLOCK, &tAllocSmall);
    if (smallBlocks == NULL) {
        fprintf(stderr, "phase 1 failed - try a smaller m\n");
        return 1;
    }
    printf("1) alloc 3m x 1 MiB:     %.6f s\n", tAllocSmall);

    tFreeOdd = FreeOddBlocks(smallBlocks, smallCount);
    printf("2) free odd-numbered:    %.6f s\n", tFreeOdd);

    largeBlocks = AllocateBlocks(m, LARGE_BLOCK, &tAllocLarge);
    if (largeBlocks == NULL) {
        printf("3) alloc m x 1.45 MiB:   FAILED (%.6f s until failure)\n",
               tAllocLarge);
        printf("\nFragmentation likely prevented fitting 1.45 MiB blocks "
               "into 1 MiB holes.\n");
        FreeAllBlocks(smallBlocks, smallCount);
        return 0;
    }
    printf("3) alloc m x 1.45 MiB:   %.6f s  (%zu blocks ok)\n",
           tAllocLarge, m);
    printf("\nNotes for your report:\n");
    printf("- Phase 1 touches every page, so time includes real RAM commit.\n");
    printf("- Phase 2 is cheap: free() mostly updates allocator metadata.\n");
    printf("- Phase 3 requests 1.45 MiB while free holes are ~1 MiB, so the\n");
    printf("  allocator must coalesce, grow the heap, or map new regions.\n");

    FreeAllBlocks(largeBlocks, m);
    FreeAllBlocks(smallBlocks, smallCount);
    return 0;
}

/*
 * Resolve m from argv or available memory, then run the demo.
 * Input: argc, argv with optional positive integer m.
 * Output: process exit status.
 * Locals: m.
 */
int main(int argc, char **argv) {
    size_t m;

    if (argc >= 2) {
        m = ParseMArgument(argc, argv, 1);
        if (m == 0) {
            fprintf(stderr, "m must be a positive integer\n");
            return 1;
        }
    } else {
        m = ChooseM();
        printf("chose m from available memory: %zu\n", m);
    }

    return RunFragmentationDemo(m);
}