/*
 * Problem 5: demonstrate heap fragmentation.
 *
 * 1) Allocate 3m blocks of 1 MiB each (m chosen so this nearly fills RAM).
 * 2) Free all odd-numbered blocks (~1.5m holes of 1 MiB).
 * 3) Allocate m blocks of 1.45 MiB each (too big for those holes).
 *
 * Prints timings for each phase. Explain the timings in your report:
 * phase 3 is often much slower / may fail or page heavily because the
 * free list is fragmented into 1 MiB gaps while requests need 1.45 MiB.
 *
 * Usage: 5.exe [m]
 *   If m is omitted, the program estimates m from available memory.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#elif defined(__APPLE__)
#include <mach/mach.h>
#include <sys/sysctl.h>
#include <unistd.h>
#elif defined(__linux__)
#include <unistd.h>
#else
#include <unistd.h>
#endif

#define MIB (1024ULL * 1024ULL)
#define SMALL_BLOCK MIB
#define LARGE_BLOCK ((size_t)(1.45 * MIB))

static double NowSeconds(void) {
#ifdef _WIN32
    static LARGE_INTEGER freq = {0};
    LARGE_INTEGER counter;
    if (freq.QuadPart == 0) {
        QueryPerformanceFrequency(&freq);
    }
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / (double)freq.QuadPart;
#else
    struct timespec ts;
#if defined(CLOCK_MONOTONIC)
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
        return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
    }
#endif
    timespec_get(&ts, TIME_UTC);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
#endif
}

static size_t PageSize(void) {
#ifdef _WIN32
    SYSTEM_INFO info;
    GetSystemInfo(&info);
    return (size_t)info.dwPageSize;
#else
    long page = sysconf(_SC_PAGESIZE);
    if (page <= 0) {
        return 4096;
    }
    return (size_t)page;
#endif
}

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

static size_t AvailableMib(void) {
#ifdef _WIN32
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    if (GlobalMemoryStatusEx(&status)) {
        return (size_t)(status.ullAvailPhys / MIB);
    }
#elif defined(__APPLE__)
    {
        vm_size_t pageSize = 0;
        vm_statistics64_data_t vmstat;
        mach_msg_type_number_t count = HOST_VM_INFO64_COUNT;
        if (host_page_size(mach_host_self(), &pageSize) == KERN_SUCCESS &&
            host_statistics64(mach_host_self(), HOST_VM_INFO64,
                              (host_info64_t)&vmstat, &count) == KERN_SUCCESS) {
            uint64_t availPages =
                (uint64_t)vmstat.free_count +
                (uint64_t)vmstat.inactive_count +
                (uint64_t)vmstat.speculative_count;
            return (size_t)((availPages * (uint64_t)pageSize) / MIB);
        }
    }
    {
        uint64_t memsize = 0;
        size_t len = sizeof(memsize);
        if (sysctlbyname("hw.memsize", &memsize, &len, NULL, 0) == 0 &&
            memsize > 0) {
            return (size_t)(memsize / MIB);
        }
    }
#elif defined(__linux__)
    {
        FILE *f = fopen("/proc/meminfo", "r");
        if (f != NULL) {
            char line[256];
            unsigned long memAvailableKb = 0;
            while (fgets(line, sizeof(line), f) != NULL) {
                if (sscanf(line, "MemAvailable: %lu kB", &memAvailableKb) == 1) {
                    break;
                }
            }
            fclose(f);
            if (memAvailableKb > 0) {
                return (size_t)(memAvailableKb / 1024UL);
            }
        }
    }
#endif
    return 1024;
}

static size_t ChooseM(void) {
    size_t avail = AvailableMib();
    size_t targetMib;
    size_t m;
    /* Aim to fill most usable RAM with 3m MiB, but cap for safety. */
    if (avail < 64) {
        targetMib = avail / 2;
    } else {
        targetMib = (avail * 8) / 10;
    }
    m = targetMib / 3;
    if (m < 1) {
        m = 1;
    }
    /* Override with: 5.exe <m>  if you need a larger exhaustion test. */
    if (m > 2500) {
        m = 2500;
    }
    return m;
}

static char **AllocateBlocks(size_t count, size_t bytes, double *secondsOut) {
    char **blocks;
    size_t i;
    double t0, t1;

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

static double FreeOddBlocks(char **blocks, size_t count) {
    size_t i;
    double t0, t1;

    t0 = NowSeconds();
    for (i = 1; i < count; i += 2) {
        free(blocks[i]);
        blocks[i] = NULL;
    }
    t1 = NowSeconds();
    return t1 - t0;
}

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

int main(int argc, char **argv) {
    size_t m;
    size_t smallCount;
    char **smallBlocks;
    char **largeBlocks;
    double tAllocSmall;
    double tFreeOdd;
    double tAllocLarge;
    size_t largeOk;

    if (argc >= 2) {
        m = (size_t)strtoull(argv[1], NULL, 10);
        if (m == 0) {
            fprintf(stderr, "m must be a positive integer\n");
            return 1;
        }
    } else {
        m = ChooseM();
    }

    smallCount = 3 * m;

    printf("Problem 5: heap fragmentation demo\n");
    printf("  available RAM (approx): %zu MiB\n", AvailableMib());
    printf("  m = %zu\n", m);
    printf("  phase 1: allocate %zu x 1 MiB = %zu MiB\n",
           smallCount, smallCount);
    printf("  phase 2: free odd-numbered blocks (~%zu holes)\n",
           smallCount / 2);
    printf("  phase 3: allocate %zu x 1.45 MiB = %.2f MiB\n\n",
           m, m * 1.45);

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
        printf("\nFragmentation likely prevented fitting 1.45 MiB blocks into 1 MiB holes.\n");
        FreeAllBlocks(smallBlocks, smallCount);
        return 0;
    }
    largeOk = m;
    printf("3) alloc m x 1.45 MiB:   %.6f s  (%zu blocks ok)\n",
           tAllocLarge, largeOk);

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