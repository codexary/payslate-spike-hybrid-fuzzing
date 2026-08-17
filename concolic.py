#!/usr/bin/env python3
"""A minimal concolic loop over a toy batch check.

The toy input is ten bytes that mirror the converter's fields:

    marker 'H' | amount1 (3 digits) | amount2 (3 digits) | declared total (3 digits)

and the check passes five branches in order -- the marker is 'H', each of the
three numeric fields is all decimal digits, and the declared total equals the sum
of the two amounts:

    marker        : byte 0 == 'H'
    amount1 digits: each of its bytes in '0'..'9'   (likewise amount2, total)
    reconciles    : int(total) == int(amount1) + int(amount2)

The loop runs the check on a concrete input and records, by hand, the Z3
condition of each branch it took -- the work a concolic engine such as SymCC does
by instrumenting the program. It then negates the last branch it has not yet
flipped, asks Z3 for an input that goes the other way, and runs again. Crossing
the reconciles branch means solving `total == amount1 + amount2` over the digits
in one step -- what blind byte mutation almost never manages, because a mutated
byte is a decimal digit only ten times in 256 and the three-digit total must land
exactly on the sum (compare.py measures that).

Run:  python3 concolic.py
"""
import z3

MARKER = ord("H")
A1, A2, TOT = range(1, 4), range(4, 7), range(7, 10)  # byte positions of each field

# One integer per input byte (0..255). Z3 Ints keep the amount arithmetic exact.
B = [z3.Int(f"b{i}") for i in range(10)]


def _digits_ok(idx):
    return z3.And(*[z3.And(B[i] >= ord("0"), B[i] <= ord("9")) for i in idx])


def _value(idx):
    v = 0
    for i in idx:
        v = v * 10 + (B[i] - ord("0"))
    return v


# The branches, in the order the check evaluates them, each paired with the Z3
# predicate that holds when the check passes it. Recorded by hand: this is the
# instrumentation a concolic engine would insert.
BRANCHES = [
    ("marker",         B[0] == MARKER),
    ("amount1 digits", _digits_ok(A1)),
    ("amount2 digits", _digits_ok(A2)),
    ("total digits",   _digits_ok(TOT)),
    ("reconciles",     _value(TOT) == _value(A1) + _value(A2)),
]


def _num(data, idx):
    return int(bytes(data[i] for i in idx))


def run(data):
    """Execute the toy check concretely on a 10-byte input. Return
    (accepted, passed, reason); `passed` is how many leading branches held, so a
    rejected input stopped at branch index `passed`. Mirrors BRANCHES exactly."""
    digit = lambda i: ord("0") <= data[i] <= ord("9")
    if data[0] != MARKER:               return (False, 0, "bad marker")
    if not all(digit(i) for i in A1):   return (False, 1, "amount 1 not all digits")
    if not all(digit(i) for i in A2):   return (False, 2, "amount 2 not all digits")
    if not all(digit(i) for i in TOT):  return (False, 3, "total not all digits")
    if _num(data, TOT) != _num(data, A1) + _num(data, A2):
        return (False, 4, "does not reconcile")
    return (True, 5, "accepted")


def show(data):
    try:
        return "%c|%s|%s|%s" % (data[0], bytes(data[i] for i in A1).decode(),
                                bytes(data[i] for i in A2).decode(),
                                bytes(data[i] for i in TOT).decode())
    except (UnicodeDecodeError, ValueError):
        return bytes(data).hex()


def solve(passed, seed):
    """Ask Z3 for a 10-byte input that passes branches 0..passed (so the branch
    the run stopped at is flipped to pass) and whose amounts differ from the
    seed's, so the loop makes progress toward genuinely new amounts."""
    s = z3.Solver()
    for b in B:
        s.add(b >= 0, b <= 255)
    for i in range(passed + 1):
        s.add(BRANCHES[i][1])
    s.add(z3.Or(_value(A1) != _num(seed, A1), _value(A2) != _num(seed, A2)))
    s.add(_value(A1) >= 1, _value(A2) >= 1)  # a non-trivial split, not all zeros
    if s.check() != z3.sat:
        return None
    m = s.model()
    return [m[b].as_long() for b in B]


def concolic(seed, max_rounds=8):
    data = list(seed)
    print("seed", show(data))
    for rnd in range(1, max_rounds + 1):
        accepted, passed, reason = run(data)
        print(f"round {rnd}: {show(data)} -> passed {passed}/5, {reason}")
        if accepted:
            print(f"accepted after {rnd} round(s): amounts {_num(data, A1)} + "
                  f"{_num(data, A2)} = {_num(data, TOT)} "
                  f"(seed amounts {_num(seed, A1)}, {_num(seed, A2)})")
            return data
        nxt = solve(passed, seed)
        if nxt is None:
            print(f"round {rnd}: no input flips '{BRANCHES[passed][0]}'")
            return None
        print(f"round {rnd}: flip '{BRANCHES[passed][0]}' -> Z3 gives {show(nxt)}")
        data = nxt
    print("gave up without reaching the gate")
    return None


# A seed that passes the marker and digit checks but fails the gate: amounts
# 010 and 020 do not add up to the declared total 099.
SEED = list(b"H010020099")

if __name__ == "__main__":
    concolic(SEED)
