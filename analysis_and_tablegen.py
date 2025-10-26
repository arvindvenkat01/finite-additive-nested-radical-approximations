# MIT License
# Copyright (c) 2025 Arvind N. Venkat
# Permission is hereby granted, free of charge...

"""
Analysis script for nested radical approximations.
Compares discovered approximations to zero-tail baselines.
Uses results from the turbo search code.
"""

!pip install mpmath pandas

import math
from mpmath import mp

# --- Precision Setup ---
mp.dps = 200

PI = mp.pi
E = mp.e
PHI = (1 + mp.sqrt(5)) / 2

# --- Core Functions ---

def description_length(coeffs):
    """
    Calculates the descriptive complexity L = sum(log2(1 + |a_i|)) for ALL coefficients.
    This matches the paper's definition and includes zeros.
    """
    if not coeffs:
        return mp.mpf(0)
    return mp.fsum([mp.log(1 + abs(int(a)), 2) for a in coeffs])

def eval_nested(coeffs):
    """Evaluates a nested radical from a list of coefficients."""
    v = mp.mpf(0)
    for a in reversed(coeffs):
        v = mp.sqrt(v + a)
    return v

def eval_rational(p, q):
    """Evaluates a rational approximation."""
    return mp.mpf(p) / mp.mpf(q)

def get_digits_score(target, approx_val):
    """
    Calculates the digits-of-accuracy score D = -log10(error).
    Returns continuous real value, not integer digit count.
    """
    error = abs(target - approx_val)
    if error == 0:
        return mp.mpf(300)  # Near-exact
    return -mp.log(error, 10)

def zero_tail_baseline(target, depth):
    """
    Calculates the zero-tail rounding baseline for a given depth.
    This is [0, 0, ..., 0, n] where n = round(target^(2^k)).
    """
    power_of_2 = 2**depth
    target_powered = target**power_of_2
    n = mp.nint(target_powered)
    approx_val = n**(mp.mpf(1)/power_of_2)
    error = abs(target - approx_val)
    
    # Coefficients are [0, 0, ..., 0, n]
    coeffs = [0] * (depth - 1) + [int(n)]
    
    return {
        "coeffs": coeffs,
        "approx_val": approx_val,
        "error": error,
        "complexity": description_length(coeffs)
    }

# --- Star Results from Turbo Search ---
# These are the best approximations found by nested_radical_search_FINAL.py

STAR_RESULTS = [
    # π approximations
    ("π", PI, "Nested", 4, [0, 52, 1889, 29924]),      # 12.4 digits, E=0.392
    ("π", PI, "Nested", 5, [0, 49, 2276, 4500, 2320]),  # 15.6 digits, E=0.388
    ("π", PI, "Nested", 6, [1, 1, 5945, 7635, 1554, 9186]),  # 16.6 digits
    
    # e approximations
    ("e", E, "Nested", 3, [0, 10, 1989]),               # 6.2 digits, E=0.427
    ("e", E, "Nested", 4, [0, 8, 2028, 20560]),         # 10.8 digits, E=0.379
    ("e", E, "Nested", 5, [1, 30, 36, 6389, 33807]),    # 15.0 digits, E=0.387
    ("e", E, "Nested", 6, [0, 0, 2780, 40193, 36413, 12323]),  # 17.2 digits
    
    # φ approximations
    ("φ", PHI, "Nested", 3, [0, 0, 47]),                # 4.0 digits, E=0.723
    ("φ", PHI, "Nested", 4, [0, 0, 0, 2207]),           # 7.7 digits, E=0.692
    ("φ", PHI, "Nested", 5, [0, 1, 12, 332, 26888]),    # 10.6 digits
    ("φ", PHI, "Nested", 6, [0, 0, 9, 1309, 17665, 15862]),  # 15.3 digits
    
    # Continued fraction baseline
    ("π", PI, "CF", None, [355, 113]),                  # 6.0 digits, E=0.392
]

# --- Analysis ---

