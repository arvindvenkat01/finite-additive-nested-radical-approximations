# MIT License
# Copyright (c) 2025 Arvind N. Venkat

# ENHANCED TURBO VERSION with:
# - High-precision error verification (no underflow)
# - Description Length (D/L) complexity metric
# - Efficiency ranking (digits per bit of complexity)

import math
import time
import sys

# Numba for fast search
try:
    from numba import njit
    import numpy as np
    HAS_NUMBA = True
    print("Numba JIT compiler available - maximum speed mode!")
except ImportError:
    HAS_NUMBA = False
    print("Numba not found - running in pure Python (slower)")
    import numpy as np
    def njit(func):
        return func

# mpmath for high-precision verification
try:
    from mpmath import mp
    mp.dps = 100  # 100 decimal places for accurate error measurement
    HAS_MPMATH = True
    print(" mpmath available - high-precision verification enabled")
except ImportError:
    HAS_MPMATH = False
    print(" mpmath not found - will use float64 (less accurate)")

@njit
def nested_radical_fast(coeffs, n):
    """Ultra-fast nested radical evaluation - JIT compiled"""
    val = 0.0
    for i in range(n - 1, -1, -1):
        val = math.sqrt(coeffs[i] + val)
    return val

@njit
def dfs_search(target, depth, level, y, coeffs, max_offset, a_min, 
               best_coeffs, best_err_container):
    """
    JIT-compiled recursive DFS with monotone enumeration.
    
    Current: range(start, end+1) with early break on y_next < 0
    This is correct and efficient for monotone increasing search.
    
    Optional enhancement (not implemented): Centered enumeration exploring
    base, base-1, base+1, base-2, base+2, ... with continue instead of break
    would provide symmetric exploration but changes search order and results.
    Since current algorithm produces excellent results, left as-is for
    reproducibility.
    """
    if level == depth:
        ak = int(round(y * y))
        coeffs[level - 1] = ak
        val = nested_radical_fast(coeffs, depth)
        err = abs(val - target)
        if err < best_err_container[0]:
            best_err_container[0] = err
            for i in range(depth):
                best_coeffs[i] = coeffs[i]
        return
    
    y_sq = y * y
    base = int(math.floor(y_sq))
    start = max(a_min, base - max_offset)
    end = base + max_offset
    
    for a in range(start, end + 1):
        y_next = y_sq - a
        if y_next < 0:
            break
        coeffs[level - 1] = a
        dfs_search(target, depth, level + 1, y_next, coeffs, 
                  max_offset, a_min, best_coeffs, best_err_container)

@njit
def search_one_config(target, depth, max_offset, a_min):
    """Single search run - fully JIT compiled with NumPy arrays"""
    coeffs = np.zeros(depth, dtype=np.int64)
    best_coeffs = np.zeros(depth, dtype=np.int64)
    best_err_container = np.array([np.inf], dtype=np.float64)
    
    dfs_search(target, depth, 1, target, coeffs, max_offset, a_min,
               best_coeffs, best_err_container)
    
    return best_coeffs, best_err_container[0]

def high_precision_verify(coeffs, target):
    """
    Verify result with high precision to avoid float64 underflow.
    Returns actual error with no underflow.
    Auto-bumps precision if error rounds to zero.
    """
    if HAS_MPMATH:
        # Start with default precision
        original_dps = mp.dps
        mp.dps = max(200, original_dps)  # At least 200 digits
        
        # High-precision evaluation
        v = mp.mpf('0')
        for a in reversed(coeffs):
            v = mp.sqrt(v + a)
        actual_error = abs(v - target)
        
        # If error rounds to zero, increase precision
        if actual_error == 0:
            mp.dps = 300  # Bump to 300 digits
            v = mp.mpf('0')
            for a in reversed(coeffs):
                v = mp.sqrt(v + a)
            actual_error = abs(v - target)
        
        # Restore original precision
        mp.dps = original_dps
        return float(actual_error), float(v)
    else:
        # Fall back to float64
        val = 0.0
        for a in reversed(coeffs):
            val = math.sqrt(a + val)
        return abs(val - target), val

