#!/usr/bin/env python3
"""Put random byte mutation next to the concolic loop on the same toy gate.

Both start from the seed in concolic.py -- a batch that passes the marker and the
digit checks but whose declared total does not equal the sum of its amounts.

- Random mutation flips one byte to a random value, up to N tries, and keeps a
  result only if it is accepted (valid digits and reconciling) with amounts
  different from the seed's. With a fixed PRNG seed the count is reproducible.
- The concolic loop solves the gate directly (see concolic.py).

The gate couples several bytes at once: to reconcile with new amounts, the three
digits of the total and the digits of an amount must change together. No single
byte flip can do that from this seed, so random single-byte mutation never
crosses it, however many tries it is given; the solver changes the coupled bytes
together and crosses in two rounds.

Run:  python3 compare.py
"""
import random

from concolic import run, concolic, SEED, A1, A2, _num

SEED_AMOUNTS = (_num(SEED, A1), _num(SEED, A2))


def random_single_byte(tries, rng):
    """Flip one random byte per try; return (first_hit_try, input) or (None, None)."""
    for i in range(1, tries + 1):
        data = list(SEED)
        data[rng.randrange(len(data))] = rng.randrange(256)
        accepted, _, _ = run(data)
        if accepted and (_num(data, A1), _num(data, A2)) != SEED_AMOUNTS:
            return i, data
    return None, None


if __name__ == "__main__":
    N = 200_000
    rng = random.Random(20260817)  # fixed -> reproducible
    hit, data = random_single_byte(N, rng)
    print(f"random single-byte mutation, {N} tries, fixed PRNG seed 20260817:")
    if hit:
        print(f"  first reconciling batch with new amounts at try {hit}: {bytes(data)!r}")
    else:
        print(f"  none in {N} tries")
    print()
    print("concolic loop:")
    concolic(list(SEED))