def analyze_all():
    """
    Analyzes all star results and compares to zero-tail baselines.
    Generates comprehensive comparison table grouped by target and depth.
    """
    print("="*100)
    print("COMPREHENSIVE ANALYSIS: Nested Radicals vs. Zero-Tail Baselines")
    print("Grouped by Target and Depth for Easy Comparison")
    print("="*100)
    
    # Collect results organized by target and depth
    by_target_depth = {}
    
    # Process star results
    for name, target, result_type, depth, coeffs in STAR_RESULTS:
        key = (name, depth if depth is not None else "—")
        if key not in by_target_depth:
            by_target_depth[key] = {}
        
        if result_type == "CF":
            approx_val = eval_rational(coeffs[0], coeffs[1])
            complexity = description_length(coeffs)
        else:
            approx_val = eval_nested(coeffs)
            complexity = description_length(coeffs)
        
        D = get_digits_score(target, approx_val)
        error = abs(target - approx_val)
        efficiency = D / complexity if complexity > 0 else 0
        
        by_target_depth[key][result_type] = {
            "Coeffs": str(coeffs),
            "L": float(complexity),
            "D": float(D),
            "E": float(efficiency),
            "Error": float(error)
        }
    
    # Add zero-tail baselines
    for name, target in [("π", PI), ("e", E), ("φ", PHI)]:
        for depth in [3, 4, 5, 6]:
            key = (name, depth)
            if key not in by_target_depth:
                by_target_depth[key] = {}
            
            baseline = zero_tail_baseline(target, depth)
            D = get_digits_score(target, baseline['approx_val'])
            efficiency = D / baseline['complexity'] if baseline['complexity'] > 0 else 0
            
            by_target_depth[key]["Zero-Tail"] = {
                "Coeffs": f"[0×{depth-1}, {baseline['coeffs'][-1]}]",
                "L": float(baseline['complexity']),
                "D": float(D),
                "E": float(efficiency),
                "Error": float(baseline['error'])
            }
    
    # Print organized table
    print()
    for target_name in ["π", "e", "φ"]:
        print(f"\n{'='*100}")
        print(f"TARGET: {target_name}")
        print(f"{'='*100}")
        print(f"{'Depth':<7} {'Type':<12} {'D':<8} {'L':<10} {'E':<10} {'Error':<12} {'Winner':<10}")
        print("-" * 100)
        
        for depth in [3, 4, 5, 6]:
            key = (target_name, depth)
            if key not in by_target_depth:
                continue
            
            data = by_target_depth[key]
            
            # Determine which types we have
            types_present = []
            if "Nested" in data:
                types_present.append("Nested")
            if "Zero-Tail" in data:
                types_present.append("Zero-Tail")
            if "CF" in data:
                types_present.append("CF")
            
            # Print each type
            for i, type_name in enumerate(types_present):
                info = data[type_name]
                
                # Determine winner (best efficiency)
                winner = ""
                if len(types_present) > 1 and "Nested" in data and "Zero-Tail" in data:
                    if i == 0:  # Only show winner on first row
                        nested_e = data["Nested"]["E"]
                        zt_e = data["Zero-Tail"]["E"]
                        if nested_e > zt_e:
                            winner = f"Nested +{((nested_e - zt_e) / zt_e * 100):.1f}%"
                        elif zt_e > nested_e:
                            winner = f"ZT +{((zt_e - nested_e) / nested_e * 100):.1f}%"
                
                depth_str = f"k={depth}" if i == 0 else ""
                
                print(f"{depth_str:<7} {type_name:<12} {info['D']:>6.1f}   "
                      f"{info['L']:>8.1f}   {info['E']:>8.3f}   "
                      f"{info['Error']:>10.2e}   {winner:<10}")
            
            # Add separator between depths
            if depth < 6:
                print()
    
    # Return all data for other functions
    all_results = []
    for (target, depth), data in by_target_depth.items():
        for type_name, info in data.items():
            all_results.append({
                "Target": target,
                "Type": type_name,
                "Depth": depth,
                **info
            })
    
    return all_results