def description_length(coeffs):
    """
    Calculate descriptive complexity (bits needed to specify coefficients).
    L = sum of log2(1 + |a_i|) for ALL coefficients (including zeros).
    For a_i = 0: log2(1 + |0|) = log2(1) = 0, which is correct.
    """
    total = 0.0
    for a in coeffs:
        total += math.log2(1 + abs(int(a)))
    return total

def search_backward_turbo(target, depth, max_offset=60, a_min=0):
    """Wrapper for JIT-compiled search with high-precision verification"""
    # Convert target to float for fast search
    if HAS_MPMATH and hasattr(target, '_mpf_'):
        target_float = float(target)
        target_hp = target
    else:
        target_float = float(target)
        target_hp = target
    
    # Fast search with float64
    coeffs_array, float_err = search_one_config(target_float, depth, max_offset, a_min)
    coeffs = [int(coeffs_array[i]) for i in range(depth)]
    
    # High-precision verification
    actual_error, approx = high_precision_verify(coeffs, target_hp)
    
    # Calculate complexity
    complexity = description_length(coeffs)
    
    # Calculate correct digits
    if actual_error > 0:
        correct_digits = -math.log10(actual_error)
    else:
        correct_digits = 100.0  # Essentially exact
    
    # Calculate efficiency (digits per bit of complexity)
    efficiency = correct_digits / complexity if complexity > 0 else 0
    
    return {
        'coeffs': coeffs,
        'err': actual_error,
        'approx': approx,
        'correct_digits': correct_digits,
        'complexity': complexity,
        'efficiency': efficiency
    }

def run_comprehensive_search(target_name, target_val, depths, search_configs):
    """Run comprehensive search with progress updates"""
    print(f"\n{'='*80}")
    if HAS_MPMATH:
        print(f"TARGET: {target_name} = {mp.nstr(target_val, 20)}")
    else:
        print(f"TARGET: {target_name} = {target_val:.15f}")
    print(f"{'='*80}")
    
    all_results = {}
    
    for depth in depths:
        print(f"\n  Depth {depth}:")
        depth_results = []
        
        for i, (offset, a_min, label) in enumerate(search_configs, 1):
            sys.stdout.write(f"    [{i}/{len(search_configs)}] {label:18s} ... ")
            sys.stdout.flush()
            
            start = time.time()
            result = search_backward_turbo(target_val, depth, offset, a_min)
            elapsed = time.time() - start
            
            result['config'] = label
            depth_results.append(result)
            
            print(f"{result['coeffs']} ({elapsed:.2f}s, err={result['err']:.2e})")
        
        # Deduplicate
        seen = set()
        unique = []
        for r in sorted(depth_results, key=lambda x: x['err']):
            t = tuple(r['coeffs'])
            if t not in seen:
                seen.add(t)
                unique.append(r)
        
        all_results[depth] = unique
        
        # Report both best-by-accuracy and best-by-efficiency
        best_by_acc = min(unique, key=lambda x: x['err'])
        best_by_eff = max(unique, key=lambda x: x['efficiency'])
        
        print(f"    → Best by accuracy: {best_by_acc['coeffs']}")
        print(f"       D={best_by_acc['correct_digits']:.1f} digits, L={best_by_acc['complexity']:.1f} bits, E={best_by_acc['efficiency']:.3f}")
        
        if best_by_eff['coeffs'] != best_by_acc['coeffs']:
            print(f"    → Best by efficiency: {best_by_eff['coeffs']}")
            print(f"       E={best_by_eff['efficiency']:.3f} digits/bit, D={best_by_eff['correct_digits']:.1f}, L={best_by_eff['complexity']:.1f}")
    
    return all_results

