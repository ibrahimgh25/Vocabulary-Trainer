import numpy as np
def rel2abs(rel_values, ref):
    """ Change relative coordinates to absolute coordinates"""
    if isinstance(rel_values, list):
        if len(rel_values) == 4:
            ref = ref + ref
            return np.multiply(rel_values, ref).astype(int).tolist()
        elif len(rel_values) == 2:
            return np.multiply(rel_values, ref).astype(int).tolist()
    return int(rel_values*ref)