# Myers Diff Algorithm

A lightweight Python implementation of the **Myers Difference Algorithm** for comparing text sequences and identifying additions, deletions, and unchanged content.

The project focuses on implementing the core Myers diff algorithm from scratch and validating its behavior against configuration files, plain-text documents, and Unicode content.

---

## Overview

The **Myers Diff Algorithm** is a shortest-edit-script algorithm used to determine the smallest sequence of insertions and deletions required to transform one sequence into another.

This implementation compares two text files line by line and produces a readable diff showing:

* `+` — Added line
* `-` — Removed line
* ` ` — Unchanged line

The implementation is designed to be simple, readable, and easy to test with different types of text input.

---

## Features

* Myers shortest-edit-script algorithm
* Line-by-line text comparison
* Detection of additions and deletions
* Preservation of unchanged lines
* UTF-8 / Unicode text support
* Simple command-line execution
* Sample files for different comparison scenarios
* TOML-based project configuration
* No external runtime dependencies

---

## Project Structure

```text
myers-diff-algorithm/
│
├── .gitignore
├── README.md
├── myers.toml
│
├── samples/
│   ├── config_new.txt
│   ├── config_old.txt
│   ├── paper_new.txt
│   ├── paper_old.txt
│   ├── unicode_new.txt
│   └── unicode_old.txt
│
└── src/
    └── main.py
```

### Directory Description

| Path          | Description                                             |
| ------------- | ------------------------------------------------------- |
| `src/main.py` | Core Myers diff implementation                          |
| `myers.toml`  | Project and diff configuration                          |
| `samples/`    | Input files used for testing                            |
| `.gitignore`  | Git files and directories excluded from version control |
| `README.md`   | Project documentation                                   |

---

## How the Algorithm Works

Myers Diff models the comparison of two sequences as a path through an **edit graph**.

For two sequences:

```text
Old → A B C D
New → A B X C D
```

The algorithm searches for the shortest edit path between the two sequences.

In this example, the required change is:

```text
 A
 B
+X
 C
 D
```

The implementation maintains diagonal paths and records the furthest reachable position for each edit distance. Once the end of both sequences is reached, the recorded trace is used to reconstruct the final edit script.

### Complexity

For sequences of lengths `N` and `M`, the Myers algorithm is commonly described with:

* **Time:** `O((N + M)D)`
* **Space:** `O(N + M)`

where `D` represents the size of the shortest edit script.

---

## Requirements

* Python 3.9 or later
* Git

No third-party Python packages are required for the core implementation.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/VIVEK342004/myers-diff-algorithm.git
```

Move into the project directory:

```bash
cd myers-diff-algorithm
```

Verify Python:

```bash
python --version
```

---

## Running the Project

The default comparison uses:

```text
samples/paper_old.txt
samples/paper_new.txt
```

Run:

```bash
python src/main.py
```

Example output:

```text
Comparing: samples/paper_old.txt
      with: samples/paper_new.txt
--------------------------------------------------
  Myers diff is an algorithm for comparing sequences.
- It finds a shortest edit sequence.
+ It finds a shortest edit sequence efficiently.
  The algorithm is useful for text comparison.
  It can identify inserted and deleted lines.
+ It is commonly used in version control systems.
```

The exact output depends on the contents of the sample files.

---

## Testing Different Samples

### Configuration Files

Compare:

```text
samples/config_old.txt
samples/config_new.txt
```

Run:

```bash
python -c "from src.main import diff_files, print_diff; print_diff(diff_files('samples/config_old.txt', 'samples/config_new.txt'))"
```

---

### Paper/Text Files

Compare:

```text
samples/paper_old.txt
samples/paper_new.txt
```

Run:

```bash
python -c "from src.main import diff_files, print_diff; print_diff(diff_files('samples/paper_old.txt', 'samples/paper_new.txt'))"
```

---

### Unicode Files

The project also includes Unicode test cases containing multiple writing systems.

Compare:

```text
samples/unicode_old.txt
samples/unicode_new.txt
```

Run:

```bash
python -c "from src.main import diff_files, print_diff; print_diff(diff_files('samples/unicode_old.txt', 'samples/unicode_new.txt'))"
```

This verifies that the implementation can process UTF-8 text correctly.

---

## Configuration

Project configuration is stored in:

```text
myers.toml
```

Current configuration:

```toml
[diff]
algorithm = "myers"
ignore_whitespace = false
ignore_case = false

[output]
show_context = true
context_lines = 3
```

The configuration documents the intended comparison behavior and output settings for the project.

---

## Output Format

Each result contains an operation marker and the corresponding line.

### Unchanged

```text
  existing line
```

### Deleted

```text
- old line
```

### Added

```text
+ new line
```

This format makes changes easy to inspect from a terminal.

---

## Design Goals

The project is intentionally kept lightweight and focused on the core algorithm.

The primary goals are:

1. Implement Myers diff without relying on external diff libraries.
2. Keep the algorithm readable and understandable.
3. Support normal text as well as Unicode input.
4. Provide reproducible sample inputs.
5. Keep the project structure simple.
6. Make the implementation easy to extend for future features.

---

## Limitations

The current implementation is intentionally minimal.

It currently:

* Compares files line by line.
* Does not provide a graphical interface.
* Does not provide side-by-side diff visualization.
* Does not implement advanced whitespace normalization.
* Does not expose a full command-line argument parser.
* Uses the sample paths configured in `main()` for the default run.

These limitations leave room for future improvements without complicating the core implementation.

---

## Possible Future Improvements

Potential extensions include:

* Command-line arguments for selecting input files.
* Unified diff output.
* Side-by-side comparison.
* Configurable whitespace handling.
* Case-insensitive comparison.
* Directory comparison.
* Automated unit tests.
* Performance benchmarking.
* Rich terminal output.
* Packaging the implementation as a reusable Python module.

---

## Development Workflow

Changes are developed incrementally and committed to Git after meaningful implementation steps.

Example workflow:

```bash
git add .
git commit -m "Implement Myers diff algorithm"
git push
```

Example development commits include:

```text
Add gitignore for Python project
Add diff configuration
Implement Myers diff algorithm
Add configuration diff samples
Add text diff samples
Add unicode diff samples
Verify diff behavior with sample files
```

---

## Verification

Before pushing changes, the project can be checked with:

```bash
python src/main.py
```

and the repository state can be verified using:

```bash
git status
```

A clean working tree should report:

```text
nothing to commit, working tree clean
```

---

## License

This project is intended for educational and development purposes.

A specific open-source license can be added in the future depending on the intended distribution of the project.

---

## Author

**Vivek Kumar**

GitHub: [VIVEK342004](https://github.com/VIVEK342004)

Repository:

`https://github.com/VIVEK342004/myers-diff-algorithm`
