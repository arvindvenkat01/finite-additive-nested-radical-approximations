# Finite Nested Radical Approximations to Mathematical Constants

**Reproducible computational artifact for the paper:**  
*"Finite Nested Radical Approximations to Mathematical Constants: A Complexity-Aware Computational Search"*



## Overview

This repository contains a systematic computational search for finite nested radical approximations to the mathematical constants π, e, and φ (golden ratio). Using a backward-squaring depth-first search algorithm with high-precision verification (200-300 decimal digits), we discover approximations achieving **12-17 correct decimal digits** at depths 3-6.

### Key Results

**Efficiency comparable to classical benchmarks:**
- π depth-4: `√(0 + √(52 + √(1889 + √29924)))` achieves **12.4 digits** with **E ≈ 0.39 digits/bit** — matching the efficiency of the celebrated continued fraction 355/113
- φ depth-3: `√(0 + √(0 + √47))` achieves **E ≈ 0.72 digits/bit** at minimal bit budget

**Structured approximations exceed zero-tail baselines:**
- At fixed depth k=5 for π, our approximation achieves E ≈ 0.39, exceeding the zero-tail rounding baseline (E ≈ 0.32) by 18%

**Emergent near-perfect-square structure:**
- Coefficients naturally cluster near perfect squares (e.g., 49=7², 2276≈47²) as an emergent property of the backward-squaring algorithm

---

## Quick Start

### Prerequisites
```bash
# Python 3.12+ recommended
python --version

# Install dependencies
pip install -r requirements.txt
```

### Running the Search

```bash
# 1. Run the main search (finds all approximations)
python 01_nested_radical_search.py

# Output: Comprehensive results for π, e, φ at depths 3-6
# Runtime: ~5-10 minutes on modern hardware
```

```bash
# 2. Run the analysis (zero-tail comparison)
python 02_analysis_and_comparison.py

# Output: Depth-matched efficiency comparisons
# Shows which approximations beat zero-tail baseline
```

---

## Repository Structure

```
finite-nested-radical-approximations/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── 01_nested_radical_search.py         # Main search algorithm
├── 02_analysis_and_comparison.py       # Zero-tail baseline analysis
├── results/                            # Cached search outputs
    ├── search_output_full.txt
    └── analysis_comparison.txt

```

---

## Scripts Description

### `01_nested_radical_search.py`
**Main search algorithm** using backward-squaring DFS with Numba JIT compilation.

**Features:**
- Exhaustive search within configurable windows (Δ = 60, 80, 100, 150, 200)
- High-precision verification (200-300 decimal digits via mpmath)
- Complexity-aware efficiency metric: **E = D/L** (digits per bit)
- Dual reporting: best by accuracy AND best by efficiency

**Key Algorithm:**
```
y₁ = τ² - a₁ ≥ 0
y₂ = y₁² - a₂ ≥ 0
...
aₖ = round(y²ₖ₋₁)
```

**Output:** Complete results for all targets at depths 3-6, sorted by efficiency.

---

### `02_analysis_and_comparison.py`
**Zero-tail baseline comparison** for depth-matched efficiency analysis.

**Features:**
- Computes zero-tail baselines: `[0, 0, ..., 0, round(τ^(2^k))]`
- Depth-matched comparisons (same k)
- Efficiency frontier analysis
- Clear winner indicators

**Key Metric:**
```
L = Σ log₂(1 + |aᵢ|)  (descriptive complexity in bits)
D = -log₁₀|τ - τ̂|    (digits-of-accuracy score)
E = D / L             (efficiency in digits per bit)
```

**Output:** Grouped comparison tables showing which approximations exceed zero-tail efficiency.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **mpmath** | 1.3.0 | High-precision arithmetic (200-300 digits) |
| **numpy** | 2.0.2 | Array operations for Numba nopython mode |
| **numba** | 0.60.0 | JIT compilation for 50-100× speedup |

**Note:** `pandas` was removed in the final version (no longer required).

---

## Reproducibility

All results are **fully deterministic** and reproducible:

✅ **Fixed search parameters:**
- Depth k ∈ {3, 4, 5, 6}
- Window sizes Δ ∈ {60, 80, 100, 150, 200}
- Depth-first enumeration order (centered around ⌊r²⌋)
- No randomization

✅ **High-precision verification:**
- All approximations verified at ≥200 decimal digits
- Auto-scales to 300 digits when errors approach underflow
- No floating-point artifacts

✅ **Complete artifact:**
- All scripts and dependencies specified
- Cached results provided for verification
- Deterministic search order documented

---

## Key Findings

### 1. Efficiency Comparable to Classical Benchmarks

Our depth-4 approximation for π achieves **E ≈ 0.39 digits/bit**, matching the efficiency of the classical continued fraction convergent 355/113. This demonstrates that computationally discovered nested radicals can be competitive with historically significant rational approximations.

