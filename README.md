<div align="center">

# PI-FINDER 🔎π

**Find number patterns inside the digits of π.**

A Python project for searching digit sequences and encoded words in a growing local π dataset.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Early%20Development-orange)

*Find it in π.*

</div>

---

## 🔢 What can it search?

- **Numbers:** search a digit sequence directly.
- **Words:** encode A–Z as fixed-width numbers (A = 01, …, Z = 26), then search the resulting digit sequence.

Both modes use the same core search engine.

## ✨ Features

- Search within a local π dataset.
- Generate additional π digits when a pattern is not found.
- Grow the persistent dataset manually or automatically.
- Inspect database size, digit count, and update information.
- Check basic dataset structure and known π prefix.
- Run benchmarks and view search statistics.
- Use a terminal-based interactive menu.

## ⚡ Quick start

```bash
git clone https://github.com/whiteby4e/PI-FINDER.git
cd PI-FINDER
python pi_finder.py
```

Use the menu to search a number or word, generate more digits, run a benchmark, or inspect the local database.

## 🔍 Example: word encoding

The project uses fixed-width A1Z26 encoding:

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
  ↓
Search this sequence in π
```

## 💾 The π dataset

The repository includes a starting dataset of approximately **1.13 million decimal digits** in `pi.txt`. This is not a complete or infinite database.

If a pattern is not found, the automatic search can grow the local dataset, doubling its size up to the current configured safety limit of **10 million digits**. If `pi.txt` is missing, the program can generate an initial dataset.

The database tools can also continue generation manually.

## 🧪 Benchmarks and tests

Run the search-engine tests:

```bash
python -m unittest discover -s tests
```

Benchmark scripts are provided in the repository:

- `benchmark.py`
- `benchmark_search.py`

Benchmark results depend on hardware, Python version, and dataset size. Use the scripts to measure your own machine rather than treating one result as universal.

## 🧠 Important mathematical note

π has infinitely many decimal digits, but any computer search can inspect only a finite dataset at a time.

**NOT FOUND does not mean a sequence never occurs anywhere in π.** It only means the sequence was not found in the digits currently searched.

It has also not been proven that π contains every possible finite digit sequence; the normality of π in base 10 remains unproven.

## 🧱 Project structure

```text
PI-FINDER/
├── pi_finder.py
├── pi_search.py
├── search_engine.py
├── generate_pi.py
├── benchmark.py
├── benchmark_search.py
├── pi.txt
└── tests/
```

## 📄 License

MIT — see [LICENSE](LICENSE).
