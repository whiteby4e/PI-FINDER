# PI-FINDER 🔎π

A high-performance tool for searching numbers and encoded words inside the digits of **π (pi)**.

> **Status:** 🚧 Early development — core search, generation, benchmarks, word search, automatic dataset growth, persistent database management, and the text interface are implemented.

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

**This is NOT the main or complete π database.** It is the dataset currently included with the project and is mainly provided as a starting point.

You can increase the dataset size manually, use the persistent database tools to grow it, or let the program increase it automatically when a searched number or word is not found.

## How it works

~~~text
PI-FINDER
│
├── π ENGINE
│   ├── Generate π
│   └── Load existing π data
│
├── STORAGE
│   └── Manage persistent π dataset
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

You can also manually generate a larger dataset whenever you want.

## Level 11 — Persistent π Database

PI-FINDER now has a dedicated database management menu for the persistent `pi.txt` dataset.

### Database Info

Shows:

- Current number of π digits
- File size
- Last update time
- Current database path
- Progress toward the automatic 10-million-digit limit

Example:

~~~text
PI-FINDER DATABASE
--------------------------------
Status:      AVAILABLE
Database:    pi.txt
Digits:      160,000
File size:   157 KB
Last update: ...
Progress:    [....................] 160,000/10,000,000
~~~

### Continue Generation

The database can be expanded with **Continue generation (2x)**.

For example:

~~~text
160,000
   ↓
320,000
   ↓
640,000
   ↓
1,280,000
   ↓
...
~~~

This uses the current database size and grows it up to the automatic generation limit.

### Search Statistics

Searches now report statistics such as:

~~~text
Search Statistics
--------------------------------
Search:     1609
Position:   396
Dataset:    160,090 digits
Time:       0.0032 s
~~~

For automatic searches, the reported time covers the complete search operation, including any additional π generation required.

### Database Integrity

The database manager can check whether `pi.txt`:

- Exists
- Has the expected `3.<decimal digits>` structure
- Starts with the known decimal prefix of π
- Contains only decimal digits after the decimal point

Example:

~~~text
Database integrity: OK
Checked: 160,002 characters
Format: 3.<decimal digits>
~~~

This is a structural integrity check; it does not mathematically prove every stored digit is correct.

## Interactive interface

Run `py pi_finder.py`.

The main menu provides:

1. **Search number** — search digits in `pi.txt`, automatically generating more π if needed.
2. **Search word** — encode A-Z with fixed-width A1Z26 and automatically generate more π if needed.
3. **Generate pi** — generate a new `pi.txt` dataset from a chosen number of digits.
4. **Benchmark** — measure search time, throughput, and Python-traced peak allocations.
5. **PI Database** — inspect, grow, and validate the persistent π dataset.
6. **Admin mode** — a joke Easter egg.
7. **Exit**

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
- 🗄️ Persistent π database management
- 🔍 Database integrity checking
- 📊 Reproducible performance benchmarks
- 🐍 Python-friendly development, with faster compiled components where useful

## License

PI-FINDER is released under the **MIT License**.

---

**PI-FINDER**  
*Find it in π.*