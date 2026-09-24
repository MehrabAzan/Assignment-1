/*
 * Times 30,000,000 unsuccessful searches over sorted arrays of increasing
 * size. Array construction is excluded from the timed region. Theory: O(log n).
 */

class Problem6 {
    /*
     * Iterative binary search on a sorted array.
     * Input: sortedArr ascending, searchTarget.
     * Output: index of hit, or -1 on miss.
     * Locals: lo, hi, mid, midVal.
     */
    static long BinarySearch(long[] sortedArr, long searchTarget) {
        long lo = 0;
        long hi = sortedArr.length - 1;
        while (lo <= hi) {
            long mid = lo + (hi - lo) / 2;
            long midVal = sortedArr[(int) mid];
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
     * Input: sizeN. Output: long array of length sizeN.
     * Locals: sortedArr, i.
     */
    static long[] MakeSortedArray(int sizeN) {
        long[] sortedArr = new long[sizeN];
        for (int i = 0; i < sizeN; i++) {
            sortedArr[i] = i;
        }
        return sortedArr;
    }

    /*
     * Time numIters binary searches. Array build is not included.
     * Input: sortedArr, searchTarget, numIters.
     * Output: elapsed seconds.
     * Locals: sink, startNs, endNs, iterIndex.
     */
    static double TimeSearches(long[] sortedArr, long searchTarget, long numIters) {
        long sink = 0;
        long startNs = System.nanoTime();
        for (long iterIndex = 0; iterIndex < numIters; iterIndex++) {
            sink = BinarySearch(sortedArr, searchTarget);
        }
        long endNs = System.nanoTime();
        if (sink == 42) {
            System.out.print("");
        }
        return (endNs - startNs) / 1_000_000_000.0;
    }

    /*
     * Resolve iteration count from --iters.
     * Input: args from main, defaultIters.
     * Output: positive long, or defaultIters if unset.
     * Locals: numIters, argIndex.
     */
    static long ParseIters(String[] args, long defaultIters) {
        long numIters = defaultIters;
        int argIndex = 0;
        while (argIndex < args.length) {
            if (args[argIndex].equals("--iters") && argIndex + 1 < args.length) {
                numIters = Long.parseLong(args[argIndex + 1]);
                argIndex += 2;
                continue;
            }
            argIndex += 1;
        }
        if (numIters < 1) {
            System.err.println("iters must be >= 1");
            System.exit(1);
        }
        return numIters;
    }

    /*
     * Print n, wall time, and time/log2(n).
     * Input: sizeList, timeList, numIters.
     * Output: none.
     * Locals: i, sizeN, elapsedSeconds, logN, ratio.
     */
    static void PrintTable(long[] sizeList, double[] timeList, long numIters) {
        System.out.printf("iterations per size: %,d%n%n", numIters);
        System.out.printf("%10s  %12s  %14s%n", "n", "time_s", "time/log2(n)");
        System.out.println("----------------------------------------");
        for (int i = 0; i < sizeList.length; i++) {
            long sizeN = sizeList[i];
            double elapsedSeconds = timeList[i];
            double logN = (sizeN > 1) ? (Math.log(sizeN) / Math.log(2.0)) : 1.0;
            double ratio = elapsedSeconds / logN;
            System.out.printf("%10d  %12.6f  %14.6f%n", sizeN, elapsedSeconds, ratio);
        }
    }

    /*
     * Build one array, check hit/miss, then time unsuccessful searches.
     * Input: sizeN, searchTarget (should miss), numIters.
     * Output: elapsed seconds.
     * Locals: sortedArr, elapsedSeconds.
     */
    static double RunSize(int sizeN, long searchTarget, long numIters) {
        long[] sortedArr = MakeSortedArray(sizeN);
        if (BinarySearch(sortedArr, searchTarget) != -1) {
            System.err.println("expected miss for target=" + searchTarget + " at n=" + sizeN);
            System.exit(1);
        }
        if (BinarySearch(sortedArr, 0) != 0) {
            System.err.println("expected hit at index 0 for n=" + sizeN);
            System.exit(1);
        }
        return TimeSearches(sortedArr, searchTarget, numIters);
    }

    /*
     * Time 30M unsuccessful searches for each assignment array size.
     * Input: optional --iters N on the command line.
     * Output: none; prints timings.
     * Locals: sizeList, defaultIters, numIters, searchTarget, timeList,
     *         i, sizeN, elapsedSeconds.
     */
    public static void main(String[] args) {
        long[] sizeList = {
            100, 400, 1600, 6400, 25600, 102400, 409600, 1638400
        };
        long defaultIters = 30_000_000L;
        long numIters = ParseIters(args, defaultIters);
        System.out.println("read iterations: " + numIters);
        long searchTarget = -1;
        System.out.println("search target (unsuccessful): " + searchTarget);
        System.out.print("array sizes:");
        for (long sizeN : sizeList) {
            System.out.print(" " + sizeN);
        }
        System.out.println();
        System.out.println();

        double[] timeList = new double[sizeList.length];
        for (int i = 0; i < sizeList.length; i++) {
            int sizeN = (int) sizeList[i];
            double elapsedSeconds = RunSize(sizeN, searchTarget, numIters);
            timeList[i] = elapsedSeconds;
            System.out.printf("n=%8d: %.6f s%n", sizeN, elapsedSeconds);
        }

        System.out.println();
        PrintTable(sizeList, timeList, numIters);
        System.out.println();
        System.out.println(
            "Binary search is O(log n), so time should grow slowly with n "
                + "(about a constant bump each time n grows by 4x)."
        );
    }
}
