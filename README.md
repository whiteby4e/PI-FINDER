# PI-FINDER 🔎π

A high-performance tool for searching numbers and encoded words inside the digits of **π (pi)**.

> **Status:** 🚧 Early development — core search, generation, benchmarks, word search, automatic dataset growth, and the text interface are implemented.

## What is PI-FINDER?

PI-FINDER is an open-source project designed to search for:

- 🔢 **Numbers** — find a numeric sequence inside the digits of π.
- 🔤 **Words** — encode a word into digits and search for the resulting sequence in π.

> **Search as fast as possible, while keeping the system practical for large amounts of π data.**

## Current π Dataset

The repository currently includes a π dataset of approximately **157 KB**, containing about **160,000 decimal digits**.

~~~text
pi.txt
├── Size: ~157 KB
└── Digits: ~160,000
~~~

The dataset is stored as a single sequential text file and can be searched in chunks, so the whole dataset does not need to be loaded into RAM at once.

The dataset can also grow automatically when a search does not find the requested pattern.

## How it works

~~~text
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
~~~

The **Number** and **Word** modes use the same core search engine. Word mode only converts its input into digits before searching.

## Search modes

### Number Mode

~~~text
Input: 123456789
Result: Found
Position: ...
~~~

### Word Mode

A word can be converted to a fixed-width numeric representation.

~~~text
A = 01
B = 02
...
Z = 26

HELLO
↓
08 05 12 12 15
↓
0805121215
~~~

The encoded sequence is then searched using the same search engine as Number Mode.

## Automatic π generation

When Number Mode or Word Mode does not find a pattern in the current `pi.txt`, PI-FINDER automatically generates a larger π dataset and searches again.

~~~text
Enter number: 123456789

Searching 100,000 pi digits...
Not found in the current number dataset.
Generating pi to 200,000 digits...

Searching 200,000 pi digits...
FOUND!
Position: ...
~~~

If `pi.txt` does not exist, PI-FINDER starts by generating a default dataset of **100,000 digits**.

The automatic search currently doubles the dataset size when it needs to grow, up to a safety limit of **10,000,000 digits**.

## Interactive interface

Run `py pi_finder.py`.

The main menu provides:

1. **Search number** — search digits in `pi.txt`, automatically generating more π if needed.
2. **Search word** — encode A-Z with fixed-width A1Z26 and automatically generate more π if needed.
3. **Generate pi** — generate a new `pi.txt` dataset from a chosen number of digits.
4. **Benchmark** — measure search time, throughput, and Python-traced peak allocations.
5. **Admin mode** — a joke Easter egg.
6. **Exit**

## Important note about π

π has infinitely many decimal digits, but a computer can only search a finite amount at a time.

**NOT FOUND does not mean that the sequence never occurs anywhere in π.**

It is also not currently proven that π contains every possible finite digit sequence, because the normality of π in base 10 has not been proven.

## Performance

Performance is a core part of this project.

Planned benchmark sizes:
- 1 MB
- 10 MB
- 100 MB
- 1 GB
- Larger datasets when practical

Metrics include search speed, π generation speed, memory usage, CPU usage, dataset loading speed, and repeated-query performance.

## Project goals

- ⚡ Fast searching
- 💾 Efficient storage
- 🧠 Memory-aware architecture
- 🔢 Large π datasets
- 🔤 Number and word searching
- 🤖 Automatic π dataset generation
- 📊 Reproducible performance benchmarks
- 🐍 Python-friendly development, with faster compiled components where useful

## License

PI-FINDER is released under the **MIT License**.

---

**PI-FINDER**  
*Find it in π.*