/* E1 - lrand48/srand48 reimplementation, pure C, from the POSIX spec.
 * V1 audit (ECDSA seed origins): model = srand48(t): x = (t & 0xFFFFFFFF) << 16 | 0x330E;
 * step: x = (0x5DEECE66D * x + 0xB) mod 2^48; lrand48() = x >> 17.
 * FROZEN at the V1 freeze commit. No libc RNG calls in this binary
 * (see engine_e1w.c for the glibc weld).
 * Usage:
 *   e1 draws <t> <k>                        print k values (state >> 17), %08X each
 *   e1 cand <t> <per> <shift> <width> <n>   print candidate n: per draws of (state >> shift)
 *                                           formatted %0<width>X, concatenated
 *   e1 scan <t> <per> <shift> <width> <target_hex> <nmax>
 *                                           print the first n' in [1, nmax] whose candidate
 *                                           equals target_hex (case-insensitive; whitespace
 *                                           in the target is ignored), else NONE
 */
#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t st;

static void my_srand48(uint64_t t)
{
    st = (((uint64_t)t & 0xFFFFFFFFULL) << 16) | 0x330EULL;
}

static uint64_t my_next_state(void)
{
    st = (0x5DEECE66DULL * st + 0xBULL) & 0xFFFFFFFFFFFFULL;
    return st;
}

static int norm_hex(const char *in, char *out, size_t outsz)
{
    size_t j = 0;
    for (const char *p = in; *p != '\0'; p++) {
        unsigned char c = (unsigned char)*p;
        if (isspace(c)) {
            continue;
        }
        if (!isxdigit(c)) {
            return -1;
        }
        if (j + 1 >= outsz) {
            return -1;
        }
        out[j++] = (char)toupper(c);
    }
    out[j] = '\0';
    return (int)j;
}

int main(int argc, char **argv)
{
    if (argc == 4 && strcmp(argv[1], "draws") == 0) {
        uint64_t t = strtoull(argv[2], 0, 10);
        long k = strtol(argv[3], 0, 10);
        if (k < 0 || k > 100000000L) {
            fprintf(stderr, "bad params\n");
            return 2;
        }
        my_srand48(t);
        for (long i = 0; i < k; i++) {
            uint64_t s = my_next_state();
            printf("%08X\n", (unsigned)(s >> 17));
        }
        return 0;
    }

    if (argc == 7 && strcmp(argv[1], "cand") == 0) {
        uint64_t t = strtoull(argv[2], 0, 10);
        int per = atoi(argv[3]), shift = atoi(argv[4]), width = atoi(argv[5]);
        long n = strtol(argv[6], 0, 10);
        if (per < 1 || per > 64 || n < 1 || shift < 0 || shift > 47 || width < 1 || width > 16) {
            fprintf(stderr, "bad params\n");
            return 2;
        }
        uint64_t keep[64];
        my_srand48(t);
        uint64_t total = (uint64_t)per * (uint64_t)n;
        for (uint64_t i = 0; i < total; i++) {
            uint64_t s = my_next_state();
            if (i >= total - (uint64_t)per) {
                keep[i - (total - (uint64_t)per)] = s;
            }
        }
        for (int i = 0; i < per; i++) {
            printf("%0*llX", width, (unsigned long long)(keep[i] >> shift));
        }
        printf("\n");
        return 0;
    }

    if (argc == 8 && strcmp(argv[1], "scan") == 0) {
        uint64_t t = strtoull(argv[2], 0, 10);
        int per = atoi(argv[3]), shift = atoi(argv[4]), width = atoi(argv[5]);
        long nmax = strtol(argv[7], 0, 10);
        if (per < 1 || per > 64 || nmax < 1 || nmax > 100000000L || shift < 0 || shift > 47 ||
            width < 1 || width > 16) {
            fprintf(stderr, "bad params\n");
            return 2;
        }
        char target[4096];
        int tlen = norm_hex(argv[6], target, sizeof target);
        if (tlen <= 0 || tlen != per * width) {
            fprintf(stderr, "bad target for format\n");
            return 2;
        }
        uint64_t slots[64];
        char buf[64 * 17];
        long found = 0;
        long total = (long)per * nmax; /* nmax counts candidates; one candidate = per draws */
        my_srand48(t);
        for (long i = 1; i <= total; i++) {
            uint64_t s = my_next_state();
            slots[(i - 1) % per] = s;
            if (i % per == 0) {
                size_t off = 0;
                for (int j = 0; j < per; j++) {
                    off += (size_t)snprintf(buf + off, sizeof buf - off, "%0*llX", width,
                                            (unsigned long long)(slots[j] >> shift));
                }
                if (strcmp(buf, target) == 0) {
                    found = i;
                    break;
                }
            }
        }
        if (found != 0) {
            printf("%ld\n", found / per); /* report the candidate index n' = draw_index / per */
        } else {
            printf("NONE\n");
        }
        return 0;
    }

    fprintf(stderr,
            "usage: e1 draws <t> <k> | e1 cand <t> <per> <shift> <width> <n> | "
            "e1 scan <t> <per> <shift> <width> <target> <nmax>\n");
    return 2;
}
