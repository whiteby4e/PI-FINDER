# PI-FINDER 🔎π

A high-performance tool for searching numbers and encoded words inside the digits of **π (pi)**.

> **Status:** 🚧 Early development — core search, generation, benchmarks, word search, and the text interface are implemented.

## What is PI-FINDER?

PI-FINDER is an open-source project designed to search for:

- 🔢 **Numbers** — find a numeric sequence inside the digits of π.
- 🔤 **Words** — encode a word into digits and search for the resulting sequence in π.

The project is being designed around one main goal:

> **Search as fast as possible, while keeping the system practical for large amounts of π data.**

## How it works

PI-FINDER is planned as separate components:

```text
PI-FINDER
│
├── π ENGINE
│   ├── Generate π
│   └── Load existing π data
│
├── STORAGE
│   └── Manage large π datasets
│
├── SEARCH ENGINE
│   └── Fast pattern searching
│
├── WORD ENCODER
│   └── Convert words → digit sequences
│
└── USER INTERFACE
    └── Search results & controls
```

The **Number** and **Word** modes will eventually use the same core search engine. Word mode only needs to convert its input into digits before searching.

## Search modes

### Number Mode

Example:

```text
Input: 123456789
Result: Found
Position: ...
```

The position refers to the location of the sequence within the searched digits of π.

### Word Mode

A word can be converted to a fixed-width numeric representation.

For example, using two-digit A1Z26 encoding:

```text
A = 01
B = 02
...
Z = 26

HELLO
↓
08 05 12 12 15
↓
0805121215
```

The encoded sequence can then be searched using the same search engine as Number Mode.


## Interactive interface

Run:

```text
py pi_finder.py
```

The main menu provides:

1. **Search number** — search digits in the current `pi.txt`.
2. **Search word** — encode A-Z with fixed-width A1Z26 and search the result.
3. **Generate pi** — generate a new `pi.txt` dataset from a chosen number of digits.
4. **Benchmark** — measure search time, throughput, and Python-traced peak allocations.
5. **Admin mode** — a hidden Easter egg.
6. **Exit**

The Admin mode is intentionally a joke feature and is not part of the search engine.

## Important note about π

π has infinitely many decimal digits, but a computer can only search a finite amount at a time.

Therefore, PI-FINDER will report results within the **searched range**.

For example:

```text
FOUND
Position: 483,291

NOT FOUND
Searched: 100,000,000 digits
```

**NOT FOUND does not mean that the sequence never occurs anywhere in π.**

It is also not currently proven that π contains every possible finite digit sequence, because the normality of π in base 10 has not been proven.

## Performance

Performance is a core part of this project.

Before choosing the final search algorithm, PI-FINDER will benchmark different approaches using the same π datasets.

Planned benchmark sizes:

- 1 MB
- 10 MB
- 100 MB
- 1 GB
- Larger datasets when practical

Metrics will include:

- Search speed
- π generation speed
- Memory usage
- CPU usage
- Dataset loading speed
- Repeated-query performance

The project will prefer measured performance over assumptions about which algorithm is theoretically fastest.

## Planned architecture

### Phase 1 — Search Engine

Build and benchmark the core digit-search system.

### Phase 2 — π Data

Add efficient generation/loading and chunked storage for large π datasets.

### Phase 3 — Word Encoding

Add word-to-number encodings and integrate them with the search engine.

### Phase 4 — Optimization

Improve performance for both single searches and repeated searches.

### Phase 5 — User Interface

Build a clean interface for searching numbers and words.

## Project goals

- ⚡ Fast searching
- 💾 Efficient storage
- 🧠 Memory-aware architecture
- 🔢 Large π datasets
- 🔤 Number and word searching
- 📊 Reproducible performance benchmarks
- 🐍 Python-friendly development, with faster compiled components where useful

## License

PI-FINDER is released under the **MIT License**.

---

**PI-FINDER**  
*Find it in π.*