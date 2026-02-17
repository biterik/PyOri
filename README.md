# PyOri - Grain Boundary Misorientation Analysis

> **Note:** This project is under active development. APIs and features may change without notice.

A Python package for analyzing grain boundaries in cubic crystals using quaternion-based methods. This tool calculates misorientations, identifies Coincidence Site Lattice (CSL) boundaries, and applies crystal symmetry operations.

**Converted from Fortran code originally by A. Rollett et al.**

## Features

- ✨ **Quaternion-based orientation representation** - Robust and singularity-free
- 🔄 **Cubic crystal symmetry operations** - All 24 proper rotations
- 📊 **CSL boundary identification** - Σ3 to Σ35 with Brandon criterion
- 🎯 **Disorientation calculation** - Minimum angle in fundamental zone
- 📥 **Multiple input formats** - Euler angles or axis-angle
- 🔧 **Clean Python API** - Object-oriented and type-annotated

## Installation

### Using Conda (Recommended)

```bash
# Clone the repository
git clone https://github.com/biterik/PyOri.git
cd pyori

# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate pyori
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/biterik/PyOri.git
cd pyori

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Command Line Interface

```bash
# Analyze from Euler angles (Bunge convention)
python src/cli.py --euler 45 90 30 60 45 15

# Analyze from axis-angle representation
python src/cli.py --axis-angle 60 1 1 1

# Get brief output
python src/cli.py --axis-angle 60 1 1 1 --brief

# Export as JSON
python src/cli.py --euler 45 90 30 60 45 15 --json
```

### Python API

```python
from src import analyze_euler_angles, analyze_axis_angle, format_output

# Example 1: Euler angles (Bunge convention)
gb = analyze_euler_angles(
    phi1_a=45.0, phi_a=90.0, phi2_a=30.0,  # Grain A
    phi1_b=60.0, phi_b=45.0, phi2_b=15.0   # Grain B
)

print(format_output(gb))

# Example 2: Axis-angle (famous Σ3 twin)
gb = analyze_axis_angle(angle=60.0, axis=[1, 1, 1])

print(f"Angle: {gb.angle:.2f}°")
print(f"Axis: {gb.axis}")
print(f"Σ value: {gb.sigma}")
print(f"Type: {gb._classify_boundary()}")
```

## Usage Examples

### Example 1: Σ3 Twin Boundary

```python
from src import analyze_axis_angle, format_output

# 60° rotation around [111] - the famous coherent twin
gb = analyze_axis_angle(60.0, [1, 1, 1])
print(format_output(gb))
```

Output:
```
======================================================================
GRAIN BOUNDARY ANALYSIS
======================================================================

Misorientation angle: 60.00°
Rotation axis: [0.577, 0.577, 0.577]
Quaternion: [0.2887, 0.2887, 0.2887, 0.8660]

Boundary type: CSL Σ3
Σ value: 3
Deviation from exact CSL: 0.000
  (Within Brandon criterion)
======================================================================
```

### Example 2: Batch Analysis

```python
from src import batch_analysis

boundaries_data = [
    (60.0, [1, 1, 1]),   # Σ3
    (36.9, [1, 0, 0]),   # Σ5
    (38.2, [1, 1, 1]),   # Σ7
]

boundaries = batch_analysis(boundaries_data, input_type='axis_angle')

for i, gb in enumerate(boundaries, 1):
    print(f"{i}. {gb}")
```

### Example 3: Full Analysis from Euler Angles

```python
from src import analyze_euler_angles

# Two crystal orientations
gb = analyze_euler_angles(
    phi1_a=0.0, phi_a=0.0, phi2_a=0.0,      # Reference orientation
    phi1_b=45.0, phi_b=90.0, phi2_b=0.0     # Rotated orientation
)

# Access results
result = gb.to_dict()
print(f"Angle: {result['angle']:.2f}°")
print(f"Boundary type: {result['boundary_type']}")
```

## Project Structure

```
pyori/
├── README.md
├── environment.yml          # Conda environment
├── requirements.txt         # pip requirements
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── quaternions.py       # Quaternion operations
│   ├── symmetry.py          # Crystal symmetry
│   ├── csl.py              # CSL identification
│   ├── misorientation.py   # Main analysis
│   └── cli.py              # Command-line interface
└── examples/
    └── example_usage.py    # Comprehensive examples
