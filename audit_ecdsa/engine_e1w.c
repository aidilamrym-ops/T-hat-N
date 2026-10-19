/* E1w - weld: calls the host C library's own lrand48/srand48 (glibc).
 * FROZEN at the V1 freeze commit. Used only to validate engine_e1/engine_e2
 * against a real implementation; draws mode only.
 * Usage: e1w draws <t> <k>   -> k values, %08lX
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv)
{
    if (argc == 4 && strcmp(argv[1], "draws") == 0) {
        long t = strtol(argv[2], 0, 10);
        long k = strtol(argv[3], 0, 10);
        if (k < 0 || k > 100000000L) {
            fprintf(stderr, "bad params\n");
            return 2;
        }
        srand48(t);
        for (long i = 0; i < k; i++) {
            printf("%08lX\n", (unsigned long)lrand48());
        }
        return 0;
    }
    fprintf(stderr, "usage: e1w draws <t> <k>\n");
    return 2;
}
