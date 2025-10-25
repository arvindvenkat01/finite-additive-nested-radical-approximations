# Finite Nested Radical Approximations to Mathematical Constants

This repository contains the full computational artifact for the paper, *"A Complexity-Aware Analysis of Finite Nested Radical Approximations to Mathematical Constants"*. It includes the search algorithms used to discover the approximations and the analysis script to reproduce the final results table.

## Abstract

We perform a systematic, complexity-aware search for finite nested radical approximations to fundamental mathematical constants such as $\pi$ and $e$. By defining a novel efficiency metric—the ratio of correct digits to the descriptive complexity of the coefficients—we identify several highly efficient, non-trivial approximations. Our key finding is a depth-5 nested radical for $\pi$ that is more efficient than both the well-known continued fraction approximation 355/113 and the "trivial" zero-tail baseline, demonstrating that structured, non-obvious integer coefficients can yield surprisingly compact and accurate formulas.

## Repository Structure

The research process is separated into three stages, represented by the three main Python scripts in this repository:

1.  **`01_search_exploratory_dfs.py`**
    *   **Purpose:** The initial "scout" algorithm. This is a fast, `numba`-accelerated Depth-First Search (DFS) that uses standard `float64` precision. It is designed to quickly scan the search space for promising candidate regions and low-to-medium accuracy approximations.

2.  **`02_search_high_precision_beam.py`**
    *   **Purpose:** The primary "discovery engine." This script implements a high-precision beam search using the `mpmath` library. Its arbitrary-precision arithmetic is essential for discovering and verifying the high-accuracy "star formulas" (12+ correct digits) that are the centerpiece of the paper. This script found the key results discussed in our work.

3.  **`03_analysis_and_tablegen.py`**
    *   **Purpose:** The final analysis and verification script. This tool takes a hard-coded list of the best coefficients discovered by the search scripts (`01` and `02`), computes their final metrics (complexity `L`, accuracy `D`, and efficiency `D/L`), compares them against baselines (zero-tail and continued fractions), and generates the final results table from the paper.

## How to Reproduce Results

### Prerequisites

*   Python `3.12.x`
*   All required libraries, specified in `requirements.txt`

### Workflow

1.  **Set up the environment:**
    Create a virtual environment and install the exact dependencies.
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

### Workflow

1.  **Exploratory Search (Optional):** To see how initial candidates were found, you can run the fast DFS script.
    ```
    python 01_search_exploratory_dfs.py
    ```

2.  **High-Precision Search (Optional):** To run the full, high-precision discovery process that found the paper's main results, you can run the beam search script. (Note: This can be time-consuming).
    ```
    python 02_search_high_precision_beam.py
    ```

3.  **Reproduce Paper's Main Table (Recommended):** To verify the final results and generate the exact table from the paper, you only need to run the final analysis script. This script uses the pre-discovered "star formulas" as its input.
    ```
    python 03_analysis_and_tablegen.py
    ```
This will produce the comprehensive results table, verifying the complexity, accuracy, and efficiency of each approximation discussed in the paper.

