"""
Quaternion operations for crystal orientation analysis.

This module provides quaternion-based mathematical operations for
representing and manipulating crystal orientations and misorientations.
"""

import numpy as np
from typing import Union, Tuple


class Quaternion:
    """
    Represents a unit quaternion for 3D rotations.
    
    Convention: q = [q1, q2, q3, q4] where q4 is the scalar part.
    Unit quaternion: q1² + q2² + q3² + q4² = 1
    
    Attributes:
        q (np.ndarray): Array of shape (4,) containing quaternion components
    """
    
    def __init__(self, q: Union[list, np.ndarray]):
        """
        Initialize a quaternion.
        
        Args:
            q: Quaternion components [q1, q2, q3, q4]
        """
        self.q = np.array(q, dtype=float)
        if self.q.shape != (4,):
            raise ValueError("Quaternion must have exactly 4 components")
    
    def normalize(self) -> 'Quaternion':
        """Normalize the quaternion to unit length."""
        norm = np.linalg.norm(self.q)
        if norm > 0:
            self.q = self.q / norm
        return self
    
    def conjugate(self) -> 'Quaternion':
        """Return the conjugate (inverse for unit quaternions)."""
        return Quaternion([-self.q[0], -self.q[1], -self.q[2], self.q[3]])
    
    def multiply(self, other: 'Quaternion') -> 'Quaternion':
        """
        Multiply this quaternion by another: self * other.
        
        Args:
            other: Another quaternion
            
        Returns:
            Product quaternion
        """
        q1, q2 = self.q, other.q
        result = np.array([
            q1[3]*q2[0] + q1[0]*q2[3] + q1[1]*q2[2] - q1[2]*q2[1],
            q1[3]*q2[1] + q1[1]*q2[3] + q1[2]*q2[0] - q1[0]*q2[2],
            q1[3]*q2[2] + q1[2]*q2[3] + q1[0]*q2[1] - q1[1]*q2[0],
            q1[3]*q2[3] - q1[0]*q2[0] - q1[1]*q2[1] - q1[2]*q2[2]
        ])
        return Quaternion(result)
    
    def misorientation(self, other: 'Quaternion') -> 'Quaternion':
        """
        Calculate misorientation as Q1 * Q2^-1.
        
        Args:
            other: Second orientation quaternion
            
        Returns:
            Misorientation quaternion
        """
        return self.multiply(other.conjugate())
    
    def to_axis_angle(self) -> Tuple[float, np.ndarray]:
        """
        Convert quaternion to axis-angle representation.
        
        Returns:
            angle: Rotation angle in degrees
            axis: Rotation axis as unit vector
        """
        # Ensure q4 is in valid range for acos
        q4 = np.clip(self.q[3], -1.0, 1.0)
        angle = 2 * np.arccos(q4) * 180.0 / np.pi
        
        # Handle small angles
        if abs(angle) < 1e-6:
            axis = np.array([0.0, 0.0, 1.0])
        else:
            axis = self.q[:3] / np.linalg.norm(self.q[:3]) if np.linalg.norm(self.q[:3]) > 1e-10 else np.array([0.0, 0.0, 1.0])
        
        return angle, axis
    
    def to_rodrigues(self) -> np.ndarray:
        """
        Convert quaternion to Rodrigues vector.
        
        Returns:
            Rodrigues vector [r1, r2, r3]
        """
        if abs(self.q[3]) < 1e-10:
            return np.array([np.inf, np.inf, np.inf])
        return self.q[:3] / self.q[3]
    
    def __repr__(self) -> str:
        return f"Quaternion([{self.q[0]:.4f}, {self.q[1]:.4f}, {self.q[2]:.4f}, {self.q[3]:.4f}])"


def euler_to_quaternion(phi1: float, phi: float, phi2: float, 
                       degrees: bool = True) -> Quaternion:
    """
    Convert Bunge Euler angles to quaternion (passive rotation).
    
    Based on Altmann's formulation. The Bunge convention uses:
    - First rotation phi1 about Z-axis
    - Second rotation Phi about new X-axis  
    - Third rotation phi2 about new Z-axis
    
    Args:
        phi1: First Euler angle
        phi: Second Euler angle (Phi)
        phi2: Third Euler angle
        degrees: If True, angles are in degrees (default True)
        
    Returns:
        Quaternion representing the orientation
    """
    if degrees:
        phi1 = np.radians(phi1)
        phi = np.radians(phi)
        phi2 = np.radians(phi2)
    
    # Half angles
    c1 = np.cos(0.5 * (phi1 - phi2))
    s1 = np.sin(0.5 * (phi1 - phi2))
    c2 = np.cos(0.5 * (phi1 + phi2))
    s2 = np.sin(0.5 * (phi1 + phi2))
    c = np.cos(0.5 * phi)
    s = np.sin(0.5 * phi)
    
    q = np.array([
        s * c1,
        s * s1,
        c * s2,
        c * c2
    ])
    
    return Quaternion(q)


def axis_angle_to_quaternion(angle: float, axis: np.ndarray, 
                             degrees: bool = True) -> Quaternion:
    """
    Convert axis-angle representation to quaternion.
    
    Args:
        angle: Rotation angle
        axis: Rotation axis [x, y, z]
        degrees: If True, angle is in degrees (default True)
        
    Returns:
        Quaternion representing the rotation
    """
    axis = np.array(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)  # Normalize
    
    if degrees:
        angle = np.radians(angle)
    
    half_angle = angle / 2.0
    sin_half = np.sin(half_angle)
    
    q = np.array([
        axis[0] * sin_half,
        axis[1] * sin_half,
        axis[2] * sin_half,
        np.cos(half_angle)
    ])
    
    return Quaternion(q)


def quaternion_to_euler(q: Quaternion) -> Tuple[float, float, float]:
    """
    Convert quaternion to Bunge Euler angles.
    
    Args:
        q: Input quaternion
        
    Returns:
        phi1, phi, phi2: Euler angles in degrees
    """
    quat = q.q
    
    # Handle special cases for atan2
    if abs(quat[1]) < 1e-35 and abs(quat[0]) < 1e-35:
        diff = np.pi / 4.0
    else:
        diff = np.arctan2(quat[1], quat[0])
    
    if abs(quat[2]) < 1e-35 and abs(quat[3]) < 1e-35:
        sum_angle = np.pi / 4.0
    else:
        sum_angle = np.arctan2(quat[2], quat[3])
    
    phi1 = diff + sum_angle
    phi2 = sum_angle - diff
    
    tmp = np.sqrt(quat[2]**2 + quat[3]**2)
    tmp = np.clip(tmp, 0.0, 1.0)
    phi = 2.0 * np.arccos(tmp)
    
    # Convert to degrees
    phi1_deg = np.degrees(phi1)
    phi_deg = np.degrees(phi)
    phi2_deg = np.degrees(phi2)
    
    # Normalize to [0, 360)
    phi1_deg = phi1_deg % 360.0
    phi2_deg = phi2_deg % 360.0
    
    return phi1_deg, phi_deg, phi2_deg
