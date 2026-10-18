/* collatz_sweep.c - P2 audit engine C: memoryless drop-check + record prefix.
 *
 * Frozen with reports/AUDIT_COLLATZ_PREREG_2026-10-19.md.
 * Build (frozen):  gcc -O2 -std=gnu11 -o collatz_sweep collatz_sweep.c
 *
 * Modes:
 *   collatz_sweep selftest
 *   collatz_sweep drop <exp> --out <path>     odd n in [3, 2^exp), exp 16..40
 *   collatz_sweep records <exp> --out <path>  records below 2^exp, exp 4..26
 *
 * Drop-check semantics (identical to engine P mode e2): for each odd n,
 * iterate the shortcut map T(n) = (3n+1)/2 (odd) | n/2 (even) until a value
 * < n appears; step cap 1e6. The prefix24 sub-result is the same metrics
 * restricted to n < 2^24 and must equal engine P's e2 result at bound 2^24.
 *
 * Records mode: t(n) via full shortcut trajectories for odd n, t(2k) =
 * max(2k, t(k)) for even n; running maxima below the bound are the record
 * prefix and must equal engine P's e3 result at the same bound.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 u128;
typedef unsigned long long u64;

#define DROP_CAP 1000000ULL

static int drop_one(u64 start64, u64 *steps, u128 *val) {
    u128 start = (u128)start64, n = (u128)start64;
    u64 c = 0;
    for (;;) {
        if (n & 1) n = (3 * n + 1) >> 1;
        else n >>= 1;
        c++;
        if (n < start) { *steps = c; *val = n; return 1; }
        if (c > DROP_CAP) return 0;
    }
}

static void u128_dec(u128 v, char *buf) {
    char tmp[48];
    int k = 0;
    if (v == 0) { buf[0] = '0'; buf[1] = 0; return; }
    while (v) { tmp[k++] = (char)('0' + (int)(v % 10)); v /= 10; }
    for (int i = 0; i < k; i++) buf[i] = tmp[k - 1 - i];
    buf[k] = 0;
}

static int records_below(u64 bound, u64 *recs_n, u64 *recs_t, u64 *count) {
    u64 *t = (u64 *)malloc((size_t)bound * sizeof(u64));
    if (!t) return 0;
    u64 runmax = 0;
    *count = 0;
    for (u64 n = 1; n < bound; n++) {
        u64 v;
        if (n == 1) {
            v = 1;
        } else if (!(n & 1)) {
            u64 prev = t[n >> 1];
            v = prev > n ? prev : n;
        } else {
            u64 mx = n;
            u64 x = n;
            while (x != 1) {
                x = (x & 1) ? (3 * x + 1) / 2 : x / 2;
                if (x > mx) mx = x;
            }
            v = mx;
        }
        t[n] = v;
        if (v > runmax) {
            runmax = v;
            recs_n[*count] = n;
            recs_t[*count] = v;
            (*count)++;
        }
    }
    free(t);
    return 1;
}

static int selftest(void) {
    int checks = 0;
    struct { u64 n, steps; u128 val; } dt[] = {{3, 4, 2}, {7, 7, 5},
                                               {15, 7, 10}, {27, 59, 23}};
    for (unsigned i = 0; i < 4; i++) {
        u64 st;
        u128 v;
        if (!drop_one(dt[i].n, &st, &v) || st != dt[i].steps || v != dt[i].val) {
            fprintf(stderr, "selftest drop fail n=%llu\n", (unsigned long long)dt[i].n);
            return 1;
        }
        checks++;
    }
    u64 rn[64], rt[64], rc = 0;
    if (!records_below(16, rn, rt, &rc)) return 1;
    {
        u64 exp_n[5] = {1, 2, 3, 7, 15};
        u64 exp_t[5] = {1, 2, 8, 26, 80};
        if (rc != 5) {
            fprintf(stderr, "selftest records count %llu\n", (unsigned long long)rc);
            return 1;
        }
        for (int i = 0; i < 5; i++) {
            if (rn[i] != exp_n[i] || rt[i] != exp_t[i]) {
                fprintf(stderr, "selftest records mismatch at %d\n", i);
                return 1;
            }
        }
    }
    checks++;
    printf("SELFTEST OK (%d checks)\n", checks);
    return 0;
}

static void emit_drop(FILE *fh, int exp, u64 bound, u64 checked, u64 maxst,
                      u64 argmax, const char *sum_str, const u64 *fail, int nfail,
                      u64 p_bound, u64 p_checked, u64 p_maxst, u64 p_argmax,
                      const char *p_sum_str) {
    fprintf(fh, "{\n");
    fprintf(fh, "  \"tool\": \"collatz_sweep\",\n");
    fprintf(fh, "  \"mode\": \"drop\",\n");
    fprintf(fh, "  \"params\": {\"exp\": %d, \"bound\": %llu, \"step_cap\": %llu},\n",
            exp, (unsigned long long)bound, (unsigned long long)DROP_CAP);
    fprintf(fh, "  \"result\": {\"bound\": %llu, \"odd_checked\": %llu, "
                "\"max_steps_to_drop\": %llu, \"argmax\": %llu, \"sum_drop\": \"%s\", "
                "\"cap_hits\": [",
            (unsigned long long)bound, (unsigned long long)checked,
            (unsigned long long)maxst, (unsigned long long)argmax, sum_str);
    for (int i = 0; i < nfail; i++)
        fprintf(fh, "%s%llu", i ? ", " : "", (unsigned long long)fail[i]);
    fprintf(fh, "]},\n");
    fprintf(fh, "  \"prefix24\": {\"bound\": %llu, \"odd_checked\": %llu, "
                "\"max_steps_to_drop\": %llu, \"argmax\": %llu, \"sum_drop\": \"%s\"}\n",
            (unsigned long long)p_bound, (unsigned long long)p_checked,
            (unsigned long long)p_maxst,
            (unsigned long long)p_argmax, p_sum_str);
    fprintf(fh, "}\n");
}

static int mode_drop(int exp, const char *out) {
    if (exp < 16 || exp > 40) { fprintf(stderr, "drop exp out of range\n"); return 2; }
    u64 bound = 1ULL << exp;
    u64 p24 = 1ULL << 24;
    u64 checked = 0, maxst = 0, argmax = 0;
    u128 sum = 0;
    u64 p_checked = 0, p_maxst = 0, p_argmax = 0;
    u128 p_sum = 0;
    u64 fail_cap = 64, nfail = 0;
    u64 *fail = (u64 *)malloc(fail_cap * sizeof(u64));
    if (!fail) return 3;
    u64 tick = 0;
    for (u64 n = 3; n < bound; n += 2) {
        u64 st;
        u128 v;
        if (!drop_one(n, &st, &v)) {
            if (nfail == fail_cap) {
                fail_cap *= 2;
                fail = (u64 *)realloc(fail, fail_cap * sizeof(u64));
                if (!fail) return 3;
            }
            fail[nfail++] = n;
            continue;
        }
        checked++;
        sum += v;
        if (st > maxst) { maxst = st; argmax = n; }
        if (n < p24) {
            p_checked++;
            p_sum += v;
            if (st > p_maxst) { p_maxst = st; p_argmax = n; }
        }
        if ((++tick & 0xFFFFFFULL) == 0)
            fprintf(stderr, "progress n=%llu checked=%llu\n",
                    (unsigned long long)n, (unsigned long long)checked);
    }
    char sbuf[48], spbuf[48];
    u128_dec(sum, sbuf);
    u128_dec(p_sum, spbuf);
    u64 p_bound = (exp <= 24) ? bound : p24;
    emit_drop(stdout, exp, bound, checked, maxst, argmax, sbuf,
              fail, (int)nfail, p_bound, p_checked, p_maxst, p_argmax, spbuf);
    if (out) {
        FILE *fh = fopen(out, "w");
        if (!fh) { fprintf(stderr, "cannot open out\n"); return 3; }
        emit_drop(fh, exp, bound, checked, maxst, argmax, sbuf,
                  fail, (int)nfail, p_bound, p_checked, p_maxst, p_argmax, spbuf);
        fclose(fh);
    }
    free(fail);
    return 0;
}

static void emit_records(FILE *fh, int exp, u64 bound, const u64 *rn,
                         const u64 *rt, u64 rc) {
    fprintf(fh, "{\n");
    fprintf(fh, "  \"tool\": \"collatz_sweep\",\n");
    fprintf(fh, "  \"mode\": \"records\",\n");
    fprintf(fh, "  \"params\": {\"exp\": %d, \"bound\": %llu},\n",
            exp, (unsigned long long)bound);
    fprintf(fh, "  \"result\": {\"bound\": %llu, \"record_count\": %llu, \"records\": [",
            (unsigned long long)bound, (unsigned long long)rc);
    for (u64 i = 0; i < rc; i++)
        fprintf(fh, "%s{\"i\": %llu, \"n\": %llu, \"t\": %llu}", i ? ", " : "",
                (unsigned long long)(i + 1), (unsigned long long)rn[i],
                (unsigned long long)rt[i]);
    fprintf(fh, "]}\n}\n");
}

static int mode_records(int exp, const char *out) {
    if (exp < 4 || exp > 26) { fprintf(stderr, "records exp out of range\n"); return 2; }
    u64 bound = 1ULL << exp;
    u64 rn[512], rt[512], rc = 0;
    if (!records_below(bound, rn, rt, &rc)) { fprintf(stderr, "alloc fail\n"); return 3; }
    if (rc > 512) { fprintf(stderr, "too many records\n"); return 3; }
    emit_records(stdout, exp, bound, rn, rt, rc);
    if (out) {
        FILE *fh = fopen(out, "w");
        if (!fh) { fprintf(stderr, "cannot open out\n"); return 3; }
        emit_records(fh, exp, bound, rn, rt, rc);
        fclose(fh);
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s selftest|drop|records <exp> [--out PATH]\n", argv[0]);
        return 64;
    }
    if (!strcmp(argv[1], "selftest")) return selftest();
    if (!strcmp(argv[1], "drop") || !strcmp(argv[1], "records")) {
        if (argc < 3) { fprintf(stderr, "missing exp\n"); return 64; }
        int exp = atoi(argv[2]);
        const char *out = NULL;
        for (int i = 3; i + 1 < argc; i++)
            if (!strcmp(argv[i], "--out")) out = argv[i + 1];
        if (!strcmp(argv[1], "drop")) return mode_drop(exp, out);
        return mode_records(exp, out);
    }
    fprintf(stderr, "unknown mode\n");
    return 64;
}
