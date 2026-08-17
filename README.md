English | [简体中文](README.zh-CN.md)

# payslate-spike-hybrid-fuzzing

A short spike: build a minimal concolic loop over a toy batch check and watch it
cross a sum-equality gate. The point is to see, on something small enough to read
in full, what a concolic engine (SymCC) automates before wiring one up against the
real converter.

`concolic.py` runs a ten-byte toy check -- a marker byte, two three-digit amount
fields, and a three-digit declared total that must equal their sum -- records
each branch condition it takes as a Z3 formula by hand, negates the last branch,
asks Z3 for an input that goes the other way, and runs again. Flipping the
sum-equality branch is what carries it across the gate.

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python3 concolic.py
```

## About this repository

Elsworne, Payslate and the team are fictional.

The code and documents in this repository were written with the help of AI tools; every recorded output comes from actually running them.
