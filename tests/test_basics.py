"""
Basic tests for grain boundary misorientation analysis package.

Run with: pytest test_basics.py -v
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from quaternions import (
    Quaternion, 
    euler_to_quaternion, 
    axis_angle_to_quaternion,
    quaternion_to_euler
)
from misorientation import analyze_axis_angle, analyze_euler_angles


class TestQuaternions:
    """Test quaternion operations."""
    
    def test_quaternion_creation(self):
        """Test basic quaternion creation."""
        q = Quaternion([0, 0, 0, 1])
        assert np.allclose(q.q, [0, 0, 0, 1])
    
    def test_quaternion_normalization(self):
        """Test quaternion normalization."""
        q = Quaternion([1, 1, 1, 1])
        q.normalize()
        assert np.isclose(np.linalg.norm(q.q), 1.0)
    
    def test_identity_quaternion(self):
        """Test identity quaternion (no rotation)."""
        q = Quaternion([0, 0, 0, 1])
        angle, axis = q.to_axis_angle()
        assert np.isclose(angle, 0.0, atol=1e-6)
    
    def test_axis_angle_conversion(self):
        """Test axis-angle to quaternion conversion."""
        angle = 90.0  # degrees
        axis = [1, 0, 0]
        q = axis_angle_to_quaternion(angle, axis, degrees=True)
        
        # Check quaternion norm
        assert np.isclose(np.linalg.norm(q.q), 1.0)
        
        # Convert back
        angle_back, axis_back = q.to_axis_angle()
        assert np.isclose(angle_back, angle, atol=0.1)
    
    def test_euler_conversion(self):
        """Test Euler angle to quaternion conversion."""
        phi1, phi, phi2 = 45.0, 90.0, 30.0
        q = euler_to_quaternion(phi1, phi, phi2, degrees=True)
        
        # Check quaternion norm
        assert np.isclose(np.linalg.norm(q.q), 1.0)
        
        # Convert back
        phi1_back, phi_back, phi2_back = quaternion_to_euler(q)
        
        # Check angles (allowing for periodicity)
        assert np.isclose(phi_back, phi, atol=1.0)


class TestCSLBoundaries:
    """Test CSL boundary identification."""
    
    def test_sigma3_twin(self):
        """Test identification of Σ3 twin boundary."""
        # 60° around [111] is the famous Σ3 twin
        gb = analyze_axis_angle(60.0, [1, 1, 1])
        
        assert gb.sigma == 3
        assert np.isclose(gb.angle, 60.0, atol=1.0)
        assert gb.deviation < 1.0  # Within Brandon criterion
    
    def test_sigma5_boundary(self):
        """Test identification of Σ5 boundary."""
        # 36.9° around [100]
        gb = analyze_axis_angle(36.9, [1, 0, 0])
        
        assert gb.sigma == 5
        assert np.isclose(gb.angle, 36.9, atol=1.0)
        assert gb.deviation < 1.0
    
    def test_low_angle_boundary(self):
        """Test low-angle boundary identification."""
        # Small misorientation should be Σ1
        gb = analyze_axis_angle(5.0, [1, 0, 0])
        
        assert gb.sigma == 1
        assert gb.angle < 15.0
    
    def test_general_boundary(self):
        """Test general high-angle boundary."""
        # Random orientation should not be CSL
        gb = analyze_axis_angle(27.5, [1, 2, 3])
        
        # Should either be None or have high deviation
        if gb.sigma is not None:
            assert gb.deviation > 1.0 or gb.sigma == 1


class TestDisorientation:
    """Test disorientation calculation."""
    
    def test_disorientation_fundamental_zone(self):
        """Test that disorientation is in fundamental zone."""
        gb = analyze_axis_angle(60.0, [1, 1, 1])
        
        q = gb.disorientation.q
        # Check fundamental zone: 0 <= q1 <= q2 <= q3 <= q4
        assert q[0] >= 0
        assert q[0] <= q[1]
        assert q[1] <= q[2]
        assert q[2] <= q[3]
    
    def test_symmetry_equivalence(self):
        """Test that symmetric orientations give same disorientation."""
        # Two different representations of same boundary
        gb1 = analyze_axis_angle(60.0, [1, 1, 1])
        gb2 = analyze_axis_angle(60.0, [-1, -1, -1])
        
        # Should have same disorientation angle
        assert np.isclose(gb1.angle, gb2.angle, atol=0.1)


class TestEulerAngles:
    """Test Euler angle input."""
    
    def test_euler_input(self):
        """Test analysis from Euler angles."""
        gb = analyze_euler_angles(
            phi1_a=0.0, phi_a=0.0, phi2_a=0.0,
            phi1_b=45.0, phi_b=90.0, phi2_b=0.0
        )
        
        # Should produce valid results
        assert gb.angle >= 0.0
        assert gb.angle <= 62.8  # Maximum for cubic
        assert np.isclose(np.linalg.norm(gb.axis), 1.0)
    
    def test_identity_orientation(self):
        """Test that identical orientations give zero misorientation."""
        gb = analyze_euler_angles(
            phi1_a=45.0, phi_a=90.0, phi2_a=30.0,
            phi1_b=45.0, phi_b=90.0, phi2_b=30.0
        )
        
        # Should be very small angle
        assert gb.angle < 1.0


def test_comparison_with_fortran():
    """
    Test comparison with original Fortran output.
    
    Original output for 180° [111]:
    grain1 2  angle   axis  quaternions        sigma orientationdist
       1   2  60.000   0.577   0.577   0.577   0.289   0.289   0.289   0.866   3   0.461
    """
    gb = analyze_axis_angle(180.0, [1, 1, 1])
    
    # Check angle
    assert np.isclose(gb.angle, 60.0, atol=0.1)
    
    # Check axis (normalized [111])
    expected_axis = np.array([1, 1, 1]) / np.sqrt(3)
    assert np.allclose(gb.axis, expected_axis, atol=0.01)
    
    # Check quaternion
    q = gb.disorientation.q
    assert np.isclose(q[0], 0.289, atol=0.01)
    assert np.isclose(q[1], 0.289, atol=0.01)
    assert np.isclose(q[2], 0.289, atol=0.01)
    assert np.isclose(q[3], 0.866, atol=0.01)
    
    # Check sigma
    assert gb.sigma == 3


if __name__ == '__main__':
    # Run tests without pytest
    print("Running basic tests...")
    
    test_q = TestQuaternions()
    test_q.test_quaternion_creation()
    test_q.test_quaternion_normalization()
    test_q.test_identity_quaternion()
    test_q.test_axis_angle_conversion()
    test_q.test_euler_conversion()
    print("✓ Quaternion tests passed")
    
    test_csl = TestCSLBoundaries()
    test_csl.test_sigma3_twin()
    test_csl.test_sigma5_boundary()
    test_csl.test_low_angle_boundary()
    test_csl.test_general_boundary()
    print("✓ CSL boundary tests passed")
    
    test_dis = TestDisorientation()
    test_dis.test_disorientation_fundamental_zone()
    test_dis.test_symmetry_equivalence()
    print("✓ Disorientation tests passed")
    
    test_euler = TestEulerAngles()
    test_euler.test_euler_input()
    test_euler.test_identity_orientation()
    print("✓ Euler angle tests passed")
    
    test_comparison_with_fortran()
    print("✓ Fortran comparison test passed")
    
    print("\nAll tests passed! ✓")