### 2. Structured Approximations Exceed Zero-Tail

At depth k=5 for π, our structured nested radical:
```
√(0 + √(49 + √(2276 + √(4500 + √2320))))
```
achieves **E ≈ 0.39**, exceeding the zero-tail rounding baseline (E ≈ 0.32) at the same depth. This demonstrates non-trivial structure beyond simple high-power rounding.

### 3. Emergent Near-Perfect-Square Structure

Discovered coefficients exhibit a striking pattern — they cluster near perfect squares as an **emergent computational property** of the backward-squaring algorithm:

**Example (π depth-5):**
- a₂ = 49 = 7² (exactly)
- a₃ = 2276 ≈ 47.7² ≈ 47² + 67
- a₄ = 4500 ≈ 67.1² ≈ 67² + 11
- a₅ = 2320 ≈ 48.2² ≈ 48² + 16

This is not a mystical property of π, but rather a consequence of centering search intervals around ⌊r²⌋ at each level.

### 4. Efficiency vs. Accuracy Trade-offs

The golden ratio φ provides a striking example: the depth-3 approximation achieves **E ≈ 0.72** at only 5.6 bits with 4 correct digits, while the depth-6 approximation achieves 15.3 digits but with lower efficiency (E ≈ 0.37) at 41.7 bits. When coefficient complexity matters, shallower formulas can be more elegant solutions.

---

## Citation

If you use this code or results in your research, please cite:

```bibtex
@article{venkat2025nested,
  title={Finite Nested Radical Approximations to Mathematical Constants: 
         A Complexity-Aware Computational Search},
  author={Venkat, Arvind N.},
  journal={[Journal Name]},
  year={2025},
  note={Reproducible artifact: https://github.com/arvindvenkat01/finite-nested-radical-approximations}
}
```

---

## Star Results Reference

For quick reference, here are the top approximations found:

### π (Pi)
- **Depth 4:** `[0, 52, 1889, 29924]` → 12.4 digits, E=0.392
- **Depth 5:** `[0, 49, 2276, 4500, 2320]` → 15.6 digits, E=0.388
- **Depth 6:** `[1, 1, 5945, 7635, 1554, 9186]` → 16.6 digits, E=0.325

### e (Euler's number)
- **Depth 3:** `[0, 10, 1989]` → 6.2 digits, E=0.427
- **Depth 4:** `[0, 8, 2028, 20560]` → 10.8 digits, E=0.379
- **Depth 5:** `[1, 30, 36, 6389, 33807]` → 15.0 digits, E=0.387
- **Depth 6:** `[0, 0, 2780, 40193, 36413, 12323]` → 17.2 digits, E=0.310

### φ (Golden ratio)
- **Depth 3:** `[0, 0, 47]` → 4.0 digits, **E=0.723**
- **Depth 4:** `[0, 0, 0, 2207]` → 7.7 digits, E=0.692
- **Depth 5:** `[0, 1, 12, 332, 26888]` → 10.6 digits, E=0.383
- **Depth 6:** `[0, 0, 9, 1309, 17665, 15862]` → 15.3 digits, E=0.366

**Decoding:** `[a₁, a₂, ..., aₖ]` represents `√(a₁ + √(a₂ + ... + √aₖ))`

---

## Performance Notes

**Runtime (on modern hardware):**
- Depth 3-4: ~1-5 seconds per configuration
- Depth 5: ~10-60 seconds per configuration
- Depth 6: ~1-5 minutes per configuration
- Full suite (all targets, all depths, all configs): ~5-10 minutes

**Speedup from Numba:**
- 50-100× faster than pure Python
- Nopython mode with NumPy arrays ensures maximum performance

**Memory:**
- Typical usage: <500 MB
- No special memory requirements

---

## Contributing

This is a research artifact accompanying a published paper. For questions, corrections, or extensions:

1. **Open an issue** for bugs or clarifications
2. **Contact the author** for collaboration opportunities
3. **Fork and extend** for your own research (cite the original paper)

---

## License

MIT License - see LICENSE file for details.
Copyright (c) 2025 Arvind N. Venkat

---

## Acknowledgments

Computational discovery was performed using Google Colaboratory. We gratefully acknowledge the developers of:
- **mpmath** (arbitrary-precision arithmetic)
- **numba** (JIT compilation)
- **numpy** (array operations)

The backward-squaring search heuristic is a natural generalization of classical continued fraction convergent methods, adapted here for nested radicals.

---

## Contact

**Arvind N. Venkat**  
Independent Researcher  
📧 arvind.venkat01@gmail.com  
🔗 GitHub: [@arvindvenkat01](https://github.com/arvindvenkat01)

---

*Last updated: Oct 2025*