```

## Scientific Background

### Quaternions

This package uses unit quaternions q = [q₁, q₂, q₃, q₄] to represent crystal orientations, where q₁² + q₂² + q₃² + q₄² = 1.

### Disorientation

The disorientation is the minimum misorientation angle obtained by applying all symmetry operations. For cubic crystals, this involves testing 24×24 = 576 symmetry combinations.

### CSL Boundaries

Coincidence Site Lattice boundaries are identified using:
- **Brandon criterion**: Δθ_max = 15° / √Σ
- **Σ values**: 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35

### Conventions

- **Euler angles**: Bunge convention (φ₁, Φ, φ₂)
- **Rotation**: Passive (coordinate transformation)
- **Crystal symmetry**: Cubic (m3m point group)

## Comparison with Original Fortran Code

| Feature | Fortran | Python |
|---------|---------|--------|
| Input | File or interactive | API or CLI |
| Quaternions | ✓ | ✓ |
| Cubic symmetry | 24 operators | 24 operators |
| CSL identification | Brandon criterion | Brandon criterion |
| Numerical accuracy | Comparable | Comparable |
| Speed | Fast | Fast (NumPy) |
| Code clarity | Legacy style | Modern OOP |

## Dependencies

- **Python** ≥ 3.8
- **NumPy** ≥ 1.20.0 (array operations, linear algebra)

## API Reference

### Main Functions

#### `analyze_euler_angles(phi1_a, phi_a, phi2_a, phi1_b, phi_b, phi2_b, degrees=True)`
Analyze grain boundary from Bunge Euler angles.

#### `analyze_axis_angle(angle, axis, degrees=True)`
Analyze misorientation from axis-angle representation.

#### `batch_analysis(orientations, input_type='euler')`
Analyze multiple grain boundaries at once.

### Classes

#### `GrainBoundary`
Represents a grain boundary with all calculated properties.

**Attributes:**
- `angle` - Misorientation angle (degrees)
- `axis` - Rotation axis (unit vector)
- `disorientation` - Quaternion in fundamental zone
- `sigma` - CSL Σ value (or None)
- `deviation` - Deviation from exact CSL

**Methods:**
- `to_dict()` - Export as dictionary
- `_classify_boundary()` - Get boundary type string

#### `Quaternion`
Unit quaternion for rotations.

**Methods:**
- `normalize()` - Normalize to unit length
- `conjugate()` - Get conjugate
- `multiply(other)` - Quaternion multiplication
- `to_axis_angle()` - Convert to axis-angle
- `to_rodrigues()` - Convert to Rodrigues vector

## Testing

Run the examples to verify installation:

```bash
python examples/example_usage.py
```

Expected output includes analyses of Σ3, Σ5, Σ7 boundaries and comparison with original Fortran tool.

## Contributing

Contributions are welcome! Areas for potential enhancement:
- Additional crystal symmetries (hexagonal, orthorhombic)
- Grain boundary plane calculations
- Visualization tools
- Performance optimization for large datasets

## Citation

If you use this code in research, please cite the original work:

```
Rollett, A.D. et al. (2003). Grain Boundary Misorientation Tool (REXGBS).
Carnegie Mellon University.
```

## License

This code is provided for educational and research purposes. Please respect the original Fortran code's licensing terms.

## References

1. Grimmer, H., Bollmann, W., & Warrington, D. H. (1974). Coincidence-site lattices and complete pattern-shift in cubic crystals. *Acta Crystallographica Section A*, 30(2), 197-207.

2. Brandon, D. G. (1966). The structure of high-angle grain boundaries. *Acta Metallurgica*, 14(11), 1479-1484.

3. Randle, V., & Engler, O. (2000). *Introduction to Texture Analysis: Macrotexture, Microtexture, and Orientation Mapping*. CRC Press.

4. Sutton, A. P., & Balluffi, R. W. (1995). *Interfaces in Crystalline Materials*. Oxford University Press.

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

## Acknowledgments

- Original Fortran code by Anthony D. Rollett and colleagues
- Dierk Raabe for MISORI subroutine
- Paul Lee for testing and validation