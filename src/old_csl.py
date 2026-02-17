"""
Coincidence Site Lattice (CSL) boundary identification for cubic crystals.

This module identifies special grain boundaries based on the CSL model
and Brandon criterion for deviation from exact CSL orientations.
"""

import numpy as np
from typing import Tuple, Optional
from quaternions import Quaternion



class CSLBoundary:
    """Represents a CSL boundary type."""
    
    def __init__(self, sigma: int, theta: float, uvw: list, 
                 rodrigues: list, quaternion: list):
        """
        Initialize a CSL boundary.
        
        Args:
            sigma: Sigma value (reciprocal density of coincident sites)
            theta: Misorientation angle in degrees
            uvw: Miller indices of rotation axis
            rodrigues: Rodrigues vector components [r1, r2, r3]
            quaternion: Quaternion representation [q1, q2, q3, q4]
        """
        self.sigma = sigma
        self.theta = theta
        self.uvw = uvw
        self.rodrigues = np.array(rodrigues)
        self.quaternion = Quaternion(quaternion)
    
    def __repr__(self) -> str:
        return f"CSL(Σ{self.sigma}, {self.theta:.1f}°, [{self.uvw[0]}{self.uvw[1]}{self.uvw[2]}])"


class CSLIdentifier:
    """Identifies CSL boundaries in cubic crystals."""
    
    def __init__(self):
        """Initialize with standard CSL boundary data for cubic crystals."""
        self.boundaries = self._load_csl_data()
    
    def _load_csl_data(self) -> list:
        """
        Load CSL boundary data with high-precision quaternions.
        
        Returns:
            List of CSLBoundary objects
        """
        # CSL data with high-precision quaternions calculated from exact axis-angle
        # Format: (sigma, theta, uvw, rodrigues, quaternion)
        csl_data = [
            (3, 60.0, [1,1,1], [0.333333, 0.333333, 0.333333], [0.28867513, 0.28867513, 0.28867513, 0.86602540]),
            (5, 36.87, [1,0,0], [0.333333, 0.0, 0.0], [0.0, 0.0, 0.31622777, 0.94868330]),
            (7, 38.21, [1,1,1], [0.199186, 0.199186, 0.199186], [0.18806701, 0.18806701, 0.18806701, 0.94368294]),
            (9, 38.94, [1,1,0], [0.25, 0.25, 0.0], [0.0, 0.23570226, 0.23570226, 0.94280904]),
            (11, 50.48, [1,1,0], [0.333333, 0.333333, 0.0], [0.0, 0.30151134, 0.30151134, 0.90453403]),
            (13, 22.62, [1,0,0], [0.2, 0.0, 0.0], [0.0, 0.0, 0.19611614, 0.98058068]),
            (13, 27.80, [1,1,1], [0.142857, 0.142857, 0.142857], [0.13917310, 0.13917310, 0.13917310, 0.97324899]),
            (15, 48.19, [2,1,0], [0.4, 0.2, 0.0], [0.0, 0.18569534, 0.37139068, 0.90963199]),
            (17, 28.07, [1,0,0], [0.25, 0.0, 0.0], [0.0, 0.0, 0.24253563, 0.97014250]),
            (17, 61.93, [2,2,1], [0.4, 0.4, 0.2], [0.17101007, 0.34202014, 0.34202014, 0.85749293]),
            (19, 26.53, [1,1,0], [0.166667, 0.166667, 0.0], [0.0, 0.16222142, 0.16222142, 0.97324899]),
            (19, 46.83, [1,1,1], [0.25, 0.25, 0.25], [0.22940312, 0.22940312, 0.22940312, 0.91855865]),
            (21, 21.79, [1,1,1], [0.111111, 0.111111, 0.111111], [0.10893394, 0.10893394, 0.10893394, 0.98224852]),
            (21, 44.42, [2,1,1], [0.333333, 0.166667, 0.166667], [0.15430335, 0.15430335, 0.30860670, 0.92541658]),
            (23, 40.45, [3,1,1], [0.334242, 0.111414, 0.111414], [0.10452846, 0.10452846, 0.31358539, 0.93763792]),
            (25, 16.26, [1,0,0], [0.142857, 0.0, 0.0], [0.0, 0.0, 0.14176307, 0.98989794]),
            (25, 51.68, [3,3,1], [0.333333, 0.333333, 0.111111], [0.10000000, 0.30000000, 0.30000000, 0.90000000]),
            (27, 31.59, [1,1,0], [0.2, 0.2, 0.0], [0.0, 0.19318517, 0.19318517, 0.96225045]),
            (27, 35.43, [2,1,0], [0.285714, 0.142857, 0.0], [0.0, 0.13613568, 0.27227136, 0.95241986]),
            (29, 46.40, [1,0,0], [0.428571, 0.0, 0.0], [0.0, 0.0, 0.39392472, 0.91914503]),
            (29, 43.60, [2,2,1], [0.285714, 0.285714, 0.142857], [0.13139329, 0.26278658, 0.26278658, 0.92168365]),
            (31, 17.90, [1,1,1], [0.090909, 0.090909, 0.090909], [0.08993958, 0.08993958, 0.08993958, 0.98628510]),
            (31, 52.20, [2,1,1], [0.4, 0.2, 0.2], [0.17994362, 0.17994362, 0.35988724, 0.89742816]),
            (33, 20.05, [1,1,0], [0.125, 0.125, 0.0], [0.0, 0.12310563, 0.12310563, 0.98473193]),
            (33, 33.56, [3,1,1], [0.272727, 0.090909, 0.090909], [0.08682431, 0.08682431, 0.26047294, 0.95630476]),
            (33, 58.99, [1,1,0], [0.4, 0.4, 0.0], [0.0, 0.34730199, 0.34730199, 0.87039087]),
            (35, 34.05, [2,1,1], [0.25, 0.125, 0.125], [0.11952286, 0.11952286, 0.23904572, 0.95618289]),
            (35, 43.23, [3,3,1], [0.272727, 0.272727, 0.090909], [0.08333333, 0.25, 0.25, 0.93333333])
        ]
        
        boundaries = []
        for sigma, theta, uvw, rod, quat in csl_data:
            q_normalized = Quaternion(quat)
            q_normalized.normalize()  # Make it a unit quaternion
            boundaries.append(CSLBoundary(sigma, theta, uvw, rod, q_normalized.q.tolist()))
    
        
        return boundaries
    
    def brandon_criterion(self, sigma: int) -> float:
        """
        Calculate Brandon criterion for allowable deviation from exact CSL.
        
        The Brandon criterion: Δθ_max = 15° / √Σ
        
        Args:
            sigma: Sigma value
            
        Returns:
            Maximum angular deviation in degrees
        """
        return 15.0 / np.sqrt(float(sigma))
    
    def identify_boundary(self, q: Quaternion, 
                    angle: float) -> Tuple[Optional[int], float]:
        """
        Identify if a misorientation corresponds to a CSL boundary.
        """
        # Low-angle boundaries (< 15°) are treated as Σ1
        if angle < 15.0:
            return 1, angle / 15.0
        
        # Search for closest CSL boundary
        min_criterion = 66.0
        best_sigma = None
        
        for csl in self.boundaries:
            # Calculate Q_measured * Q_CSL^(-1) to get angular deviation
            delta_q = q.multiply(csl.quaternion.conjugate())
            
            # Extract angle from delta quaternion
            q4_clamped = np.clip(delta_q.q[3], -1.0, 1.0)
            theta = np.arccos(abs(q4_clamped)) * 360.0 / np.pi
            
            # DEBUG: Print for Σ19
            if csl.sigma == 19 and csl.theta > 45:
                print(f"DEBUG Σ19:")
                print(f"  delta_q = [{delta_q.q[0]:.6f}, {delta_q.q[1]:.6f}, {delta_q.q[2]:.6f}, {delta_q.q[3]:.6f}]")
                print(f"  q4_clamped = {q4_clamped:.6f}")
                print(f"  theta = {theta:.4f}°")
                print(f"  Brandon = {self.brandon_criterion(csl.sigma):.4f}°")
            
            # Brandon criterion
            brandon = self.brandon_criterion(csl.sigma)
            criterion = theta / brandon
            
            if criterion < min_criterion:
                min_criterion = criterion
                best_sigma = csl.sigma
        
        print(f"FINAL: best_sigma={best_sigma}, min_criterion={min_criterion:.6f}")
        return best_sigma if best_sigma else None, min_criterion
        
    def _angular_deviation(self, q1: Quaternion, q2: Quaternion) -> float:
        """
        Calculate angular deviation between two quaternions.
        
        Args:
            q1: First quaternion
            q2: Second quaternion (CSL boundary)
            
        Returns:
            Angular deviation in degrees
        """
        # Calculate q1 * q2^-1
        delta = q1.multiply(q2.conjugate())
        
        # Extract angle
        q4 = np.clip(delta.q[3], -1.0, 1.0)
        theta = 2.0 * np.arccos(abs(q4)) * 180.0 / np.pi
        
        return theta
    
    def get_boundary_info(self, sigma: int) -> list:
        """
        Get all CSL boundaries with given sigma value.
        
        Args:
            sigma: Sigma value
            
        Returns:
            List of CSLBoundary objects
        """
        return [csl for csl in self.boundaries if csl.sigma == sigma]
