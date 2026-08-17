English | [简体中文](FINDINGS.zh-CN.md)

# What the concolic loop shows, and what a concolic engine would add

## The gate that byte mutation misses

The toy check passes four structural branches -- the marker and the three
digit fields -- and then a sum-equality gate: the declared total must equal the
two amounts added together. Starting from a batch that clears the structure but
fails the gate (`H|010|020|099`), reaching a reconciling batch with *different*
amounts needs two coordinated changes: the digits of an amount and the digits of
the total have to move together. No single byte flip makes both, so random
single-byte mutation never crosses the gate -- 200,000 tries from a fixed PRNG
seed found none (`compare.py`).

The concolic loop crosses it in two rounds (`concolic.py`): it runs once, sees
the reconciles branch fail, negates that branch, and asks Z3 for an input that
satisfies `total == amount1 + amount2` along with the structural branches and
`amounts != seed`. Z3 returns one -- for example `H|001|001|002` -- and the
second run is accepted.

## What made that work, and the blind spot it implies

The loop could negate the gate only because the gate's condition was *recorded*:
every branch in `BRANCHES` is written out by hand as a Z3 formula over the input
bytes. That hand-recording is exactly the work a concolic engine automates -- it
instruments the compiled program so each branch adds its condition to the path on
its own, with no table to maintain by hand.

The limit follows from the same mechanism. The loop can only reason about
conditions it has recorded. A branch whose value is computed by code the engine
did not instrument -- for instance a library routine it does not trace -- never
enters the path condition, so the solver cannot flip it. In this toy everything
sits in one file and is recorded. In a real converter the digit fields are turned
into integers by library routines, and whether those routines are traced decides
whether the solver can see the reconciliation arithmetic at all. That is the
question to take to the real converter next.
