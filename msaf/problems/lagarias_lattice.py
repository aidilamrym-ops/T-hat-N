# Lagarias Spectral Criterion Validation

import sys
from mpmath import mp

mp.dps = 100

def harmonic_number(n):
    return sum(mp.mpf(1) / mp.mpf(i) for i in range(1, n + 1))

def verify_lagarias(n_max=1000):
    print(f"Running Lagarias inequality scan up to N = {n_max}...")
    for n in range(1, n_max + 1):
        divisors = [i for i in range(1, n + 1) if n % i == 0]
        sigma_n = sum(divisors)
        hn = harmonic_number(n)
        bound = hn + mp.exp(hn) * mp.log(hn)
        if sigma_n > bound:
            print(f"ANOMALY at n={n}: sigma={sigma_n}, bound={bound}")
    print("Lagarias scan completed successfully.")

if __name__ == "__main__":
    verify_lagarias(500)
