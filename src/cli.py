#!/usr/bin/env python3
"""
Command-line interface for grain boundary misorientation analysis.

Usage:
    python cli.py --euler 45 90 30 60 45 15
    python cli.py --axis-angle 60 1 1 1
    python cli.py --help
"""

import argparse
import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from misorientation import (
    analyze_euler_angles,
    analyze_axis_angle,
    format_output
)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Grain Boundary Misorientation Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Euler angles (Bunge convention):
    %(prog)s --euler 45 90 30 60 45 15
    
  Axis-angle representation:
    %(prog)s --axis-angle 60 1 1 1
    
  With brief output:
    %(prog)s --euler 45 90 30 60 45 15 --brief
        """
    )
    
    # Input mode selection
    input_group = parser.add_mutually_exclusive_group(required=True)
    
    input_group.add_argument(
        '--euler',
        nargs=6,
        type=float,
        metavar=('PHI1_A', 'PHI_A', 'PHI2_A', 'PHI1_B', 'PHI_B', 'PHI2_B'),
        help='Bunge Euler angles (degrees) for grains A and B'
    )
    
    input_group.add_argument(
        '--axis-angle',
        nargs=4,
        type=float,
        metavar=('ANGLE', 'AXIS_X', 'AXIS_Y', 'AXIS_Z'),
        help='Misorientation as axis-angle: angle (degrees) and axis [x,y,z]'
    )
    
    # Output options
    parser.add_argument(
        '--brief',
        action='store_true',
        help='Show brief output (less verbose)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Perform analysis based on input type
    try:
        if args.euler:
            phi1_a, phi_a, phi2_a, phi1_b, phi_b, phi2_b = args.euler
            gb = analyze_euler_angles(phi1_a, phi_a, phi2_a, 
                                     phi1_b, phi_b, phi2_b)
            
            print(f"\nInput: Euler angles (Bunge convention, degrees)")
            print(f"  Grain A: φ₁={phi1_a}° Φ={phi_a}° φ₂={phi2_a}°")
            print(f"  Grain B: φ₁={phi1_b}° Φ={phi_b}° φ₂={phi2_b}°")
        
        elif args.axis_angle:
            angle, ax, ay, az = args.axis_angle
            axis = [ax, ay, az]
            gb = analyze_axis_angle(angle, axis)
            
            print(f"\nInput: Axis-angle representation")
            print(f"  Angle: {angle}°")
            print(f"  Axis: [{ax}, {ay}, {az}]")
        
        # Output results
        if args.json:
            import json
            print("\n" + json.dumps(gb.to_dict(), indent=2))
        else:
            print()
            print(format_output(gb, verbose=not args.brief))
        
        return 0
    
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
