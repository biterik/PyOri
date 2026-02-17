"""
Crystal symmetry operations for cubic materials.

This module handles cubic crystal symmetry operations using quaternions
to find the minimum disorientation between crystal orientations.
"""

import numpy as np
from typing import Tuple, Optional
from quaternions import Quaternion

    
class CubicSymmetry:
    """Handles cubic crystal symmetry operations."""
    
    def __init__(self):
        """Initialize with 24 cubic symmetry operators."""
        self.operators = self._load_cubic_symmetry()
        self.num_symm = len(self.operators)
    
    def _load_cubic_symmetry(self) -> list:
        """
        Load the 24 cubic symmetry operators as quaternions.
        
        Returns:
            List of Quaternion objects representing symmetry operations
        """
        # 24 proper rotations for cubic symmetry
        symm_data = [
            [0, 0, 0, 1],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0.707107, 0, 0, 0.707107],
            [0, 0.707107, 0, 0.707107],
            [0, 0, 0.707107, 0.707107],
            [-0.707107, 0, 0, 0.707107],
            [0, -0.707107, 0, 0.707107],
            [0, 0, -0.707107, 0.707107],
            [0.707107, 0.707107, 0, 0],
            [-0.707107, 0.707107, 0, 0],
            [0, 0.707107, 0.707107, 0],
            [0, -0.707107, 0.707107, 0],
            [0.707107, 0, 0.707107, 0],
            [-0.707107, 0, 0.707107, 0],
            [0.5, 0.5, 0.5, 0.5],
            [-0.5, -0.5, -0.5, 0.5],
            [0.5, -0.5, 0.5, 0.5],
            [-0.5, 0.5, -0.5, 0.5],
            [-0.5, 0.5, 0.5, 0.5],
            [0.5, -0.5, -0.5, 0.5],
            [-0.5, -0.5, 0.5, 0.5],
            [0.5, 0.5, -0.5, 0.5]
        ]
        
        return [Quaternion(op) for op in symm_data]
    
    def apply_pre_symmetry(self, q: Quaternion, index: int) -> Quaternion:
        """
        Apply symmetry operator before the misorientation quaternion.
        
        Computes: S * Q where S is symmetry operator
        
        Args:
            q: Input quaternion
            index: Index of symmetry operator (0-23)
            
        Returns:
            Result quaternion after applying symmetry
        """
        if index < 0 or index >= self.num_symm:
            raise ValueError(f"Symmetry index must be 0-{self.num_symm-1}")
        
        return self.operators[index].multiply(q)
    
    def apply_post_symmetry(self, q: Quaternion, index: int) -> Quaternion:
        """
        Apply symmetry operator after the misorientation quaternion.
        
        Computes: Q * S^-1 where S is symmetry operator
        
        Args:
            q: Input quaternion
            index: Index of symmetry operator (0-23)
            
        Returns:
            Result quaternion after applying symmetry
        """
        if index < 0 or index >= self.num_symm:
            raise ValueError(f"Symmetry index must be 0-{self.num_symm-1}")
        
        # Q * S^-1
        return q.multiply(self.operators[index].conjugate())
    
    def find_disorientation(self, q: Quaternion) -> Tuple[Quaternion, int, int, bool, bool]:
        """
        Find the disorientation (minimum angle) representation of a misorientation.
        
        This applies all 24x24 = 576 combinations of cubic symmetry operators
        to find the representation with the smallest rotation angle in the
        fundamental zone where 0 <= q1 <= q2 <= q3 <= q4.
        
        Args:
            q: Misorientation quaternion (Q1 * Q2^-1)
            
        Returns:
            disorientation: Quaternion in fundamental zone
            index1: Index of first symmetry operator used
            index2: Index of second symmetry operator used  
            neg_q4: Whether q4 was negated
            neg_all: Whether all components were negated
        """
        qmax = 0.0
        best_q = None
        best_i = 0
        best_j = 0
        best_neg_q4 = False
        best_neg_all = False
        
        for i in range(24):
            # Apply first symmetry: S1 * Q
            quint = self.apply_pre_symmetry(q, i)
            
            for j in range(24):
                # Apply second symmetry: (S1 * Q) * S2^-1
                quintn = self.apply_post_symmetry(quint, j)
                
                # Try both positive and negative versions
                for neg_all in [False, True]:
                    if neg_all:
                        qqn = Quaternion(-quintn.q)
                    else:
                        qqn = quintn
                    
                    # Try both q4 and -q4 (switching symmetry)
                    for neg_q4 in [False, True]:
                        qresult = qqn.q.copy()
                        if neg_q4:
                            qresult[3] = -qqn.q[3]
                        
                        # Check if in fundamental zone: 0 <= q1 <= q2 <= q3 <= q4
                        if (qresult[0] >= 0.0 and 
                            qresult[0] <= qresult[1] and
                            qresult[1] <= qresult[2] and
                            qresult[2] <= qresult[3]):
                            
                            # Check if this gives smaller angle (larger q4)
                            if qresult[3] > qmax:
                                qmax = qresult[3]
                                best_q = Quaternion(qresult)
                                best_i = i
                                best_j = j
                                best_neg_q4 = neg_q4
                                best_neg_all = neg_all
        
        if best_q is None:
            raise RuntimeError("Failed to find disorientation in fundamental zone")
        
        return best_q, best_i, best_j, best_neg_q4, best_neg_all
    
    def reconstruct_disorientation(self, q: Quaternion, index1: int, index2: int,
                                   neg_q4: bool, neg_all: bool) -> Quaternion:
        """
        Reconstruct the disorientation from symmetry indices.
        
        Args:
            q: Original misorientation quaternion
            index1: First symmetry operator index
            index2: Second symmetry operator index
            neg_q4: Whether q4 was negated
            neg_all: Whether all components were negated
            
        Returns:
            Reconstructed disorientation quaternion
        """
        # Apply symmetries
        quint = self.apply_pre_symmetry(q, index1)
        qqn = self.apply_post_symmetry(quint, index2)
        
        # Apply negations if needed
        result = qqn.q.copy()
        if neg_all:
            result = -result
        if neg_q4:
            result[3] = -result[3]
        
        return Quaternion(result)


def calculate_misorientation_sutton_balluffi(q: Quaternion) -> float:
    """
    Calculate minimum misorientation angle using Sutton & Balluffi method.
    
    This is a faster approximation that doesn't require searching through
    all symmetry combinations. It finds the maximum among q4 values after
    considering absolute values.
    
    Args:
        q: Misorientation quaternion
        
    Returns:
        Minimum misorientation angle in degrees
    """
    qabs = np.abs(q.q)
    
    # Find max component
    qmax = np.max(qabs)
    
    # Find second largest
    qabs_sorted = np.sort(qabs)
    q1max = qabs_sorted[-2]
    
    # Calculate disorientation
    disor = max(qmax, 
                (qmax + q1max) / np.sqrt(2.0),
                np.sum(qabs) / 2.0)
    
    disor = np.clip(disor, -1.0, 1.0)
    angle = np.arccos(disor) * 360.0 / np.pi
    
    return angle