# Main
if __name__ == "__main__":
    print("="*80)
    print("ENHANCED TURBO-OPTIMIZED NESTED RADICAL SEARCH")
    print("With Description Length metric and high-precision verification")
    print("="*80)
    
    # Warm up JIT compiler with dummy call
    if HAS_NUMBA:
        print("\nWarming up JIT compiler (first run)...")
        _ = search_backward_turbo(3.14, 3, 10, 0)
        print("JIT compilation complete - subsequent searches will be fast!\n")
    
    targets = [
        ("π", math.pi),
        ("e", math.e),
        ("φ", (1 + math.sqrt(5)) / 2),
    ]
    
    # Get high-precision target values if available
    if HAS_MPMATH:
        targets = [
            ("π", mp.pi),
            ("e", mp.e),
            ("φ", (1 + mp.sqrt(5)) / 2),
        ]
    
    depths = [3, 4, 5, 6]
    
    # Optimized order: quick configs first
    search_configs = [
        (60, 0, "DFS-60"),
        (60, 1, "DFS-60-min1"),
        (80, 0, "DFS-80"),
        (80, 1, "DFS-80-min1"),
        (80, 2, "DFS-80-min2"),
        (100, 0, "DFS-100"),
        (100, 1, "DFS-100-min1"),
        (100, 2, "DFS-100-min2"),
        (150, 0, "DFS-150"),
        (200, 0, "DFS-200"),
    ]
    
    start_time = time.time()
    all_results = {}
    
    for target_name, target_val in targets:
        results = run_comprehensive_search(target_name, target_val, depths, search_configs)
        all_results[target_name] = results
    
    total_time = time.time() - start_time
    
    # ====================================================================
    # SUMMARY (Best by Accuracy per Depth)
    # ====================================================================
    
    print("\n" + "="*80)
    print(f"SUMMARY (Best by Accuracy) - Total runtime: {total_time:.1f}s")
    print("="*80)
    
    for target_name in ["π", "e", "φ"]:
        print(f"\n{target_name}:")
        for depth in sorted(all_results[target_name].keys()):
            results = all_results[target_name][depth]
            if results:
                # Explicitly select best by accuracy (minimum error)
                best = min(results, key=lambda r: r['err'])
                print(f"  Depth {depth}: {best['coeffs']}")
                print(f"           Accuracy: {best['correct_digits']:.1f} digits")
                print(f"           Complexity: {best['complexity']:.1f} bits")
                print(f"           Efficiency: {best['efficiency']:.3f} digits/bit")
    
    # ====================================================================
    # STAR PERFORMERS BY ACCURACY
    # ====================================================================
    
    print("\n" + "="*80)
    print("STAR PERFORMERS BY ACCURACY (≥10 correct digits)")
    print("="*80)
    
    stars = []
    for target_name, results_dict in all_results.items():
        for depth, results in results_dict.items():
            if results:
                best = min(results, key=lambda r: r['err'])
                if best['correct_digits'] >= 10:
                    stars.append((target_name, depth, best))
    
    stars.sort(key=lambda x: x[2]['correct_digits'], reverse=True)
    
    print(f"\n{'Rank':<5} {'Target':<6} {'Depth':<6} {'Digits':<8} {'Complexity':<12} {'Efficiency':<12} {'Coefficients'}")
    print("-" * 100)
    
    for i, (target_name, depth, r) in enumerate(stars, 1):
        print(f"{i:<5} {target_name:<6} {depth:<6} {r['correct_digits']:>6.1f}   "
              f"{r['complexity']:>10.1f}   {r['efficiency']:>10.3f}   {r['coeffs']}")
    
    # ====================================================================
    # BEST BY EFFICIENCY (digits per bit)
    # ====================================================================
    
    print("\n" + "="*80)
    print("BEST BY EFFICIENCY (most digits per bit of complexity)")
    print("="*80)
    
    all_by_efficiency = []
    for target_name, results_dict in all_results.items():
        for depth, results in results_dict.items():
            for r in results:
                if r['correct_digits'] >= 3:  # At least 3 digits
                    all_by_efficiency.append((target_name, depth, r))
    
    all_by_efficiency.sort(key=lambda x: x[2]['efficiency'], reverse=True)
    
    print(f"\n{'Rank':<5} {'Target':<6} {'Depth':<6} {'Efficiency':<12} {'Digits':<8} {'Complexity':<12} {'Coefficients'}")
    print("-" * 100)
    
    for i, (target_name, depth, r) in enumerate(all_by_efficiency[:15], 1):  # Top 15
        print(f"{i:<5} {target_name:<6} {depth:<6} {r['efficiency']:>10.3f}   "
              f"{r['correct_digits']:>6.1f}   {r['complexity']:>10.1f}   {r['coeffs']}")
    
    # ====================================================================
    # COMPARISON TABLE
    # ====================================================================
    
    print("\n" + "="*80)
    print("COMPARISON: Your Original Star vs New Best")
    print("="*80)
    
    comparisons = [
        ("π depth 5", "π", 5, [2, 6, 3081, 2193, 1493], "Original star performer"),
        ("π depth 5", "π", 5, None, "New best (by accuracy)"),
    ]
    
    print(f"\n{'Description':<20} {'Coefficients':<35} {'Digits':<8} {'D/L':<10} {'Efficiency'}")
    print("-" * 90)
    
    # Original star
    orig_coeffs = [2, 6, 3081, 2193, 1493]
    if HAS_MPMATH:
        orig_err, orig_approx = high_precision_verify(orig_coeffs, mp.pi)
    else:
        orig_err, orig_approx = high_precision_verify(orig_coeffs, math.pi)
    orig_digits = -math.log10(orig_err) if orig_err > 0 else 100
    orig_complexity = description_length(orig_coeffs)
    orig_efficiency = orig_digits / orig_complexity
    
    print(f"{'π d5 (original)':<20} {str(orig_coeffs):<35} {orig_digits:>6.1f}   "
          f"{orig_complexity:>8.1f}   {orig_efficiency:>6.3f}")
    
    # New best (explicitly select by accuracy)
    new_best = min(all_results["π"][5], key=lambda r: r['err'])
    print(f"{'π d5 (new best)':<20} {str(new_best['coeffs']):<35} {new_best['correct_digits']:>6.1f}   "
          f"{new_best['complexity']:>8.1f}   {new_best['efficiency']:>6.3f}")
    
    print(f"\n→ New result has {new_best['correct_digits'] - orig_digits:.1f} more digits!")
    if new_best['efficiency'] > orig_efficiency:
        print(f"→ AND it's more efficient: {new_best['efficiency']:.3f} vs {orig_efficiency:.3f} digits/bit")
    
    # ====================================================================
    # LATEX
    # ====================================================================
    
    print("\n" + "="*80)
    print("LATEX TABLE ENTRIES (Best by accuracy per depth)")
    print("="*80)
    
    for target_name in ["π", "e", "φ"]:
        print(f"\n% {target_name}")
        for depth in sorted(all_results[target_name].keys()):
            results = all_results[target_name][depth]
            if results:
                # Explicitly select best by accuracy
                best = min(results, key=lambda r: r['err'])
                expr = "\\sqrt{" + str(best['coeffs'][0])
                for c in best['coeffs'][1:]:
                    expr += " + \\sqrt{" + str(c)
                expr += "}" * len(best['coeffs'])
                # Use continuous D score (1 decimal) to match paper
                print(f"{depth} & Add & ${expr}$ & ${best['err']:.2e}$ & "
                      f"{best['correct_digits']:.1f} & {best['complexity']:.1f} \\\\")
    
    print("\n" + "="*80)
    if HAS_NUMBA and HAS_MPMATH:
        print("Search complete with numba acceleration and high-precision verification")
    elif HAS_NUMBA:
        print("Search complete with numba acceleration")
    else:
        print("Search complete")
    print("="*80)
