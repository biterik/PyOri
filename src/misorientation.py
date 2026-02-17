"""
Main module for grain boundary misorientation analysis.

This module provides high-level functions for calculating grain boundary
misorientations, disorientations, and identifying special boundaries.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from quaternions import (Quaternion, euler_to_quaternion, 
                         axis_angle_to_quaternion, quaternion_to_euler)
from symmetry import CubicSymmetry, calculate_misorientation_sutton_balluffi
from csl import CSLIdentifier


class GrainBoundary:
    """
    Represents a grain boundary between two crystal orientations.
    
    Attributes:
        grain1: First grain orientation (Quaternion)
        grain2: Second grain orientation (Quaternion)
        misorientation: Misorientation quaternion (Q1 * Q2^-1)
        disorientation: Minimum angle representation in fundamental zone
        angle: Misorientation angle in degrees
        axis: Rotation axis (unit vector)
        sigma: CSL sigma value (None if not CSL)
        deviation: Deviation from exact CSL
    """
    
    def __init__(self, q1: Quaternion, q2: Quaternion):
        """
        Initialize grain boundary from two orientations.
        
        Args:
            q1: First grain orientation quaternion
            q2: Second grain orientation quaternion
        """
        self.grain1 = q1
        self.grain2 = q2
        self.symmetry = CubicSymmetry()
        self.csl = CSLIdentifier()
        
        # Calculate misorientation and disorientation
        self._calculate_misorientation()
    
    def _calculate_misorientation(self):
        """Calculate misorientation and find disorientation."""
        # Misorientation: Q1 * Q2^-1
        self.misorientation = self.grain1.misorientation(self.grain2)
        
        # Find disorientation (minimum angle in fundamental zone)
        self.disorientation, self.symm_i, self.symm_j, self.neg_q4, self.neg_all = \
            self.symmetry.find_disorientation(self.misorientation)
        
        # Extract angle and axis
        self.angle, self.axis = self.disorientation.to_axis_angle()
        
        # Identify CSL boundary
        self.sigma, self.deviation = self.csl.identify_boundary(
            self.disorientation, self.angle)
    
    def to_dict(self) -> Dict:
        """
        Convert grain boundary to dictionary.
        
        Returns:
            Dictionary containing all boundary properties
        """
        return {
            'angle': self.angle,
            'axis': self.axis.tolist(),
            'quaternion': self.disorientation.q.tolist(),
            'rodrigues': self.disorientation.to_rodrigues().tolist(),
            'sigma': self.sigma,
            'deviation': self.deviation,
            'boundary_type': self._classify_boundary()
        }
    
    def _classify_boundary(self) -> str:
        """Classify the boundary type."""
        if self.sigma == 1:
            return "Low-angle"
        elif self.sigma and self.deviation < 1.0:
            return f"CSL Σ{self.sigma}"
        elif self.sigma:
            return f"Near-CSL Σ{self.sigma}"
        else:
            return "General high-angle"
    
    def __repr__(self) -> str:
        return (f"GrainBoundary(angle={self.angle:.2f}°, "
                f"axis=[{self.axis[0]:.3f}, {self.axis[1]:.3f}, {self.axis[2]:.3f}], "
                f"type={self._classify_boundary()})")


def analyze_euler_angles(phi1_a: float, phi_a: float, phi2_a: float,
                         phi1_b: float, phi_b: float, phi2_b: float,
                         degrees: bool = True) -> GrainBoundary:
    """
    Analyze grain boundary from two sets of Bunge Euler angles.
    
    Args:
        phi1_a, phi_a, phi2_a: Euler angles for grain A
        phi1_b, phi_b, phi2_b: Euler angles for grain B
        degrees: If True, angles are in degrees (default True)
        
    Returns:
        GrainBoundary object containing complete analysis
    """
    q1 = euler_to_quaternion(phi1_a, phi_a, phi2_a, degrees=degrees)
    q2 = euler_to_quaternion(phi1_b, phi_b, phi2_b, degrees=degrees)
    
    return GrainBoundary(q1, q2)


def analyze_axis_angle(angle: float, axis: list,
                      degrees: bool = True) -> GrainBoundary:
    """
    Analyze misorientation from axis-angle representation.
    
    This assumes grain A is at reference orientation (identity)
    and grain B has the specified misorientation.
    
    Args:
        angle: Rotation angle
        axis: Rotation axis [x, y, z]
        degrees: If True, angle is in degrees (default True)
        
    Returns:
        GrainBoundary object containing complete analysis
    """
    # Grain A at identity
    q1 = Quaternion([0, 0, 0, 1])
    
    # Grain B at specified orientation
    q2 = axis_angle_to_quaternion(angle, axis, degrees=degrees)
    
    return GrainBoundary(q1, q2)


def compare_with_misori(phi1_a: float, phi_a: float, phi2_a: float,
                       phi1_b: float, phi_b: float, phi2_b: float,
                       nsymm: int = 4) -> Dict:
    """
    Calculate misorientation using Dierk Raabe's MISORI algorithm.
    
    This provides an alternative calculation method for comparison.
    Note: Full implementation would require matrix operations.
    
    Args:
        phi1_a, phi_a, phi2_a: Euler angles for grain A (degrees)
        phi_b, phi_b, phi2_b: Euler angles for grain B (degrees)
        nsymm: Sample symmetry (1-4, default 4 for orthorhombic)
        
    Returns:
        Dictionary with angle and axis from MISORI method
    """
    # This is a simplified version - full MISORI uses rotation matrices
    gb = analyze_euler_angles(phi1_a, phi_a, phi2_a, 
                              phi1_b, phi_b, phi2_b)
    
    return {
        'angle': gb.angle,
        'axis': gb.axis.tolist(),
        'method': 'quaternion (equivalent to MISORI)'
    }


def batch_analysis(orientations: list, 
                  input_type: str = 'euler') -> list:
    """
    Analyze multiple grain boundaries.
    
    Args:
        orientations: List of orientation pairs
            - For 'euler': [(phi1_a, phi_a, phi2_a, phi1_b, phi_b, phi2_b), ...]
            - For 'axis_angle': [(angle, [ax, ay, az]), ...]
        input_type: 'euler' or 'axis_angle'
        
    Returns:
        List of GrainBoundary objects
    """
    boundaries = []
    
    if input_type == 'euler':
        for ori in orientations:
            if len(ori) != 6:
                raise ValueError("Euler input requires 6 values per pair")
            gb = analyze_euler_angles(*ori)
            boundaries.append(gb)
    
    elif input_type == 'axis_angle':
        for ori in orientations:
            if len(ori) != 2:
                raise ValueError("Axis-angle input requires (angle, [axis])")
            angle, axis = ori
            gb = analyze_axis_angle(angle, axis)
            boundaries.append(gb)
    
    else:
        raise ValueError("input_type must be 'euler' or 'axis_angle'")
    
    return boundaries


def format_output(gb: GrainBoundary, verbose: bool = True) -> str:
    """
    Format grain boundary results for display.
    
    Args:
        gb: GrainBoundary object
        verbose: If True, include detailed information
        
    Returns:
        Formatted string output
    """
    output = []
    output.append("=" * 70)
    output.append("GRAIN BOUNDARY ANALYSIS")
    output.append("=" * 70)
    
    # Basic results
    output.append(f"\nMisorientation angle: {gb.angle:.2f}°")
    output.append(f"Rotation axis: [{gb.axis[0]:.3f}, {gb.axis[1]:.3f}, {gb.axis[2]:.3f}]")
    
    # Quaternion
    q = gb.disorientation.q
    output.append(f"Quaternion: [{q[0]:.4f}, {q[1]:.4f}, {q[2]:.4f}, {q[3]:.4f}]")
    
    # Rodrigues vector
    rod = gb.disorientation.to_rodrigues()
    if not np.any(np.isinf(rod)):
        output.append(f"Rodrigues vector: [{rod[0]:.4f}, {rod[1]:.4f}, {rod[2]:.4f}]")
    
    # CSL identification
    output.append(f"\nBoundary type: {gb._classify_boundary()}")
    if gb.sigma:
        output.append(f"Σ value: {gb.sigma}")
        output.append(f"Deviation from exact CSL: {gb.deviation:.3f}")
        if gb.deviation < 1.0:
            output.append("  (Within Brandon criterion)")
        else:
            output.append("  (Outside Brandon criterion)")
    
    if verbose:
        output.append(f"\nSymmetry operators used: ({gb.symm_i}, {gb.symm_j})")
        
        # Euler angles for both grains (if available)
        euler1 = quaternion_to_euler(gb.grain1)
        euler2 = quaternion_to_euler(gb.grain2)
        output.append(f"\nGrain A Euler angles: φ₁={euler1[0]:.2f}° Φ={euler1[1]:.2f}° φ₂={euler1[2]:.2f}°")
        output.append(f"Grain B Euler angles: φ₁={euler2[0]:.2f}° Φ={euler2[1]:.2f}° φ₂={euler2[2]:.2f}°")
    
    output.append("=" * 70)
    
    return "\n".join(output)
