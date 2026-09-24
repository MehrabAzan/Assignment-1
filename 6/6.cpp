/*
 * Times 30,000,000 unsuccessful searches over sorted arrays of increasing
 * size. Array construction is excluded from the timed region. Theory: O(log n).
 */

#include <chrono>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <vector>

using namespace std;

/*
 * Iterative binary search on a sorted array.
 * Input: sortedArr of length sizeN, searchTarget.
 * Output: index of hit, or -1 on miss.
 * Locals: lo, hi, mid, midVal.
 */
static long long BinarySearch(const long long *sortedArr, long long sizeN,
                              long long searchTarget) {
    long long lo = 0;
    long long hi = sizeN - 1;

    while (lo <= hi) {
        long long mid = lo + (hi - lo) / 2;
        long long midVal = sortedArr[mid];
        if (midVal < searchTarget) {
            lo = mid + 1;
        } else if (midVal > searchTarget) {
            hi = mid - 1;
        } else {
            return mid;
        }
    }
    return -1;
}

/*
 * Build a sorted array of values 0 .. sizeN-1.
 * Input: sizeN. Output: vector of length sizeN.
 * Locals: sortedArr, i.
 */
static vector<long long> MakeSortedArray(long long sizeN) {
    vector<long long> sortedArr(static_cast<size_t>(sizeN));
    for (long long i = 0; i < sizeN; i++) {
        sortedArr[static_cast<size_t>(i)] = i;
    }
    return sortedArr;
}

/*
 * Time numIters binary searches. Array build is not included.
 * Input: sortedArr, sizeN, searchTarget, numIters.
 * Output: elapsed seconds.
 * Locals: startTime, endTime, iterIndex, sink.
 */
static double TimeSearches(const long long *sortedArr, long long sizeN,
                           long long searchTarget, long long numIters) {
    volatile long long sink = 0;
    auto startTime = chrono::steady_clock::now();
    for (long long iterIndex = 0; iterIndex < numIters; iterIndex++) {
        sink = BinarySearch(sortedArr, sizeN, searchTarget);
    }
    auto endTime = chrono::steady_clock::now();
    (void)sink;
    chrono::duration<double> elapsed = endTime - startTime;
    return elapsed.count();
}

/*
 * Resolve iteration count from --iters.
 * Input: argc, argv, defaultIters.
 * Output: positive count, or defaultIters if unset.
 * Locals: numIters, argIndex.
 */
static long long ParseIters(int argc, char **argv, long long defaultIters) {
    long long numIters = defaultIters;
    int argIndex = 1;

    while (argIndex < argc) {
        if (strcmp(argv[argIndex], "--iters") == 0 &&
            argIndex + 1 < argc) {
            numIters = strtoll(argv[argIndex + 1], nullptr, 10);
            argIndex += 2;
            continue;
        }
        argIndex += 1;
    }
    if (numIters < 1) {
        cerr << "iters must be >= 1\n";
        exit(1);
    }
    return numIters;
}

/*
 * Print n, wall time, and time/log2(n).
 * Input: sizeList, timeList, sizeCount, numIters.
 * Output: none.
 * Locals: i, sizeN, elapsedSeconds, logN, ratio.
 */
static void PrintTable(const long long *sizeList, const double *timeList,
                       int sizeCount, long long numIters) {
    cout << "iterations per size: " << numIters << "\n\n";
    cout << setw(10) << "n"
         << "  " << setw(12) << "time_s"
         << "  " << setw(14) << "time/log2(n)" << "\n";
    cout << "----------------------------------------\n";
    for (int i = 0; i < sizeCount; i++) {
        long long sizeN = sizeList[i];
        double elapsedSeconds = timeList[i];
        double logN = (sizeN > 1) ? log2(static_cast<double>(sizeN)) : 1.0;
        double ratio = elapsedSeconds / logN;
        cout << setw(10) << sizeN
             << "  " << setw(12) << fixed << setprecision(6)
             << elapsedSeconds
             << "  " << setw(14) << ratio << "\n";
    }
}

/*
 * Build one array, check hit/miss, then time unsuccessful searches.
 * Input: sizeN, searchTarget (should miss), numIters.
 * Output: elapsed seconds.
 * Locals: sortedArr, data, elapsedSeconds.
 */
static double RunSize(long long sizeN, long long searchTarget,
                      long long numIters) {
    vector<long long> sortedArr = MakeSortedArray(sizeN);
    const long long *data = sortedArr.data();

    if (BinarySearch(data, sizeN, searchTarget) != -1) {
        cerr << "expected miss for target=" << searchTarget
             << " at n=" << sizeN << "\n";
        exit(1);
    }
    if (BinarySearch(data, sizeN, 0) != 0) {
        cerr << "expected hit at index 0 for n=" << sizeN << "\n";
        exit(1);
    }

    return TimeSearches(data, sizeN, searchTarget, numIters);
}

/*
 * Time 30M unsuccessful searches for each assignment array size.
 * Input: optional --iters N on the command line.
 * Output: process exit status.
 * Locals: sizeList, sizeCount, defaultIters, numIters, searchTarget,
 *         timeList, i, sizeN, elapsedSeconds.
 */
int main(int argc, char **argv) {
    const long long sizeList[] = {
        100, 400, 1600, 6400, 25600, 102400, 409600, 1638400
    };
    const int sizeCount = 8;
    const long long defaultIters = 30000000LL;
    long long numIters;
    long long searchTarget;
    double timeList[8];
    int i;

    numIters = ParseIters(argc, argv, defaultIters);
    cout << "read iterations: " << numIters << "\n";
    searchTarget = -1;
    cout << "search target (unsuccessful): " << searchTarget << "\n";
    cout << "array sizes:";
    for (i = 0; i < sizeCount; i++) {
        cout << " " << sizeList[i];
    }
    cout << "\n\n";

    for (i = 0; i < sizeCount; i++) {
        long long sizeN = sizeList[i];
        double elapsedSeconds = RunSize(sizeN, searchTarget, numIters);
        timeList[i] = elapsedSeconds;
        cout << "n=" << setw(8) << sizeN << ": "
             << fixed << setprecision(6) << elapsedSeconds
             << " s\n" << flush;
    }

    cout << "\n";
    PrintTable(sizeList, timeList, sizeCount, numIters);
    cout << "\n";
    cout << "Binary search is O(log n), so time should grow slowly with n "
            "(about a constant bump each time n grows by 4x).\n";

    return 0;
}