/*
 * Problem 5: demonstrate heap fragmentation (macOS).
 *
 * Usage: 5.exe [m]
 *   If m is omitted, the program estimates m from available memory.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <mach/mach.h>
#include <sys/sysctl.h>

#define MIB (1024ULL * 1024ULL)
#define SMALL_BLOCK MIB
#define LARGE_BLOCK ((size_t)(1.45 * MIB))

/*
 * Returns the current monotonic time in seconds.
 * Input: none. Output: seconds since an arbitrary epoch as double.
 * Locals: ts holds the clock sample.
 */
static double NowSeconds(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
        return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
    }
    timespec_get(&ts, TIME_UTC);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

/*
 * Returns the system memory page size in bytes.
 * Input: none. Output: page size, or 4096 if sysconf fails.
 * Locals: page is the raw sysconf result.
 */
static size_t PageSize(void) {
    long page = sysconf(_SC_PAGESIZE);
    if (page <= 0) {
        return 4096;
    }
    return (size_t)page;
}

/*
 * Touches every page in a block so the OS commits physical RAM.
 * Input: p points at bytes bytes of writable memory.
 * Output: none (writes one byte per page, and the last byte).
 * Locals: page is the stride; i walks page starts.
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
 * Estimates currently available physical RAM in mebibytes (macOS).
 * Input: none. Output: available MiB, or a fallback from hw.memsize / 1024.
 * Locals: pageSize, vmstat, availPages for Mach VM; memSize for sysctl.
 */
static size_t AvailableMib(void) {
    vm_size_t pageSize = 0;
    vm_statistics64_data_t vmstat;
    mach_msg_type_number_t count = HOST_VM_INFO64_COUNT;
    uint64_t memSize = 0;
    size_t len = sizeof(memSize);

    if (host_page_size(mach_host_self(), &pageSize) == KERN_SUCCESS &&
        host_statistics64(mach_host_self(), HOST_VM_INFO64,
                          (host_info64_t)&vmstat, &count) == KERN_SUCCESS) {
        uint64_t availPages =
            (uint64_t)vmstat.free_count +
            (uint64_t)vmstat.inactive_count +
            (uint64_t)vmstat.speculative_count;
        return (size_t)((availPages * (uint64_t)pageSize) / MIB);
    }

    if (sysctlbyname("hw.memsize", &memSize, &len, NULL, 0) == 0 &&
        memSize > 0) {
        return (size_t)(memSize / MIB);
    }
    return 1024;
}

/*
 * Chooses a default block-count parameter m from available RAM.
 * Input: none. Output: m in [1, 2500] so that 3m MiB fits most usable RAM.
 * Locals: avail is approximate free MiB; targetMib is the fill budget; m is result.
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
 * Allocates count blocks of bytes each, touching every page; times the work.
 * Input: count, bytes; secondsOut receives elapsed seconds on success.
 * Output: pointer array of count blocks, or NULL on calloc/malloc failure.
 * Locals: blocks is the array; i indexes allocations; t0/t1 bound the timer.
 */
static char **AllocateBlocks(size_t count, size_t bytes, double *secondsOut) {
    char **blocks;
    size_t i;
    double t0;
    double t1;

    blocks = (char **)calloc(count, sizeof(char *));
    if (blocks == NULL) {
        return NULL;
    }

    t0 = NowSeconds();
    for (i = 0; i < count; i++) {
        blocks[i] = (char *)malloc(bytes);
        if (blocks[i] == NULL) {
            size_t j;
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
 * Frees every odd-indexed block and times the frees.
 * Input: blocks array of count pointers (even slots left allocated).
 * Output: elapsed seconds; odd slots become NULL.
 * Locals: i walks odd indices; t0/t1 bound the timer.
 */
static double FreeOddBlocks(char **blocks, size_t count) {
    size_t i;
    double t0;
    double t1;

    t0 = NowSeconds();
    for (i = 1; i < count; i += 2) {
        free(blocks[i]);
        blocks[i] = NULL;
    }
    t1 = NowSeconds();
    return t1 - t0;
}

/*
 * Frees every non-NULL block pointer and the array itself.
 * Input: blocks (may be NULL) and count. Output: none.
 * Locals: i indexes each slot.
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
 * Parses optional m from argv[1]; writes the accepted value when echoOn.
 * Input: argc/argv; echoOn non-zero prints the parsed m to stdout.
 * Output: m > 0 on success, 0 on bad/missing positive integer.
 * Locals: parsed holds the converted argument.
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
 * Prints the planned phase sizes for the chosen m.
 * Input: m and smallCount (= 3*m). Output: setup lines on stdout.
 */
static void PrintPlan(size_t m, size_t smallCount) {
    printf("Problem 5: heap fragmentation demo (macOS)\n");
    printf("  available RAM (approx): %zu MiB\n", AvailableMib());
    printf("  m = %zu\n", m);
    printf("  phase 1: allocate %zu x 1 MiB = %zu MiB\n",
           smallCount, smallCount);
    printf("  phase 2: free odd-numbered blocks (~%zu holes)\n",
           smallCount / 2);
    printf("  phase 3: allocate %zu x 1.45 MiB = %.2f MiB\n\n",
           m, m * 1.45);
}

/*
 * Runs the three fragmentation phases and prints timings.
 * Input: m > 0. Output: 0 on completion (phase 3 may fail), 1 on phase-1 failure.
 * Locals: small/large block arrays and per-phase timings.
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
        fprintf(stderr, "phase 1 failed — try a smaller m\n");
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
    printf("  allocator must coalesce / extend the heap / use new virtual\n");
    printf("  ranges — often much slower than phase 1 per byte, and may fail.\n");

    FreeAllBlocks(largeBlocks, m);
    FreeAllBlocks(smallBlocks, smallCount);
    return 0;
}

/*
 * Entry point: resolve m from argv or AvailableMib, then run the demo.
 * Input: argc/argv with optional positive integer m.
 * Output: process exit status (0 success, 1 bad args or phase-1 failure).
 * Locals: m is the block-count parameter.
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
