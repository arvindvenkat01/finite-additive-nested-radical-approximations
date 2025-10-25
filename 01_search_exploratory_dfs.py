# MIT License
# Copyright (c) 2025 Arvind N. Venkat
# Permission is hereby granted, free of charge...

# Colab-ready: pip installs (uncomment if needed)
# !pip install numba

import math
from numba import njit

@njit
def nested_radical(coeffs):
    # R_k(a1..ak) = sqrt(a1 + sqrt(a2 + ... + sqrt(ak)))
    val = 0.0
    for a in coeffs[::-1]:
        val = math.sqrt(a + val)
    return val

def search_backward(target, depth, max_offset=60, a_min=0, a_max=None):
    """
    Backward-squaring DFS:
      y1 = t^2 - a1 >= 0, y2 = y1^2 - a2 >= 0, ..., ak = round(y_{k-1}^2)
    Search a_j in [floor(y_j^2)±max_offset] intersected with [a_min, a_max].
    """
    best = {'coeffs': None, 'err': float('inf'), 'approx': None}

    def dfs(level, y, coeffs):
        if level == depth:
            ak = int(round(y*y))
            if a_max is not None and ak > a_max:
                return
            coeffs.append(ak)
            val = nested_radical(coeffs)
            err = abs(val - target)
            if err < best['err']:
                best['err'] = err
                best['coeffs'] = coeffs.copy()
                best['approx'] = val
            coeffs.pop()
            return

        base = int(math.floor(y*y))
        start = max(a_min, base - max_offset)
        end = base + max_offset
        for a in range(start, end+1):
            y_next = y*y - a
            if y_next < 0:
                break  # increasing a only decreases y_next further
            if a_max is not None and a > a_max:
                break
            coeffs.append(a)
            dfs(level+1, y_next, coeffs)
            coeffs.pop()

    dfs(1, target, [])
    return best

# Example usage:
if __name__ == "__main__":
    pi_target = math.pi
    e_target  = math.e
    for d in [3, 4, 5]:
        res_pi = search_backward(pi_target, d, max_offset=60)
        print(f"pi depth {d}:", res_pi)
        res_e  = search_backward(e_target,  d, max_offset=60)
        print(f"e  depth {d}:", res_e)

"""
######################## OUTPUT #########################
pi depth 3: {'coeffs': [1, 44, 1202], 'err': 9.496882125148431e-08, 'approx': 3.141592558620972}
e  depth 3: {'coeffs': [0, 10, 1989], 'err': 6.996177126517011e-07, 'approx': 2.7182825280767577}
pi depth 4: {'coeffs': [0, 46, 2586, 3237], 'err': 1.1575007619057942e-10, 'approx': 3.141592653474043}
e  depth 4: {'coeffs': [0, 33, 410, 3190], 'err': 3.7909231309640745e-11, 'approx': 2.7182818284969543}
pi depth 5: {'coeffs': [2, 6, 3081, 2193, 1493], 'err': 1.865174681370263e-14, 'approx': 3.1415926535897745}
e  depth 5: {'coeffs': [2, 11, 304, 408, 2995], 'err': 2.1094237467877974e-13, 'approx': 2.718281828459256}
"""