def compare_at_fixed_depth():
    """
    Depth-matched comparison: nested radicals vs. zero-tail at same k.
    This is the fair comparison emphasized in the paper.
    """
    print("\n" + "="*100)
    print("DEPTH-MATCHED COMPARISON: Nested Radicals vs. Zero-Tail (Same k)")
    print("="*100)
    
    comparisons = [
        ("π", PI, 4, [0, 52, 1889, 29924]),
        ("π", PI, 5, [0, 49, 2276, 4500, 2320]),
        ("e", E, 4, [0, 8, 2028, 20560]),
        ("e", E, 5, [1, 30, 36, 6389, 33807]),
        ("φ", PHI, 5, [0, 1, 12, 332, 26888]),
        ("φ", PHI, 6, [0, 0, 9, 1309, 17665, 15862]),
    ]
    
    for name, target, depth, coeffs in comparisons:
        # Nested radical
        nested_val = eval_nested(coeffs)
        nested_L = description_length(coeffs)
        nested_D = get_digits_score(target, nested_val)
        nested_E = nested_D / nested_L
        
        # Zero-tail baseline
        baseline = zero_tail_baseline(target, depth)
        zt_L = baseline['complexity']
        zt_D = get_digits_score(target, baseline['approx_val'])
        zt_E = zt_D / zt_L
        
        print(f"\n{name} depth-{depth}:")
        print(f"  Nested:    {coeffs}")
        print(f"             D={float(nested_D):.1f}, L={float(nested_L):.1f}, E={float(nested_E):.3f}")
        print(f"  Zero-Tail: [0×{depth-1}, {baseline['coeffs'][-1]}]")
        print(f"             D={float(zt_D):.1f}, L={float(zt_L):.1f}, E={float(zt_E):.3f}")
        
        if nested_E > zt_E:
            delta = float(((nested_E - zt_E) / zt_E) * 100)
            print(f"  → Nested is {delta:.1f}% more efficient")
        else:
            delta = float(((zt_E - nested_E) / nested_E) * 100)
            print(f"  → Zero-tail is {delta:.1f}% more efficient")

def efficiency_frontier():
    """
    Shows the efficiency frontier: which approximations maximize E at each bit budget.
    """
    print("\n" + "="*100)
    print("EFFICIENCY FRONTIER: Best D/L at Each Complexity Level")
    print("="*100)
    
    # Collect all results with efficiency
    points = []
    
    for name, target, result_type, depth, coeffs in STAR_RESULTS:
        if result_type == "CF":
            approx_val = eval_rational(coeffs[0], coeffs[1])
        else:
            approx_val = eval_nested(coeffs)
        
        L = description_length(coeffs)
        D = get_digits_score(target, approx_val)
        E = D / L if L > 0 else 0
        
        points.append({
            "Target": name,
            "Type": result_type,
            "L": float(L),
            "D": float(D),
            "E": float(E),
            "Coeffs": str(coeffs)
        })
    
    # Sort by efficiency descending
    points.sort(key=lambda x: -x["E"])
    
    print(f"\n{'Rank':<6} {'Target':<8} {'Type':<8} {'E':<8} {'D':<8} {'L':<10} {'Coeffs'}")
    print("-" * 100)
    
    for i, p in enumerate(points[:15], 1):  # Top 15
        print(f"{i:<6} {p['Target']:<8} {p['Type']:<8} {p['E']:>6.3f}   "
              f"{p['D']:>6.1f}   {p['L']:>8.1f}   {p['Coeffs']}")

# --- Main Execution ---

if __name__ == "__main__":
    print("\n" + "="*100)
    print("ANALYSIS OF NESTED RADICAL APPROXIMATIONS")
    print("Using results from nested_radical_search_FINAL.py")
    print("="*100)
    
    # Run all analyses
    all_results = analyze_all()
    compare_at_fixed_depth()
    efficiency_frontier()
    
    print("\n" + "="*100)
    print("Analysis complete!")
    print("="*100)

print("\n--- Comprehensive Results Table ---")
print(df_sorted)
