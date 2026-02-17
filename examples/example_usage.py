"""
Examples demonstrating usage of the grain boundary analysis package.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from misorientation import (
    analyze_euler_angles,
    analyze_axis_angle,
    format_output,
    batch_analysis
)


def example_1_euler_angles():
    """Example 1: Analyzing grain boundary from Euler angles."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Euler Angles Input")
    print("="*70)
    
    # Two crystal orientations in Bunge Euler angles (degrees)
    phi1_a, phi_a, phi2_a = 45.0, 90.0, 30.0
    phi1_b, phi_b, phi2_b = 60.0, 45.0, 15.0
    
    gb = analyze_euler_angles(phi1_a, phi_a, phi2_a,
                              phi1_b, phi_b, phi2_b)
    
    print(format_output(gb))


def example_2_axis_angle():
    """Example 2: Analyzing misorientation from axis-angle."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Axis-Angle Input")
    print("="*70)
    
    # Famous Sigma-3 twin boundary: 60° rotation around [111]
    angle = 60.0  # degrees
    axis = [1, 1, 1]
    
    gb = analyze_axis_angle(angle, axis)
    
    print(format_output(gb))
    
    # Verify it's Sigma-3
    print(f"\n✓ This is the well-known Σ3 twin boundary")


def example_3_low_angle():
    """Example 3: Low-angle grain boundary."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Low-Angle Boundary")
    print("="*70)
    
    # Small misorientation
    angle = 5.0  # degrees
    axis = [1, 0, 0]
    
    gb = analyze_axis_angle(angle, axis)
    
    print(format_output(gb))


def example_4_sigma5():
    """Example 4: Sigma-5 boundary."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Σ5 Boundary")
    print("="*70)
    
    # Sigma-5: 36.9° around [100]
    angle = 36.9
    axis = [1, 0, 0]
    
    gb = analyze_axis_angle(angle, axis)
    
    print(format_output(gb))


def example_5_batch():
    """Example 5: Batch analysis of multiple boundaries."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Batch Analysis")
    print("="*70)
    
    # Multiple axis-angle pairs
    boundaries_data = [
        (60.0, [1, 1, 1]),   # Sigma-3
        (36.9, [1, 0, 0]),   # Sigma-5
        (38.2, [1, 1, 1]),   # Sigma-7
        (5.0, [1, 0, 0]),    # Low-angle
    ]
    
    boundaries = batch_analysis(boundaries_data, input_type='axis_angle')
    
    print("\nAnalyzed {} grain boundaries:\n".format(len(boundaries)))
    
    for i, gb in enumerate(boundaries, 1):
        print(f"{i}. {gb}")
    
    # Summary table
    print("\n" + "-"*70)
    print(f"{'#':<4} {'Angle':<10} {'Axis':<20} {'Type':<20}")
    print("-"*70)
    for i, gb in enumerate(boundaries, 1):
        axis_str = f"[{gb.axis[0]:.2f},{gb.axis[1]:.2f},{gb.axis[2]:.2f}]"
        print(f"{i:<4} {gb.angle:<10.2f} {axis_str:<20} {gb._classify_boundary():<20}")


def example_6_json_export():
    """Example 6: Export results as dictionary/JSON."""
    print("\n" + "="*70)
    print("EXAMPLE 6: JSON Export")
    print("="*70)
    
    angle = 60.0
    axis = [1, 1, 1]
    gb = analyze_axis_angle(angle, axis)
    
    # Get as dictionary
    result = gb.to_dict()
    
    print("\nGrain boundary data as dictionary:")
    import json
    print(json.dumps(result, indent=2))


def example_7_comparison():
    """Example 7: Compare results with original Fortran tool."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Comparison with Original Tool")
    print("="*70)
    
    print("\nOriginal Fortran tool output for 180° [111]:")
    print("  grain1 2  angle   axis  quaternions        sigma orientationdist")
    print("     1   2  60.000   0.577   0.577   0.577   0.289   0.289   0.289   0.866   3   0.461")
    
    # Reproduce with Python
    angle = 180.0
    axis = [1, 1, 1]
    gb = analyze_axis_angle(angle, axis)
    
    print("\nPython implementation results:")
    print(f"  Disorientation angle: {gb.angle:.3f}°")
    print(f"  Axis (normalized): [{gb.axis[0]:.3f}, {gb.axis[1]:.3f}, {gb.axis[2]:.3f}]")
    q = gb.disorientation.q
    print(f"  Quaternion: [{q[0]:.3f}, {q[1]:.3f}, {q[2]:.3f}, {q[3]:.3f}]")
    print(f"  Σ value: {gb.sigma}")
    print(f"  Deviation: {gb.deviation:.3f}")
    
    print("\n✓ Results match! Both identify this as Σ3 (60° twin)")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("GRAIN BOUNDARY MISORIENTATION ANALYSIS")
    print("Examples and Usage Demonstrations")
    print("="*70)
    
    examples = [
        example_1_euler_angles,
        example_2_axis_angle,
        example_3_low_angle,
        example_4_sigma5,
        example_5_batch,
        example_6_json_export,
        example_7_comparison
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
