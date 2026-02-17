# Usage Guide

Comprehensive guide for using PyOri, the grain boundary misorientation analysis package.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Command Line Usage](#command-line-usage)
4. [Python API](#python-api)
5. [Understanding the Output](#understanding-the-output)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/biterik/PyOri.git
cd pyori
```

### Step 2: Set Up Environment

**Option A: Using Conda (Recommended)**

```bash
conda env create -f environment.yml
conda activate pyori
```

**Option B: Using pip**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python examples/example_usage.py
```

If you see output analyzing Σ3, Σ5, and Σ7 boundaries, you're all set!

## Quick Start

### From Command Line

```bash
# Analyze the famous Σ3 twin boundary
python src/cli.py --axis-angle 60 1 1 1

# Analyze from Euler angles
python src/cli.py --euler 0 0 0 45 90 0
```

### From Python

```python
from src import analyze_axis_angle

# Analyze Σ3 twin
gb = analyze_axis_angle(60.0, [1, 1, 1])
print(f"Σ value: {gb.sigma}, Angle: {gb.angle:.2f}°")
```

## Command Line Usage

### Basic Syntax

```bash
python src/cli.py [--euler | --axis-angle] VALUES [OPTIONS]
```

### Input Modes

#### 1. Euler Angles (Bunge Convention)

```bash
python src/cli.py --euler PHI1_A PHI_A PHI2_A PHI1_B PHI_B PHI2_B
```

**Example:**
```bash
python src/cli.py --euler 45 90 30 60 45 15
```

This analyzes the boundary between:
- Grain A: φ₁=45°, Φ=90°, φ₂=30°
- Grain B: φ₁=60°, Φ=45°, φ₂=15°

#### 2. Axis-Angle

```bash
python src/cli.py --axis-angle ANGLE AXIS_X AXIS_Y AXIS_Z
```

**Example:**
```bash
python src/cli.py --axis-angle 60 1 1 1
```

This analyzes a 60° rotation around the [111] axis.

### Output Options

#### Brief Output

```bash
python src/cli.py --axis-angle 60 1 1 1 --brief
```

Shows only essential information.

#### JSON Output

```bash
python src/cli.py --axis-angle 60 1 1 1 --json
```

Outputs results in JSON format for programmatic use.

### Examples

```bash
# Σ3 twin boundary
python src/cli.py --axis-angle 60 1 1 1

# Σ5 boundary
python src/cli.py --axis-angle 36.9 1 0 0

# Σ7 boundary
python src/cli.py --axis-angle 38.2 1 1 1

# Low-angle boundary
python src/cli.py --axis-angle 5 1 0 0

# Random orientation
python src/cli.py --euler 23.5 67.8 41.2 87.3 12.9 55.6
```

## Python API

### Basic Usage

```python
from src import (
    analyze_euler_angles,
    analyze_axis_angle,
    format_output
)

# Method 1: Axis-angle input
gb = analyze_axis_angle(angle=60.0, axis=[1, 1, 1])

# Method 2: Euler angles input
gb = analyze_euler_angles(
    phi1_a=45.0, phi_a=90.0, phi2_a=30.0,
    phi1_b=60.0, phi_b=45.0, phi2_b=15.0
)

# Display results
print(format_output(gb))
```

### Accessing Results

```python
gb = analyze_axis_angle(60.0, [1, 1, 1])

# Basic properties
print(f"Angle: {gb.angle:.2f}°")
print(f"Axis: {gb.axis}")
print(f"Σ value: {gb.sigma}")
print(f"Deviation: {gb.deviation:.3f}")

# Boundary classification
print(f"Type: {gb._classify_boundary()}")

# Quaternion representation
print(f"Quaternion: {gb.disorientation.q}")

# Rodrigues vector
rod = gb.disorientation.to_rodrigues()
print(f"Rodrigues: {rod}")

# Export as dictionary
result = gb.to_dict()
```

### Batch Processing

```python
from src import batch_analysis

# Define multiple boundaries
boundaries_data = [
    (60.0, [1, 1, 1]),   # Σ3
    (36.9, [1, 0, 0]),   # Σ5
    (38.2, [1, 1, 1]),   # Σ7
]

# Analyze all at once
boundaries = batch_analysis(boundaries_data, input_type='axis_angle')

# Process results
for i, gb in enumerate(boundaries, 1):
    print(f"{i}. Σ{gb.sigma}: {gb.angle:.2f}°")
```

### Working with Quaternions Directly

```python
from src.quaternions import (
    Quaternion,
    euler_to_quaternion,
    axis_angle_to_quaternion
)

# Create quaternion from Euler angles
q1 = euler_to_quaternion(45, 90, 30, degrees=True)

# Create quaternion from axis-angle
q2 = axis_angle_to_quaternion(60, [1, 1, 1], degrees=True)

# Calculate misorientation
misori = q1.misorientation(q2)

# Convert to axis-angle
angle, axis = misori.to_axis_angle()
print(f"Misorientation: {angle:.2f}° around {axis}")
```

## Understanding the Output

### Example Output

```
======================================================================
GRAIN BOUNDARY ANALYSIS
======================================================================

Misorientation angle: 60.00°
Rotation axis: [0.577, 0.577, 0.577]
Quaternion: [0.2887, 0.2887, 0.2887, 0.8660]
Rodrigues vector: [0.3333, 0.3333, 0.3333]

Boundary type: CSL Σ3
Σ value: 3
Deviation from exact CSL: 0.000
  (Within Brandon criterion)

Symmetry operators used: (16, 0)

Grain A Euler angles: φ₁=0.00° Φ=0.00° φ₂=0.00°
Grain B Euler angles: φ₁=45.00° Φ=90.00° φ₂=45.00°
======================================================================
```

### Field Descriptions

- **Misorientation angle**: The minimum rotation angle in degrees
- **Rotation axis**: Unit vector defining the rotation axis
- **Quaternion**: [q₁, q₂, q₃, q₄] representation in fundamental zone
- **Rodrigues vector**: [r₁, r₂, r₃] = [q₁/q₄, q₂/q₄, q₃/q₄]
- **Boundary type**: Classification (Low-angle, CSL, Near-CSL, or General)
- **Σ value**: Reciprocal density of coincident sites (lower = more special)
- **Deviation**: Angular deviation / Brandon criterion (< 1.0 = true CSL)
- **Symmetry operators**: Indices of cubic symmetry operations used

### Boundary Classifications

| Type | Description | Σ Value | Deviation |
|------|-------------|---------|-----------|
| Low-angle | θ < 15° | 1 | < 15° |
| CSL Σn | Special boundary | 3-35 | < 1.0 |
| Near-CSL Σn | Close to CSL | 3-35 | ≥ 1.0 |
| General | Random high-angle | None | N/A |

## Advanced Usage

### Custom CSL Identification

```python
from src.csl import CSLIdentifier

csl = CSLIdentifier()

# Get Brandon criterion for Σ5
brandon = csl.brandon_criterion(5)
print(f"Σ5 Brandon criterion: ±{brandon:.2f}°")

# Get all Σ3 variants
sigma3_boundaries = csl.get_boundary_info(3)
for boundary in sigma3_boundaries:
    print(boundary)
```

### Crystal Symmetry Operations

```python
from src.symmetry import CubicSymmetry
from src.quaternions import Quaternion

symm = CubicSymmetry()

# Apply symmetry operation
q = Quaternion([0.1, 0.2, 0.3, 0.9])
q_symm = symm.apply_pre_symmetry(q, index=5)

# Find disorientation
disor, i, j, neg_q4, neg_all = symm.find_disorientation(q)
print(f"Disorientation angle: {disor.to_axis_angle()[0]:.2f}°")
```

### Exporting Results

#### To JSON

```python
import json
from src import analyze_axis_angle

gb = analyze_axis_angle(60, [1, 1, 1])
result = gb.to_dict()

# Save to file
with open('boundary_analysis.json', 'w') as f:
    json.dump(result, f, indent=2)
```

#### To CSV

```python
import csv
from src import batch_analysis

boundaries_data = [(60, [1, 1, 1]), (36.9, [1, 0, 0])]
boundaries = batch_analysis(boundaries_data, input_type='axis_angle')

# Write to CSV
with open('boundaries.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Angle', 'Axis_X', 'Axis_Y', 'Axis_Z', 'Sigma', 'Type'])
    
    for gb in boundaries:
        writer.writerow([
            f"{gb.angle:.2f}",
            f"{gb.axis[0]:.3f}",
            f"{gb.axis[1]:.3f}",
            f"{gb.axis[2]:.3f}",
            gb.sigma,
            gb._classify_boundary()
        ])
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
Make sure you're running from the project root directory or add the src path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
```

#### 2. Numerical Precision

**Problem:** Slightly different results from Fortran code.

**Solution:** This is normal due to:
- Different rounding in numerical libraries
- Order of operations in symmetry search
- Results should agree within ~0.1° for angles

#### 3. Unexpected Σ Values

**Problem:** Expected a specific Σ but got different/None.

**Solution:**
- Check if deviation > 1.0 (outside Brandon criterion)
- Verify input angles are correct
- Some orientations are genuinely not CSL

### Getting Help

1. Check the examples: `python examples/example_usage.py`
2. Run tests: `python tests/test_basics.py`
3. Read the scientific references in README.md
4. Open an issue on GitHub

## Tips and Best Practices

1. **Use axis-angle for known misorientations** - More direct than Euler angles
2. **Check deviation values** - Low deviation means true CSL boundary
3. **Batch process when possible** - More efficient for multiple boundaries
4. **Validate against known boundaries** - Test with Σ3 (60°/[111]) first
5. **Consider numerical precision** - Angles within 0.1° are essentially equal

## References

For theoretical background, see:
- README.md (Scientific Background section)
- Original Fortran code comments
- Sutton & Balluffi textbook on interfaces