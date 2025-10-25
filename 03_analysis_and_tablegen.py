# MIT License
# Copyright (c) 2025 Arvind N. Venkat
# Permission is hereby granted, free of charge...

!pip install mpmath pandas

import pandas as pd
from mpmath import mp

# --- Precision and Target Setup ---
mp.dps = 200
PI = mp.pi
E = mp.e

# --- Core Functions from Critique ---

def description_length(coeffs):
    """Calculates the descriptive complexity (total bit-length) of the coefficients."""
    if not coeffs:
        return 0
    return mp.fsum([mp.log(1 + a, 2) for a in coeffs])

def zero_tail_baseline(target, depth):
    """Calculates the 'trivial' zero-tail approximation for a given depth."""
    power_of_2 = 2**depth
    target_powered = target**power_of_2
    n = mp.nint(target_powered)
    approx_val = n**(mp.mpf(1)/power_of_2)
    error = abs(target - approx_val)
    return {
        "description": f"Round({target.name}**{power_of_2})",
        "coeffs": [int(n)],
        "approx_val": approx_val,
        "error": error,
        "complexity": description_length([n])
    }

# --- Helper Functions ---

def eval_nested(coeffs):
    """Evaluates a nested radical from a list of coefficients."""
    v = mp.mpf(0)
    for a in reversed(coeffs):
        v = mp.sqrt(v + a)
    return v

def get_correct_digits(target, approx_val):
    """Calculates the number of correct digits."""
    error = abs(target - approx_val)
    if error == 0:
        return mp.inf
    return mp.floor(-mp.log(error, 10))
    
# --- Main Analysis ---

results_to_analyze = [
    ("π", PI, "Type II", 5, [2, 6, 3081, 2193, 1493]),
    ("π", PI, "Type II", 4, [0, 46, 2586, 3237]),
    ("e", E, "Type II", 5, [2, 11, 304, 408, 2995]),
    ("e", E, "Type II", 4, [0, 33, 410, 3190]),
    ("π", PI, "Type I", 4, [3, 44, 2, 67]),
    ("π", PI, "CF", None, [355, 113]),

     # The new, interesting Depth-6 results
    ("π", mp.pi, "Type II", 6, [0, 63, 1115, 4668, 8199, 6890]),
    ("e", mp.e, "Type II", 6, [0, 1, 2833, 1521, 3501, 9606]),
    ("phi", mp.phi, "Type II", 6, [0, 0, 1, 2031, 6818, 6083]), # Assuming 'phi' is defined
]

analysis_data = []

for name, target, r_type, depth, coeffs in results_to_analyze:
    if r_type == "CF":
        approx_val = mp.mpf(coeffs[0]) / coeffs[1]
        complexity = description_length(coeffs)
        expr_str = f"{coeffs[0]}/{coeffs[1]}"
    else:
        approx_val = eval_nested(coeffs)
        complexity = description_length(coeffs)
        expr_str = f"sqrt({coeffs[0]} + ...)"
        
    correct_digits = get_correct_digits(target, approx_val)
    error_val = abs(target - approx_val)
    
    analysis_data.append({
        "Target": name,
        "Type": r_type,
        "Depth": depth if r_type != "CF" else "N/A",
        "Expression": expr_str,
        "Coefficients": str(coeffs),
        "Complexity (bits)": float(complexity),
        "Correct Digits": int(correct_digits),
        # FINAL FIX: Convert the mpf error value to a float before formatting
        "Error": f"{float(error_val):.2e}"
    })

for name, target in [("π", PI), ("e", E)]:
    for depth in [4, 5]:
        baseline = zero_tail_baseline(target, depth)
        correct_digits = get_correct_digits(target, baseline['approx_val'])
        
        analysis_data.append({
            "Target": name,
            "Type": "Zero-Tail Baseline",
            "Depth": depth,
            "Expression": baseline['description'],
            "Coefficients": str(baseline['coeffs']),
            "Complexity (bits)": float(baseline['complexity']),
            "Correct Digits": int(correct_digits),
            # FINAL FIX: Convert the mpf error value to a float before formatting
            "Error": f"{float(baseline['error']):.2e}"
        })

# --- Create and Display the DataFrame ---
df = pd.DataFrame(analysis_data)
df_sorted = df.sort_values(by=["Target", "Correct Digits"], ascending=[True, False]).reset_index(drop=True)

pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 140)

print("\n--- Comprehensive Results Table ---")
print(df_sorted)

"""
####################### OUTPUT ##########################

--- Comprehensive Results Table ---
  Target                Type Depth             Expression              Coefficients  Complexity (bits)  Correct Digits     Error
0      e  Zero-Tail Baseline     5  Round(e = exp(1)**32)          [78962960182681]          46.166241              15  3.28e-16
1      e             Type II     5          sqrt(2 + ...)   [2, 11, 304, 408, 2995]          33.647369              12  2.11e-13
2      e             Type II     4          sqrt(0 + ...)        [0, 33, 410, 3190]          25.410250              10  3.79e-11
3      e  Zero-Tail Baseline     4  Round(e = exp(1)**16)                 [8886111]          23.083121               8  9.17e-09
4      π  Zero-Tail Baseline     5          Round(pi**32)        [8105800789910710]          52.847876              17  4.20e-18
5      π             Type II     5          sqrt(2 + ...)  [2, 6, 3081, 2193, 1493]          37.626281              13  1.86e-14
6      π             Type II     4          sqrt(0 + ...)       [0, 46, 2586, 3237]          28.552540               9  1.16e-10
7      π  Zero-Tail Baseline     4          Round(pi**16)                [90032221]          26.423938               9  3.43e-10
8      π              Type I     4          sqrt(3 + ...)            [3, 44, 2, 67]          15.164278               6  1.70e-07
9      π                  CF   N/A                355/113                [355, 113]          15.308623               6  2.67e-07
"""
